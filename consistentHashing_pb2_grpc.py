# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import consistentHashing_pb2 as consistentHashing__pb2


class ConsistentHashingStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Get = channel.unary_unary(
                '/consistentHashing.ConsistentHashing/Get',
                request_serializer=consistentHashing__pb2.GetRequest.SerializeToString,
                response_deserializer=consistentHashing__pb2.GetResponse.FromString,
                )
        self.Put = channel.unary_unary(
                '/consistentHashing.ConsistentHashing/Put',
                request_serializer=consistentHashing__pb2.PutRequest.SerializeToString,
                response_deserializer=consistentHashing__pb2.PutResponse.FromString,
                )
        self.AddNode = channel.unary_unary(
                '/consistentHashing.ConsistentHashing/AddNode',
                request_serializer=consistentHashing__pb2.AddNodeRequest.SerializeToString,
                response_deserializer=consistentHashing__pb2.AddNodeResponse.FromString,
                )
        self.RemoveNode = channel.unary_unary(
                '/consistentHashing.ConsistentHashing/RemoveNode',
                request_serializer=consistentHashing__pb2.PutRequest.SerializeToString,
                response_deserializer=consistentHashing__pb2.PutResponse.FromString,
                )


class ConsistentHashingServicer(object):
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

    def AddNode(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RemoveNode(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ConsistentHashingServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Get': grpc.unary_unary_rpc_method_handler(
                    servicer.Get,
                    request_deserializer=consistentHashing__pb2.GetRequest.FromString,
                    response_serializer=consistentHashing__pb2.GetResponse.SerializeToString,
            ),
            'Put': grpc.unary_unary_rpc_method_handler(
                    servicer.Put,
                    request_deserializer=consistentHashing__pb2.PutRequest.FromString,
                    response_serializer=consistentHashing__pb2.PutResponse.SerializeToString,
            ),
            'AddNode': grpc.unary_unary_rpc_method_handler(
                    servicer.AddNode,
                    request_deserializer=consistentHashing__pb2.AddNodeRequest.FromString,
                    response_serializer=consistentHashing__pb2.AddNodeResponse.SerializeToString,
            ),
            'RemoveNode': grpc.unary_unary_rpc_method_handler(
                    servicer.RemoveNode,
                    request_deserializer=consistentHashing__pb2.PutRequest.FromString,
                    response_serializer=consistentHashing__pb2.PutResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'consistentHashing.ConsistentHashing', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ConsistentHashing(object):
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
        return grpc.experimental.unary_unary(request, target, '/consistentHashing.ConsistentHashing/Get',
            consistentHashing__pb2.GetRequest.SerializeToString,
            consistentHashing__pb2.GetResponse.FromString,
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
        return grpc.experimental.unary_unary(request, target, '/consistentHashing.ConsistentHashing/Put',
            consistentHashing__pb2.PutRequest.SerializeToString,
            consistentHashing__pb2.PutResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def AddNode(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/consistentHashing.ConsistentHashing/AddNode',
            consistentHashing__pb2.AddNodeRequest.SerializeToString,
            consistentHashing__pb2.AddNodeResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RemoveNode(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/consistentHashing.ConsistentHashing/RemoveNode',
            consistentHashing__pb2.PutRequest.SerializeToString,
            consistentHashing__pb2.PutResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
