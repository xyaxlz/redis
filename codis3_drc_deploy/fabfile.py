'''
#  =============================================================================
#       FileName: fabfile.py
#           Desc: 
#       HomePage: 
#        Created: 2017-08-24 12:17:21
#        Version: 0.0.1
#     LastChange: 2017-09-28 16:51:34
#        History:
#  =============================================================================
'''
from fabric.api import task, env, settings, execute, sudo
from fabric.network import disconnect_all
from getpass import getpass
import os

from deploy_sepical_scenes import chk_and_deploy_codis_cluster, deploy_fe,\
     deploy_and_startup_dashboard, deploy_and_startup_proxy,\
     deploy_and_startup_redis, config_special_dashboard,\
     deploy_and_startup_watcher, deploy_sepical_codis_env,\
     dashboard_add_groups_and_servers,\
     dashboard_add_servers, dashboard_add_watcher,\
     chk_and_deploy_codis_cluster_without_drc
from utils.setting import GlobalVar as gvar

gvar.set_logger()
env.password = getpass("SSH password:")

# 2 data node
@task
def deploy_drc_codis_cluster(): 
    product_name = "cache162"
    max_mem_size = 0

    m5_dashboard_host = "10.100.42.30"
    m5_master1 = "10.100.42.51"
    m5_slave1 = "10.100.42.52"
    m5_master2 = "10.100.42.53"
    m5_slave2 = "10.100.42.56"
    m5_master3 = "10.100.42.57"
    m5_slave3 = "10.100.42.58"
    m5_redis_host_list = [(m5_master1, m5_slave1), (m5_master2, m5_slave2), (m5_master3, m5_slave3)]
    m5_proxy_hosts = [m5_master1, m5_slave1, m5_master2, m5_slave2, m5_master3, m5_slave3]
    m5_sync_hosts = [m5_master1, m5_slave1, m5_master2, m5_slave2, m5_master3, m5_slave3]
    m5_sentinel_hosts = [m5_master1, m5_slave1, m5_master2, m5_slave2, m5_master3, m5_slave3, m5_dashboard_host]

    yz_dashboard_host = "10.100.86.51"
    yz_master1 = "10.100.86.27"
    yz_slave1 = "10.100.86.28"
    yz_master2 = "10.100.86.29"
    yz_slave2 = "10.100.86.30"
    yz_master3 = "10.100.86.31"
    yz_slave3 = "10.100.86.32"
    yz_redis_host_list = [(yz_master1, yz_slave1), (yz_master2, yz_slave2), (yz_master3, yz_slave3)]
    yz_proxy_hosts = [yz_master1, yz_slave1, yz_master2, yz_slave2, yz_master3, yz_slave3]
    yz_sync_hosts = [yz_master1, yz_slave1, yz_master2, yz_slave2, yz_master3, yz_slave3]
    yz_sentinel_hosts = [yz_master1, yz_slave1, yz_master2, yz_slave2, yz_master3, yz_slave3, yz_dashboard_host]

    redis_start_port = 6100
    dashboard_port = 18032
    proxy_port_list=[(19100, 21100)]
    backup_invl=24
    group_num_of_each_pair = 1

    redis_end_port = redis_start_port + group_num_of_each_pair - 1
    sentinel_port = dashboard_port - 1000
    sync_port_pair = (dashboard_port + 2000, dashboard_port + 4000)


    # Changeless config
    user="op_DBA01"
    ssh_port=33312
    m5_zk_servers = "10.100.21.122:5181,10.100.21.123:5181,10.100.21.124:5181,10.100.21.125:5181,10.100.21.126:5181"
    yz_zk_servers = "10.100.96.69:5181,10.100.96.70:5181,10.100.96.71:5181,10.100.96.245:5181,10.100.96.246:5181"
    repo_url = "http://192.168.7.24"

    m5_sync_zk_servers = "10.100.21.122:4181,10.100.21.123:4181,10.100.21.124:4181,10.100.21.125:4181,10.100.21.126:4181"
    yz_sync_zk_servers = "10.100.96.69:4181,10.100.96.70:4181,10.100.96.71:4181,10.100.96.245:4181,10.100.96.246:4181"

    gvar.set_names(product_name)
    gvar.set_urls(repo_url)

    ## m5
    #chk_and_deploy_codis_cluster(
    #    user=user, ssh_port=ssh_port,
    #    redis_host_list=m5_redis_host_list, redis_port=[redis_start_port, redis_end_port], max_mem_size=max_mem_size,
    #    dashboard_host=m5_dashboard_host, dashboard_port=dashboard_port,
    #    proxy_hosts=m5_proxy_hosts, proxy_port_list=proxy_port_list, proxy_seq=0,
    #    sync_hosts=m5_sync_hosts, sync_port_pair=sync_port_pair,
    #    sync_local_zk_servers=m5_sync_zk_servers, sync_remote_zk_servers=yz_sync_zk_servers,
    #    product_name=product_name,
    #    zk_servers=m5_zk_servers,
    #    repo_url=repo_url, backup_invl=backup_invl,
    #    sentinel_port=sentinel_port, sentinel_hosts=m5_sentinel_hosts)
    #
    #for each_proxy_host in m5_proxy_hosts:
    #    for _, admin_port in proxy_port_list:
    #        admin_url = "%s:%d" % (each_proxy_host, admin_port)
    #        cmd = "curl -X PUT 'http://%s/api/proxy/flags/write/on'" % admin_url
    #        os.system(cmd)

    ## yz
    #chk_and_deploy_codis_cluster(
    #    user=user, ssh_port=ssh_port,
    #    redis_host_list=yz_redis_host_list, redis_port=[redis_start_port, redis_end_port], max_mem_size=max_mem_size,
    #    dashboard_host=yz_dashboard_host, dashboard_port=dashboard_port,
    #    proxy_hosts=yz_proxy_hosts, proxy_port_list=proxy_port_list, proxy_seq=0,
    #    sync_hosts=yz_sync_hosts, sync_port_pair=sync_port_pair,
    #    sync_local_zk_servers=yz_sync_zk_servers, sync_remote_zk_servers=m5_sync_zk_servers,
    #    product_name=product_name,
    #    zk_servers=yz_zk_servers,
    #    repo_url=repo_url, backup_invl=0,
    #    sentinel_port=sentinel_port, sentinel_hosts=yz_sentinel_hosts)

