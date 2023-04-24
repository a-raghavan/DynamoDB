from kazoo.client import KazooClient
import kazoo.exceptions as zke
from kazoo.protocol.states import EventType
import signal
import sys
import time
import random

class LeaderElection:
    def __init__(self, id, rsm) -> None:
        self.myID = id
        self.currLeader = ""
        self.rsm = rsm
    
    def contest(self) -> None:
        self.rsm.zk.ensure_path("/election")

        peerNumProcessedEntries = -1
        peerid = ""
        while peerNumProcessedEntries == -1:
            # can't proceed since we have only 1 active node (that is us)
            children = self.rsm.zk.get_children("/cluster")
            for c in children:
                if c != self.myID:
                    data = self.rsm.zk.get("/cluster/"+c)
                    peerNumProcessedEntries = max(int(data[0].decode()), peerNumProcessedEntries)
                    peerid = c
            # wait until another node comes up
            time.sleep(0.2)
        
        if peerNumProcessedEntries <= self.rsm.myNumProcessedEntries:
            # Try to become a leader
            try:
                self.rsm.zk.create("/election/leader", value=bytes(sys.argv[1], encoding='utf8'), ephemeral=True)
                self.currLeader = self.myID
            except zke.NodeExistsError:
                # leader already exists
                data = self.rsm.zk.get("/election/leader", watch=self.rsm.watchLeaderFile)
                self.currLeader = data[0].decode()
        else:
            # allow peer to become the leader
            self.rsm.zk.exists("/election/leader", watch=self.rsm.watchLeaderFile)
            self.currLeader = peerid
    
    def leader(self) -> bool:
        return self.myID == self.currLeader

class ReplicatedStateMachine:
    def __init__(self, id):
        self.zk = KazooClient(hosts='127.0.0.1:2181')
        self.zk.start()
        self.isFollower = True
        self.electionModule = LeaderElection(id, self)
        self.zk.ensure_path("/cluster")
        self.myNumProcessedEntries = random.randint(1,10)
        self.zk.create("/cluster/"+id, value=bytes(str(self.myNumProcessedEntries), encoding='utf8'), ephemeral=True)
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def __del__(self):
        self.zk.stop()
    
    def watchLeaderFile(self, event):
        if event.type == EventType.DELETED:
            self.isFollower = False
        elif event.type == EventType.CREATED:
            data = self.zk.get("/election/leader")
            self.electionModule.currLeader = data[0].decode()

    def run(self):
        while True:
            self.electionModule.contest()
            if self.electionModule.leader():
                self.isFollower = False
                self.leader_function()
            else:
                self.isFollower = True
                self.follower_function()

    def leader_function(self):
        print("I'm the king of the world ", sys.argv[1])
        signal.pause()
    
    def signal_handler(self, sig, frame):
        print('You pressed Ctrl+C!')
        self.zk.stop()
        sys.exit(0)
    
    def follower_function(self):
        print("I hate following others ", sys.argv[1])
        while self.isFollower:
            time.sleep(1)

if __name__ == "__main__":

    rsm = ReplicatedStateMachine(sys.argv[1])
    rsm.run()

