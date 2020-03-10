'''
#  ============================================================================
#       FileName: deploy_redis_env.py
#           Desc:
#       HomePage:
#        Created: 2017-09-12 15:15:56
#        Version: 0.0.1
#     LastChange: 2017-09-21 18:57:58
#        History:
#  ============================================================================
'''
from fabric.api import settings, task, execute, env
from fabric.network import disconnect_all

from utils.fab_cmd import sudo_and_chk, get_code_info
from utils.setting import GlobalVar as gvar


@task
def deploy_redis_env(redis_host_str, redis_url,
                     redis_pkg_name, redis_unpack_dir):

    with settings(parallel=True):
        ret = execute(chk_redis_dir,
                      hosts=redis_host_str,
                      info_only=1)

        for each_host, ret in ret.items():
            if not ret:
                ret = execute(install_redis_pkg,
                              hosts=each_host,
                              redis_urls=redis_url,
                              redis_pkg_name=redis_pkg_name,
                              redis_unpack_dir=redis_unpack_dir)

                for _, each_ret in ret.items():
                    if not each_ret:
                        return 201

                ret = execute(chk_redis_dir,
                              hosts=each_host,
                              info_only=0)

                for _, each_ret in ret.items():
                    if not each_ret:
                        return 201
        disconnect_all()
    gvar.LOGGER.info("Deploy codis env success.")
    return 1


def chk_redis_dir(info_only):
    err_flg = [0]

    with settings(warn_only=True):
        chk_cmd = 'ls %s/{redis-server,redis-cli}' % gvar.REDIS_BIN_DIR
        log_str = '[%s] Redis command files `%s`' % (env.host, chk_cmd)
        sudo_and_chk(chk_cmd, log_str, err_flg,
                     get_code_info(), info_only=info_only)
        if err_flg[0]:
            return 0
        else:
            return 1


def install_redis_pkg(redis_urls, redis_pkg_name, redis_unpack_dir):
    err_flg = [0]

    with settings(warn_only=True):
        wget_cmd = 'cd /data/server;wget %s' % redis_urls
        log_str = '[%s] Wget redis package' % env.host
        sudo_and_chk(wget_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        unpack_cmd = 'cd /data/server;tar xf %s;mv %s redis' %\
            (redis_pkg_name, redis_unpack_dir)
        log_str = '[%s] Unpack redis package' % env.host
        sudo_and_chk(unpack_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        compile_cmd = 'cd %s;make' % gvar.REDIS_SRC_DIR
        log_str = '[%s] Redis compile' % env.host
        sudo_and_chk(compile_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        move_comand_file = 'mkdir -p %s;mv %s/{%s} %s' %\
            (gvar.REDIS_BIN_DIR, gvar.REDIS_SRC_DIR,
             gvar.REDIS_CMD, gvar.REDIS_BIN_DIR)
        log_str = '[%s] Move redis comand file' % env.host
        sudo_and_chk(move_comand_file, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        chown_cmd = 'chown -R web.web %s' % gvar.REDIS_DIR
        log_str = '[%s] Chown `%s`' % (env.host, gvar.REDIS_DIR)
        sudo_and_chk(chown_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

    return 1
