# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: rsm.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\trsm.proto\x12\x03rsm\"7\n\x08LogEntry\x12\x0f\n\x07\x63ommand\x18\x01 \x01(\t\x12\x0b\n\x03key\x18\x02 \x01(\t\x12\r\n\x05value\x18\x03 \x01(\t\"E\n\x14\x41ppendEntriesRequest\x12\r\n\x05index\x18\x01 \x01(\x03\x12\x1e\n\x07\x65ntries\x18\x02 \x03(\x0b\x32\r.rsm.LogEntry\"7\n\x15\x41ppendEntriesResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\r\n\x05index\x18\x02 \x01(\x03\x32O\n\x03RSM\x12H\n\rAppendEntries\x12\x19.rsm.AppendEntriesRequest\x1a\x1a.rsm.AppendEntriesResponse\"\x00\x42(\n\x14io.grpc.examples.rsmB\x08RsmProtoP\x01\xa2\x02\x03HLWb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'rsm_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\024io.grpc.examples.rsmB\010RsmProtoP\001\242\002\003HLW'
  _LOGENTRY._serialized_start=18
  _LOGENTRY._serialized_end=73
  _APPENDENTRIESREQUEST._serialized_start=75
  _APPENDENTRIESREQUEST._serialized_end=144
  _APPENDENTRIESRESPONSE._serialized_start=146
  _APPENDENTRIESRESPONSE._serialized_end=201
  _RSM._serialized_start=203
  _RSM._serialized_end=282
# @@protoc_insertion_point(module_scope)
