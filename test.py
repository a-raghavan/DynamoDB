# from merklepatricia import *

# mp = MerklePatriciaTrie([("6f0", "1"), ("cb1", "2")])
# mp.print()

import leveldb

db1 = leveldb.LevelDB("db1")
db1.Put(bytearray("abc", encoding="utf8"), bytearray("1", encoding="utf8"))
db1.Put(bytearray("def", encoding="utf8"), bytearray("2", encoding="utf8"))


db2 = leveldb.LevelDB("db2")

db1.Put(bytearray("abc", encoding="utf8"), bytearray("3", encoding="utf8"))
db1.Put(bytearray("ghi", encoding="utf8"), bytearray("4", encoding="utf8"))

# from merklepatricia import *

# itr1 = db1.RangeIter()
# items1 = [(k,v) for k,v in itr1]

# itr2 = db2.RangeIter()
# items2 = [(k,v) for k,v in itr2]
# mp = 