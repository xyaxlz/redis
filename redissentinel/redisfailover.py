#!/sbin/python
# -*- coding: UTF-8 -*-
import json
import requests
import sys
import os
import socket
import zynsc
import time
from zyqconf import qconf_py as qconf
import argparse

#yz_httpproxy = zynsc_cli.use_cluster("yz").get_service("arch.testSentinel_redisProxy.http")
#m5_httpproxy = zynsc_cli.use_cluster("m5").get_service("arch.testSentinel_redisProxy.http")

print(sys.argv)

#namespace = "arch.testSentinel_redisProxy.http"
#failed_addr = "10.100.90.161:9999" 
#success_addr = "10.100.90.162:9999"

namespace = sys.argv[1]
failed_addr = sys.argv[4]+":"+sys.argv[5] 
success_addr = sys.argv[6]+":"+sys.argv[7]

print namespace
print failed_addr
print success_addr

fail_idc = bytes.decode(qconf.get_conf("/arch_group/idc/current"),  encoding="utf-8")
print fail_idc


def send_mail(title, level="error"):


    body = "<table align='center' border='2' cellpadding='0' cellspacing='0' width='700' style='border-collapse:collapse;'>" \
        "<tr><td colspan=2 align='center' style='color:red'>{title}</td></tr>" \
        "<tr><td class='left'>集群名字</td><td>{namespace}</td></tr>" \
        "<tr><td class='left'>old master</td><td>{failed_addr}</td></tr>" \
        "<tr><td class='left'>new master</td><td>{success_addr}</td></tr>" \
    "</table>".format(
        title=title,
        namespace=namespace,
        failed_addr=failed_addr,
        success_addr=success_addr
    )

    style = "<style>table tr {text-align:center;font-size:16px;height: 80px;border: 2px solid #000;}table td.left {width:150px}</style>" 
    body = style + body

    if level == "error":
        subject = "sentinel (redis HA) error"
    else:
        subject = "sentinel (redis HA) notice"
    
    data = {
        "body_type": "html",
        "body": body,
        "from_addr": "service_warning@zhangyue.com",
        #"to_addr": "architecture.list@zhangyue.com,dba.list@zhangyue.com",
        "to_addr": "liqingbin@zhangyue.com",
        "subject": subject,
    }

    ser = zynsc_cli.get_service("arch.zkapi_email.http")
    
    email_url = "http://{}:{}/v1/email".format(ser.host, ser.port)
    try:    
        res=requests.post(email_url, data=data, timeout=3)
        log("send_mail:" + res.text)
    except Exception as err:
        log("send_mail:" + str(err.args))




def log(msg):
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    metadata = "namespace={};failed_addr={};success_addr={}\n" \
           .format(
            namespace,
            failed_addr,
            success_addr
        )

    print("%s: %s, metadata: %s" % (t, msg, metadata))

def http_post(url, param):
    for idx in range(3):
        try:
            res = requests.post(url, params=param, timeout=20)
            log("http_put=: idx={};url={}; text={};http_code={};".format(
                idx,
                url,
                res.text,
                res.status_code
            ))
            if res.status_code == 200:
                response = res.json()
                return response
        except Exception as err:
            log(str(err.args))


def http_put(url, data, isJson=True):
    headers = {}
    if isJson:
        headers = {"Content-Type": "application/json"}
        data = json.dumps(data)

    for idx in range(3):
        try:
            res = requests.put(url, data=data, headers=headers, timeout=20)
            log("http_put=: idx={};url={}; text={};http_code={};".format(
                idx,
                url,
                res.text,
                res.status_code
            ))
            if res.status_code == 200:
                try:
                    return res.json()
                except Exception as err:
                    return res.text
        except Exception as err:
            log(str(err.args))


def put_ns(namespace, failed_addr, success_addr,fail_idc):
    
    #idc = "m5"
    for idc in ["m5","yz"]:
        http_proxy = zynsc_cli.use_cluster(idc).get_service(namespace) 
        url = "http://{}/api/update/conf".format(http_proxy)
    
        param = {
            "failed_addr": failed_addr,
            "success_addr": success_addr,
            "idc": fail_idc
        }

        
        res = http_put(url, param)
        if not res:
            return "http_put_error"
        if res['msg'] != "ok":
            return res 
    return "ok"

res=put_ns(namespace, failed_addr, success_addr,fail_idc)  
if res == "ok":
    send_mail("Redis 主从切换成功", level="notice")
else:
    send_mail("Redis 主从切换失败", level="error")

#curl -X PUT -H "Content-Type: application/json" -d '{"failed_addr":"10.100.90.161:7777","success_addr":"10.100.90.161:9999","idc":"m5"}' http://10.100.20.219:18888/api/update/conf

#curl -X PUT -H "Content-Type: application/json" -d '{"failed_addr":"10.100.90.162:8888","success_addr":"10.100.90.161:8888","idc":"yz"}' http://10.100.90.162:18888/api/update/conf
