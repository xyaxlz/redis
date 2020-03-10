'''
#  ============================================================================
#       FileName: deploy_sepical_scenes.py
#           Desc:
#       HomePage:
#        Created: 2017-09-25 15:52:57
#        Version: 0.0.1
#     LastChange: 2017-10-20 12:15:19
#        History:
#  ============================================================================
'''
from deploy_codis_instance import *
from fabric.api import task, execute

from check_env import check
from deploy_codis_env import deploy_codis_env, install_codis3_pkg, chk_codis3_dir
from utils.parm_parse import ParmParse
from utils.setting import GlobalVar as gvar


@task
def chk_and_deploy_codis_cluster(user, ssh_port, redis_host_list,
                                 redis_port, max_mem_size,
                                 dashboard_host, dashboard_port,
                                 proxy_hosts, proxy_port_list, proxy_seq,
                                 sync_hosts, sync_port_pair,
                                 sync_local_zk_servers, sync_remote_zk_servers,
                                 product_name, zk_servers,
                                 repo_url, backup_invl,
                                 sentinel_port, sentinel_hosts):   #written by liyouwei
    parm = ParmParse(**locals())

    ret = check(parm.redis_host_str, parm.redis_port, parm.dashboard_host_str, parm.dashboard_port,
                parm.proxy_host_str, parm.proxy_port_list, parm.product_name, parm.zk_servers)
    if ret != 1:
        return ret

    ret = deploy_codis_env(parm.codis_host_str)
    if ret != 1:
        return ret

    ret = deploy_codis_instance(
        parm.redis_host_list, parm.dashboard_host,
        parm.dashboard_port, parm.dashboard_host_str,
        parm.proxy_host_str, parm.proxy_port_list, parm.proxy_seq,
        parm.sync_host_str, parm.sync_port_pair, 
        parm.sync_local_zk_servers, parm.sync_remote_zk_servers,
        parm.redis_host_str, parm.redis_port,
        parm.zk_servers, parm.product_name, parm.max_mem_size,
        parm.backup_invl,
        parm.sentinel_port, parm.sentinel_hosts, parm.sentinel_host_str)  #written by liyouwei
    if ret != 1:
        return ret

    return 1

def deploy_codis_without_drc(redis_host_list, dashboard_host,
                          dashboard_port, dashboard_host_str, proxy_host_str,
                          proxy_port_list, proxy_seq,
                          redis_host_str, redis_port,
                          zk_servers, product_name, max_mem_size,
                          backup_invl,
                          sentinel_port, sentinel_hosts, sentinel_host_str):
    dashboard_addr = "%s:%d" % (dashboard_host, dashboard_port)
    group_num = len(redis_host_list) * len(redis_port)

    with settings(parallel=True):
        ret = execute(deploy_dashboard,
                      host=dashboard_host_str,
                      zk_servers=zk_servers,
                      dashboard_port=dashboard_port,
                      product_name=product_name)
        for _, each_ret in ret.items():
            if not each_ret:
                return 301

        ret = execute(deploy_proxy,
                      hosts=proxy_host_str,
                      port_list=proxy_port_list,
                      product_name=product_name,
                      dashboard_addr=dashboard_addr,
                      permission=1,
                      seq=proxy_seq)
        for _, each_ret in ret.items():
            if not each_ret:
                return 302

        ret = execute(deploy_redis,
                      hosts=redis_host_str,
                      redis_port=redis_port,
                      max_mem_size=max_mem_size)
        for _, each_ret in ret.items():
            if not each_ret:
                return 304

        ret = execute(deploy_sentinel,
                      hosts=sentinel_host_str,
                      sentinel_port=sentinel_port)
        for _, each_ret in ret.items():
            if not each_ret:
                return 317
        if backup_invl:
            ret = execute(config_redis_backup,
                          hosts=redis_host_str,
                          redis_port=redis_port,
                          backup_invl=backup_invl)
            for _, each_ret in ret.items():
                if not each_ret:
                    return 306

        ret = execute(startup_dashboard,
                      host=dashboard_host_str,
                      dashboard_port=dashboard_port)
        for _, each_ret in ret.items():
            if not each_ret:
                return 307

        ret = execute(startup_redis,
                      hosts=redis_host_str,
                      redis_port=redis_port)
        for _, each_ret in ret.items():
            if not each_ret:
                return 308

        ret = execute(add_groups,
                      host=dashboard_host_str,
                      dashboard_port=dashboard_port,
                      group_num=group_num)
        for _, each_ret in ret.items():
            if not each_ret:
                return 310

        ret = execute(add_servers,
                      host=dashboard_host_str,
                      redis_port=redis_port,
                      dashboard_port=dashboard_port,
                      host_list=redis_host_list)
        for _, each_ret in ret.items():
            if not each_ret:
                return 311

        ret = execute(setup_redis_replication,
                      hosts=dashboard_host_str,
                      dashboard_port=dashboard_port)
        for _, each_ret in ret.items():
            if not each_ret:
                return 321

        ret = execute(startup_sentinel,
                      hosts=sentinel_host_str,
                      sentinel_port=sentinel_port)
        for _, each_ret in ret.items():
            if not each_ret:
                return 318

        ret = execute(add_sentinel,
                      hosts=dashboard_host_str,
                      sentinel_port=sentinel_port,
                      dashboard_port=dashboard_port,
                      host_list=sentinel_hosts)
        for _, each_ret in ret.items():
            if not each_ret:
                return 319

        ret = execute(resync_sentinel,
                      hosts=dashboard_host_str,
                      dashboard_port=dashboard_port)
        for _, each_ret in ret.items():
            if not each_ret:
                return 320

        ret = execute(rebalance_slots,
                      host=dashboard_host_str,
                      dashboard_port=dashboard_port)
        for _, each_ret in ret.items():
            if not each_ret:
                return 312

        ret = execute(startup_proxy,
                      hosts=proxy_host_str,
                      port_list=proxy_port_list,
                      seq=proxy_seq)
        for _, each_ret in ret.items():
            if not each_ret:
                return 314

    return 1

