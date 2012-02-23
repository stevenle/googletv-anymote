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

"""Flings a URI to a Google TV server."""

__author__ = 'stevenle08@gmail.com (Steven Le)'

import optparse
import os
import sys
import googletv


def get_parser():
  """Creates an optparse.OptionParser object used by this script."""
  usage = 'Usage: %prog [--host=] [--port=9551] [--cert=cert.pem] <uri>'
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

  uri = args[0]
  with googletv.AnymoteProtocol(host, cert, port=port) as gtv:
    gtv.fling(uri)


if __name__ == '__main__':
  main()
