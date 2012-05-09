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

"""Sends some keys to a Google TV server."""

__author__ = 'masterpi314@gmail.com (Adam Lohr)'

import optparse
import os
import sys
import googletv
from googletv.proto import keycodes_pb2


def get_parser():
  """Creates an optparse.OptionParser object used by this script."""
  usage = 'Usage: %prog [--host=] [--port=9551] [--cert=cert.pem] <key ...>'
  parser = optparse.OptionParser(usage=usage)

  parser.add_option(
      '--cert',
      default='cert.pem',
      help='Path to cert file.')

  parser.add_option(
      '--host',
      default='NSZGT1-6131194.local',
      help='Host of the Google TV server.')

  parser.add_option(
      '--port',
      default=9551,
      type='int',
      help='Port number.')

  return parser


def main():
  parser = get_parser()
  options, args = parser.parse_args()
  if not args:
    sys.exit(parser.get_usage())

  host = options.host
  port = options.port
  cert = options.cert
  if not os.path.isfile(cert):
    sys.exit('No cert file. Use --cert.')

  keys = []
  for arg in args:
    if ':' in arg:
      keycode_name, direction = arg.split(':')
      keycode = getattr(keycodes_pb2, 'KEYCODE_%s' % keycode_name)
    else:
      keycode = getattr(keycodes_pb2, 'KEYCODE_%s' % arg)
      direction = None
    keys.append((keycode, direction))

  with googletv.AnymoteProtocol(host, cert, port=port) as gtv:
    for (keycode, direction) in keys:
      if direction:
        action = 'up' if direction.lower() == 'u' else 'down'
        gtv.keycode(keycode, action)
      else:
        gtv.press(keycode)


if __name__ == '__main__':
  main()
