# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import antientropy_pb2 as antientropy__pb2


class AntiEntropyStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Sync = channel.unary_unary(
                '/ae.AntiEntropy/Sync',
                request_serializer=antientropy__pb2.SyncRequest.SerializeToString,
                response_deserializer=antientropy__pb2.SyncResponse.FromString,
                )


class AntiEntropyServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Sync(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_AntiEntropyServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Sync': grpc.unary_unary_rpc_method_handler(
                    servicer.Sync,
                    request_deserializer=antientropy__pb2.SyncRequest.FromString,
                    response_serializer=antientropy__pb2.SyncResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'ae.AntiEntropy', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class AntiEntropy(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Sync(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ae.AntiEntropy/Sync',
            antientropy__pb2.SyncRequest.SerializeToString,
            antientropy__pb2.SyncResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
