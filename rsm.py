from kazoo.client import KazooClient
import kazoo.exceptions as zke
from kazoo.protocol.states import EventType

import signal
import sys
import time
import random
import leveldb
from concurrent import futures
import threading

import grpc
import rsm_pb2
import rsm_pb2_grpc
import database_pb2
import database_pb2_grpc

def othernodes(nodes, port):
    '''
    Helper function to extract peers by eliminating my nodeport
    Args:
        nodes: set of all nodes in the network
        port: my port
    returns:
        list of peers
    '''
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    mynodeport = s.getsockname()[0] + ":" + port
    myaddresses = [mynodeport, "localhost:"+port, "127.0.0.1:"+port]
    ret = [nodeport for nodeport in nodes if nodeport not in myaddresses]
    return ret

class Leader(database_pb2_grpc.DatabaseServicer):
    '''
    Leader class that listens for input get/put RPC requests from the upper layer
    '''
    def __init__(self, rsm):
        self.rsm = rsm 
    
    def Get(self, request, context):
        return database_pb2.GetResponse(value=self.rsm.get(request.key))
    
    def Put(self, request, context):
        self.rsm.put(request.key, request.value)
        return database_pb2.PutResponse(errormsg="")

    def serve(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        database_pb2_grpc.add_DatabaseServicer_to_server(self, server)
        server.add_insecure_port('[::]:' + "50051")
        server.start()
        print("Server started, listening on " + "50051")
        server.wait_for_termination()

class Follower(rsm_pb2_grpc.RSMServicer):
    '''
    Follower class that listens to AppendEntries to replicate distributed log
    '''
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
        # send my log length if master tries to append past my log length
        if len(self.rsm.log) != request.index:
            return rsm_pb2.AppendEntriesResponse(success=False, index=len(self.rsm.log))
        # append all entries in the request to my replicated log and return success
        for e in request.entries:
            self.rsm.log.append(e)
            self.rsm.db.Put(bytearray(e.key, 'utf-8'), bytearray(e.value, 'utf-8'))
            self.rsm.persistLog(e)

        return rsm_pb2.AppendEntriesResponse(success=True, index=len(self.rsm.log))

    def GetCommitIndex(self, request, context):
        # return my log length to peer. Used in leader election
        return rsm_pb2.GetCommitIndexResponse(commitindex=len(self.rsm.log))

class LeaderElection:
    ''' 
    Leader Election module for the Replicated state machine
    '''
    def __init__(self, id, rsm) -> None:
        self.myID = id
        self.currLeader = ""
        self.rsm = rsm
    
    def contest(self) -> None:
        # Contest in election
        self.rsm.zk.ensure_path("/election")

        peerNumProcessedEntries = -1
        peerid = ""
        while peerNumProcessedEntries == -1:
            # can't proceed since we have only 1 active node (that is us)
            children = self.rsm.zk.get_children("/cluster")
            for c in children:
                if c != self.myID:
                    try:
                        with grpc.insecure_channel(self.rsm.getpeer(c)) as channel:
                            stub = rsm_pb2_grpc.RSMStub(channel)
                            response = stub.GetCommitIndex(rsm_pb2.GetCommitIndexRequest())
                            peerNumProcessedEntries = max(response.commitindex, peerNumProcessedEntries)
                            peerid = c
                    except Exception as e:
                        # other follower died too! wait until f+1 nodes back up
                        break
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
            # allow peer to become the leader as it has a longer log
            self.rsm.zk.exists("/election/leader", watch=self.rsm.watchLeaderFile)
            self.currLeader = peerid
    
    def leader(self) -> bool:
        # check if I am the leader
        return self.myID == self.currLeader

class ReplicatedStateMachine:
    '''
    The replicated state machine
    '''
    def getpeer(self, port):
        '''
        Helper function to get a peer when it's port is given
        '''
        for np in self.peers:
            if port == np.split(':')[1]:
                return np
        return ""

    def setupDB(self, id):
        '''
        Helper method to set up levelDB
        '''
        dbpath = './{}_db'.format(id)
        #from shutil import rmtree
        #rmtree(dbpath, ignore_errors=True)
        self.db = leveldb.LevelDB(dbpath)

    def persistLog(self, entry):
        '''
        Helper to persist log entry to disk
        '''
        logpath = './{}_log'.format(self.port)
        with open(logpath, 'a') as file:
            file.write(entry.command + " " + entry.key + " " + entry.value+"\n")
    
    def retreivePersistedLog(self):
        '''
        Helper function to fetch log entries to memory upon start up
        '''
        logpath = './{}_log'.format(self.port)
        try:
            with open(logpath, 'r') as file:
                entries = file.readlines()
                for e in entries:
                    if e == "":
                        continue
                    elst = e.split(" ")
                    self.log.append(rsm_pb2.LogEntry(command=elst[0], key=elst[1], value=elst[1]))
        except OSError:
            # ignore if file not found
            return
        
    def __init__(self, port, peers):
        self.zk = KazooClient(hosts='127.0.0.1:2181')
        self.zk.start()
        self.isFollower = True
        self.electionModule = LeaderElection(port, self)
        self.port = port
        self.log = []       # log of ReplicatedLogEntries
        self.peers = peers

        self.retreivePersistedLog()

        #set up levelDB
        self.setupDB(port)

        self.zk.ensure_path("/cluster")
        self.zk.create("/cluster/"+self.port, ephemeral=True)
        
        self.replicateFollower1 = futures.ThreadPoolExecutor(max_workers=1)
        self.replicateFollower2 = futures.ThreadPoolExecutor(max_workers=1)
        
        signal.signal(signal.SIGINT, self.signal_handler)

    
    def __del__(self):
        self.zk.stop()
    
    def watchLeaderFile(self, event):
        '''
        Kazoo watcher to trigger election when leader dies
        '''
        if event.type == EventType.DELETED:
            self.isFollower = False
        elif event.type == EventType.CREATED:
            data = self.zk.get("/election/leader")
            self.electionModule.currLeader = data[0].decode()

    def run(self):
        while True:
            # need followers to listen for GetCommitIndex RPC calls
            follower = Follower(self)
            self.electionModule.contest()
            del follower

            if self.electionModule.leader():
                self.isFollower = False
                self.leader_function()
            else:
                self.isFollower = True
                self.follower_function()

    def leader_function(self):
        '''
        wait for incoming upper layer requests (GET/PUT)
        '''
        print("I'm the king of the world ")
        leader = Leader(self)
        leader.serve()
    
    def signal_handler(self, sig, frame):
        print('You pressed Ctrl+C!')
        self.zk.stop()
        sys.exit(0)
    
    def follower_function(self):
        '''
        Wait for replication events from leader
        '''
        print("I hate following others ")
        follower = Follower(self)
        while self.isFollower:
            time.sleep(1)
        del follower
    
    def __appendEntries(self, follower, currentry, idx):
        '''
        Thread that appends replicated log enttries to followers
        '''
        with grpc.insecure_channel(follower) as channel:
            stub = rsm_pb2_grpc.RSMStub(channel)
            response = rsm_pb2.AppendEntriesResponse(success=False, index=0)
            entries = [currentry]
            reqidx = idx
            while response.success == False:
                
                try:
                    response = stub.AppendEntries(rsm_pb2.AppendEntriesRequest(index=reqidx, entries=entries), timeout=0.5)
                except Exception as e:
                    time.sleep(0.5)
                    # timeout
                    continue

                # client caught up
                if response.success:
                    return

                # send log entries from follower requested index
                reqidx = response.index
                entries = self.log[reqidx:]
                
                # do not miss current entry when sending log entries from requested index
                # this condition distinguishes 2 cases:
                # 1. Follower catching up after it restarted. 
                #       currentry might have been replicated in another follower and added to self.log 
                # 2. Follower catching up. Other follower is currently dead. 
                #       Meaning catchup is requried and currentry must also be sent as it is commited to self.log after committing in the follower
                if idx == len(self.log):
                    entries.append(currentry)

    def put(self, key, value):
        if self.isFollower:
            return False
        
        currentry = rsm_pb2.LogEntry(command="PUT", key=key, value=value)
        idx = len(self.log)

        # Submit jobs to append entries in followers
        f1 = self.replicateFollower1.submit(self.__appendEntries, follower=self.peers[0], currentry=currentry, idx=idx)
        f2 = self.replicateFollower2.submit(self.__appendEntries, follower=self.peers[1], currentry=currentry, idx=idx)

        while True:
            # If either one is done, majority replication achieved. break
            if f1.done() or f2.done():
                break
            time.sleep(0.1)

        # commit to log after ack from follower
        self.log.append(currentry)
        self.persistLog(currentry)
        self.db.Put(bytearray(key, 'utf-8'), bytearray(value, 'utf-8'))

        # respond sucess
        return True
    
    def get(self, key):
        # get from local db
        # GETs from upper layer are sent only to the leader, strong consistency
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