@task
def deploy_drc_codis_cluster2(): 
    product_name = "cache154"
    max_mem_size = 0

    m5_dashboard_host = "10.100.42.30"
    m5_master1 = "10.100.42.28"
    m5_slave1 = "10.100.42.29"
    m5_master2 = "10.100.42.12"
    m5_slave2 = "10.100.42.16"
    m5_redis_host_list = [(m5_master1, m5_slave1), (m5_master2, m5_slave2)]
    m5_proxy_hosts = [m5_master1, m5_slave1, m5_master2, m5_slave2]
    m5_sync_hosts = [m5_master1, m5_slave1, m5_master2, m5_slave2]
    m5_sentinel_hosts = [m5_master1, m5_slave1, m5_master2, m5_slave2, m5_dashboard_host]

    yz_dashboard_host = "10.100.86.51"
    yz_master1 = "10.100.86.21"
    yz_slave1 = "10.100.86.24"
    yz_master2 = "10.100.86.25"
    yz_slave2 = "10.100.86.26"
    yz_redis_host_list = [(yz_master1, yz_slave1), (yz_master2, yz_slave2)]
    yz_proxy_hosts = [yz_master1, yz_slave1, yz_master2, yz_slave2]
    yz_sync_hosts = [yz_master1, yz_slave1, yz_master2, yz_slave2]
    yz_sentinel_hosts = [yz_master1, yz_slave1, yz_master2, yz_slave2, yz_dashboard_host]

    redis_start_port = 6100
    dashboard_port = 18024
    proxy_port_list=[(19001, 21001)]
    backup_invl=24
    group_num_of_each_pair = 10

    redis_end_port = redis_start_port + group_num_of_each_pair - 1
    sentinel_port = dashboard_port - 1000
    sync_port_pair = (dashboard_port + 2000, dashboard_port + 4000)


    # Changeless config
    user="op_DBA01"
    ssh_port=33312
    m5_zk_servers = "10.100.21.122:5181,10.100.21.123:5181,10.100.21.124:5181,10.100.21.125:5181,10.100.21.126:5181"
    yz_zk_servers = "10.100.96.69:5181,10.100.96.70:5181,10.100.96.71:5181,10.100.96.245:5181,10.100.96.246:5181"
    repo_url = "http://192.168.7.24"

    m5_sync_zk_servers = "10.100.21.122:4181,10.100.21.123:4181,10.100.21.124:4181,10.100.21.125:4181,10.100.21.126:4181"
    yz_sync_zk_servers = "10.100.96.69:4181,10.100.96.70:4181,10.100.96.71:4181,10.100.96.245:4181,10.100.96.246:4181"

    gvar.set_names(product_name)
    gvar.set_urls(repo_url)

    # m5
    chk_and_deploy_codis_cluster(
        user=user, ssh_port=ssh_port,
        redis_host_list=m5_redis_host_list, redis_port=[redis_start_port, redis_end_port], max_mem_size=max_mem_size,
        dashboard_host=m5_dashboard_host, dashboard_port=dashboard_port,
        proxy_hosts=m5_proxy_hosts, proxy_port_list=proxy_port_list, proxy_seq=0,
        sync_hosts=m5_sync_hosts, sync_port_pair=sync_port_pair,
        sync_local_zk_servers=m5_sync_zk_servers, sync_remote_zk_servers=yz_sync_zk_servers,
        product_name=product_name,
        zk_servers=m5_zk_servers,
        repo_url=repo_url, backup_invl=backup_invl,
        sentinel_port=sentinel_port, sentinel_hosts=m5_sentinel_hosts)
    
    dashboard_url = "%s:%d" % (m5_dashboard_host, dashboard_port)
    for each_proxy_host in m5_proxy_hosts:
        for _, admin_port in proxy_port_list:
            admin_url = "%s:%d" % (each_proxy_host, admin_port)
            #cmd = "curl -X PUT 'http://%s/api/proxy/flags/write/on'" % admin_url
            cmd = "curl -X PUT 'http://%s/topom/proxy/flags/%s/write/on'" % (dashboard_url, admin_url)
            print(cmd)
            os.system(cmd)

    # yz
    chk_and_deploy_codis_cluster(
        user=user, ssh_port=ssh_port,
        redis_host_list=yz_redis_host_list, redis_port=[redis_start_port, redis_end_port], max_mem_size=max_mem_size,
        dashboard_host=yz_dashboard_host, dashboard_port=dashboard_port,
        proxy_hosts=yz_proxy_hosts, proxy_port_list=proxy_port_list, proxy_seq=0,
        sync_hosts=yz_sync_hosts, sync_port_pair=sync_port_pair,
        sync_local_zk_servers=yz_sync_zk_servers, sync_remote_zk_servers=m5_sync_zk_servers,
        product_name=product_name,
        zk_servers=yz_zk_servers,
        repo_url=repo_url, backup_invl=0,
        sentinel_port=sentinel_port, sentinel_hosts=yz_sentinel_hosts)

