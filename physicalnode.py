import logging
import grpc
import consistentHashing_pb2
import consistentHashing_pb2_grpc


def run():
    with grpc.insecure_channel('127.0.0.1:50055') as channel:
        stub = consistentHashing_pb2_grpc.ConsistentHashingStub(channel)
        response = stub.Put(consistentHashing_pb2.PutRequest(key='GFS', value='Google'))
        print(response.errormsg)
        response = stub.Get(consistentHashing_pb2.GetRequest(key='GFS'))
        print(response.value)

        response = stub.Delete(consistentHashing_pb2.DeleteRequest(key='GFS'))
        print(response.errormsg)

        response = stub.Get(consistentHashing_pb2.GetRequest(key='GFS'))
        print(response.value)

if __name__ == '__main__':
    logging.basicConfig()
    run()