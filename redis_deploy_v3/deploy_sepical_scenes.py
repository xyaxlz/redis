'''
#  ============================================================================
#       FileName: deploy_sepical_scenes.py
#           Desc:
#       HomePage:
#        Created: 2017-09-19 11:40:09
#        Version: 0.0.1
#     LastChange: 2017-09-25 10:53:40
#        History:
#  ============================================================================
'''

import requests
import json

from jinja2 import Template
from fabric.api import task, env, settings
from fabric.network import disconnect_all

from check_env import chk_redis_ver_btw_ms, chk_redis_dir,\
    get_redis_ver, chk_redis_env, check

from deploy_redis_instance import *
from deploy_redis_env import deploy_redis_env, install_redis_pkg,\
    install_redis_pkg
from utils.setting import GlobalVar as gvar, Cfg
from utils.parm_parse import parm_parse
from utils._exceptions import DeployErr


@task
def deploy_redis_on_special_server(user, ssh_port, target_host,
                                   repo_url, redis_pkg_name):
    parm = parm_parse(locals())

    #ret = execute(chk_redis_dir,
    #              host=parm.target_host_str)
    #if not ret.values()[0]:
    #    gvar.LOGGER.error("Please clean `/data/server/redis` dir")
    #    raise DeployErr(103)

    redis_unpack_dir = parm.redis_pkg_name.split('.tar')[0]
    ret = execute(install_redis_pkg,
                  hosts=parm.target_host_str,
                  redis_urls=parm.pkg_urls['redis'],
                  redis_pkg_name=parm.redis_pkg_name,
                  redis_unpack_dir=parm.redis_unpack_dir)
    if not ret.values()[0]:
        raise DeployErr(201)
    gvar.LOGGER.info("Deploy codis succeed.")
    return 1


@task
def chk_and_deploy_special_subordinate_server(user, ssh_port, subordinate_host, subordinate_port,
                                        main_host, main_port, repo_url,
                                        redis_pkg_name, backup_invl,
                                        aof=0, aof_rewrite=1,
                                        max_mem_size=0):
    parm = parm_parse(locals())

    redis_cfg =\
        Template(Cfg.redis_cfg).render(port=parm.subordinate_port, aof=parm.aof,
                                       aof_rewrite=parm.aof_rewrite,
                                       max_mem_size=parm.max_mem_size)
    try:
        r = redis.Redis(host=main_host, port=main_port, db=0)
        ret = r.ping()
        gvar.LOGGER.info("Redis main is alived.")
    except Exception as e:
        gvar.LOGGER.error("Please check orgin main. Error:[%s]" % e)
        raise DeployErr(305)

    ret = execute(chk_redis_env,
                  host=parm.subordinate_host_str,
                  redis_port=parm.subordinate_port)
    if not ret.values()[0]:
        raise DeployErr(102)

    ret = execute(chk_redis_dir,
                  host=parm.subordinate_host_str)
    if ret.values()[0]:
        ret = execute(install_redis_pkg,
                      host=parm.subordinate_host_str,
                      redis_urls=parm.pkg_urls['redis'],
                      redis_pkg_name=parm.redis_pkg_name,
                      redis_unpack_dir=parm.redis_unpack_dir)
        if not ret.values()[0]:
            raise DeployErr(201)

    ret = execute(deploy_redis,
                  hosts=parm.subordinate_host_str,
                  redis_port=parm.subordinate_port,
                  redis_cfg=redis_cfg)
    if not ret.values()[0]:
        raise DeployErr(301)

    if parm.backup_invl:
        ret = execute(config_redis_backup,
                      hosts=parm.subordinate_host_str,
                      redis_port=parm.subordinate_port,
                      script_url=parm.pkg_urls['bk_script'],
                      backup_invl=parm.backup_invl)
        if not ret.values()[0]:
            raise DeployErr(302)

    ret = execute(startup_redis,
                  hosts=parm.subordinate_host_str,
                  redis_port=parm.subordinate_port)
    if not ret.values()[0]:
        raise DeployErr(303)

    ret = subordinateof(parm.subordinate_host, parm.subordinate_port,
                  parm.main_host, parm.main_port)
    if not ret:
        raise DeployErr(304)
    gvar.LOGGER.info("Deploy subordinate succeed.")
    return 1