@task
def deploy_drc_codis_cluster3(): 
    product_name = "cache328"
    max_mem_size = 0

    m5_dashboard_host = "10.100.42.30"
    m5_master1 = "10.100.42.11"
    m5_slave1 =  "10.100.42.15"
    m5_master2 = "10.100.42.20"
    m5_slave2 =  "10.100.42.37"
    m5_redis_host_list = [(m5_master1, m5_slave1), (m5_master2, m5_slave2)]
    m5_proxy_hosts = [m5_master1, m5_slave1, m5_master2, m5_slave2]
    m5_sync_hosts = [m5_master1, m5_slave1, m5_master2, m5_slave2]
    m5_sentinel_hosts = [m5_master1, m5_slave1, m5_master2, m5_slave2, m5_dashboard_host]

    yz_dashboard_host = "10.100.86.51"
    yz_master1 = "10.100.86.33"
    yz_slave1 =  "10.100.86.34"
    yz_master2 = "10.100.86.35"
    yz_slave2 =  "10.100.86.36"
    yz_redis_host_list = [(yz_master1, yz_slave1), (yz_master2, yz_slave2)]
    yz_proxy_hosts = [yz_master1, yz_slave1, yz_master2, yz_slave2]
    yz_sync_hosts = [yz_master1, yz_slave1, yz_master2, yz_slave2]
    yz_sentinel_hosts = [yz_master1, yz_slave1, yz_master2, yz_slave2, yz_dashboard_host]

    redis_start_port = 6190
    dashboard_port = 18195
    proxy_port_list = [(19190, 21190)]
    #proxy_port_list = [(19020, 21020) ,(19021, 21021)]    # --> 2*4
    #proxy_port_list = [(19030, 21030) ,(19031, 21031) ,(19032, 21032) ,(19033, 21033) ,(19034, 21034) ,(19035, 21035) ,(19036, 21036) ,(19037, 21037) ,(19038, 21038) ,(19039, 21039)]
    backup_invl=24
    group_num_of_each_pair = 2       #num*2

    redis_end_port = redis_start_port + group_num_of_each_pair - 1
    sentinel_port = dashboard_port - 1000
    sync_port_pair = (dashboard_port + 2000, dashboard_port + 4000)


    # Changeless config
    user="op_DBA01"
    ssh_port=33312
    m5_zk_servers = "10.100.21.122:5181,10.100.21.123:5181,10.100.21.124:5181,10.100.21.125:5181,10.100.21.126:5181"
    yz_zk_servers = "10.100.96.69:5181,10.100.96.70:5181,10.100.96.71:5181,10.100.96.245:5181,10.100.96.246:5181"
    repo_url = "http://192.168.7.24"

    m5_sync_zk_servers = "10.100.21.122:4181,10.100.21.123:4181,10.100.21.124:4181,10.100.21.125:4181,10.100.21.126:4181"
    yz_sync_zk_servers = "10.100.96.69:4181,10.100.96.70:4181,10.100.96.71:4181,10.100.96.245:4181,10.100.96.246:4181"

    gvar.set_names(product_name)
    gvar.set_urls(repo_url)

    # m5
    chk_and_deploy_codis_cluster(
        user=user, ssh_port=ssh_port,
        redis_host_list=m5_redis_host_list, redis_port=[redis_start_port, redis_end_port], max_mem_size=max_mem_size,
        dashboard_host=m5_dashboard_host, dashboard_port=dashboard_port,
        proxy_hosts=m5_proxy_hosts, proxy_port_list=proxy_port_list, proxy_seq=0,
        sync_hosts=m5_sync_hosts, sync_port_pair=sync_port_pair,
        sync_local_zk_servers=m5_sync_zk_servers, sync_remote_zk_servers=yz_sync_zk_servers,
        product_name=product_name,
        zk_servers=m5_zk_servers,
        repo_url=repo_url, backup_invl=backup_invl,
        sentinel_port=sentinel_port, sentinel_hosts=m5_sentinel_hosts)
    
    dashboard_url = "%s:%d" % (m5_dashboard_host, dashboard_port)
    for each_proxy_host in m5_proxy_hosts:
        for _, admin_port in proxy_port_list:
            admin_url = "%s:%d" % (each_proxy_host, admin_port)
            #cmd = "curl -X PUT 'http://%s/api/proxy/flags/write/on'" % admin_url
            cmd = "curl -X PUT 'http://%s/topom/proxy/flags/%s/write/on'" % (dashboard_url, admin_url)
            print(cmd)
            os.system(cmd)

    # yz
    chk_and_deploy_codis_cluster(
        user=user, ssh_port=ssh_port,
        redis_host_list=yz_redis_host_list, redis_port=[redis_start_port, redis_end_port], max_mem_size=max_mem_size,
        dashboard_host=yz_dashboard_host, dashboard_port=dashboard_port,
        proxy_hosts=yz_proxy_hosts, proxy_port_list=proxy_port_list, proxy_seq=0,
        sync_hosts=yz_sync_hosts, sync_port_pair=sync_port_pair,
        sync_local_zk_servers=yz_sync_zk_servers, sync_remote_zk_servers=m5_sync_zk_servers,
        product_name=product_name,
        zk_servers=yz_zk_servers,
        repo_url=repo_url, backup_invl=0,
        sentinel_port=sentinel_port, sentinel_hosts=yz_sentinel_hosts)

@task
def deploy_no_drc_codis_cluster(): 
    product_name = "cache236"
    max_mem_size = 0

    m5_dashboard_host = "10.100.42.30"
    m5_master1 = "10.100.42.61"
    m5_slave1 = "10.100.42.62"
    m5_master2 = "10.100.42.64"
    m5_slave2 = "10.100.42.65"
    m5_redis_host_list = [(m5_master1, m5_slave1), (m5_master2, m5_slave2)]
    m5_proxy_hosts = [m5_master1, m5_slave1, m5_master2, m5_slave2]
    m5_sentinel_hosts = [m5_master1, m5_slave1, m5_master2, m5_slave2, m5_dashboard_host]

    yz_dashboard_host = "10.100.86.51"
    yz_master1 = "10.100.86.1"
    yz_slave1 = "10.100.86.2"
    yz_master2 = "10.100.86.3"
    yz_slave2 = "10.100.86.4"
    yz_redis_host_list = [(yz_master1, yz_slave1), (yz_master2, yz_slave2)]
    yz_proxy_hosts = [yz_master1, yz_slave1, yz_master2, yz_slave2]
    yz_sentinel_hosts = [yz_master1, yz_slave1, yz_master2, yz_slave2, yz_dashboard_host]

    redis_start_port = 6400
    group_num_of_each_pair = 1
    dashboard_port = 18103
    proxy_port_list=[(19026, 21026)]
    backup_invl=24


    redis_end_port = redis_start_port + group_num_of_each_pair - 1
    sentinel_port = dashboard_port - 1000

    user="op_DBA01"
    ssh_port=33312
    m5_zk_servers = "10.100.21.122:6181,10.100.21.123:6181,10.100.21.124:6181,10.100.21.125:6181,10.100.21.126:6181"
    yz_zk_servers = "10.100.96.69:6181,10.100.96.70:6181,10.100.96.71:6181,10.100.96.245:6181,10.100.96.246:6181"
    repo_url = "http://192.168.7.24"

    gvar.set_names(product_name)
    gvar.set_urls(repo_url)

    # m5
    chk_and_deploy_codis_cluster_without_drc(
        user=user, ssh_port=ssh_port,
        redis_host_list=m5_redis_host_list, redis_port=[redis_start_port, redis_end_port], max_mem_size=max_mem_size,
        dashboard_host=m5_dashboard_host, dashboard_port=dashboard_port,
        proxy_hosts=m5_proxy_hosts, proxy_port_list=proxy_port_list, proxy_seq=0,
        product_name=product_name,
        zk_servers=m5_zk_servers,
        repo_url=repo_url, backup_invl=backup_invl,
        sentinel_port=sentinel_port, sentinel_hosts=m5_sentinel_hosts)

    # yz
    chk_and_deploy_codis_cluster_without_drc(
        user=user, ssh_port=ssh_port,
        redis_host_list=yz_redis_host_list, redis_port=[redis_start_port, redis_end_port], max_mem_size=max_mem_size,
        dashboard_host=yz_dashboard_host, dashboard_port=dashboard_port,
        proxy_hosts=yz_proxy_hosts, proxy_port_list=proxy_port_list, proxy_seq=0,
        product_name=product_name,
        zk_servers=yz_zk_servers,
        repo_url=repo_url, backup_invl=0,
        sentinel_port=sentinel_port, sentinel_hosts=yz_sentinel_hosts)