@task
def chk_and_deploy_codis_cluster_without_drc(user, ssh_port, redis_host_list,
                                 redis_port, max_mem_size,
                                 dashboard_host, dashboard_port,
                                 proxy_hosts, proxy_port_list, proxy_seq,
                                 product_name, zk_servers,
                                 repo_url, backup_invl,
                                 sentinel_port, sentinel_hosts):
    parm = ParmParse(**locals())

    ret = check(parm.redis_host_str, parm.redis_port, parm.dashboard_host_str, parm.dashboard_port,
                parm.proxy_host_str, parm.proxy_port_list, parm.product_name, parm.zk_servers)
    if ret != 1:
        return ret

    ret = deploy_codis_env(parm.codis_host_str)
    if ret != 1:
        return ret

    ret = deploy_codis_without_drc(
        parm.redis_host_list, parm.dashboard_host,
        parm.dashboard_port, parm.dashboard_host_str,
        parm.proxy_host_str, parm.proxy_port_list, parm.proxy_seq,
        parm.redis_host_str, parm.redis_port,
        parm.zk_servers, parm.product_name, parm.max_mem_size,
        parm.backup_invl,
        parm.sentinel_port, parm.sentinel_hosts, parm.sentinel_host_str)
    if ret != 1:
        return ret

    return 1


@task
def deploy_sepical_codis_env(user, ssh_port, target_host, repo_url, codis3_package_name):
    parm = ParmParse(**locals())

    ret = execute(install_codis3_pkg,
                  hosts=parm.target_host_str)
    if ret != 1:
        return ret

    ret = execute(chk_codis3_dir,
                  hosts=parm.target_host_str,
                  info_only=0)

    for _, each_ret in ret.items():
        if not each_ret:
            return 202
    
    return 1

@task
def deploy_fe(user, ssh_port, fe_host, fe_port, zk_servers,
              repo_url):
    parm = ParmParse(**locals())

    ret = deploy_codis_env(parm.fe_host_str)
    if ret != 1:
        return ret

    ret = deploy_fe_instance(parm.fe_host_str, parm.fe_port, parm.zk_servers)
    if ret != 1:
        return ret

    return 1


@task
def deploy_and_startup_dashboard(user, ssh_port, dashboard_host,
                                 dashboard_port, zk_servers, product_name):
    parm = ParmParse(**locals())
    gvar.set_names(parm.product_name)

    ret = execute(deploy_dashboard,
                  host=parm.dashboard_host_str,
                  zk_servers=parm.zk_servers,
                  dashboard_port=parm.dashboard_port,
                  product_name=parm.product_name)
    for _, each_ret in ret.items():
        if not each_ret:
            return 301

    ret = execute(startup_dashboard,
                  host=parm.dashboard_host_str,
                  dashboard_port=parm.dashboard_port)
    for _, each_ret in ret.items():
        if not each_ret:
            return 307
    return 1


