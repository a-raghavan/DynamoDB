from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BucketEntry(_message.Message):
    __slots__ = ["key", "value"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class SyncRequest(_message.Message):
    __slots__ = ["bucket", "hash", "path"]
    BUCKET_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    bucket: _containers.RepeatedCompositeFieldContainer[BucketEntry]
    hash: str
    path: str
    def __init__(self, hash: _Optional[str] = ..., path: _Optional[str] = ..., bucket: _Optional[_Iterable[_Union[BucketEntry, _Mapping]]] = ...) -> None: ...

class SyncResponse(_message.Message):
    __slots__ = ["bucket", "same"]
    BUCKET_FIELD_NUMBER: _ClassVar[int]
    SAME_FIELD_NUMBER: _ClassVar[int]
    bucket: _containers.RepeatedCompositeFieldContainer[BucketEntry]
    same: bool
    def __init__(self, same: bool = ..., bucket: _Optional[_Iterable[_Union[BucketEntry, _Mapping]]] = ...) -> None: ...
