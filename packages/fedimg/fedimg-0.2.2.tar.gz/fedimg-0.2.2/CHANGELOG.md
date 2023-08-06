# Changelog

## 0.1.0

-   Initial PyPI realease

## 0.2.0

-   start working on RPM for fedora
-   setup.py improvements
-   Config file is now read from /etc/fedimg.cfg
-   PEP 8 fixes

## 0.2.1

-   Fix `packages` argument in setup.py to take `find_packages()`
-   More work on RPM packaging

## 0.2.2

-   Actually import `find_packages` so the previous change works
-   Include .pyc and .pyo files for the consumer in /etc/fedmsg.d/
-   Minor fix -- missing comma
