#!/usr/bin/python
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


arg = argparse.ArgumentParser("This is a test!")
arg.add_argument("--failureType", "-t", type=str)
arg.add_argument("--failedHost", "-fh", type=str)
arg.add_argument("--failedPort", "-fp", type=int)
arg.add_argument("--failureClusterAlias", "-a", type=str)
arg.add_argument("--successorHost", "-sh", type=str)
arg.add_argument("--successorPort", "-sp", type=int)
arg.add_argument("--recoveryUID", "-id", type=str)
arg.add_argument("--commandHint", "-c", type=str)
args = arg.parse_args()

failureType = args.failureType
failedHost = args.failedHost
failedPort = args.failedPort
failureClusterAlias = args.failureClusterAlias
successorHost = args.successorHost
successorPort = args.successorPort
recoveryUID = args.recoveryUID
commandHint = args.commandHint

idc = bytes.decode(qconf.get_conf("/arch_group/idc/current"),  encoding="utf-8")
#"http://localhost:8300"
ns_idc_urls = {
    "m5":[
        "http://10.100.20.1:8181",
        "http://10.100.20.2:8181",
    ],
    "yz":[
        "http://10.100.96.134:8181",
        "http://10.100.96.33:8181",
    ]
}

ns_urls = ns_idc_urls[idc]
mydrc_ns = "arch.mysqldrc.http"
orch_url = "http://{{ zyvar_localip }}:{}".format(os.getenv("ZYAGENT_HTTPPORT"))


mysql_type = "mysql"
if failureClusterAlias:
    try:
        mysql_type = failureClusterAlias.split(".")[1].split("_")[-1]
    except Exception as err:
        mysql_type = "mysql"


#一个IP:port可能对应多个ns
def get_all_ns(host, port):
    ip = socket.gethostbyname(host)
    path = "/archapi/paas/ext/provider/{}_{}".format(ip, port)
    param = {
        "type": mysql_type,
    }
    for url in ns_urls:
        res = http_get(url+path, {})
        if res:
            return res
    return None


def put_and_create_ns(host, port, appoint_host, appoint_port, role, ns, weight=None):
    res = put_ns(host, port, role, ns, weight)
    if not res:
        res = create_ns(host, port, appoint_host, appoint_port, role, ns, weight)
    return res


def create_ns(host, port, appoint_host, appoint_port, role, ns, weight=None):
    path = "/archapi/paas/ext/provider/{}_{}".format(socket.gethostbyname(appoint_host), appoint_port)

    param = {
        "type": mysql_type,
        "uri": role,
        "provider": "{}_{}".format(socket.gethostbyname(host), port),
        "weight": weight,
    }
    if weight is None:
        param["weight"] = 1

    for url in ns_urls:
        res = http_put(url+path, param, False)
        if res and ns in res['success']:
            return res
    return None


def put_ns(host, port, role, ns, weight=None):
    ip = socket.gethostbyname(host)
    path = "/archapi/paas/ext/provider/{}_{}".format(ip, port)

    param = {
        "type": mysql_type,
        "uri": role,
    }

    if weight is not None:
        param["weight"] = weight

    for url in ns_urls:
        res = http_post(url+path, param)
        if res and ns in res['success']:
            return res
    return None


def delete_ns(host, port, ns):
    ip = socket.gethostbyname(host)
    path = "/archapi/paas/ext/provider/{}_{}".format(ip, port)

    param = {
        "type": mysql_type,
         # "namespace": ns // 去除ns
    }

    for url in ns_urls:
        res = http_del(url+path, param)
        if not res:
            return None
        else:
            return res

def stop_drc():
    jobs = get_drc_jobs()
    #没有加入DRC
    if jobs and failureClusterAlias not in jobs:
        return True

    url = get_drc_url(failureClusterAlias)
    param = {"main": ""}
    res = http_put(url, param)
    return res


def get_drc_jobs():
    ser = zynsc_cli.get_service(mydrc_ns)
    url = "http://{}:{}/mydrc/cluster/all/job_ids".format(ser.host, ser.port)
    res = http_get(url, {})
    return res

def start_drc(host, port):
    jobs = get_drc_jobs()
    #没有加入DRC
    if jobs and failureClusterAlias not in jobs:
        return True

    url = get_drc_url(failureClusterAlias)

    param = {"main": "{}:{}".format(host, port)}
    res = http_put(url, param)
    return res


def get_drc_url(clusterName):
    ser = zynsc_cli.get_service(mydrc_ns)
    return "http://{}:{}/mydrc/mariadb/{}/main".format(ser.host, ser.port, clusterName)


def forget(host, port):
    url = "{}/api/forget/{}/{}".format(orch_url, host, port)
    res = http_get(url, {})
    if res and res["Code"] == "OK":
        return res
    return None


def start_subordinate(host, port):
    url = "{}/api/start-subordinate/{}/{}".format(orch_url, host, port)
    res = http_get(url, {})
    if res and res["Code"] == "OK":
        return res

    return None


