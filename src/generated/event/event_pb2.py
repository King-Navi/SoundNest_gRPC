# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: event/event.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'event/event.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11\x65vent/event.proto\x12\x05\x65vent\"g\n\x13\x45ventMessageRequest\x12$\n\nevent_type\x18\x01 \x01(\x0e\x32\x10.event.EventType\x12\x19\n\x11\x63ustom_event_type\x18\x02 \x01(\t\x12\x0f\n\x07payload\x18\x03 \x01(\t\"\xaa\x01\n\x12\x45ventMessageReturn\x12,\n\x12\x65vent_type_respose\x18\x01 \x01(\x0e\x32\x10.event.EventType\x12\x19\n\x11\x63ustom_event_type\x18\x02 \x01(\t\x12\x17\n\x0fis_succes_event\x18\x03 \x01(\x08\x12\x0f\n\x07message\x18\x04 \x01(\t\x12\x11\n\ttimestamp\x18\x05 \x01(\t\x12\x0e\n\x06status\x18\x06 \x01(\t*\xc2\x01\n\tEventType\x12\x0b\n\x07UNKNOWN\x10\x00\x12\n\n\x06\x43USTOM\x10\x01\x12\x10\n\x0cNOTIFICATION\x10\x02\x12\x0f\n\x0b\x44\x41TA_UPDATE\x10\x03\x12\x13\n\x0fHANDSHAKE_START\x10\x04\x12\x14\n\x10HANDSHAKE_FINISH\x10\x05\x12\x16\n\x12\x43OMMENT_REPLY_SEND\x10\x06\x12\x18\n\x14\x43OMMENT_REPLY_RECIVE\x10\x07\x12\x1c\n\x18SONG_VISITS_NOTIFICATION\x10\x08\x32R\n\x0c\x45ventService\x12\x42\n\x05\x45vent\x12\x1a.event.EventMessageRequest\x1a\x19.event.EventMessageReturn(\x01\x30\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'event.event_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_EVENTTYPE']._serialized_start=307
  _globals['_EVENTTYPE']._serialized_end=501
  _globals['_EVENTMESSAGEREQUEST']._serialized_start=28
  _globals['_EVENTMESSAGEREQUEST']._serialized_end=131
  _globals['_EVENTMESSAGERETURN']._serialized_start=134
  _globals['_EVENTMESSAGERETURN']._serialized_end=304
  _globals['_EVENTSERVICE']._serialized_start=503
  _globals['_EVENTSERVICE']._serialized_end=585
# @@protoc_insertion_point(module_scope)