# 2 data node
@task
def arch_Call_chk_and_deploy_codis_cluster(): 
    product_name = "cache_46"
    max_mem_size = 0

    m5_dashboard_host = "10.100.20.1"
    m5_redis_master = "10.100.20.1"
    m5_redis_slave = "10.100.20.2"
    m5_redis_host_list = [(m5_redis_master, m5_redis_slave)]
    m5_proxy_hosts = [m5_redis_slave, m5_redis_master]
    m5_sync_hosts = [m5_redis_master, m5_redis_slave]

    yz_dashboard_host = "10.100.93.88"
    yz_redis_master = "10.100.93.88"
    yz_redis_slave = "10.100.93.89"
    yz_redis_host_list = [(yz_redis_master, yz_redis_slave)]
    yz_proxy_hosts = [yz_redis_slave, yz_redis_master]
    yz_sync_hosts = [yz_redis_master, yz_redis_slave]

    redis_start_port = 6000
    group_num = 2
    redis_end_port = redis_start_port + group_num - 1
    dashboard_port = 18000
    sync_port_pair = (dashboard_port + 3000, dashboard_port + 4000)
    proxy_port_list=[(19000, 20000)]
    backup_invl=24

    #sentinel config (liyouwei)
    sentinel_port = 26000
    sentinel_hosts = ["10.100.21.154","10.100.21.155","10.100.21.157"]

    # Changeless config
    user="op_DBA01"
    ssh_port=33312
    m5_zk_servers = "10.100.42.49:2183,10.100.42.47:2183,10.100.42.54:2183"
    yz_zk_servers = "10.100.86.16:2183,10.100.86.17:2183,10.100.86.18:2183"
    repo_url="http://192.168.7.24"

    m5_sync_zk_servers = "10.100.21.122:4181,10.100.21.123:4181,10.100.21.124:4181,10.100.21.125:4181,10.100.21.126:4181"
    yz_sync_zk_servers = "10.100.93.100:4181,10.100.93.101:4181,10.100.93.102:4181,10.100.93.103:4181,10.100.93.104:4181"

    # m5
    chk_and_deploy_codis_cluster(
        user=user, ssh_port=ssh_port,
        redis_host_list=m5_redis_host_list, redis_port=[redis_start_port, redis_end_port], max_mem_size=max_mem_size,
        dashboard_host=m5_dashboard_host, dashboard_port=dashboard_port,
        proxy_hosts=m5_proxy_hosts, proxy_port_list=proxy_port_list, proxy_seq=0,
        sync_hosts=m5_sync_hosts, sync_port_pair=sync_port_pair,
        sync_local_zk_servers=m5_sync_zk_servers, sync_remote_zk_servers=yz_sync_zk_servers,
        product_name=product_name,
        zk_servers=m5_zk_servers,
        repo_url=repo_url, backup_invl=backup_invl,
        sentinel_port=sentinel_port, sentinel_hosts=sentinel_hosts)  #written by liyouwei

    ## yz
    #chk_and_deploy_codis_cluster(
    #    user=user, ssh_port=ssh_port,
    #    redis_host_list=yz_redis_host_list, redis_port=[redis_start_port, redis_end_port], max_mem_size=max_mem_size,
    #    dashboard_host=yz_dashboard_host, dashboard_port=dashboard_port,
    #    proxy_hosts=yz_proxy_hosts, proxy_port_list=proxy_port_list, proxy_seq=0,
    #    sync_hosts=yz_sync_hosts, sync_port_pair=sync_port_pair,
    #    sync_local_zk_servers=yz_sync_zk_servers, sync_remote_zk_servers=m5_sync_zk_servers,
    #    product_name=product_name,
    #    zk_servers=yz_zk_servers,
    #    repo_url=repo_url, backup_invl=0)

