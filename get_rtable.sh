#!/bin/bash

PW="zebra"

expect -c "
 set timeout 5
 spawn telnet localhost 2605
 expect \"Password:\"
 send \"${PW}\n\"
 expect \"bgpd>\"
 send \"show ip bgp summary\n\"
 expect \"bgpd>\"
 send \"show ip bgp\n\"
 expect \"bgpd>\"
 send \"exit\n\"
 exit 0
"
