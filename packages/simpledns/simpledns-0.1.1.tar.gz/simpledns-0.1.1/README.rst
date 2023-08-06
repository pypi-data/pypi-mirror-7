SimpleDNS
=========

A lightweight yet useful proxy DNS server 

Install
-------
::

    $ pip install simpledns

Usage
-----

Run ``sudo simpledns`` on your local machine. Then set your DNS server to 127.0.0.1.

::

	$ dig www.twitter.com +short
	twitter.com.
	199.59.149.230
	199.59.148.10
	199.59.150.7
	199.59.150.39

Advanced
--------

::

	$ simpledns -h
	usage: simpledns [-h] [-b BIND_ADDR] [-p BIND_PORT]
	                 [--upstream-ip UPSTREAM_IP] [--upstream-port UPSTREAM_PORT]
	                 [--query-timeout QUERY_TIMEOUT] [--min-ttl MIN_TTL]
	                 [--max-ttl MAX_TTL] [--cache-size CACHE_SIZE] [-t]
	                 [--hosts-file HOSTS_FILE] [--dispatch-conf DISPATCH_CONF]
	                 [-v {0,1,2}] [-q] [-V]

	A lightweight yet useful proxy DNS server

	optional arguments:
	  -h, --help            show this help message and exit
	  -b BIND_ADDR, --bind-addr BIND_ADDR
	                        local address to listen
	  -p BIND_PORT, --bind-port BIND_PORT
	                        local port to listen
	  --upstream-ip UPSTREAM_IP
	                        upstream DNS server ip address
	  --upstream-port UPSTREAM_PORT
	                        upstream DNS server port
	  --query-timeout QUERY_TIMEOUT
	                        time before close port used for querying
	  --min-ttl MIN_TTL     the minimum time a record is held in cache
	  --max-ttl MAX_TTL     the maximum time a record is held in cache
	  --cache-size CACHE_SIZE
	                        record cache size
	  -t, --tcp-server      enables TCP serving
	  --hosts-file HOSTS_FILE
	                        hosts file
	  --dispatch-conf DISPATCH_CONF
	                        URL dispatch conf file
	  -v {0,1,2}, --verbosity {0,1,2}
	                        output verbosity
	  -q, --quiet           disable output
	  -V, --version         print version number and exit
	  
	  
License
-------

MIT
