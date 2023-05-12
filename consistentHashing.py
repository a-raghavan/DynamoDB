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
from kazoo.client import KazooClient
import kazoo.exceptions as zke
from kazoo.protocol.states import EventType

SESSION_STR = 'rsm'
LOCALHOST_STR = '127.0.0.1:'


class ConsistentHashing(consistentHashing_pb2_grpc.ConsistentHashingServicer):
    def __init__(self, no_of_virtual_nodes):
        self.zk = KazooClient(hosts='127.0.0.1:2181')
        self.zk.start()
        self.no_of_virtual_nodes = no_of_virtual_nodes
        self.ring = {}
        self.checkForLoad = futures.ThreadPoolExecutor(max_workers= 10)  #Should ideally be equal to number of physcial nodes
        self.AddOrRemoveNodes = futures.ThreadPoolExecutor(max_workers= 2) 
        self.updateNode = futures.ThreadPoolExecutor(max_workers= 10)
        self.clusterNameToIpMap = self.populateClusterNameToIp()
        print("=========================Current cluster Mapping===========================")
        print(self.clusterNameToIpMap)
        print("===========================================================================")
        
        self.nodes = self.clusterNameToIpMap.keys()
        for node in self.nodes:
            self.appendToRing(node)
        self.checkLoad()
        

    #region Exposed API's
    def Get(self, request, context):
        physicalNode,leftVirtualHash, virtualHash = self.get_node(request.key)
        print(physicalNode, leftVirtualHash, virtualHash )
        with grpc.insecure_channel(physicalNode) as channel:
            stub = database_pb2_grpc.DatabaseStub(channel)
            response= stub.Get(database_pb2.GetRequest(key=str(virtualHash)))
            [actualKey,actualValue] = response.value.split("~")
            return consistentHashing_pb2.GetResponse(value=actualValue)
    
    def Put(self,request, context):
        physicalNode, leftVirtualHash, virtualHash = self.get_node(request.key)
        print(physicalNode, leftVirtualHash, virtualHash)
        with grpc.insecure_channel(physicalNode) as channel:
            stub = database_pb2_grpc.DatabaseStub(channel)
            dbValue = request.key+"~"+request.value
            stub.Put(database_pb2.PutRequest(key=str(virtualHash), value=dbValue))
            return consistentHashing_pb2.PutResponse(errormsg="")

    def Delete(self,request, context):
        physicalNode, leftVirtualHash, virtualHash = self.get_node(request.key)
        print(physicalNode, leftVirtualHash, virtualHash)
        with grpc.insecure_channel(physicalNode) as channel:
            stub = database_pb2_grpc.DatabaseStub(channel)
            stub.Delete(database_pb2.DeleteRequest(key=str(virtualHash)))
            return consistentHashing_pb2.PutResponse(errormsg="Success")
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
        newClusterLeader, newClusterName = self.setupRSMNodes()
        self.clusterNameToIpMap[newClusterName] = newClusterLeader
        self.nodes.append(newClusterName)
        previousOwners = self.appendToRing(newClusterName)
        
        #Call Physical nodes to get all keys
        for i in range(len(previousOwners)):
            self.updateNode.submit(self.__fetchAndUpdateData ,address = previousOwners[i][0], start_key= previousOwners[i][1], end_key= previousOwners[i][3], newNodeAddress= getLeaderNodeOfCluster(newClusterName))
        
    
    def __fetchAndUpdateData(self, address, start_key, end_key,newNodeAddress):
        with grpc.insecure_channel(address) as channel:
                stub = database_pb2_grpc.DatabaseStub(channel)
                keysToMoveResponse = stub.KeysToMove(database_pb2.KeysToMoveRequest(startKey= start_key, endKey = end_key)) 
                
                
                
                for i in range(len(keysToMoveResponse.entries)):
                    #We are removing the keys from the previous owners DB.
                    deleteResposne = stub.Delete(database_pb2.DeleteRequest(key=keysToMoveResponse(i).key))
                
                with grpc.insecure_channel(newNodeAddress) as channel:
                    for i in range(len(keysToMoveResponse.entries)):
                        #for every entry we are getting the key and store it as the string format. 
                        putResposne = stub.Put(database_pb2.PutRequest(key=keysToMoveResponse(i).key, value=keysToMoveResponse(i).value))
                        
    def appendToRing(self, clusterName):
        previousOwners =  []
        for i in range(self.no_of_virtual_nodes):
            key = f'{clusterName}:{i}'
            physicalNode, leftVirtualHash, virtualHash = self.get_node(key)
            previousOwners.append([physicalNode, leftVirtualHash, virtualHash, key])
            self.ring[self.hash_key(key)] = clusterName
        return previousOwners

    def remove_node(self, clusterName):
        for i in range(self.no_of_virtual_nodes):
            key = f'{clusterName}:{i}'
            del self.ring[self.hash_key(key)]

    def get_node(self, key):
        if not self.ring:
            return None, None, None
        hash_key = self.hash_key(key)
        node_keys = sorted(self.ring.keys())
        hash_index = bisect.bisect_right(node_keys, hash_key) % len(node_keys)
        hash_left_index = bisect.bisect_left(node_keys, hash_key) % len(node_keys)
        physicalNode = self.getLeaderNodeOfCluster(self.ring[node_keys[hash_index]])
        return  physicalNode, hash_left_index, hash_index 

    def hash_key(self, key):
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)
    
    #Does this require kazoo?
    def setupRSMNodes(self):
        result= self.getAvailablePorts()
        clusterName ="cluster:{}:{}:{}".format(result[0], result[1], result[2])
        script = '''\
    tmux new -d -s {0}
    tmux new-window -d -t {0} -n {1}_1
    tmux select-window -t '={1}_1'
    tmux send-keys -t 0  "python3 rsm.py -p {2} -n localhost:{2} localhost:{3} localhost:{4} -cn {5}" Enter

    tmux new-window -d -t {0} -n {1}_2
    tmux select-window -t '={1}_2'
    tmux send-keys -t 0  "python3 rsm.py -p {3} -n localhost:{2} localhost:{3} localhost:{4} -cn {5}" Enter

    tmux new-window -d -t {0} -n {1}_3
    tmux select-window -t '={1}_3'
    tmux send-keys -t 0  "python3 rsm.py -p {4} -n localhost:{2} localhost:{3} localhost:{4} -cn {5}" Enter
        '''.format(
                SESSION_STR,
                "node_{}".format(len(self.nodes)),
                result[0],
                result[1],
                result[2],
                clusterName
            )
        sp.check_call('{}'.format(script), shell=True)
        
        
        while(self.zk.exists("/{}/election/leaderRSMPort".format(clusterName), watch=self.watchLeaderFile) is None):
            time.sleep(0.5)
            
        leaderPort = self.zk.get("/{}/election/leaderRSMPort".format(clusterName))
        leader = LOCALHOST_STR+"{}".format(leaderPort[0].decode())
        return leader, clusterName

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

    #region Zookeeper
    def populateClusterNameToIp(self):
        result = {}
        children = self.zk.get_children("/")
        for c in children:
            if "cluster:" in c:
                self.zk.exists("/{}/election".format(c), watch= self.watchLeaderFile)
                if self.zk.exists("/{}/election/leaderRSMPort".format(c)) is not None:
                    data = self.zk.get("/{}/election/leaderRSMPort".format(c))
                    result[c]= LOCALHOST_STR+"{}".format(data[0].decode())
                else:
                    result[c]= ""
        return result     
        
    def watchLeaderFile(self, event):
        if event.type == EventType.DELETED:
            if "leaderRSMPort" in event.path:
                self.clusterNameToIpMap[event.path.split("/")[1]] = ""
        elif event.type == EventType.CREATED:
            if "leaderRSMPort" in event.path:
                data = self.zk.get(event.path)
                self.clusterNameToIpMap[event.path.split("/")[1]] = LOCALHOST_STR+"{}".format(data[0].decode())
            
    #endregion
    
    def getLeaderNodeOfCluster(self,clusterName):
        return self.clusterNameToIpMap[clusterName]


def serve(no_of_virtual_nodes):
    port = '50055'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    consistentHashing_pb2_grpc.add_ConsistentHashingServicer_to_server(ConsistentHashing(no_of_virtual_nodes), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == '__main__':  
    no_of_virtual_nodes = 3
    serve(no_of_virtual_nodes)
