for i in `seq 14`
do
	#echo rdb${i}v.infra.bjac.pdtv.it
	scp  info.sh   rdb${i}v.infra.bjac.pdtv.it:/data/install >/dev/null 2>&1
	ssh rdb${i}v.infra.bjac.pdtv.it "cd /data/install; sh info.sh"
	#ssh mdb${i}v.infra.bjac.pdtv.it "/etc/init.d/iptables restart"
	echo ""
done

