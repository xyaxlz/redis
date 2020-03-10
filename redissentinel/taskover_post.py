#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 手动触发主从切换，切换成功之后调用

# 1、通知 MySQL——DRC 最新的master
# 2、对老的master做 start slave 操作
# 3、更改namespace 最新的 master/slave 关系
# 4、把namespace设置到新的master上做关联

import common as cm


errmsg = ""

if not cm.put_and_create_ns(
    cm.successorHost,
    cm.successorPort,
    cm.failedHost,
    cm.failedPort,
    "/master",
    cm.failureClusterAlias
):
    errmsg += "step1 : qconf setting new master failed \n"

if not cm.put_ns(cm.failedHost, cm.failedPort, "/slave", cm.failureClusterAlias):
    errmsg += "step2 : qconf old master reset slave failed \n"

if not cm.start_slave(cm.failedHost, cm.failedPort):
    errmsg += "step3 : old master start slave failed \n"

if not cm.start_drc(cm.successorHost, cm.successorPort):
    errmsg += "step4 : new master start drc failed \n"

if not cm.reset_cluster_alias(cm.successorHost, cm.successorPort, cm.failureClusterAlias):
    errmsg += "step5 : new master reset alias \n"


if not errmsg:
    cm.send_mail("mysql手动迁移，主从切换<b>成功</b>", "notice")
    cm.log("success taskover_post")
else:
    msg = "mysql手动迁移, 主从切换<b>失败</b> \n 失败原因：%s" % (errmsg)
    cm.log(msg)
    cm.send_mail(msg)
    exit(1)