#!/bin/bash
#copyleft 2012 vpstrace.com

echo " #     # ######   #####  #######                             
 #     # #     # #     #    #    #####    ##    ####  ###### 
 #     # #     # #          #    #    #  #  #  #    # #      
 #     # ######   #####     #    #    # #    # #      #####  
  #   #  #             #    #    #####  ###### #      #      
   # #   #       #     #    #    #   #  #    # #    # #      
    #    #        #####     #    #    # #    #  ####  ###### 
                                                             "


function install_dependencies(){
	if [ `which apt-get >/dev/null 2>&1; echo $?` -ne 0 ]; then
		yum install -y kernel-devel libaio-devel gcc-c++ perl python perl-Time-HiRes  
	else
		apt-get install -y build-essential libaio-dev perl
	fi
}

function mk_log_dir(){
	mkdir log
}

echo "Installing dependencies....."
install_dependencies
mk_log_dir

chmod u+x run.sh
nohup ./run.sh > ./log/run.log 2>&1 & &> /dev/null

echo "Benchmark started in backgroud, you will be notified by email after the benchmark is done. It's safe to terminate SSH connection now. "
tail -n 25 -F ./log/run.log
