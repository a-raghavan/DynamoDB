from merklepatricia import *
import leveldb

db2 = leveldb.LevelDB("db2")
itr2 = db2.RangeIter()
items2 = [(k,v) for k,v in itr2]

mp = MerklePatriciaTrie(False, items2, db2)
mp.sync_client(mp.root, "")