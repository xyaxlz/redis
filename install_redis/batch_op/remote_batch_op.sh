for i in `seq 14`
do
	echo $i 
	scp ../redis/redislogin   rdb${i}v.infra.bjac.pdtv.it:/data/install
	scp batch_op.sh   rdb${i}v.infra.bjac.pdtv.it:/data/install
	ssh rdb${i}v.infra.bjac.pdtv.it "cd /data/install; sh batch_op.sh"
	#ssh mdb${i}v.infra.bjac.pdtv.it "/etc/init.d/iptables restart"
done