@task
def call_deploy_sepical_codis_env():
    #servers = ['10.100.96.46', '10.100.96.48', '10.100.96.54', '10.100.96.55', '10.100.96.109', '10.100.96.110', '10.100.96.112', '10.100.96.47', '10.100.96.124', '10.100.96.50', '10.100.96.125', '10.100.96.51', '10.100.96.126', '10.100.96.117', '10.100.96.131', '10.100.96.118', '10.100.96.132', '10.100.96.121', '10.100.96.133', '10.100.20.11', '10.100.20.8', '10.100.20.229', '10.100.20.230', '10.100.20.16', '10.100.20.18', '10.100.42.11', '10.100.42.15', '10.100.20.231', '10.100.20.232', '10.100.42.13', '10.100.42.17', '10.100.42.12', '10.100.42.16', '10.100.42.20', '10.100.20.125', '10.100.96.135', '10.100.96.134', '10.100.20.183', '10.100.20.184', '10.100.42.18', '10.100.96.123', '10.100.96.45', '10.100.96.49', '10.100.96.108']
   # servers = ["10.100.42.61","10.100.42.62", "10.100.42.64", "10.100.42.65", "10.100.42.30", "10.100.86.1", "10.100.86.2", "10.100.86.3", "10.100.86.4", "10.100.86.51"]
    #servers = ['10.100.86.18','10.100.86.31','10.100.42.62','10.100.86.24','10.100.42.29','10.100.42.57', '10.100.42.64','10.100.42.33','10.100.42.31','10.100.86.30','10.100.86.17','10.100.42.30', '10.100.86.21','10.100.42.65','10.100.86.3','10.100.86.1','10.100.86.25','10.100.42.53', '10.100.86.16','10.100.42.58','10.100.42.28','10.100.42.52','10.100.86.27','10.100.42.51', '10.100.86.4','10.100.86.51','10.100.86.28','10.100.42.61','10.100.86.29','10.100.86.32', '10.100.86.2','10.100.42.34','10.100.86.26','10.100.42.32','10.100.42.16','10.100.42.56', '10.100.42.12','10.100.86.19']
    #servers = ['10.100.86.51', '10.100.86.32', '10.100.86.30', '10.100.86.28', '10.100.86.31', '10.100.86.27', '10.100.86.29']
    #servers = ['10.100.42.61', '10.100.42.62', '10.100.42.64', '10.100.42.65','10.100.42.30']
    servers = ['10.100.42.31','10.100.42.32','10.100.42.33','10.100.42.34','10.100.86.16','10.100.86.17','10.100.86.18','10.100.86.19']
    #servers = ['10.100.42.61','10.100.42.62','10.100.42.64','10.100.42.65','10.100.42.30','10.100.86.51','10.100.86.1','10.100.86.2','10.100.86.3','10.100.86.4']
    #servers = ['10.100.20.128','10.100.42.12','10.100.42.16','10.100.42.28','10.100.42.29','10.100.86.21','10.100.86.24','10.100.86.25','10.100.86.26']
    #servers = ['10.100.42.51','10.100.42.52','10.100.42.53','10.100.42.56','10.100.42.57','10.100.42.58','10.100.86.28','10.100.86.29','10.100.86.30','10.100.86.31','10.100.86.32','10.100.86.37']
    #servers = ['10.100.42.47','10.100.42.48','10.100.42.49','10.100.42.50','10.100.86.113', '10.100.86.114', '10.100.86.115' ,'10.100.86.116']
    #servers = ['10.100.42.39','10.100.42.40','10.100.42.54','10.100.42.55','10.100.86.109','10.100.86.110','10.100.86.111','10.100.86.112']

    #servers = ['192.168.7.75','192.168.7.76','10.100.42.30']
    #servers = ['10.100.42.73','10.100.42.74','10.100.42.75','10.100.42.76','10.100.86.20','10.100.86.22','10.100.86.49','10.100.86.50']
    #servers = ['10.100.42.17','10.100.42.70','10.100.42.71','10.100.42.72','10.100.86.105','10.100.86.106','10.100.86.107','10.100.86.108']
    repo_url="http://192.168.7.24"
    gvar.set_urls(repo_url)
    for each_host in servers:
        deploy_sepical_codis_env(
            user="op_DBA01", ssh_port=33312,
            target_host=each_host,
            repo_url=repo_url,
            codis3_package_name="codis3_drc.tar.bz2")


def get_version():
    with settings(warn_only=True):
        ret = sudo('/data/server/codis3_sync/bin/codis-proxy --version|grep "version:"')
        return ret

@task
def call_get_version():
    ssh_port=33312
    #servers = ['10.100.96.46', '10.100.96.48', '10.100.96.54', '10.100.96.55', '10.100.96.109', '10.100.96.110', '10.100.96.112', '10.100.96.47', '10.100.96.124', '10.100.96.50', '10.100.96.125', '10.100.96.51', '10.100.96.126', '10.100.96.117', '10.100.96.131', '10.100.96.118', '10.100.96.132', '10.100.96.121', '10.100.96.133', '10.100.20.11', '10.100.20.8', '10.100.20.229', '10.100.20.230', '10.100.20.16', '10.100.20.18', '10.100.42.11', '10.100.42.15', '10.100.20.231', '10.100.20.232', '10.100.42.13', '10.100.42.17', '10.100.42.12', '10.100.42.16', '10.100.42.20', '10.100.20.125', '10.100.96.135', '10.100.96.134', '10.100.20.183', '10.100.20.184']
    host_str = []
    for server in servers:
        host_str.append('%s:%d' % (server, ssh_port))
    with settings(parallel=True, pool_size=8):
        ret = execute(get_version,
                      hosts=host_str)
        print(ret)

@task
def call_deploy_fe():
    gvar.set_urls("192.168.7.24")
    #m5_zk_servers = "10.100.42.49:2183,10.100.42.47:2183,10.100.42.54:2183"
    #yz_zk_servers = "10.100.86.16:2183,10.100.86.17:2183,10.100.86.18:2183"
    #deploy_fe("op_DBA01",33312,"10.100.42.57",9090,"10.100.42.49:2183.10.100.42.47:2183,10.100.42.54:2183", "http://192.168.7.24")
    #deploy_fe("op_DBA01", 33312, "10.100.20.1", 9091, "10.100.20.201:4181,10.100.20.202:4181,10.100.20.203:4181", "http://192.168.7.24")
    #deploy_fe("op_DBA01", 33312, "10.100.97.245", 9091, "10.100.96.248:4181,10.100.96.249:4181,10.100.96.250:4181", "http://192.168.7.24")
    deploy_fe("op_DBA01", 33312, "10.100.86.51", 9093, "10.100.96.69:7181,10.100.96.70:7181,10.100.96.71:7181,10.100.96.245:7181,10.100.96.246:7181", "http://192.168.7.24")

@task
def call_deploy_and_startup_dashboard():
    deploy_and_startup_dashboard("Li_QingBin",33312,"10.100.90.21",18095,"10.100.90.20:2181,10.100.90.21:2181,10.100.90.22:2181","test5")

