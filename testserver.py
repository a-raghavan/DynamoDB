from merklepatricia import *
import leveldb

db1 = leveldb.LevelDB("db1")

mp = MerklePatriciaTrie(True, db1, 60061)