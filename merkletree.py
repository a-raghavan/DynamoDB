import hashlib
import grpc
import antientropy_pb2
import antientropy_pb2_grpc
from concurrent import futures

class MerkleTreeNode:
    def computeHashLeaf(self, items):
        h = hashlib.new('sha256')
        s = ""
        for k in items:
            s += k.key
            s += k.value 
        h.update(bytes(s, encoding="utf8"))
        return h.hexdigest()
    
    def computeHashBranch(self, items):
        h = hashlib.new('sha256')
        s = ""
        for i in items:
            s += i
        h.update(bytes(s, encoding="utf8"))
        return h.hexdigest()
    
    def __init__(self, isLeaf, items, left = None, right = None):
        self.leaf = isLeaf
        self.left = left
        self.right = right
        self.items = items
        if isLeaf:
            self.hash = self.computeHashLeaf(items)
        else:
            self.hash = self.computeHashBranch([self.left.hash, self.right.hash])
        return

class MerkleTree(antientropy_pb2_grpc.AntiEntropyServicer):
    def __init__(self, range, isServer):
        self.sanitizeRange(range)
        self.root = self.createTree(0, len(range)-1, range)
        self.server = isServer
        self.print()
        if (isServer):
            server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
            antientropy_pb2_grpc.add_AntiEntropyServicer_to_server(self, server)
            server.add_insecure_port('[::]:' + "50051")
            server.start()
            print("Server started, listening on " + "50051")
            server.wait_for_termination()

    def createTree(self, b, e, range):
        if b == e:
            return MerkleTreeNode(True, range[b])
        else:
            mid = int((b+e)/2)
            l = self.createTree(b, mid, range)
            r = self.createTree(mid+1, e, range)
            myNode = MerkleTreeNode(False, [], l, r)
            return myNode
   
    def sanitizeRange(self, range):
        power = 0
        mul = 1
        n = len(range)
        while mul < n:
            power += 1
            mul *= 2
        
        padding = [[antientropy_pb2.BucketEntry(key="opo", value="pop")]]* (mul-n)
        range.extend(padding)
    
    def print(self):
        q = [self.root]
        while len(q) != 0:
            n = q[0]
            print("self= ", n)
            print("leaf= ", n.leaf)
            print("hash= ", n.hash)
            print("left= ", n.left)
            print("right= ", n.right)
            print("items= ", n.items)
            if n.left is not None:
                q.append(n.left)
            if n.right is not None:
                q.append(n.right)
            q.pop(0)

    def updateBucket(self, mybucket, peerbucket):
        keys = {x.key for x in mybucket}
        newbucket = [x for x in mybucket]
        for item in peerbucket:
            if item.key not in keys:
                newbucket.append(item)
        return newbucket
    
    def sync_client(self, root, path):
        if root is None:
            return
        
        done = False
        while (not done):
            try:
                with grpc.insecure_channel("localhost:50051") as channel:
                    stub = antientropy_pb2_grpc.AntiEntropyStub(channel)
                    response = stub.Sync(antientropy_pb2.SyncRequest(hash=root.hash, path=path, bucket=root.items))
                    done = True
            except Exception as e:
                continue
            
        if response.same:
            return
        else:
            if len(response.bucket) != 0:
                root.items = self.updateBucket(root.items, response.bucket)
            self.sync_client(root.left, path+"l")
            self.sync_client(root.right, path+"r")


    def traverse(self, root, curr, path):
        assert root is not None
        if curr == len(path):
            return root
        elif path[curr] == "l":
            return self.traverse(root.left, curr+1, path)
        else:
            return self.traverse(root.right, curr+1, path)
        
    def Sync(self, request, context):
        currNode = self.traverse(self.root, 0, request.path)        # inefficient *sigh*
        if request.hash == currNode.hash:
            return antientropy_pb2.SyncResponse(same=True, bucket=currNode.items)
        else:
            if len(request.bucket) != 0:
                currNode.items = self.updateBucket(currNode.items, request.bucket)
                print(currNode.items)
            return antientropy_pb2.SyncResponse(same=False, bucket=currNode.items)

def createBucket(lst):
    i = 0
    bucket = []
    while i < len(lst): 
        bucket.append(antientropy_pb2.BucketEntry(key=lst[i], value=lst[i+1]))
        i += 2
    return bucket