@task
def call_m5_deploy_and_startup_proxy():
    gvar.set_names("cache38")
    deploy_and_startup_proxy(
        user="Li_QingBin", ssh_port=33312,
        proxy_host="10.100.42.41", port_list=[(19205,21205)],
        dashboard_host="10.100.42.24", dashboard_port=18116,
        product_name="cache38",
        permission=1,
        seq=1)

@task
def call_deploy_and_startup_redis():
    deploy_and_startup_redis(
        user="op_DBA01", ssh_port=33312,
        redis_host="10.100.42.31", redis_port=[6061, 6064], max_mem_size=10,
        repo_url="http://192.168.7.24/codis/codis3",
        backup_invl=24)
    deploy_and_startup_redis(
        user="op_DBA01", ssh_port=33312,
        redis_host="10.100.42.32", redis_port=[6061, 6064], max_mem_size=10,
        repo_url="http://192.168.7.24/codis/codis3",
        backup_invl=24)

    deploy_and_startup_redis(
        user="op_DBA01", ssh_port=33312,
        redis_host="10.100.42.33", redis_port=[6061, 6064], max_mem_size=10,
        repo_url="http://192.168.7.24/codis/codis3",
        backup_invl=24)
    deploy_and_startup_redis(
        user="op_DBA01", ssh_port=33312,
        redis_host="10.100.42.34", redis_port=[6061, 6064], max_mem_size=10,
        repo_url="http://192.168.7.24/codis/codis3",
        backup_invl=24)

    deploy_and_startup_redis(
        user="op_DBA01", ssh_port=33312,
        redis_host="10.100.86.16", redis_port=[6061, 6064], max_mem_size=10,
        repo_url="http://192.168.7.24/codis/codis3",
        backup_invl=24)
    deploy_and_startup_redis(
        user="op_DBA01", ssh_port=33312,
        redis_host="10.100.86.17", redis_port=[6061, 6064], max_mem_size=10,
        repo_url="http://192.168.7.24/codis/codis3",
        backup_invl=24)

    deploy_and_startup_redis(
        user="op_DBA01", ssh_port=33312,
        redis_host="10.100.86.18", redis_port=[6061, 6064], max_mem_size=10,
        repo_url="http://192.168.7.24/codis/codis3",
        backup_invl=24)
    deploy_and_startup_redis(
        user="op_DBA01", ssh_port=33312,
        redis_host="10.100.86.19", redis_port=[6061, 6064], max_mem_size=10,
        repo_url="http://192.168.7.24/codis/codis3",
        backup_invl=24)
@task
def call_add_servers():
    dashboard_add_servers(
        user="op_DBA01", ssh_port=33312,
        dashboard_host='10.100.42.30', dashboard_port=18036,
        redis_host='10.100.42.31', redis_port=[6000, 6007],
        start_group=3, interval=0)

@task
def call_dashboard_add_groups_and_servers():
    dashboard_add_groups_and_servers(
        user="op_DBA01", ssh_port=33312,
        dashboard_host='10.100.86.51', dashboard_port=18038,
        master_host='10.100.86.16', slave_host='10.100.86.17', redis_port=[6082, 6083],
        start_group=5)

    dashboard_add_groups_and_servers(
        user="op_DBA01", ssh_port=33312,
        dashboard_host='10.100.86.51', dashboard_port=18038,
        master_host='10.100.86.18', slave_host='10.100.86.19', redis_port=[6082, 6083],
        start_group=7)



@task
def call_yz_dashboard_add_groups_and_servers():
    dashboard_add_groups_and_servers(
        user="Li_QingBin", ssh_port=33312,
        dashboard_host='10.100.97.41', dashboard_port=18001,
        master_host='10.100.97.11', slave_host='10.100.97.13', redis_port=[6030, 6059],
        start_group=11)


@task
def call_config_special_dashboard():
    config_special_dashboard("Li_QingBin",33312,"10.100.90.21",18095,18000,"10.100.90.21","10.100.90.20","6320,6325", 7)

@task
def call_deploy_and_startup_watcher():
    deploy_and_startup_watcher("Li_QingBin",33312,"10.100.20.124",18090,17100,"10.100.20.124:2181,10.100.20.125:2181,10.100.20.127:2181","cache29")

@task
def call_single_deploy_and_startup_proxy():
    product_name = "cache33"
    gvar.set_names(product_name)
    deploy_and_startup_proxy(
        user="Li_QingBin", ssh_port=33312,
        proxy_host="10.100.20.162", port_list=[(19990,21990)],
        dashboard_host="10.100.96.108", dashboard_port=18120,
        product_name=product_name,
        kafka_addrs=[], ip_prefix='10.100.96',
        seq=0)

@task
def yz_cps_call_chk_and_deploy_codis_cluster():
    chk_and_deploy_codis_cluster(
        ser="Li_QingBin", ssh_port=33312,
        master_host="10.100.96.51", slave_host="10.100.96.126", redis_port=[6000, 6014], max_mem_size=0,
        dashboard_host="10.100.96.131", dashboard_port=18100,
        watcher_port=17100,
        proxy_hosts=['10.100.96.51', '10.100.96.131'], port_list=[(19340, 21340), (19350, 21350)], ip_prefix='10.100.96', kafka_addrs=["10.100.20.218:6678", "10.100.20.219:6678", "10.100.20.220:6678", "10.100.96.69:6678", "10.100.96.70:6678", "10.100.96.71:6678"], proxy_seq=0,
        product_name="cache74",
        zk_servers="10.100.96.45:2181,10.100.96.46:2181,10.100.96.47:2181",
        repo_url="http://192.168.7.24/codis/codis3", codis3_package_name="codis3_sync.tar.bz2", bk_script_name="codis3_sync_backup.sh",
        backup_invl=4)

