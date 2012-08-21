#!/usr/bin/env python
"""Script for benchmarking scripts on a Unix platform.

Relies on /usr/bin/time being available (and with the same output format as it
has on my current Debian box ;P).
"""

from __future__ import print_function

import subprocess
import argparse
import re

from collections import defaultdict
from datetime import timedelta

TIME = "/usr/bin/time"
MATCH_TIME_RE = "((?:\d+:)?\d{1,2}\.\d\d)"
EXTRACT_TIME_RE = re.compile("(?:(\d+):)?(\d{1,2})\.(\d\d)")
TIMES = ("system", "user", "elapsed")

class BenchmarkError(Exception):
    """Module-level exception.
    """
    pass

class ProcessError(BenchmarkError):
    """Thrown when error executing the user's command.
    """
    def __init__(self, return_code, error):
        self.return_code = return_code
        self.error = error

    def __str__(self):
        return "Error {} executing process: {}".format(self.return_code, \
                                                           self.error)

class ParseTimeError(BenchmarkError):
    """Thrown when error parsing a time string as returned by the time
    command.
    """
    pass
    
def parse_time(time):
    """Given a time string as returned as part of the output of the
    /usr/bin/time command, returns the equivalent timedelta.

    Raises ParseTimeError when given a string that cannot be parsed.

    >>> parse_time("12:12.00")
    datetime.timedelta(0, 732)
    """
    match = EXTRACT_TIME_RE.search(time)
    if not match:
        raise ParseTimeError("{} could not be parsed as a time".format(time))
    minutes, seconds, microseconds = match.groups(0)
    return timedelta(microseconds=int(microseconds), \
                         seconds=int(seconds), \
                         minutes=int(minutes))

def parse_time_output(output):
    """Parses the output of the /usr/bin/time command, returning a dict of
    deltas representing the running time of the process.
    """
    def extract_time(name):
        reg_ex = re.compile(MATCH_TIME_RE + name)
        match = reg_ex.search(output)
        if not match:
            raise ParseTimeError(("Could not find {} time in output: " + \
                                     "{}").format(name, output))
        return parse_time(match.group(1))

    return dict((k, extract_time(k)) for k in TIMES)
    
def time_process(command):
    """Given the name of a command, times it, returning a dict of timedeltas
    describing the running time.
    """
    p = subprocess.Popen([TIME] + command, stdout=subprocess.PIPE, \
                             stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()

    if p.returncode is not 0:
        raise ProcessError(return_code=p.returncode, error=stderr)

    return parse_time_output(stderr)

def main():
    parser = argparse.ArgumentParser(description="Profile the running time " + \
                                         "of a shell command.")
    parser.add_argument('n_times', type=int, metavar='N', \
                            help="Number of times to run command.")
    parser.add_argument('command', type=str, nargs="+", help="Command to profile")

    args = parser.parse_args()

    history = defaultdict(list)

    for i in range(args.n_times):
        times = time_process(args.command)
        for t in TIMES:
            history[t].append(times[t])
        
    columns = "".join("{" + "{}:<20".format(i) + "}" for i in \
                          range(len(history) + 1))
    
    print(columns.format("", *TIMES))

    def print_row(name, f):
        f_history = [f(history[k]) for k in TIMES]
        print(columns.format(name, *f_history))
    
    print_row("min", min)
    print_row("max", max)
    print_row("total", lambda x: sum(x, timedelta(seconds=0)))
    print_row("average", lambda x: sum(x, timedelta(seconds=0)) / args.n_times)

if __name__ == '__main__':
    main()
