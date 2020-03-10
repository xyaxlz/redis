#!/bin/bash
#for i in {1,2,3,4}
for i in {1,2,3,4,5,6,7,8,9,10,11,12,13,14}
do 
	echo $i
	ssh rdb${i}v.infra.bjac.pdtv.it  "mkdir -p /data/scripts"
	scp redisdbback.sh  rdb${i}v.infra.bjac.pdtv.it:/data/scripts
	ssh rdb${i}v.infra.bjac.pdtv.it  "chmod +x  /data/scripts/redisdbback.sh"
	ssh rdb${i}v.infra.bjac.pdtv.it  "sed -i '/###redis数据库备份/d'  /var/spool/cron/root"
	ssh rdb${i}v.infra.bjac.pdtv.it  "sed -i '/redisdbback.sh/d' /var/spool/cron/root"
	ssh rdb${i}v.infra.bjac.pdtv.it  'echo "###redis数据库备份" >> /var/spool/cron/root'
	ssh rdb${i}v.infra.bjac.pdtv.it  'echo "0 5 * * * /data/scripts/redisdbback.sh >/dev/null 2>&1" >> /var/spool/cron/root '
	
done
