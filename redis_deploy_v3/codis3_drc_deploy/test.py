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

# M5 single test
@task
def deploy_no_drc_codis_cluster_m5test():
    product_name = "test_cache106"
    max_mem_size = 0

    m5_dashboard_host = "10.100.90.163"
    m5_main1 = "10.100.90.161"
    m5_subordinate1 = "10.100.90.162"
    m5_redis_host_list = [(m5_main1, m5_subordinate1)]
    m5_proxy_hosts = [m5_main1, m5_subordinate1]
    m5_sentinel_hosts = [m5_main1, m5_subordinate1, m5_dashboard_host]
    #m5_sentinel_hosts = [m5_main1, m5_subordinate1]

    redis_start_port = 7150
    group_num_of_each_pair = 2
    dashboard_port = 18039
    proxy_port_list=[(19045, 21045),(19046,21046)]
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

    dashboard_url = "%s:%d" % (m5_dashboard_host, dashboard_port)
    for each_proxy_host in m5_proxy_hosts:
        for _, admin_port in proxy_port_list:
            admin_url = "%s:%d" % (each_proxy_host, admin_port)
            # cmd = "curl -X PUT 'http://%s/api/proxy/flags/write/on'" % admin_url
            cmd = "curl -X PUT 'http://%s/topom/proxy/flags/%s/write/on'" % (dashboard_url, admin_url)
            print(cmd)
            #os.system(cmd)

# Upgrade Codis Installpkg
@task
def call_deploy_sepical_codis_env():
    #servers = ["10.100.90.161","10.100.90.162","10.100.90.163"]
    #servers = ["10.100.42.30","10.100.42.31","10.100.42.33","10.100.42.34"]
    #servers = ["10.100.86.51","10.100.86.16","10.100.86.17","10.100.86.18","10.100.86.19"]
    #servers = ["10.100.42.30", "10.100.42.31", "10.100.42.32", "10.100.42.33", "10.100.42.34"]
    #servers = ["10.100.86.28","10.100.86.29","10.100.86.30","10.100.86.31","10.100.86.32","10.100.86.37"]
    #servers = ["10.100.42.51","10.100.42.52","10.100.42.53","10.100.42.56","10.100.42.57","10.100.42.58"]
    #servers = ["10.100.42.3","10.100.42.4","10.100.42.5","10.100.42.6","10.100.86.44","10.100.86.45","10.100.86.46","10.100.86.47"]
    servers = ["10.100.42.7"]
    repo_url="http://192.168.7.24"
    gvar.set_urls(repo_url)
    for each_host in servers:
        deploy_sepical_codis_env(
            user="op_DBA01", ssh_port=33312,
            target_host=each_host,
            repo_url=repo_url,
            codis3_package_name="codis3_drc.tar.bz2")
