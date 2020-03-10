'''
#  ============================================================================
#       FileName: fabfile.py
#           Desc:
#       HomePage:
#        Created: 2017-09-18 12:05:47
#        Version: 0.0.1
#     LastChange: 2017-09-25 11:46:36
#        History:
#  ============================================================================
'''
import time
from getpass import getpass
from fabric.api import env, task

from deploy_sepical_scenes import deploy_redis_on_special_server,\
    chk_and_deploy_special_slave_server,\
    chk_and_deploy_redis_replica_for_migrate,\
    chk_and_deploy_redis_replica,\
    deploy_sepical_redis
from utils.setting import GlobalVar as gvar

env.password = getpass("SSH password:")
gvar.set_logger()

@task
def call_chk_and_deploy_redis_replica():
    #chk_and_deploy_redis_replica(user='li_qingbin', ssh_port=33312, master_host='192.168.7.145', slave_host='192.168.7.146', redis_port=6301, repo_url='http://192.168.7.24/redis', redis_pkg_name='redis-2.8.13.tar.gz', backup_invl=0, aof=0, aof_rewrite=1, max_mem_size=0, vip1='', vip2='', apply_id=116)
    #chk_and_deploy_redis_replica(user='li_qingbin', ssh_port=33312, master_host='10.100.20.11', slave_host='10.100.20.8', redis_port=6303, repo_url='http://192.168.7.24/redis', redis_pkg_name='redis-2.8.13.tar.gz', backup_invl=0, aof=0, aof_rewrite=1, max_mem_size=0, vip1='', vip2='', apply_id=116)
    chk_and_deploy_redis_replica(user='li_qingbin', ssh_port=33312, master_host='10.100.96.114', slave_host='10.100.96.130', redis_port=6000, repo_url='http://192.168.7.24/redis', redis_pkg_name='redis-4.0.11.tar.gz', backup_invl=0, aof=0, aof_rewrite=1, max_mem_size=0, vip1='', vip2='', apply_id=116)
    #chk_and_deploy_redis_replica(user='li_qingbin', ssh_port=33312, master_host='10.100.21.120', slave_host='10.100.96.87', redis_port=6000, repo_url='http://192.168.7.24/redis', redis_pkg_name='redis-2.8.13.tar.gz', backup_invl=0, aof=0, aof_rewrite=1, max_mem_size=0, vip1='', vip2='', apply_id=116)
    #chk_and_deploy_redis_replica(user='li_qingbin', ssh_port=33312, master_host='10.100.96.112', slave_host='10.100.96.113', redis_port=6000, repo_url='http://192.168.7.24/redis', redis_pkg_name='redis-2.8.13.tar.gz', backup_invl=0, aof=0, aof_rewrite=1, max_mem_size=0, vip1='', vip2='', apply_id=116)

@task
def call_chk_and_deploy_special_slave_server():
    #for i in range(0, 4):
    #    chk_and_deploy_special_slave_server(
    #        user='li_qingbin', ssh_port=33312,
    #        slave_host='10.100.40.24', slave_port=6800+i,
    #        master_host='10.100.20.127', master_port=6570+i,
    #        repo_url='http://192.168.7.24/redis', redis_pkg_name='redis-2.8.13.tar.gz',
    #        backup_invl=0,
    #        instance_name='cache18_%d' % i,
    #        aof=1, aof_rewrite=0, max_mem_size=0)
    #    time.sleep(0)
    chk_and_deploy_special_slave_server(
        user='li_qingbin', ssh_port=33312,
        slave_host='10.100.40.24', slave_port=6009,
        master_host='10.100.21.29', master_port=6389,
        repo_url='http://192.168.7.24/redis', redis_pkg_name='redis-2.8.13.tar.gz',
        backup_invl=0,
        instance_name='bi_cache1',
        aof=1, aof_rewrite=0, max_mem_size=0)

@task
def call_deploy_sepical_redis():
    deploy_sepical_redis(
        user='li_qingbin', ssh_port=33300,
        target_host='127.0.0.1', redis_port=6000,
        aof=0, aof_rewrite=1, max_mem_size=0)

@task
def call_deploy_redis_on_special_server():
    #deploy_redis_on_special_server(user='li_qingbin', ssh_port=33300, target_host='127.0.0.1', repo_url='http://59.151.100.24/redis', redis_pkg_name='redis-2.8.13.tar.gz')
    deploy_redis_on_special_server(user='li_qingbin', ssh_port=33312, target_host='10.100.97.14', repo_url='http://192.168.7.24/redis', redis_pkg_name='redis-4.0.11.tar.gz')

#@task
#def call_chk_and_deploy_redis_replica_for_migrate():
#    chk_and_deploy_redis_replica_for_migrate(
#        user='li_qingbin', ssh_port=33312,
#        orgin_master_host='10.100.20.76', orgin_master_port=6380,
#        master_host='192.168.7.44',
#        slave_host, new_port,
#        repo_url='http://192.168.7.24/redis', redis_pkg_name='redis-2.8.13.tar.gz', backup_invl=0,
#        instance_name, redis_config, aof=0,
#        aof_rewrite=1, max_mem_size=0)
