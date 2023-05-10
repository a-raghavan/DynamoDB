import logging
import grpc
import database_pb2
import database_pb2_grpc


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = database_pb2_grpc.DatabaseStub(channel)
        response = stub.Put(database_pb2.PutRequest(key='lalo', value='salamanca'))
        print(response.errormsg)
        response = stub.Put(database_pb2.PutRequest(key='Jimmy', value='McGill'))
        print(response.errormsg)
        response = stub.Get(database_pb2.GetRequest(key='lalo'))
        print(response.value)
        response = stub.Get(database_pb2.GetRequest(key='Jimmy'))
        print(response.value)

if __name__ == '__main__':
    logging.basicConfig()
    run()