def reset_cluster_alias(host, port, alias):
    url = "{}/api/set-cluster-alias/{}:{}".format(orch_url, host, port)
    param = {
        "alias": alias
    }
    res = http_get(url, param)
    if res and res["Code"] == "OK":
        return res

    return None


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
    return None


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
    return None


def http_get(url, param):
    for idx in range(3):
        try:
            res = requests.get(url, params=param, timeout=20)
            log("http_put=: idx={};url={}; text={};http_code={};".format(
                idx,
                url,
                res.text,
                res.status_code
            ))

            if res.status_code == 200:
                response = res.json(encoding="utf-8")
                return response
        except Exception as err:
            log(str(err.args))

    return None


def http_del(url, param):
    for idx in range(3):
        try:
            res = requests.delete(url, params=param, timeout=20)
            log("http_put=: idx={};url={}; text={};http_code={};".format(
                idx,
                url,
                res.text,
                res.status_code
            ))

            if res.status_code == 200:
                response = res.json(encoding="utf-8")
                return response
        except Exception as err:
            log(str(err.args))

    return None


def send_mail(title, level="error"):

    all_ns_str = ""
    all_ns = None
    if successorHost:
        all_ns = get_all_ns(successorHost, successorPort)
    else:
        all_ns = get_all_ns(failedHost, failedPort)

    if not all_ns:
        all_ns_str = failureClusterAlias
    else:
        for ns in all_ns:
            all_ns_str = "%s, %s" % (all_ns_str, ns)

    all_ns_str = all_ns_str.strip(",")

    body = "<table align='center' border='2' cellpadding='0' cellspacing='0' width='700' style='border-collapse:collapse;'>" \
        "<tr><td colspan=2 align='center' style='color:red'>{title}</td></tr>" \
        "<tr><td class='left'>集群名字</td><td>{namespace}</td></tr>" \
        "<tr><td class='left'>迁移的原因</td><td>{failureType}</td></tr>" \
        "<tr><td class='left'>old main</td><td>{failedHost}:{failedPort}</td></tr>" \
        "<tr><td class='left'>new main</td><td>{successorHost}:{successorPort}</td></tr>" \
        "<tr><td class='left'>详情</td><td><a style='width: 550px; display: block;word-break:break-word;'>{link}</a></td></tr>" \
    "</table>".format(
        title=title,
        failureType=failureType,
        namespace=all_ns_str,
        failedHost=failedHost,
        failedPort=failedPort,
        successorHost=successorHost,
        successorPort=successorPort,
        link="{}/web/audit-recovery/uid/{}".format(orch_url, recoveryUID)
    )

    style = "<style>table tr {text-align:center;font-size:16px;height: 80px;border: 2px solid #000;}table td.left {width:150px}</style>" 
    body = style + body

    if level == "error":
        subject = "orchestrator(mysql HA) error"
    else:
        subject = "orchestrator(mysql HA) notice"
    
    data = {
        "body_type": "html",
        "body": body,
        "from_addr": "service_warning@zhangyue.com",
        "to_addr": "architecture.list@zhangyue.com,dba.list@zhangyue.com",
        "subject": subject,
    }

    ser = zynsc_cli.get_service("arch.zkapi_email.http")
    
    email_url = "http://{}:{}/v1/email".format(ser.host, ser.port)
    try:    
        res=requests.post(email_url, data=data, timeout=3)
        log("send_mail:" + res.text)
    except Exception as err:
        log("send_mail:" + str(err.args))


def send_sms(res):
    msg = "mysql故障迁移，结果:{res}，集群:{namespace}，原因:{failureType}，"\
        "old-main（{failedHost}:{failedPort}），new-main:（{successorHost}:{successorPort}）".format(
        res=res,
        namespace=failureClusterAlias,
        failureType=failureType,
        failedHost=failedHost,
        failedPort=failedPort,
        successorHost=successorHost,
        successorPort=successorPort
    )

    param = {}
    param["content"] = msg
    param["biz_type"] = "net_warn"

    ser = zynsc_cli.get_service("uc.ngx_common.http")
    url = "http://{}:{}/notify/sms/send_warn_sms".format(ser.host, ser.port)
    keys = qconf.get_batch_keys("/arch_group/orch/failover/phone")

    for key in keys:
        param["phone"] = key
        param["mobile"] = key

        try:    
            res=requests.post(url, data=param, timeout=3)
            log("send_mail:" + res.text)
        except Exception as err:
            log("send_mail:" + str(err.args))


def log(msg):
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 

    metadata = "failureType={};failedHost={};failedPort={};namespace={}\n" \
        "successorHost={};successorPort={};recoveryUID={}".format(
            failureType,
            failedHost,
            failedPort,
            failureClusterAlias,
            successorHost,
            successorPort,
            recoveryUID
        )

    print("%s: %s, metadata: %s" % (t, msg, metadata))
