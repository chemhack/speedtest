#!/bin/bash
#copyleft 2012 vpstrace.com

echo "Running fio...."
cd fio
make
./fio ../config/fio_reads.ini > ../log/fio_read.log 2> ../log/fio_read-error.log
./fio ../config/fio_reads.ini > ../log/fio_write.log 2> ../log/fio_write-error.log
cd ..
echo "Running ioping..."
cd ioping
make
echo "**ioping***" >> ../log/ioping.log
./ioping -c 10 . >> ../log/ioping.log 2>> ../log/ioping-error.log
echo "**ioping seek rate***" >> ../log/ioping.log
./ioping -RD . >> ../log/ioping.log 2>> ../log/ioping-error.log
echo "**ioping sequential***" >> ../log/ioping.log
./ioping -RL . >> ../log/ioping.log 2>> ../log/ioping-error.log
echo "**ioping cached***" >> ../log/ioping.log
./ioping -RC . >> ../log/ioping.log 2>> ../log/ioping-error.log
cd ..
echo "Running network test..."
cd network
python latencytest.py -o ../log/network.log
cd ..
echo "Running UnixBench...."
cd UnixBench
./Run -c 1 -c `grep -c processor /proc/cpuinfo` > ../log/unixbench.log 2> ../log/unixbench-error.log
