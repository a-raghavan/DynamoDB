from merklepatricia import *
import antientropy_pb2
import leveldb

db2 = leveldb.LevelDB("db2")

mp = MerklePatriciaTrie(False, db2, 60061)
mp.CreateMerkleTree(antientropy_pb2.AppendEntriesRequest(), None)
mp.sync_client_wrapper()