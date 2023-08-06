# netdns

Network DNS Utilities extending and adapting RT Halley's dnspython
library for use within the HyperDNS family of software.

To the extent possible, we have attempted to maintain parsimony with
the python3 branch of dnspython.

We add additional utility functions, primarily around the conversion
of DNS information to and from JSON format.

    http://tools.ietf.org/html/draft-bortzmeyer-dns-json-01
	
    github: bortzmeyer/dns-lg



## Quickstart

### From GitHub

	>>git clone git@github.com:hyperdns/hyperdns-netdns-python3 netdns
	>>cd netdns
	>>. devup
	>>nosetests

### From PyPI

	>>virtualenv -p python3 .python
	>>. .python/bin/activate
	>>pip install hyperdns-netdns
	
