import hashlib
import bisect
import logging
import grpc
import database_pb2
import database_pb2_grpc
import consistentHashing_pb2
import consistentHashing_pb2_grpc
from concurrent import futures
import subprocess as sp
import time

SESSION_STR = 'rsm'
LOCALHOST_STR = '127.0.0.1:'


class ConsistentHashing(consistentHashing_pb2_grpc.ConsistentHashingServicer):
    def __init__(self, nodes, no_of_virtual_nodes):
        self.no_of_virtual_nodes = no_of_virtual_nodes
        self.ring = {}
        self.nodes= nodes
        self.checkForLoad = futures.ThreadPoolExecutor(max_workers= 10)  #Should ideally be equal to number of physcial nodes
        self.AddOrRemoveNodes = futures.ThreadPoolExecutor(max_workers= 2) 
        self.updateNode = futures.ThreadPoolExecutor(max_workers= 10)
        for node in nodes:
            self.appendToRing(node)
        self.checkLoad()
        

    #region Exposed API's
    def Get(self,request, context):
        physicalNode,leftVirtualHash, virtualHash = self.get_node(key)
        with grpc.insecure_channel(physicalNode) as channel:
            stub = database_pb2_grpc.DatabaseStub(channel)
            response= stub.Get(database_pb2.GetRequest(key=request.key))
            return consistentHashing_pb2.GetResponse(value=response)
    
    def Put(self,request, context):
        physicalNode, leftVirtualHash, virtualHash = self.get_node(key)
        with grpc.insecure_channel(physicalNode) as channel:
            stub = database_pb2_grpc.DatabaseStub(channel)
            #todo :: Update value to have object of key value pairs
            stub.Put(database_pb2.PutRequest(key=self.hash_key(), value=request.value))
            return consistentHashing_pb2.PutResponse(errormsg="")
    #endregion


    #region InternalFunctions
    def __serverLoad(self, node):
        while(True):
            time.sleep(120)
            with grpc.insecure_channel(node) as channel:
                stub = database_pb2_grpc.DatabaseStub(channel)
                response = stub.IsMemoryUsageHigh(database_pb2.EmptyParams())
                if response.isHigh:
                    self.AddOrRemoveNodes.submit(self.__add_node)
                
        
    def checkLoad(self):
        checkLoadThreads = [self.checkForLoad.submit(self.__serverLoad, node= node) for node in self.nodes]
   
    def __add_node(self):
        newPorts = setupRSMNodes()
        owners = appendToRing(LOCALHOST_STR+newPorts[0])
        #Call Physical nodes to get all keys
        for i in range(len(owners)):
            self.updateNode.submit(self.__fetchAndUpdateData ,address = owners[i][0], start_key= owners[i][1], end_key= owners[i][3], newNodeAddress= newPorts[0])
        
    
    def __fetchAndUpdateData(self, address, start_key, end_key,newNodeAddress):
        with grpc.insecure_channel(address) as channel:
                stub = database_pb2_grpc.DatabaseStub(channel)
                response = stub.KeysToMove(database_pb2.KeysToMoveRequest(startKey= start_key, endKey = end_key))
                with grpc.insecure_channel(newNodeAddress) as channel:
                    for i in range(len(response.entries)):
                        resposne = stub.Put(database_pb2.PutRequest(key=self.hash_key(), value=request.value))
                        
    def appendToRing(self, node):
        previousOwners =  []
        for i in range(self.no_of_virtual_nodes):
            key = f'{node}:{i}'
            physicalNode, leftVirtualHash, virtualHash = self.get_node(key)
            previousOwners.append([physicalNode, leftVirtualHash, virtualHash, key])
            self.ring[self.hash_key(key)] = node
        return previousOwners

    def remove_node(self, node):
        for i in range(self.no_of_virtual_nodes):
            key = f'{node}:{i}'
            del self.ring[self.hash_key(key)]

    def get_node(self, key):
        if not self.ring:
            return None, None, None
        hash_key = self.hash_key(key)
        print(type(hash_key))
        node_keys = sorted(self.ring.keys())
        hash_index = bisect.bisect_right(node_keys, hash_key) % len(node_keys)
        hash_left_index = bisect.bisect_left(node_keys, hash_key) % len(node_keys)
        return self.ring[node_keys[hash_index]] , hash_left_index, hash_index 

    def hash_key(self, key):
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)
    
    #Does this require kazoo?
    def setupRSMNodes(self):
        result= getAvailablePorts()
        script = '''\
    tmux new -d -s {0}
    tmux new-window -d -t {0} -n {1}_1
    tmux select-window -t '={1}_1'
    tmux send-keys -t 0  "python3 rsm.py -p {2} -n localhost:{2} localhost:{3} localhost:{4}" Enter

    tmux new-window -d -t {0} -n {1}_2
    tmux select-window -t '={1}_2'
    tmux send-keys -t 0  "python3 rsm.py -p {3} -n localhost:{2} localhost:{3} localhost:{4}" Enter

    tmux new-window -d -t {0} -n {1}_3
    tmux select-window -t '={1}_3'
    tmux send-keys -t 0  "python3 rsm.py -p {4} -n localhost:{2} localhost:{3} localhost:{4}" Enter
        '''.format(
                SESSION_STR,
                "node_{}".format(len(self.nodes)),
                result[0],
                result[1],
                result[2]
            )
        sp.check_call('{}'.format(script), shell=True)
        return result

    def getAvailablePorts():
        result =[]
        for i in range(3):
            from socket import socket
            with socket() as s:
                s.bind(('',0))
                print(s.getsockname()[1])
                result.append(s.getsockname()[1])
        return result
    #endregion


def serve(nodes, no_of_virtual_nodes):
    port = '50051'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    consistentHashing_pb2_grpc.add_ConsistentHashingServicer_to_server(ConsistentHashing(nodes, no_of_virtual_nodes), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == '__main__':  
    nodes = ["127.0.0.1:5000","127.0.0.1:5001","127.0.0.1:5002"]  
    no_of_virtual_nodes = 3
    serve(nodes, no_of_virtual_nodes)