@task
def m5_cps_call_chk_and_deploy_codis_cluster():
    chk_and_deploy_codis_cluster(
        user="Li_QingBin", ssh_port=33312,
        master_host="10.100.20.126", slave_host="10.100.20.130", redis_port=[6000, 6014], max_mem_size=0,
        dashboard_host="10.100.42.14", dashboard_port=18100,
        watcher_port=17100,
        proxy_hosts=['10.100.20.126', '10.100.42.14'], port_list=[(19340, 21340), (19350, 21350)], ip_prefix='10.100.20', kafka_addrs=["10.100.20.218:6678", "10.100.20.219:6678", "10.100.20.220:6678", "10.100.96.69:6678", "10.100.96.70:6678", "10.100.96.71:6678"], proxy_seq=0,
        product_name="cache74",
        zk_servers="10.100.20.16:2181,10.100.20.17:2181,10.100.20.18:2181",
        repo_url="http://192.168.7.24/codis/codis3", codis3_package_name="codis3_sync.tar.bz2", bk_script_name="codis3_sync_backup.sh",
        backup_invl=4)


@task
def test_single_call_chk_and_deploy_codis_cluster():
    chk_and_deploy_codis_cluster(
        user="Li_QingBin", ssh_port=33312,
        #redis_host_list=[('10.100.90.20', '10.100.90.22')], redis_port=[6010, 6012], max_mem_size=0,
        redis_host_list=[('10.100.21.121', '10.100.20.239')], redis_port=[6000, 6004], max_mem_size=0,
        dashboard_host="10.100.20.239", dashboard_port=18000,
        watcher_port=17000,
        proxy_hosts=['10.100.20.227'], port_list=[(19800, 21800)], ip_prefix='10.100.20', kafka_addrs=[], proxy_seq=0,
        product_name="test0814",
        zk_servers="10.100.90.20:2181,10.100.90.22:2181",
        repo_url="http://192.168.7.24/codis/codis3", codis3_package_name="codis3_sync.tar.bz2", bk_script_name="codis3_sync_backup.sh",
        backup_invl=0)

@task
def m5_test_call_chk_and_deploy_codis_cluster():
    chk_and_deploy_codis_cluster(
        user="Li_QingBin", ssh_port=33312,
        redis_host_list=[('10.100.90.20', '10.100.90.22')], redis_port=[6000, 6002], max_mem_size=5,
        dashboard_host="10.100.90.22", dashboard_port=18000,
        watcher_port=17000,
        proxy_hosts=['10.100.90.20', '10.100.90.22'], proxy_port_list=[(19000, 21000)], proxy_seq=0,
        sync_hosts=['10.100.90.20', '10.100.90.22'], sync_port=20000, local_brokers='"10.100.20.218:6678", "10.100.20.219:6678", "10.100.20.220:6678"', remote_brokers='"10.100.96.69:6678", "10.100.96.70:6678", "10.100.96.69:6678"',
        product_name="Functional_testing",
        zk_servers="10.100.20.16:2181,10.100.20.17:2181,10.100.20.18:2181",
        repo_url="http://192.168.7.24/codis/codis3", codis3_package_name="codis3_sync.tar.bz2", bk_script_name="codis3_sync_backup.sh",
        backup_invl=0)

@task
def yz_test_call_chk_and_deploy_codis_cluster():
    chk_and_deploy_codis_cluster(
        user="Li_QingBin", ssh_port=33312,
        redis_host_list=[("10.100.96.86", "10.100.96.87")], redis_port=[6000, 6005], max_mem_size=5,
        dashboard_host="10.100.96.86", dashboard_port=18000,
        watcher_port=17000,
        proxy_hosts=['10.100.96.86', '10.100.96.87'], proxy_port_list=[(19000, 21000)], proxy_seq=0,
        sync_hosts=['10.100.90.20', '10.100.90.22'], sync_port=20000, remote_brokers='"10.100.20.218:6678", "10.100.20.219:6678", "10.100.20.220:6678"', local_brokers='"10.100.96.69:6678", "10.100.96.70:6678", "10.100.96.69:6678"',
        product_name="Functional_testing",
        zk_servers="10.100.96.45:2181,10.100.96.46:2181,10.100.96.47:2181",
        repo_url="http://192.168.7.24/codis/codis3", codis3_package_name="codis3_sync.tar.bz2", bk_script_name="codis3_sync_backup.sh",
        backup_invl=0)

@task
def call_test_deploy_and_startup_proxy():
    gvar.set_names("Functional_testing")
    deploy_and_startup_proxy(
        user="Li_QingBin", ssh_port=33312,
        proxy_host="10.100.97.12", port_list=[(19000,21000)],
        dashboard_host="10.100.96.86", dashboard_port=18000,
        product_name="Functional_testing",
        permission=2, seq=0)


