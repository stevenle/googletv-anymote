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
from googletv.proto import keycodes_pb2
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

  def __exit__(self, unused_type, unused_val, unused_traceback):
    self.close()

  def close(self):
    self.ssl.close()

  def send(self, data):
    data_len = struct.pack('!I', len(data))
    sent = self.ssl.write(data_len + data)
    assert sent == len(data) + 4
    return sent


class PairingProtocol(BaseProtocol):
  """Google TV Pairing Protocol.

  More info:
    https://developers.google.com/tv/remote/docs/pairing
  """

  def __init__(self, host, certfile, port=9552):
    super(PairingProtocol, self).__init__(host, port, certfile)

  def send_pairing_request(self, client_name, service_name='AnyMote'):
    """Initiates a new PairingRequest with the Google TV server.

    Args:
      client_name: A string that can be used to identify the client making reqs.
      service_name: The name of the service to pair with.
    """
    req = polo_pb2.PairingRequest()
    req.service_name = service_name
    req.client_name = client_name
    self._send_message(req, polo_pb2.OuterMessage.MESSAGE_TYPE_PAIRING_REQUEST)

  def send_options(self, *args, **kwargs):
    """Sends an Options message to the Google TV server.

    Currently, only a 4-length HEXADECIMAL message is supported. Will support
    other types in the future.
    """
    options = polo_pb2.Options()
    encoding = options.input_encodings.add()
    encoding.type = ENCODING_TYPE_HEXADECIMAL
    encoding.symbol_length = 4
    self._send_message(options, polo_pb2.OuterMessage.MESSAGE_TYPE_OPTIONS)

  def send_configuration(self, encoding_type=ENCODING_TYPE_HEXADECIMAL,
                         symbol_length=4, client_role=ROLE_TYPE_INPUT):
    """Sends a Configuration message to the Google TV server.

    Currently, only a 4-length HEXADECIMAL message is supported. Will support
    other types in the future.
    """
    req = polo_pb2.Configuration()
    req.encoding.type = encoding_type
    req.encoding.symbol_length = symbol_length
    req.client_role = client_role
    self._send_message(req, polo_pb2.OuterMessage.MESSAGE_TYPE_CONFIGURATION)

  def send_secret(self, code):
    """Sends a Secret message to the Google TV server.

    Args:
      code: Hex code string displayed by the Google TV.
    """
    req = polo_pb2.Secret()
    req.secret = self._encode_hex_secret(code)
    self._send_message(req, polo_pb2.OuterMessage.MESSAGE_TYPE_SECRET)

  def _encode_hex_secret(self, secret):
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
      result[i] = int(secret[start_index:end_index], 16)
    return bytes(result)

  def _send_message(self, message, message_type):
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
    return self.send(data)


class AnymoteProtocol(BaseProtocol):
  """Google TV Anymote Protocol.

  More info:
    https://developers.google.com/tv/remote/docs/
  """

  def __init__(self, host, certfile, port=9551):
    super(AnymoteProtocol, self).__init__(host, port, certfile)

  def keycode(self, keycode, action):
    """Sends a KeyCode event to Google TV.

    Args:
      keycode: A Code from keycodes_pb2.
      action: Either "down" (pressed) or "up" (released).
    """
    req = remote_pb2.RequestMessage()
    req.key_event_message.keycode = keycode
    if action == 'up':
      req.key_event_message.action = keycodes_pb2.UP
    else:
      req.key_event_message.action = keycodes_pb2.DOWN
    self._send_message(req)

  def fling(self, uri):
    """Sends a Fling event to Google TV.

    Use a Fling event to request Google TV to start an activity associated with
    the specified URI.

    Args:
      uri: URI to send to Google TV.
    """
    req = remote_pb2.RequestMessage()
    req.fling_message.uri = uri
    self._send_message(req)

  def mouse(self, x=0, y=0):
    """Sends a MouseEvent to Google TV.

    Args:
      x: Relative movement of the cursor on the x-axis.
      y: Relative movement of the cursor on the y-axis.
    """
    req = remote_pb2.RequestMessage()
    req.mouse_event_message.x_delta = x
    req.mouse_event_message.y_delta = y
    self._send_message(req)

  def press(self, keycode):
    """Sends a keycode down then up.

    Args:
      keycode: A Code from keycodes_pb2.
    """
    self.keycode(keycode, 'down')
    self.keycode(keycode, 'up')

  def _send_message(self, message):
    """Sends a RequestMessage wrapped in a RemoteMessage.

    Args:
      message: A remote_pb2.RequestMessage object.
    """
    req = remote_pb2.RemoteMessage()
    req.request_message.CopyFrom(message)
    data = req.SerializeToString()
    return self.send(data)
