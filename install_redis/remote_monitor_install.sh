#!/bin/bash

usage()
{
    cat <<EOF
Redis zabbix客户端安装
Usage:$0 [OPTION] [str] 
   -h     help              
   -m     redis ip or hostname 
   
EOF
exit
}
[ $# == 0 ] && usage 


while getopts ":m:s:p:P:t:g:fh" opts;do
  case $opts in
	h)
		usage
		;;
	m)
		HOST=$OPTARG
		;;
	*)
		-$OPTARG unvalid
		usage;;
  esac
done



scp -r  monitor  $HOST:/data/install/
ssh $HOST  "cd /data/install/monitor;sh zabbix_agent.install"

ssh $HOST  "cd /data/install/monitor;\cp -rf  scripts/ /etc/zabbix/"
ssh $HOST  "cd /data/install/monitor;\cp -rf  redis.conf /etc/zabbix/zabbix_agentd.d/"
ssh $HOST  "chmod +s /bin/netstat"
ssh $HOST  "yum install python-simplejson -y"
ssh $HOST  "/etc/init.d/zabbix-agent restart"



