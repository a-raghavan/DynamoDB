from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DeleteRequest(_message.Message):
    __slots__ = ["key"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: str
    def __init__(self, key: _Optional[str] = ...) -> None: ...

class DeleteResponse(_message.Message):
    __slots__ = ["errormsg"]
    ERRORMSG_FIELD_NUMBER: _ClassVar[int]
    errormsg: str
    def __init__(self, errormsg: _Optional[str] = ...) -> None: ...

class EmptyParams(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class GetRequest(_message.Message):
    __slots__ = ["key"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: str
    def __init__(self, key: _Optional[str] = ...) -> None: ...

class GetResponse(_message.Message):
    __slots__ = ["value"]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    def __init__(self, value: _Optional[str] = ...) -> None: ...

class KVpair(_message.Message):
    __slots__ = ["key", "value"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class KeysToMoveRequest(_message.Message):
    __slots__ = ["endKey", "startKey"]
    ENDKEY_FIELD_NUMBER: _ClassVar[int]
    STARTKEY_FIELD_NUMBER: _ClassVar[int]
    endKey: str
    startKey: str
    def __init__(self, startKey: _Optional[str] = ..., endKey: _Optional[str] = ...) -> None: ...

class KeysToMoveResponse(_message.Message):
    __slots__ = ["entries"]
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[KVpair]
    def __init__(self, entries: _Optional[_Iterable[_Union[KVpair, _Mapping]]] = ...) -> None: ...

class MemoryUsageResponse(_message.Message):
    __slots__ = ["isHigh"]
    ISHIGH_FIELD_NUMBER: _ClassVar[int]
    isHigh: bool
    def __init__(self, isHigh: bool = ...) -> None: ...

class PutRequest(_message.Message):
    __slots__ = ["key", "value"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class PutResponse(_message.Message):
    __slots__ = ["errormsg"]
    ERRORMSG_FIELD_NUMBER: _ClassVar[int]
    errormsg: str
    def __init__(self, errormsg: _Optional[str] = ...) -> None: ...
