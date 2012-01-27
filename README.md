# Google TV: Python implementation of Pairing Protocol and Anymote Protocol #

## Installation ##

    sudo python setup.py install

## Pairing Protocol ##

The "scripts" directory contains some sample scripts to aid with the Google TV
pairing process.

### Discovery Phase ###

If you're not sure what IP address or hostname your Google TV is running on, you
can use the "discover" script to determine its IP and port. The script requires
[pybonjour](http://code.google.com/p/pybonjour/).

    googletv/scripts$ ./discover

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
server. For example, if the Anymore server is on 9551, then the Pairing Protocol
server listens on 9552.

    googletv/scripts$ ./pair --cert=mycert.pem

## Anymote Protocol ##

TBD
