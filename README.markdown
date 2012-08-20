# benchmark.py

Script for benchmarking command line scripts. Runs the command multiple times
and collates the running times from the `usr/bin/time` command, printing out
maximum, minimum and average running times.

## Usage

```sh
  benchmark.py [-h] N command [command ...]
```

* N - the number of times to run the command
* command - the command to profile

## Example output

```sh
  $ benchmark.py 5 sudo apt-get update
                 system              user                total               
  min            0:00:00.000012      0:00:01.000029      0:00:01.000044      
  max            0:00:00.000016      0:00:01.000034      0:00:01.000046      
  total          0:00:00.000067      0:00:05.000158      0:00:05.000225      
  average        0:00:00.000013      0:00:01.000031      0:00:01.000045      
```

## Copyright

Released under the GPL 3.0. See LICENSE.

