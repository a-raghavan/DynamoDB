from kazoo.client import KazooClient
from kazoo.exceptions import NodeExistsError
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
        try:
            self.rsm.zk.create("/election/leader", value=bytes(sys.argv[1], encoding='utf8'), ephemeral=True)
            self.currLeader = self.myID
        except NodeExistsError:
            data = self.rsm.zk.get("/election/leader", watch=self.rsm.watchLeaderFile)
            self.currLeader = data[0].decode()
    
    def leader(self) -> bool:
        return self.myID == self.currLeader

class ReplicatedStateMachine:
    def __init__(self, id):
        self.zk = KazooClient(hosts='127.0.0.1:2181')
        self.zk.start()
        self.isFollower = True
        self.electionModule = LeaderElection(id, self)
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def __del__(self):
        self.zk.stop()
    
    def watchLeaderFile(self, event):
        if event.type == EventType.DELETED:
            self.isFollower = False
        
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

    time.sleep(random.random()+1) 

    rsm.run()
    
    time.sleep(3)

