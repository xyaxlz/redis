for i in `seq 14`
do
	echo rdb${i}v.infra.bjac.pdtv.it
	scp  config_set.sh   rdb${i}v.infra.bjac.pdtv.it:/data/install
	ssh rdb${i}v.infra.bjac.pdtv.it "cd /data/install; sh config_set.sh"
	#ssh mdb${i}v.infra.bjac.pdtv.it "/etc/init.d/iptables restart"
	echo ""
done

