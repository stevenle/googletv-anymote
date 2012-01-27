#!/usr/bin/env python
#
# Copyright 2012 Steven Le (stevenle08@gmail.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Python client for the Google TV Pairing and Anymote protocols."""

__author__ = 'stevenle08@gmail.com (Steven Le)'

import socket
import ssl
import struct
from googletv.proto import polo_pb2
from googletv.proto import remote_pb2

ENCODING_TYPE_HEXADECIMAL = polo_pb2.Options.Encoding.ENCODING_TYPE_HEXADECIMAL
ROLE_TYPE_INPUT = polo_pb2.Options.ROLE_TYPE_INPUT


class Error(Exception):
  """Base class for all exceptions in this module."""


class BaseProtocol(object):
  """Base class for protocols used by this module.

  Attributes:
    host: The host of the Google TV server.
    port: The port to connect to. Default is 9551 for Anymote Protocol and 9552
        for Pairing Protocol.
    sock: A socket.socket object.
    ssl: SSL-wrapped socket.socket object.
  """

  def __init__(self, host, port, certfile):
    self.host = host
    self.port = port
    self.sock = socket.socket()
    self.ssl = ssl.wrap_socket(self.sock, certfile=certfile)
    self.ssl.connect((self.host, self.port))

  def __enter__(self):
    return self

  def __exit__(self):
    self.Close()

  def Close(self):
    self.ssl.close()

  def Send(self, data):
    data_len = struct.pack('!I', len(data))
    sent = self.ssl.write(data_len + data)
    assert sent == len(data) + 4
    return sent


class PairingProtocol(BaseProtocol):
  """Google TV Pairing Protocol.

  More info:
    http://code.google.com/tv/remote/docs/pairing.html
  """

  def __init__(self, host, certfile, port=9552):
    super(PairingProtocol, self).__init__(host, port, certfile)

  def SendPairingRequest(self, client_name, service_name='AnyMote'):
    """Initiates a new PairingRequest with the Google TV server.

    Args:
      client_name: A string that can be used to identify the client making reqs.
      service_name: The name of the service to pair with.
    """
    req = polo_pb2.PairingRequest()
    req.service_name = service_name
    req.client_name = client_name
    self._SendMessage(req, polo_pb2.OuterMessage.MESSAGE_TYPE_PAIRING_REQUEST)

  def SendOptions(self, *args, **kwargs):
    """Sends an Options message to the Google TV server.

    Currently, only a 4-length HEXADECIMAL message is supported. Will support
    other types in the future.
    """
    options = polo_pb2.Options()
    encoding = options.input_encodings.add()
    encoding.type = ENCODING_TYPE_HEXADECIMAL
    encoding.symbol_length = 4
    self._SendMessage(options, polo_pb2.OuterMessage.MESSAGE_TYPE_OPTIONS)

  def SendConfiguration(self, encoding_type=ENCODING_TYPE_HEXADECIMAL,
                        symbol_length=4, client_role=ROLE_TYPE_INPUT):
    """Sends a Configuration message to the Google TV server.

    Currently, only a 4-length HEXADECIMAL message is supported. Will support
    other types in the future.
    """
    req = polo_pb2.Configuration()
    req.encoding.type = encoding_type
    req.encoding.symbol_length = symbol_length
    req.client_role = client_role
    self._SendMessage(req, polo_pb2.OuterMessage.MESSAGE_TYPE_CONFIGURATION)

  def SendSecret(self, code):
    """Sends a Secret message to the Google TV server.

    Args:
      code: Hex code string displayed by the Google TV.
    """
    req = polo_pb2.Secret()
    req.secret = self._EncodeHexSecret(code)
    self._SendMessage(req, polo_pb2.OuterMessage.MESSAGE_TYPE_SECRET)

  def _EncodeHexSecret(self, secret):
    """Encodes a hex secret.

    Args:
      secret: The hex code string displayed by the Google TV.

    Returns:
      An encoded value that can be used in the Secret message.
    """
    # TODO(stevenle): Something further encodes the secret to a 64-char hex
    # string. For now, use adb logcat to figure out what the expected challenge
    # is. Eventually, make sure the encoding matches the server reference
    # implementation:
    #   http://code.google.com/p/google-tv-pairing-protocol/source/browse/src/com/google/polo/pairing/PoloChallengeResponse.java
    result = bytearray(len(secret) / 2)
    for i in xrange(len(result)):
      start_index = 2 * i
      end_index = 2 * (i + 1)
      result[i] = int(code[start_index:end_index], 16)
    return bytes(result)

  def _SendMessage(self, message, message_type):
    """Sends a message to the Google TV server.

    Args:
      message: A proto request message.
      message_type: A polo_pb2.OuterMessage.MESSAGE_TYPE_* constant.

    Returns:
      The amount of data sent, in bytes.
    """
    req = polo_pb2.OuterMessage()
    req.protocol_version = 1
    req.status = polo_pb2.OuterMessage.STATUS_OK
    req.type = message_type
    req.payload = message.SerializeToString()
    data = req.SerializeToString()
    return self.Send(data)


class AnymoteProtocol(BaseProtocol):

  def __init__(self):
    # Work in progress...
    raise NotImplementedError
