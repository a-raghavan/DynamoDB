from merkletree import *

if __name__ == "__main__":
    range = [createBucket(["a", "b", "c", "d"]), createBucket(["e","f", "m", "n"]), createBucket(["g","h"]), createBucket(["i","j"]), createBucket(["k","l"])]
    mt = MerkleTree(range, False)
    mt.sync_client(mt.root,"")
    print("SYNCED!!!")
    mt.print()