from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AppendEntriesRequest(_message.Message):
    __slots__ = ["command", "key", "value"]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    command: str
    key: str
    value: str
    def __init__(self, command: _Optional[str] = ..., key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class AppendEntriesResponse(_message.Message):
    __slots__ = ["success"]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class CreateMerkleTreeRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class CreateMerkleTreeResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class KVPair(_message.Message):
    __slots__ = ["key", "value"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class SyncRequest(_message.Message):
    __slots__ = ["hash", "path", "subtree"]
    HASH_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    SUBTREE_FIELD_NUMBER: _ClassVar[int]
    hash: str
    path: str
    subtree: _containers.RepeatedCompositeFieldContainer[KVPair]
    def __init__(self, hash: _Optional[str] = ..., path: _Optional[str] = ..., subtree: _Optional[_Iterable[_Union[KVPair, _Mapping]]] = ...) -> None: ...

class SyncResponse(_message.Message):
    __slots__ = ["retcode", "subtree"]
    RETCODE_FIELD_NUMBER: _ClassVar[int]
    SUBTREE_FIELD_NUMBER: _ClassVar[int]
    retcode: int
    subtree: _containers.RepeatedCompositeFieldContainer[KVPair]
    def __init__(self, retcode: _Optional[int] = ..., subtree: _Optional[_Iterable[_Union[KVPair, _Mapping]]] = ...) -> None: ...
