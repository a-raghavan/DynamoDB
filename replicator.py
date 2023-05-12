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
import antientropy_pb2
import antientropy_pb2_grpc
import database_pb2
import database_pb2_grpc
from merkletree import *

import threading

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

class Entry:
    def __init__(self, key, value) -> None:
        self.command = "PUT"
        self.key = key
        self.value = value

class Leader(database_pb2_grpc.DatabaseServicer, antientropy_pb2_grpc.AntiEntropyServicer):
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

class Follower(antientropy_pb2_grpc.AntiEntropyServicer):
    '''
    Follower class that listens to AppendEntries to replicate distributed log
    '''
    def __init__(self, rsm):
        self.rsm = rsm
        _thread = threading.Thread(target= self.__grpcServerThread)
        _thread.start()

    def __grpcServerThread(self):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))    # TODO increase max_workers
        antientropy_pb2_grpc.add_AntiEntropyServicer_to_server(self, self.server)
        self.server.add_insecure_port('[::]:' + self.rsm.port)
        self.server.start()
        self.server.wait_for_termination()
    
    def __del__(self):
        self.server.stop()

    def AppendEntries(self, request, context):
        # push to  DB
        self.rsm.db.Put(bytearray(request.key, 'utf-8'), bytearray(request.value, 'utf-8'))
        return antientropy_pb2.AppendEntriesResponse(success=True)

class LeaderElection:
    ''' 
    Leader Election module for the Replicated state machine
    '''
    def __init__(self, id, rsm) -> None:
        self.myID = id
        self.currLeader = ""
        self.rsm = rsm
    
    def contest(self) -> None:
        self.rsm.zk.ensure_path("/election")
        try:
            self.rsm.zk.create("/election/leader", value=bytes(self.myID, encoding='utf8'), ephemeral=True)
            self.currLeader = self.myID
        except zke.NodeExistsError:
            # leader already exists
            data = self.rsm.zk.get("/election/leader", watch=self.rsm.watchLeaderFile)
            self.currLeader = data[0].decode()
    
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
        from shutil import rmtree
        rmtree(dbpath, ignore_errors=True)
        self.db = leveldb.LevelDB(dbpath)
        
    def __init__(self, port, peers):
        self.zk = KazooClient(hosts='127.0.0.1:2181')
        self.zk.start()
        self.isFollower = True
        self.electionModule = LeaderElection(port, self)
        self.port = port
        self.peers = peers

        #set up levelDB
        self.setupDB(port)

        self.zk.ensure_path("/cluster")
        self.zk.create("/cluster/"+self.port, ephemeral=True)
        
        self.replicateFollower = [futures.ThreadPoolExecutor(max_workers=1), futures.ThreadPoolExecutor(max_workers=1)]
        self.concurrentRequests = set([])
        self.concurrentRequestsLock = threading.Lock()
        
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
            self.electionModule.contest()

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
    
    def getLevelDBEntries(self, low, high):
        itr = self.db.RangeIter(bytearray(low, encoding="utf8"), bytearray(high, encoding="utf8"))
        range = []
        for key, value in itr:
            range.append([antientropy_pb2.BucketEntry(key=key.decode(), value=value.decode())])
        return range   

    def follower_function(self):
        '''
        Wait for replication events from leader
        '''
        print("I hate following others ")

        with grpc.insecure_channel("localhost:" + str(self.electionModule.currLeader)) as channel:
            stub = antientropy_pb2_grpc.AntiEntropyStub(channel)
            while True:
                try:
                    stub.CreateMerkleTree(antientropy_pb2.CreateMerkleTreeRequest(), timeout=0.5)
                    break
                except Exception as e:
                    continue

        follower = Follower(self)
        while self.isFollower:
            time.sleep(1)
        del follower
    
    def __appendEntries(self, threadpoolidx, currentry):
        '''
        Thread that appends replicated log enttries to followers
        '''     
        with grpc.insecure_channel(self.peers[threadpoolidx]) as channel:
            stub = antientropy_pb2_grpc.AntiEntropyStub(channel)
            response = antientropy_pb2.AppendEntriesResponse(success=False)
            while response.success == False:
                try:
                    response = stub.AppendEntries(antientropy_pb2.AppendEntriesRequest(command= "PUT", key=currentry.key, value=currentry.value), timeout=0.5)
                except Exception as e:
                    return False
        return True
    
    def put(self, key, value):
        if self.isFollower:
            return False
        
        currentry = Entry(key, value)

        while True:
            with self.concurrentRequestsLock:
                if currentry.key not in self.concurrentRequests:
                    self.concurrentRequests.add(currentry.key)
                    break
                time.sleep(0.5)

        while True:
            # Submit jobs to append entries in followers
            f1 = self.replicateFollower[0].submit(self.__appendEntries, threadpoolidx=0, currentry=currentry)
            f2 = self.replicateFollower[1].submit(self.__appendEntries, threadpoolidx=1, currentry=currentry)
            # If either one is done, majority replication achieved. break
            if f1.result() or f2.result():
                break
            time.sleep(0.1)

        # commit to log after ack from follower
        self.db.Put(bytearray(key, 'utf-8'), bytearray(value, 'utf-8'))

        with self.concurrentRequestsLock:   
            self.concurrentRequests.remove(currentry.key)

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