@task
def deploy_and_startup_proxy(user, ssh_port, proxy_host, port_list,
                             dashboard_host, dashboard_port, product_name,
                             permission, seq):
    parm = ParmParse(**locals())

    dashboard_addr = '%s:%d' % (parm.dashboard_host, parm.dashboard_port)

    with settings(parallel=True):
        ret = execute(deploy_proxy,
                      host=parm.proxy_host_str,
                      port_list=parm.port_list,
                      product_name=parm.product_name,
                      dashboard_addr=dashboard_addr,
                      permission=parm.permission,
                      seq=seq)
        for _, each_ret in ret.items():
            if not each_ret:
                return 302

        ret = execute(startup_proxy,
                      host=parm.proxy_host_str,
                      port_list=parm.port_list,
                      seq=seq)
        for _, each_ret in ret.items():
            if not each_ret:
                return 311
        return 1


@task
def deploy_and_startup_redis(user, ssh_port, redis_host, redis_port, max_mem_size,
                             repo_url, backup_invl):
    parm = ParmParse(**locals())

    with settings(parallel=True):
        ret = execute(deploy_redis,
                      host=parm.redis_host_str,
                      redis_port=parm.redis_port,
                      max_mem_size=parm.max_mem_size)
        for _, each_ret in ret.items():
            if not each_ret:
                return 304

        if parm.backup_invl:
            ret = execute(config_redis_backup,
                          host=parm.redis_host_str,
                          redis_port=parm.redis_port,
                          backup_invl=parm.backup_invl)
            for _, each_ret in ret.items():
                if not each_ret:
                    return 306

        ret = execute(startup_redis,
                      hosts=parm.redis_host_str,
                      redis_port=parm.redis_port)
        for _, each_ret in ret.items():
            if not each_ret:
                return 308

        return 1


@task
def dashboard_add_groups_and_servers(user, ssh_port, dashboard_host, dashboard_port, master_host, slave_host, redis_port, start_group):
    parm = ParmParse(**locals())
    ret = execute(add_groups,
                  host=parm.dashboard_host_str,
                  dashboard_port=parm.dashboard_port,
                  group_num=len(parm.redis_port),
                  start_group=parm.start_group)
    for _, each_ret in ret.items():
        if not each_ret:
            return 310

    ret = execute(add_servers,
                  host=parm.dashboard_host_str,
                  redis_port=parm.redis_port,
                  dashboard_port=parm.dashboard_port,
                  host_list=[(parm.master_host, parm.slave_host)],
                  start_group=parm.start_group)
    for _, each_ret in ret.items():
        if not each_ret:
            return 311
    return 1


@task
def dashboard_add_servers(user, ssh_port, dashboard_host, dashboard_port, redis_host, redis_port, start_group, interval):
    parm = ParmParse(**locals())
    ret = execute(add_servers,
                  host=parm.dashboard_host_str,
                  redis_port=parm.redis_port,
                  dashboard_port=parm.dashboard_port,
                  host_list=[parm.redis_host],
                  start_group=parm.start_group,
                  interval=parm.interval)
    for _, each_ret in ret.items():
        if not each_ret:
            return 311
    return 1


@task
def dashboard_add_watcher(user, ssh_port, dashboard_host, dashboard_port, watcher_port):
    parm = ParmParse(**locals())
    ret = execute(add_watcher,
                  host=parm.dashboard_host_str,
                  dashboard_port=parm.dashboard_port,
                  watcher_port=watcher_port)
    for _, each_ret in ret.items():
        if not each_ret:
            return 313


@task
def config_special_dashboard(user, ssh_port, dashboard_host, dashboard_port,
                             watcher_port, master_host, slave_host,
                             redis_port, start_group):
    parm = ParmParse(**locals())
    ret = execute(config_dashboard,
                  host=parm.dashboard_host_str,
                  redis_port=parm.redis_port,
                  dashboard_port=parm.dashboard_port,
                  master_host=parm.master_host,
                  slave_host=parm.slave_host,
                  start_group=start_group)
    for _, each_ret in ret.items():
        if not each_ret:
            return 310
    return 1


@task
def deploy_and_startup_watcher(user, ssh_port, dashboard_host, dashboard_port,
                               watcher_port, zk_servers, product_name):
    parm = ParmParse(**locals())
    gvar.set_names(parm.product_name)

    dashboard_addr = "%s:%d" % (dashboard_host, dashboard_port)
    ret = execute(deploy_watcher,
                  host=parm.dashboard_host_str,
                  zk_servers=parm.zk_servers,
                  watcher_port=parm.watcher_port,
                  product_name=parm.product_name,
                  dashboard_addr=dashboard_addr)
    for _, each_ret in ret.items():
        if not each_ret:
            return 303

    ret = execute(startup_watcher,
                  host=parm.dashboard_host_str,
                  watcher_port=watcher_port)
    for _, each_ret in ret.items():
        if not each_ret:
            return 309
    return 1
