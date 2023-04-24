from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AppendEntriesRequest(_message.Message):
    __slots__ = ["entries", "index"]
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[LogEntry]
    index: int
    def __init__(self, index: _Optional[int] = ..., entries: _Optional[_Iterable[_Union[LogEntry, _Mapping]]] = ...) -> None: ...

class AppendEntriesResponse(_message.Message):
    __slots__ = ["index", "success"]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    index: int
    success: bool
    def __init__(self, success: bool = ..., index: _Optional[int] = ...) -> None: ...

class LogEntry(_message.Message):
    __slots__ = ["command", "key", "value"]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    command: str
    key: str
    value: str
    def __init__(self, command: _Optional[str] = ..., key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
