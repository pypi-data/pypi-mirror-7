safe argparse library
=====================

argparse is a library which is a backport, so it's only needed on Python 2.6.
Unfortunately, this makes it hard to consume in things that want to run on
2.7 and above as well and just want to declare that they need it.

argparse-safe encapsulates the logic and provides a requirement that can
be safely used in 2.6 and 2.7.
