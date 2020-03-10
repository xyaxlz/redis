'''
#  ============================================================================
#       FileName: check_env.py
#           Desc:
#       HomePage:
#        Created: 2017-09-12 18:16:50
#        Version: 0.0.1
#     LastChange: 2017-09-22 15:29:29
#        History:
#  ============================================================================
'''
from fabric.api import settings, env, task, execute
from fabric.network import disconnect_all

from utils.fab_cmd import sudo_and_chk, get_code_info
from utils.setting import GlobalVar as gvar


@task
def check(master_host, master_host_str, slave_host, slave_host_str,
          redis_host_str, redis_port, redis_ver):

    with settings(parallel=True):
        ret = chk_redis_ver_btw_ms(master_host, master_host_str, slave_host,
                                   slave_host_str, redis_ver)
        if not ret:
            return 101

        ret = execute(chk_redis_env,
                      hosts=redis_host_str,
                      redis_port=redis_port)
        for _, each_ret in ret.items():
            if not each_ret:
                return 102
        disconnect_all()
        gvar.LOGGER.info("Check codis env success.")

    return 1


@task
def chk_redis_ver_btw_ms(master_host, master_host_str, slave_host,
                         slave_host_str, redis_ver):
    ret = execute(get_redis_ver,
                  host=master_host_str)
    master_ver = ret.values()[0]

    ret = execute(get_redis_ver,
                  host=slave_host_str)
    slave_ver = ret.values()[0]

    """Judge whether one of slave's version or master's version is None,
    and whether the another server's version is different with redis package
    version"""
    if master_ver != slave_ver and\
       (not master_ver and slave_ver and slave_ver != redis_ver)\
       or\
       (master_ver and not slave_ver and master_ver != redis_ver):
        if master_ver:
            log_str = "Master redis version is different with redis"\
                "package version. And slave need to be installed redis."\
                "Master version is %s" % master_ver
        else:
            log_str = "Slave redis version is different with redis"\
                "package version. And master need to be installed redis."\
                "Slave version is %s" % slave_ver
        gvar.LOGGER.error(log_str)
        return 0

    if master_ver and slave_ver and master_ver != slave_ver:
        gvar.LOGGER.error("Master and slave are not the same version. "
                          "Master version is `%s`. Slave is `%s`." %
                          (master_ver, slave_ver))

        return 0

    """If any server could not get redis version,
    then check redis dir whether exist"""
    err_flg = [0]
    if not master_ver:
        ret = execute(chk_redis_dir,
                      host=master_host_str)
        if not ret.values()[0]:
            err_flg[0] = 1
            gvar.LOGGER.error(
                "[%s] e_____ clean master `/data/server/redis` dir" %
                master_host)

    if not slave_ver:
        ret = execute(chk_redis_dir,
                      host=slave_host_str)
        if not ret.values()[0]:
            err_flg[0] = 1
            gvar.LOGGER.error(
                "[%s] Please clean slave `/data/server/redis` dir" %
                slave_host)

    if err_flg[0]:
        return 0
    else:
        return 1


def get_redis_ver():
    err_flg = [0]
    ver_ret = [0]

    with settings(warn_only=True):
        get_ver = "%s/redis-server --version" % gvar.REDIS_BIN_DIR
        log_str = '[%s] Get version' % env.host
        sudo_and_chk(get_ver, log_str, err_flg,
                     get_code_info(), get_ret=ver_ret, info_only=1)
        if err_flg[0]:
            return None
        else:
            return ver_ret[0].split()[2].split('=')[1]


def chk_redis_dir():
    with settings(warn_only=True):
        chk_dir = '[ ! -f /data/server/redis ] && [ ! -d /data/server/redis ]'
        log_str = '[%s] Check /data/server/redis' % env.host
        ret = sudo_and_chk(chk_dir, log_str, [0],
                           get_code_info(), info_only=1)
        if ret:
            return 1
        else:
            return 0


def chk_redis_env(redis_port):
    err_flg = [0]

    with settings(warn_only=True):
        redis_file = {}
        redis_file['rdb_file'] = "%s/redis-%d-dump.rdb" %\
            (gvar.REDIS_DATA_DIR, redis_port)
        redis_file['redis_pid_file'] = "%s/redis-%d.pid" %\
            (gvar.REDIS_PID_DIR, redis_port)
        redis_file['redis_log_file'] = "%s/redis-%d.log" %\
            (gvar.REDIS_LOG_DIR, redis_port)

        for filetype, filepath in redis_file.items():
            redis_file_chk = '[ ! -f %s ] && [ ! -d %s ]' %\
                (filepath, filepath)
            log_str = '[%s] %s `%s` check' %\
                (env.host, filetype, filepath)
            sudo_and_chk(redis_file_chk, log_str, err_flg, get_code_info())
            if err_flg[0]:
                return 0
    return 1
