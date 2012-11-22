#!/bin/bash
#copyleft 2012 vpstrace.com

echo "Running fio...."
cd fio
make
./fio --bs=4k --size=128m --direct=1 --runtime=10 --rw=randread --numjobs=32 --group_reporting --time_based --name=128m > ../log/fio_read.log 2> ../log/fio_read-error.log
./fio --bs=4k --size=128m --direct=1 --runtime=10 --rw=randwrite --numjobs=32 --group_reporting --time_based --name=128m > ../log/fio_write.log 2> ../log/fio_write-error.log
cd ..
echo "Running UnixBench...."
cd UnixBench
./Run -c 1 -c `grep -c processor /proc/cpuinfo` > ../log/unixbench.log 2> ../log/unixbench-error.log
