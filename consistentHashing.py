import hashlib
import bisect

class ConsistentHashing:
    def __init__(self, nodes,no_of_virtual_nodes):
        self.no_of_virtual_nodes = no_of_virtual_nodes
        self.ring = {}
        for node in nodes:
            self.add_node(node)

    def add_node(self, node):
        for i in range(self.no_of_virtual_nodes):
            key = self.hash_key(f'{node}:{i}')
            self.ring[key] = node
        #need to reshuffle the keys


    def remove_node(self, node):
        for i in range(self.no_of_virtual_nodes):
            key = self.hash_key(f'{node}:{i}')
            del self.ring[key]

        #need to reshuffle the keys
    def reshuffle(self, new_nodes):

        #one more issue - if the md5 doesn't give the new node in between the two required machines?
        new_ring = ConsistentHashing(new_nodes, self.no_of_virtual_nodes)
        old_keys = self.ring.keys()
        for old_key in old_keys:
            node = self.ring[old_key]
            new_node = new_ring.get_node(old_key)
            if node != new_node:
                new_ring.add_node(node)
                del self.ring[old_key]
        self.ring = new_ring.ring

    def get_node(self, key):
        if not self.ring:
            return None
        hash_key = self.hash_key(key)
        node_keys = sorted(self.ring.keys())
        hash_index = bisect.bisect_left(node_keys, hash_key) % len(node_keys)
        return self.ring[node_keys[hash_index]]

    def hash_key(self, key):
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)


if __name__ == '__main__':  
    nodes = ["127.0.0.1:5000","127.0.0.1:5001","127.0.0.1:5002"]  
    no_of_virtual_nodes = 3
    ConsistentHashing(nodes,no_of_virtual_nodes)
