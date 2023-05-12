# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import database_pb2 as database__pb2


class DatabaseStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Get = channel.unary_unary(
                '/database.Database/Get',
                request_serializer=database__pb2.GetRequest.SerializeToString,
                response_deserializer=database__pb2.GetResponse.FromString,
                )
        self.Put = channel.unary_unary(
                '/database.Database/Put',
                request_serializer=database__pb2.PutRequest.SerializeToString,
                response_deserializer=database__pb2.PutResponse.FromString,
                )
        self.IsMemoryUsageHigh = channel.unary_unary(
                '/database.Database/IsMemoryUsageHigh',
                request_serializer=database__pb2.EmptyParams.SerializeToString,
                response_deserializer=database__pb2.MemoryUsageResponse.FromString,
                )
        self.KeysToMove = channel.unary_unary(
                '/database.Database/KeysToMove',
                request_serializer=database__pb2.KeysToMoveRequest.SerializeToString,
                response_deserializer=database__pb2.KeysToMoveResponse.FromString,
                )
        self.Delete = channel.unary_unary(
                '/database.Database/Delete',
                request_serializer=database__pb2.DeleteRequest.SerializeToString,
                response_deserializer=database__pb2.DeleteResponse.FromString,
                )


class DatabaseServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Get(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Put(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def IsMemoryUsageHigh(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def KeysToMove(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Delete(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_DatabaseServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Get': grpc.unary_unary_rpc_method_handler(
                    servicer.Get,
                    request_deserializer=database__pb2.GetRequest.FromString,
                    response_serializer=database__pb2.GetResponse.SerializeToString,
            ),
            'Put': grpc.unary_unary_rpc_method_handler(
                    servicer.Put,
                    request_deserializer=database__pb2.PutRequest.FromString,
                    response_serializer=database__pb2.PutResponse.SerializeToString,
            ),
            'IsMemoryUsageHigh': grpc.unary_unary_rpc_method_handler(
                    servicer.IsMemoryUsageHigh,
                    request_deserializer=database__pb2.EmptyParams.FromString,
                    response_serializer=database__pb2.MemoryUsageResponse.SerializeToString,
            ),
            'KeysToMove': grpc.unary_unary_rpc_method_handler(
                    servicer.KeysToMove,
                    request_deserializer=database__pb2.KeysToMoveRequest.FromString,
                    response_serializer=database__pb2.KeysToMoveResponse.SerializeToString,
            ),
            'Delete': grpc.unary_unary_rpc_method_handler(
                    servicer.Delete,
                    request_deserializer=database__pb2.DeleteRequest.FromString,
                    response_serializer=database__pb2.DeleteResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'database.Database', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Database(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Get(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/database.Database/Get',
            database__pb2.GetRequest.SerializeToString,
            database__pb2.GetResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Put(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/database.Database/Put',
            database__pb2.PutRequest.SerializeToString,
            database__pb2.PutResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def IsMemoryUsageHigh(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/database.Database/IsMemoryUsageHigh',
            database__pb2.EmptyParams.SerializeToString,
            database__pb2.MemoryUsageResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def KeysToMove(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/database.Database/KeysToMove',
            database__pb2.KeysToMoveRequest.SerializeToString,
            database__pb2.KeysToMoveResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Delete(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/database.Database/Delete',
            database__pb2.DeleteRequest.SerializeToString,
            database__pb2.DeleteResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