# 2 data node
@task
def deploy_test_drc_codis_cluster(): 
    product_name = "cache_test1"
    max_mem_size = 0

    m5_dashboard_host = "10.100.20.1"
    m5_master1 = "10.100.20.1"
    m5_slave1 = "10.100.20.2"
    m5_redis_host_list = [(m5_master1, m5_slave1)]
    m5_proxy_hosts = [m5_master1, m5_slave1]
    m5_sync_hosts = [m5_master1, m5_slave1]
    m5_sentinel_hosts = [m5_master1, m5_slave1]

    yz_dashboard_host = "10.100.97.245"
    yz_master1 = "10.100.97.245"
    yz_slave1 = "10.100.97.246"
    yz_redis_host_list = [(yz_master1, yz_slave1)]
    yz_proxy_hosts = [yz_master1, yz_slave1]
    yz_sync_hosts = [yz_master1, yz_slave1]
    yz_sentinel_hosts = [yz_master1, yz_slave1]

    redis_start_port = 6110
    dashboard_port = 18011
    proxy_port_list=[(19011, 21011)]
    backup_invl=24
    group_num_of_each_pair = 2

    redis_end_port = redis_start_port + group_num_of_each_pair - 1
    sentinel_port = dashboard_port - 1000
    sync_port_pair = (dashboard_port + 2000, dashboard_port + 4000)


    # Changeless config
    user="op_DBA01"
    ssh_port=33312
    m5_zk_servers = "10.100.20.201:4181,10.100.20.202:4181,10.100.20.203:4181"
    yz_zk_servers = "10.100.96.248:4181,10.100.96.249:4181,10.100.96.250:4181"
    repo_url = "http://192.168.7.24"

    m5_sync_zk_servers = "10.100.20.201:4181,10.100.20.202:4181,10.100.20.203:4181"
    yz_sync_zk_servers = "10.100.96.248:4181,10.100.96.249:4181,10.100.96.250:4181"

    gvar.set_names(product_name)
    gvar.set_urls(repo_url)

    # m5
    chk_and_deploy_codis_cluster(
        user=user, ssh_port=ssh_port,
        redis_host_list=m5_redis_host_list, redis_port=[redis_start_port, redis_end_port], max_mem_size=max_mem_size,
        dashboard_host=m5_dashboard_host, dashboard_port=dashboard_port,
        proxy_hosts=m5_proxy_hosts, proxy_port_list=proxy_port_list, proxy_seq=0,
        sync_hosts=m5_sync_hosts, sync_port_pair=sync_port_pair,
        sync_local_zk_servers=m5_sync_zk_servers, sync_remote_zk_servers=yz_sync_zk_servers,
        product_name=product_name,
        zk_servers=m5_zk_servers,
        repo_url=repo_url, backup_invl=backup_invl,
        sentinel_port=sentinel_port, sentinel_hosts=m5_sentinel_hosts)
    
    for each_proxy_host in m5_proxy_hosts:
        for _, admin_port in proxy_port_list:
            admin_url = "%s:%d" % (each_proxy_host, admin_port)
            cmd = "curl -X PUT 'http://%s/api/proxy/flags/write/on'" % admin_url
            os.system(cmd)

    # yz
    chk_and_deploy_codis_cluster(
        user=user, ssh_port=ssh_port,
        redis_host_list=yz_redis_host_list, redis_port=[redis_start_port, redis_end_port], max_mem_size=max_mem_size,
        dashboard_host=yz_dashboard_host, dashboard_port=dashboard_port,
        proxy_hosts=yz_proxy_hosts, proxy_port_list=proxy_port_list, proxy_seq=0,
        sync_hosts=yz_sync_hosts, sync_port_pair=sync_port_pair,
        sync_local_zk_servers=yz_sync_zk_servers, sync_remote_zk_servers=m5_sync_zk_servers,
        product_name=product_name,
        zk_servers=yz_zk_servers,
        repo_url=repo_url, backup_invl=0,
        sentinel_port=sentinel_port, sentinel_hosts=yz_sentinel_hosts)


# test
@task
def deploy_no_drc_codis_cluster_single():
    product_name = "cache322"
    max_mem_size = 0

    m5_dashboard_host = "10.100.42.30"
    m5_master1 = "10.100.42.24"
    m5_slave1 = "10.100.42.27"
    m5_redis_host_list = [(m5_master1, m5_slave1)]
    m5_proxy_hosts = [m5_master1, m5_slave1]
    m5_sentinel_hosts = [m5_master1, m5_slave1, m5_dashboard_host]
    #m5_sentinel_hosts = [m5_master1, m5_slave1]

    redis_start_port = 6400
    group_num_of_each_pair = 2
    dashboard_port = 18189
    proxy_port_list=[(19010, 21010),(19011,21011)]
    backup_invl=24


    redis_end_port = redis_start_port + group_num_of_each_pair - 1
    sentinel_port = dashboard_port - 1000

    user="op_DBA01"
    ssh_port=33312
    m5_zk_servers = "10.100.21.122:7181,10.100.21.123:7181,10.100.21.124:7181,10.100.21.125:7181,10.100.21.126:7181"
    #yz_zk_servers = "10.100.96.69:6181,10.100.96.70:6181,10.100.96.71:6181,10.100.96.245:6181,10.100.96.246:6181"
    repo_url = "http://192.168.7.24"

    gvar.set_names(product_name)
    gvar.set_urls(repo_url)

    # m5
    chk_and_deploy_codis_cluster_without_drc(
        user=user, ssh_port=ssh_port,
        redis_host_list=m5_redis_host_list, redis_port=[redis_start_port, redis_end_port], max_mem_size=max_mem_size,
        dashboard_host=m5_dashboard_host, dashboard_port=dashboard_port,
        proxy_hosts=m5_proxy_hosts, proxy_port_list=proxy_port_list, proxy_seq=0,
        product_name=product_name,
        zk_servers=m5_zk_servers,
        repo_url=repo_url, backup_invl=backup_invl,
        sentinel_port=sentinel_port, sentinel_hosts=m5_sentinel_hosts)

# test
@task
def deploy_no_drc_codis_cluster_m5test():
    product_name = "test_cacte014"
    max_mem_size = 0

    m5_dashboard_host = "10.100.90.163"
    m5_master1 = "10.100.90.161"
    m5_slave1 = "10.100.90.162"
    m5_redis_host_list = [(m5_master1, m5_slave1)]
    m5_proxy_hosts = [m5_master1, m5_slave1]
    m5_sentinel_hosts = [m5_master1, m5_slave1, m5_dashboard_host]
    #m5_sentinel_hosts = [m5_master1, m5_slave1]

    redis_start_port = 8800
    group_num_of_each_pair = 3
    dashboard_port = 29049
    proxy_port_list=[(29400, 34000),(29401,31401)]
    backup_invl=24


    redis_end_port = redis_start_port + group_num_of_each_pair - 1
    sentinel_port = dashboard_port - 1000

    user="op_DBA01"
    ssh_port=33312
    m5_zk_servers = "10.100.90.161:4181,10.100.90.162:4181,10.100.90.163:4181"
    #yz_zk_servers = "10.100.96.69:6181,10.100.96.70:6181,10.100.96.71:6181,10.100.96.245:6181,10.100.96.246:6181"
    repo_url = "http://192.168.7.24"

    gvar.set_names(product_name)
    gvar.set_urls(repo_url)

    # m5
    chk_and_deploy_codis_cluster_without_drc(
        user=user, ssh_port=ssh_port,
        redis_host_list=m5_redis_host_list, redis_port=[redis_start_port, redis_end_port], max_mem_size=max_mem_size,
        dashboard_host=m5_dashboard_host, dashboard_port=dashboard_port,
        proxy_hosts=m5_proxy_hosts, proxy_port_list=proxy_port_list, proxy_seq=0,
        product_name=product_name,
        zk_servers=m5_zk_servers,
        repo_url=repo_url, backup_invl=backup_invl,
        sentinel_port=sentinel_port, sentinel_hosts=m5_sentinel_hosts)
