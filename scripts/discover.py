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

"""Simple script to discover a Google TV server.

Currently only supports discovery of one Google TV server. If there are
multiple Google TVs on the network, see the pybonjour documentation for sample
scripts.

Requires pybonjour:
  http://code.google.com/p/pybonjour/
"""

__author__ = 'stevenle08@gmail.com (Steven Le)'

import select
import pybonjour

REGTYPE  = '_anymote._tcp'
TIMEOUT  = 5


def BrowseCallback(sdRef, flags, interfaceIndex, errorCode, serviceName,
                   regtype, replyDomain):
    if errorCode != pybonjour.kDNSServiceErr_NoError:
        return

    resolved = False

    def ResolveCallback(sdRef, flags, interfaceIndex, errorCode, fullname,
                        hosttarget, port, txtRecord):
      global resolved
      if errorCode == pybonjour.kDNSServiceErr_NoError:
        print 'Resolved service:'
        print '  host =', hosttarget
        print '  port       =', port
        resolved = True

    resolver = pybonjour.DNSServiceResolve(
        0, interfaceIndex, serviceName, regtype, replyDomain, ResolveCallback)
    try:
      while not resolved:
        ready = select.select([resolver], [], [], TIMEOUT)
        if resolver not in ready[0]:
            print 'Resolve timed out'
            break
        pybonjour.DNSServiceProcessResult(resolver)
    finally:
      resolver.close()


def main():
  browser = pybonjour.DNSServiceBrowse(regtype=REGTYPE, callBack=BrowseCallback)
  try:
    ready = select.select([browser], [], [])
    if browser in ready[0]:
      pybonjour.DNSServiceProcessResult(browser)
  finally:
    browser.close()


if __name__ == '__main__':
  main()
