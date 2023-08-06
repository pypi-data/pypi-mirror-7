=======
watchit
=======

*I'm walking here*


Using
=======


A typical use of the this is to wait a second after a file has changed and then
run `make`. Put that all in a loop.::

    while true; do watchit && sleep 1 && make; done

Issues
========

It stops when doing a `ctrl-c` but doesn't exit.  The workaround right now is
to use `ctrl-z` and then `kill %1`.  
