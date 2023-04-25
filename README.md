# DynamoDB
Highly scalable, available and strongly consistent distributed KV store

# Pre requisites
```sh
sudo apt update
sudo apt -y install python3-pip
pip3 install grpcio
pip3 install grpcio-tools
pip3 install kazoo
pip3 install leveldb
```
# Building protos
```sh
python3 -m grpc_tools.protoc -I ./protos --python_out=. --pyi_out=. --grpc_python_out=. ./protos/*
```

# Start Zookeeper
Currently zookeeper is stand alone. In production, must deploy in multiple servers for fault tolerance and availability
## Server
```sh
bin/zkServer.sh start
```
## Client
(Needed only for testing)
```sh
bin/zkCli.sh -server 127.0.0.1:2181
```

# Running rsm.py
**Start rsm.py only after zookeeper is running**
Leader default port : 50051
```sh
python3 rsm.py -p 5000 -n localhost:5000 localhost:5001 localhost:5002
python3 rsm.py -p 5001 -n localhost:5000 localhost:5001 localhost:5002
python3 rsm.py -p 5002 -n localhost:5000 localhost:5001 localhost:5002
```

# Run physicalnode.py
```sh
python3 physicalnode.py
```

# Documentations:
https://kazoo.readthedocs.io/en/latest/basic_usage.html
https://zookeeper.apache.org/doc/current/zookeeperStarted.html
https://zookeeper.apache.org/releases.html
