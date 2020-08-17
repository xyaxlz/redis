#! /usr/bin/python2.7
# -*- coding: utf-8 -*-
#Created zolker



import argparse
import sys
import os
import stat
import socket
import time
import threading
import re
import logging
import copy
import MySQLdb
import subprocess
import socket
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append('/etc/db_tools')
from mysqllib import * 
host_pd_dict={'db':'MySQL','rdb':"Redis",'mdb':'Mongodb'}
host_idc={'bjac':'AliYun','bjza':'Amazon'}
admin_host='127.0.0.1'
admin_port=3307
admin_user='db_admin'
admin_password='BZs*gIyVeH4o0q!f'
dbadmin_host='10.131.9.133'
dbadmin_port=3306
idc_list={'bjac':0,'bjza':1}
role_list={'main':0,"subordinate":1}
def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def arg_parse():

    parse = argparse.ArgumentParser(description='Redis OPS')
    parse.add_argument('--cmd', '-c', default='add_host',help='add host')
    parse.add_argument('--port', '-P', default='0',help='redis port')
    parse.add_argument('--role', '-r', default='subordinate',help='redis role')
    parse.add_argument('--vip', '-L', default='',help='vip')
    parse.add_argument('--subordinate', '-H', type=str, default='',help='hostname')
    parse.add_argument('--idc', '-I', default='bjac',help='redis idc')
    parse.add_argument('--ip', '-a', default='',help='redis idc')
    parse.add_argument('--prod_info', '-d', default='',help='redis prod')
    parse.add_argument('--main', '-m', default='',help='redis main')
    parse.add_argument('--tag', '-t', default='',help='host tag')
    return parse, parse.parse_args()
def add_redis(port,db_role,vip,hostname,idc,ip,prod_info,main):
    db_ins=MySQLBase(admin_host,admin_port,admin_user,admin_password) 
    dbadmin_ins=MySQLBase(dbadmin_host,dbadmin_port,admin_user,admin_password) 
    db_ins.connection()
    db_ins.cursor()
    dbadmin_ins.connection()
    dbadmin_ins.cursor()
    cur_dt=get_time()
    if int(db_role)==0:
	role='main'
    else:
	role='subordinate'
    sql="replace into  cmdb.redis_ins (port,db_role,vip,hostname,idc,ip,prod_info,main)values(%d,%d,'%s','%s',%d,'%s','%s','%s');"%(int(port),int(db_role),vip,hostname,int(idc),ip,prod_info,main)
    dbadmin_sql="replace into dbadmin.app_redis(ip,port,role,owner,version,vip,date) values('%s',%d,'%s','%s','3.2','%s','%s')"%(ip,int(port),role,prod_info,vip,cur_dt)
    print sql
    print dbadmin_sql
    rt=db_ins.query(sql)
    rt=dbadmin_ins.query(dbadmin_sql)
    print rt
    
def add_host(hostname,ip,os,cpu,cpu_num,mem,disk,service):
    db_ins=MySQLBase(admin_host,admin_port,admin_user,admin_password) 
    db_ins.connection()
    db_ins.cursor()
    sql="insert into  cmdb.host (hostname,ip,os,cpu,cpu_num,mem,disk,service,add_time)values('%s','%s',%d,'%s',%d,%d,%d,%d,'%s');"%(hostname,ip,os,cpu,cpu_num,mem,disk,service,'2016-11-01')
    print sql
    rt=db_ins.query(sql)
    print rt
def add_dbadmin_host(hostname,ip):
    db_ins=MySQLBase(dbadmin_host,dbadmin_port,admin_user,admin_password) 
    db_ins.connection()
    db_ins.cursor()
    h_list=hostname.split('.')
    zabbix_name='%s_%s_%s'%(h_list[2],h_list[1],h_list[0])
    sql="insert ignore into  dbadmin.app_host (hostname,ip,zabbix_name)values('%s','%s','%s');"%(hostname,ip,zabbix_name)
    print sql
    rt=db_ins.query(sql)
    print rt
