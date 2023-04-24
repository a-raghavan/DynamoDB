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

# Running rsm.py
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