@task
def chk_and_deploy_redis_replica(user, ssh_port, main_host, subordinate_host,
                                 redis_port, repo_url, redis_pkg_name,
                                 backup_invl, aof,
                                 aof_rewrite, max_mem_size,
                                 vip1, vip2, apply_id):
    parm = parm_parse(locals())
    redis_host_str = (parm.main_host_str, parm.subordinate_host_str)
    redis_cfg =\
        Template(Cfg.redis_cfg).render(port=parm.redis_port, aof=parm.aof,
                                       aof_rewrite=parm.aof_rewrite,
                                       max_mem_size=parm.max_mem_size)

    ret = check(parm.main_host, parm.main_host_str, parm.subordinate_host,
                parm.subordinate_host_str, redis_host_str, parm.redis_port,
                parm.redis_ver)

    if ret != 1:
        raise DeployErr(ret)

    ret = deploy_redis_env(redis_host_str, parm.pkg_urls['redis'],
                           parm.redis_pkg_name, parm.redis_unpack_dir)
    if ret != 1:
        raise DeployErr(ret)

    ret = deploy_redis_replica(parm.main_host, parm.subordinate_host,
                               redis_host_str, parm.redis_port,
                               parm.backup_invl, parm.pkg_urls,
                               redis_cfg)
    if ret != 1:
        raise DeployErr(ret)

    return 1


@task
def chk_and_deploy_redis_replica_for_migrate(
        user, ssh_port, orgin_main_host, orgin_main_port, main_host,
        subordinate_host, new_port, repo_url, redis_pkg_name, backup_invl,
        redis_config, aof=0, aof_rewrite=1, max_mem_size=0):

    try:
        r = redis.Redis(host=orgin_main_host, port=orgin_main_port, db=0)
        ret = r.ping()
        gvar.LOGGER.info("Redis orgin main is alived.")
    except Exception as e:
        gvar.LOGGER.error("Please check orgin main. Error:[%s]" % e)
        raise DeployErr(305)

    ret = chk_and_deploy_redis_replica(user, ssh_port, main_host, subordinate_host,
                                       new_port, repo_url, redis_pkg_name,
                                       backup_invl, redis_config,
                                       aof, aof_rewrite, max_mem_size)
    if ret != 1:
        raise DeployErr(ret)

    ret = subordinateof(main_host, new_port,
                  orgin_main_host, orgin_main_port)
    if not ret:
        raise DeployErr(304)
    gvar.LOGGER.info("Deploy redis replica for migrate succeed.")
    return 1


@task
def deploy_sepical_redis(user, ssh_port, target_host, redis_port, aof=0,
                         aof_rewrite=1, max_mem_size=0):
    with settings(parallel=True):
        parm = parm_parse(locals())
        redis_cfg =\
            Template(Cfg.redis_cfg).render(port=parm.redis_port, aof=parm.aof,
                                 aof_rewrite=parm.aof_rewrite,
                                 max_mem_size=parm.max_mem_size)

        ret = execute(deploy_redis,
                      host=parm.target_host_str,
                      redis_port=parm.redis_port,
                      redis_cfg=redis_cfg)
        for _, each_ret in ret.items():
            if not each_ret:
                return 301

        ret = execute(startup_redis,
                      host=parm.target_host_str,
                      redis_port=parm.redis_port)

        for _, each_ret in ret.items():
            if not each_ret:
                return 303

    disconnect_all()
    gvar.LOGGER.info("Init redis succeed.")
    return 1
