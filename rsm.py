from kazoo.client import KazooClient
import signal
import sys
import time
import random

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

def getLeaderFile(guids) -> str:
    leader_guid = 10000000000
    leader_file =""
    for c in guids:
        t = int(c.split('_')[1])
        if leader_guid > t:
            leader_guid = t
            leader_file = c
    return leader_file

class LeaderElection:
    def __init__(self, id, zk) -> None:
        self.myID = id
        self.currLeader = ""
        self.zk = zk

    def contest(self) -> None:
        self.zk.ensure_path("/election")
        self.zk.create("/election/guid-n_", value=bytes(sys.argv[1], encoding='utf8'), ephemeral=True, sequence=True)
        self.findLeader()
    
    def findLeader(self) -> None:
        children = self.zk.get_children("/election", watch=None, include_data=False)
        leader_file = getLeaderFile(children)
        data = self.zk.get("/election/"+leader_file)
        self.currLeader = data[0].decode()
    
    def leader(self) -> bool:
        return self.myID == self.currLeader

class ReplicatedStateMachine:
    def __init__(self, id):
        self.zk = KazooClient(hosts='127.0.0.1:2181')
        self.zk.start()
        self.isFollower = True
        self.electionModule = LeaderElection(id, self.zk)
    
    def __del__(self):
        self.zk.stop()
        
    def run(self):
        self.electionModule.contest()
        if self.electionModule.leader():
            self.isFollower = False
            self.leader_function()
        else:
            self.follower_function()

    def leader_function(self):
        print("I'm the king of the world ", sys.argv[1])
    
    def follower_function(self):
        print("I hate following others ", sys.argv[1])

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    rsm = ReplicatedStateMachine(sys.argv[1])

    time.sleep(random.random()+1) 

    rsm.run()
    #signal.pause()
    
    time.sleep(3)

