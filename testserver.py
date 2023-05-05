from merkletree import *

if __name__ == "__main__":
    range = [createBucket(["a", "b", "c", "d"]), createBucket(["e","f"]), createBucket(["g","h"]), createBucket(["i","j", "x", "y"]), createBucket(["k","l"])]
    mt = MerkleTree(range, True)