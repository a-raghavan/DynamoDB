from merklepatricia import *
import leveldb

db1 = leveldb.LevelDB("db1")
itr1 = db1.RangeIter()
items1 = [(k.decode(),v.decode()) for k,v in itr1]

mp = MerklePatriciaTrie(True, items1, db1)