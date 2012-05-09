# Python client for the Google TV Pairing and Anymote protocols. #

## Installation ##

    # Install M2Crypto (required for pairing script)
    sudo easy_install m2crypto

    # Install googletv-anymote
    sudo python setup.py install

## Pairing Protocol ##

The "scripts" directory contains some sample scripts to aid with the Google TV
pairing process.

### Discovery Phase ###

If you're not sure what IP address or hostname your Google TV is running on, you
can use the "discover" script to determine its IP and port. The script requires
[pybonjour](http://code.google.com/p/pybonjour/).

    googletv/scripts$ ./discover.py

(Only tested on Mac.)

### Identification and Authentication Phases ###

Next, you'll need to start the pairing process by authenticating a certificate
with Google TV. The "pair" script provides an example of communicating with
Google TV using the
[Pairing Protocol](http://code.google.com/tv/remote/docs/pairing.html).

If you do not have a cert, the "pair" script can auto-generate a self-signed
cert that you can use. [OpenSSL](http://www.openssl.org/) is required for
certificate generation.

The Pairing Protocol server typically runs on the port one more than the Anymote
server. For example, if the Anymote server runs on 9551, then the Pairing
Protocol server listens on 9552.

    googletv/scripts$ ./pair.py --host=NSZGT1-6131194.local --cert=cert.pem

Once the cert is paired, you can use it to make all subsequent requests to the
Anymote Protocol.

## Anymote Protocol ##

After the certificate has been paired with Google TV, the certificate can be
used to send messages to Google TV via the Anymote Protocol.

Example, fling a URI to Google TV:

```python
import googletv

HOST = 'NSZGT1-6131194.local'
CERT = 'cert.pem'


def main():
  uri = 'http://www.google.com'
  with googletv.AnymoteProtocol(HOST, CERT) as gtv:
    gtv.fling(uri)


if __name__ == '__main__':
  main()
```

Example, turn off the TV after X seconds (requires
[twisted](http://twistedmatrix.com/)):

```python
import os
import sys
import time
import googletv
from googletv.proto import keycodes_pb2
from twisted.internet import reactor
from twisted.internet import task

HOST = 'NSZGT1-6131194.local'
CERT = 'cert.pem'


def turn_off(gtv):
  gtv.press(keycodes_pb2.KEYCODE_TV_POWER)
  print 'Sent power signal to GTV'
  return gtv


def exit(gtv):
  gtv.close()
  reactor.stop()


def main(argv):
  if len(argv) < 2:
    sys.exit('Usage: %s <seconds>' % os.path.basename(argv[0]))

  gtv = googletv.AnymoteProtocol(HOST, CERT)
  seconds = int(argv[1])
  d = task.deferLater(reactor, seconds, turn_off, gtv)
  d.addCallback(exit)
  print 'Turning off TV after %s secs...' % seconds
  gtv.connect()
  reactor.run()


if __name__ == '__main__':
  main(sys.argv)
```