def cmdb_op():
     parser, opts = arg_parse()
     cmd=opts.cmd
     tag=opts.tag
     port=opts.port
     db_role=int(role_list[opts.role])
     vip=opts.vip
     subordinate=opts.subordinate
     idc=idc_list[opts.idc]
     ip=opts.ip
     #if not ip:
    # 	ip=socket.gethostbyname(hostname)	
     prod_info=opts.prod_info
     main=opts.main
     if subordinate=='' and main == "":
	print "Subordinate & main is null"
	sys.exit()
     os=0
     cpu='Intel(R) Xeon(R) CPU E5-2680 v3 @ 2.50GHz'	
     cpu_num=1
     redis_config={"cpu":"Intel(R) Xeon(R) CPU E5-2680 v3 @ 2.50GHz","cpu_num":1,"mem":64,"disk":400,"service":1,'os':0}
     redis_bjza_config={"cpu":"Intel(R) Xeon(R) CPU E5-2666 v3 @ 2.90GHz","cpu_num":1,"mem":32,"disk":600,"service":1,'os':0}
     #redis_low_config={"cpu":"Intel(R) Xeon(R) CPU E5-2680 v3 @ 2.50GHz","cpu_num":1,"mem":32,"disk":400,"service":1,'os':0}
     redis_low_config={"cpu":"Intel(R) Xeon(R) CPU E5-2682 v4 @ 2.50GHz","cpu_num":1,"mem":32,"disk":400,"service":1,'os':0}
     mysql_config={"cpu":"Intel(R) Xeon(R) CPU E5-2680 v3 @ 2.50GHz","cpu_num":1,"mem":32,"disk":400,"service":0,'os':0}
     mysql_low_config={"cpu":"Intel(R) Xeon(R) CPU E5-2680 v3 @ 2.50GHz","cpu_num":0,"mem":16,"disk":400,"service":0,'os':0}
     print cmd
     
     if cmd=="add_redis":
        if main != '' and subordinate=='':
     	     main_ip=socket.gethostbyname(main)	
     	     add_redis(port,0,vip,main,idc,main_ip,prod_info,'')
             sys.exit()
        
     	main_ip=socket.gethostbyname(main)	
        add_redis(port,0,vip,main,idc,main_ip,prod_info,'')
        for s in subordinate.split(','):
     	      subordinate_ip=socket.gethostbyname(s)	
              add_redis(port,1,vip,s,idc,subordinate_ip,prod_info,main)
      
     	#add_redis(port,db_role,vip,hostname,idc,ip,prod_info,main)
	
     if cmd=="add_dbadmin_host":
     	add_dbadmin_host(hostname,ip)
     if cmd=="add_host":
	if tag=="redis":
     		add_host(hostname,ip,redis_config["os"],redis_config["cpu"],redis_config["cpu_num"],redis_config["mem"],redis_config["disk"],redis_config["service"])
	if tag=="redis_low":
     		add_host(hostname,ip,redis_low_config["os"],redis_low_config["cpu"],redis_low_config["cpu_num"],redis_low_config["mem"],redis_low_config["disk"],redis_low_config["service"])
	if tag=="mysql":
     		add_host(hostname,ip,mysql_config["os"],mysql_config["cpu"],mysql_config["cpu_num"],mysql_config["mem"],mysql_config["disk"],mysql_config["service"])
	if tag=="mysql_low":
     		add_host(hostname,ip,mysql_low_config["os"],mysql_low_config["cpu"],mysql_low_config["cpu_num"],mysql_low_config["mem"],mysql_low_config["disk"],mysql_low_config["service"])
	if tag=="redis_bjza":
     		add_host(hostname,ip,redis_bjza_config["os"],redis_bjza_config["cpu"],redis_bjza_config["cpu_num"],redis_bjza_config["mem"],redis_bjza_config["disk"],redis_bjza_config["service"])
mysqlbase = MySQLBase('127.0.0.1', '3307', 'db_admin', 'BZs*gIyVeH4o0q!f')
mysqlbase.connection()
cmdb_op()
#f=open('redis_c.txt').readlines()
#for i in f:
#	i=i.strip()
#	i=i.split#(',')
#	i[1]=role_list[i[1]]
#	i[2]=idc_list[i[2]]
#	i[3]="%s.infra.bjac.pdtv.it"%i[3]
#	if i[5]:
#		i[5]="%s.infra.bjac.pdtv.it"%i[5]
#	print i
 #       add_redis(int(i[0]),int(i[1]),'',i[3],int(i[2]),i[4],'订阅提醒',i[5])	
