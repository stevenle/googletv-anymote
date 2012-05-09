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
import googletv.proto.keycodes_pb2


def get_parser():
  """Creates an optparse.OptionParser object used by this script."""
  usage = 'Usage: %prog [--host=] [--port=9551] [--cert=cert.pem] <key> ...'
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

  def before(n,h):
      loc=h.find(n)
      if loc==-1:
          return h
      return h[:loc]

  def after(n,h):
      loc=h.find(n)
      if loc==-1:
          return h
      return h[loc+1:]

  keys = [(getattr(googletv.proto.keycodes_pb2,"KEYCODE_"
      +before(":",arg.upper())),after(":",arg.upper()))
          for arg in args]
  with googletv.AnymoteProtocol(host, cert, port=port) as gtv:
    for (key,ud) in keys:
      if ud=="U":
        gtv.keycode(key,"up")
      elif ud=="D":
        gtv.keycode(key,"down")
      else:
        gtv.press(key)


if __name__ == '__main__':
  main()
