from kazoo.client import KazooClient
import kazoo.exceptions as zke
from kazoo.protocol.states import EventType
import signal
import sys
import time
import random
import leveldb
import grpc
import rsm_pb2
import rsm_pb2_grpc
import database_pb2
import database_pb2_grpc
from concurrent import futures
import threading

def othernodes(nodes, port):
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    mynodeport = s.getsockname()[0] + ":" + port
    myaddresses = [mynodeport, "localhost:"+port, "127.0.0.1:"+port]
    ret = [nodeport for nodeport in nodes if nodeport not in myaddresses]
    return ret

class Leader(database_pb2_grpc.DatabaseServicer):
    def __init__(self, rsm):
        self.rsm = rsm
    
    def Get(self, request, context):
        return database_pb2.GetResponse(value=self.rsm.get(request.key))
    
    def Put(self, request, context):
        self.rsm.put(request.key, request.value)
        return database_pb2.PutResponse(errormsg="")

    def serve(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        database_pb2_grpc.add_DatabaseServicer_to_server(self, server)
        server.add_insecure_port('[::]:' + "50051")
        server.start()
        print("Server started, listening on " + "50051")
        server.wait_for_termination()

class Follower(rsm_pb2_grpc.RSMServicer):
    def __init__(self, rsm):
        self.rsm = rsm
        _thread = threading.Thread(target= self.__grpcServerThread)
        _thread.start()

    def __grpcServerThread(self):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        rsm_pb2_grpc.add_RSMServicer_to_server(self, self.server)
        self.server.add_insecure_port('[::]:' + self.rsm.port)
        self.server.start()
        self.server.wait_for_termination()
    
    def __del__(self):
        self.server.stop()

    def AppendEntries(self, request, context):
        if len(self.rsm.log) != request.index:
            return rsm_pb2.AppendEntriesResponse(success=False, index=len(self.rsm.log))
        for e in request.entries:
            # TODO persist replicated log
            self.rsm.log.append(e)
            self.rsm.db.Put(bytearray(e.key, 'utf-8'), bytearray(e.value, 'utf-8'))
        
        self.rsm.zk.set("/cluster/"+self.rsm.port, value=bytes(str(len(self.rsm.log)), encoding='utf8'))

        return rsm_pb2.AppendEntriesResponse(success=True, index=len(self.rsm.log))

class LeaderElection:
    def __init__(self, id, rsm) -> None:
        self.myID = id
        self.currLeader = ""
        self.rsm = rsm
    
    def contest(self) -> None:
        self.rsm.zk.ensure_path("/election")

        peerNumProcessedEntries = -1
        peerid = ""
        while peerNumProcessedEntries == -1:
            # can't proceed since we have only 1 active node (that is us)
            children = self.rsm.zk.get_children("/cluster")
            for c in children:
                if c != self.myID:
                    data = self.rsm.zk.get("/cluster/"+c)
                    peerNumProcessedEntries = max(int(data[0].decode()), peerNumProcessedEntries)
                    peerid = c
            # wait until another node comes up
            time.sleep(0.1)
        
        if peerNumProcessedEntries <= len(self.rsm.log):
            # Try to become a leader
            try:
                self.rsm.zk.create("/election/leader", value=bytes(self.myID, encoding='utf8'), ephemeral=True)
                self.currLeader = self.myID
            except zke.NodeExistsError:
                # leader already exists
                data = self.rsm.zk.get("/election/leader", watch=self.rsm.watchLeaderFile)
                self.currLeader = data[0].decode()
        else:
            # allow peer to become the leader
            self.rsm.zk.exists("/election/leader", watch=self.rsm.watchLeaderFile)
            self.currLeader = peerid
    
    def leader(self) -> bool:
        return self.myID == self.currLeader

class ReplicatedLogEntry:
    def __init__(self, key, value) -> None:
        self.operation = "PUT"
        self.key = key
        self.value = value

class ReplicatedStateMachine:
    def setupDB(self, id):
        path ='./{}_db'.format(id)
        from shutil import rmtree
        rmtree(path, ignore_errors=True)
        self.db = leveldb.LevelDB(path)

    def __init__(self, port, peers):
        self.zk = KazooClient(hosts='127.0.0.1:2181')
        self.zk.start()
        self.isFollower = True
        self.electionModule = LeaderElection(port, self)
        self.port = port
        self.log = []       # log of ReplicatedLogEntries
        self.peers = peers

        self.zk.ensure_path("/cluster")
        self.zk.create("/cluster/"+self.port, value=bytes(str(len(self.log)), encoding='utf8'), ephemeral=True)
        signal.signal(signal.SIGINT, self.signal_handler)

        #set up levelDB
        self.setupDB(id)

    
    def __del__(self):
        self.zk.stop()
    
    def watchLeaderFile(self, event):
        if event.type == EventType.DELETED:
            self.isFollower = False
        elif event.type == EventType.CREATED:
            data = self.zk.get("/election/leader")
            self.electionModule.currLeader = data[0].decode()

    def run(self):
        while True:
            self.electionModule.contest()
            if self.electionModule.leader():
                self.isFollower = False
                self.leader_function()
                # TODO: wait for requests
            else:
                self.isFollower = True
                self.follower_function()

    def leader_function(self):
        print("I'm the king of the world ")
        leader = Leader(self)
        leader.serve()
    
    def signal_handler(self, sig, frame):
        print('You pressed Ctrl+C!')
        self.zk.stop()
        sys.exit(0)
    
    def follower_function(self):
        print("I hate following others ")
        follower = Follower(self)
        while self.isFollower:
            time.sleep(1)
        del follower
    
    def put(self, key, value):
        if self.isFollower:
            return False

        # broadcast to followers
        # TODO move to queue model
        for follower in self.peers:
            with grpc.insecure_channel(follower) as channel:
                stub = rsm_pb2_grpc.RSMStub(channel)
                response = rsm_pb2.AppendEntriesResponse(success=False, index=0)
                idx = len(self.log)
                while response.success == False:
                    entries = self.log[idx:]
                    entries.append(rsm_pb2.LogEntry(command="PUT", key=key, value=value))
                    response = stub.AppendEntries(rsm_pb2.AppendEntriesRequest(index=idx, entries=entries))
                    idx = response.index

        # commit to log after ack from follower
        self.log.append(rsm_pb2.LogEntry(command="PUT", key=key, value=value))
        self.db.Put(bytearray(key, 'utf-8'), bytearray(value, 'utf-8'))
        self.zk.set("/cluster/"+self.port, value=bytes(str(len(self.log)), encoding='utf8'))

        # respond sucess
        return True
    
    def get(self, key):
        try:
            val = self.db.Get(bytearray(key, 'utf-8'))
        except Exception as e:
            return ""
        return val.decode()

if __name__ == "__main__":
    
    # parse CLI inputs
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', help='My replicated state machine port', required=True)
    parser.add_argument('-n', '--nodes', nargs='*', help='node-ports of all quorum nodes (space separated). e.g. -n 10.0.0.1:5001 10.0.0.1:5002 10.0.0.1:5003', required=True)
    args = parser.parse_args()

    rsm = ReplicatedStateMachine(args.port, othernodes(args.nodes, args.port))     # port will act as unique ID
    rsm.run()