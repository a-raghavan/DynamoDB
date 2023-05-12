import hashlib
import grpc
import antientropy_pb2
import antientropy_pb2_grpc
from concurrent import futures

class MerklePatriciaTrieNode:
    """A node in the trie structure"""

    def __init__(self, nibble):
        self.nibble = nibble
        self.leaf = False
        self.val = ""
        self.hash = ""
        self.children = {}

class MerklePatriciaTrie(antientropy_pb2_grpc.AntiEntropyServicer):
    """The trie object"""

    def __init__(self, isServer, db, leaderPort):
        """
        start grpc server
        """
        self.root = MerklePatriciaTrieNode("")
        self.isServer = isServer
        self.db = db
        self.leaderPort = leaderPort

        if (isServer):
            server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
            antientropy_pb2_grpc.add_AntiEntropyServicer_to_server(self, server)
            server.add_insecure_port('[::]:' + str(leaderPort))
            server.start()
            print("Server started, listening on " + str(leaderPort))
            server.wait_for_termination()
    
    def populateHash(self, node):
        """Update the hash of each node"""
        if node.leaf:
            h = hashlib.new('sha256')
            h.update(bytes(node.val, encoding="utf8"))
            node.hash = h.hexdigest()
            return node.hash
        
        s = ""
        for child in node.children.values():
            s += self.populateHash(child)
        
        h = hashlib.new('sha256')
        h.update(bytes(s, encoding="utf8"))
        node.hash = h.hexdigest()
        return node.hash
    
    def insert(self, key, val):
        """Insert a key into the trie"""
        node = self.root
        
        for nibble in key:
            if nibble in node.children:
                node = node.children[nibble]
            else:
                new_node = MerklePatriciaTrieNode(nibble)
                node.children[nibble] = new_node
                node = new_node
        
        node.leaf = True
        node.val = val
        return
    
    def sync_client_wrapper(self):
        with grpc.insecure_channel("localhost:" + str(self.leaderPort)) as channel:
            stub = antientropy_pb2_grpc.AntiEntropyStub(channel)
            while True:
                try:
                    stub.CreateMerkleTree(antientropy_pb2.CreateMerkleTreeRequest(), timeout=0.5)
                    break
                except Exception as e:
                    continue
        
        self.sync_client(self.root, "")

    def sync_client(self, root, path):
        done = False
        while (not done):
            try:
                with grpc.insecure_channel("localhost:60061") as channel:
                    stub = antientropy_pb2_grpc.AntiEntropyStub(channel)
                    if root is None:
                        response = stub.Sync(antientropy_pb2.SyncRequest(hash="", path=path, subtree=[]))
                    else:
                        response = stub.Sync(antientropy_pb2.SyncRequest(hash=root.hash, path=path, subtree=[]))
                    done = True
            except Exception as e:
                continue
        
        # print(path, response)
        
        if response.retcode == 1:    # same in peer
            return
        elif response.retcode == 2:  # node exists in peer
            if root is None:         # I dont have the node that is present in peer
                for item in response.subtree:
                    self.db.Put(bytearray(item.key, encoding="utf8"), bytearray(item.value, encoding="utf8"))
            elif len(path) < 32:
                for n in '0123456789abcdef':
                    if n in root.children:
                        self.sync_client(root.children[n], path+n)
                    else:
                        self.sync_client(None, path+n)
            else:
                for item in response.subtree:
                    self.db.Put(bytearray(item.key, encoding="utf8"), bytearray(item.value, encoding="utf8"))
        else:                        # node dosent exist in peer
            if root is not None:
                done = False
                while (not done):
                    try:
                        with grpc.insecure_channel("localhost:60061") as channel:
                            stub = antientropy_pb2_grpc.AntiEntropyStub(channel)
                            response = stub.Sync(antientropy_pb2.SyncRequest(hash=root.hash, path=path, subtree=self.query(path)))
                            done = True
                    except Exception as e:
                        continue
        return
    
    def Sync(self, request, context):
        
        node = self.root
        # print(request)
        for nibble in request.path:
            if nibble in node.children:
                node = node.children[nibble]
            elif request.hash == "":
                return antientropy_pb2.SyncResponse(retcode=1, subtree=[])
            elif len(request.subtree) == 0:
                return antientropy_pb2.SyncResponse(retcode=3, subtree=[])
            else:
                for item in request.subtree:
                    self.db.Put(bytearray(item.key, encoding="utf8"), bytearray(item.value, encoding="utf8"))
                return antientropy_pb2.SyncResponse(retcode=1, subtree=[])
        
        if node.hash == request.hash:
            return antientropy_pb2.SyncResponse(retcode=1, subtree=[])
        else:
            if request.hash == "" or len(request.path) == 32:
                return antientropy_pb2.SyncResponse(retcode=2, subtree=self.query(request.path)) # need timestamps
            else:
                return antientropy_pb2.SyncResponse(retcode=2, subtree=[])
    
    def CreateMerkleTree(self, request, context):
        self.root = MerklePatriciaTrieNode("")
        itr = self.db.RangeIter()
        items = [(k.decode(), v.decode()) for k,v in itr]
        for k, v in items:
            self.insert(k, v)
        self.populateHash(self.root)
        return antientropy_pb2.CreateMerkleTreeResponse()

    
    def dfs(self, node, prefix):
        """Depth-first traversal of the trie
        
        Args:
            - node: the node to start with
            - prefix: the current prefix, for tracing a
                word while traversing the trie
        """
        if node.leaf:
            self.output.append(antientropy_pb2.KVPair(key=prefix + node.nibble, value=node.val))
        
        for child in node.children.values():
            self.dfs(child, prefix + node.nibble)

    def query(self, x):
        """Given an input (a prefix), retrieve all words stored in
        the trie with that prefix, sort the words by the number of 
        times they have been inserted
        """
        # Use a variable within the class to keep all possible outputs
        # As there can be more than one word with such prefix
        self.output = []
        node = self.root
        
        # Check if the prefix is in the trie
        for nibble in x:
            if nibble in node.children:
                node = node.children[nibble]
            else:
                # cannot found the prefix, return empty list
                return []
        
        # Traverse the trie to get all candidates
        self.dfs(node, x[:-1])

        # Sort the results in reverse order and return
        return self.output

    
    def print(self):
        """Level order traversal"""
        q = [self.root]
        while len(q) != 0:
            node = q[0]
            print(node.nibble)
            print(node.leaf)
            print(node.hash)
            print(node.val)
            print(node.children)
            print("================")
            for nibble in node.children:
                q.append(node.children[nibble])
            q.pop(0)