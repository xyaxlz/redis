'''
#  ============================================================================
#       FileName: check_env.py
#           Desc:
#       HomePage:
#        Created: 2017-08-22 15:30:36
#        Version: 0.0.1
#     LastChange: 2017-09-28 16:52:18
#        History:
#  ============================================================================
'''
from fabric.api import settings, env, task, execute
from fabric.network import disconnect_all
from kazoo.client import KazooClient

from utils.fab_cmd import sudo_and_chk, get_code_info
from utils.setting import GlobalVar as gvar


@task
def check(redis_host_str, redis_port, dashboard_host_str, dashboard_port,
          proxy_host_str, proxy_port_list, product_name, zk_servers):
    with settings(parallel=True):
        ret = execute(chk_redis_env,
                      hosts=redis_host_str,
                      redis_port=redis_port)
        for _, each_ret in ret.items():
            if not each_ret:
                return 101

        ret = execute(chk_dashboard,
                      hosts=dashboard_host_str,
                      product_name=product_name,
                      dashboard_port=dashboard_port)
        for _, each_ret in ret.items():
            if not each_ret:
                return 102

        if proxy_host_str != "":
            ret = execute(chk_proxy_env,
                          hosts=proxy_host_str,
                          product_name=product_name,
                          proxy_port_list=proxy_port_list)
            for _, each_ret in ret.items():
                if not each_ret:
                    return 103

        ret = chk_zk_node(zk_servers, product_name)
        if not ret:
            return 104

        disconnect_all()
        return 1


def chk_redis_env(redis_port):
    err_flg = [0]

    with settings(warn_only=True):
        for each_port in redis_port:
            """check redis file"""
            redis_file = {}
            redis_file['rdb_file'] = "%s/redis-%d-dump.rdb" %\
                (gvar.REDIS_DATA_DIR, each_port)
            redis_file['redis_pid_file'] = "%s/%d.pid" %\
                (gvar.REDIS_TMP_DIR, each_port)
            redis_file['redis_log_file'] = "%s/redis-%d.log" %\
                (gvar.REDIS_LOG_DIR, each_port)

            for filetype, filepath in redis_file.items():
                redis_file_chk = '[ ! -f %s ]' % filepath
                log_str = '[%s] %d %s `%s` check' %\
                    (env.host, each_port, filetype, filepath)
                sudo_and_chk(redis_file_chk, log_str, err_flg, get_code_info())

            port_chk = "[ `ss -lnt|awk '{print $4}'| grep %d|wc -l` -eq 0 ]" % each_port
            log_str = '[%s] Check port %d whether free' %\
                (env.host, each_port)
            sudo_and_chk(port_chk, log_str, err_flg, get_code_info())

    if err_flg[0]:
        return 0
    else:
        return 1


def chk_dashboard(product_name, dashboard_port):
    err_flg = [0]

    with settings(warn_only=True):
        dashboard_supervise_path = '%s/%s' % (
            gvar.SUPERVISE_DIR, gvar.DASHBOARD_NAME)
        dashboard_supervise_chk = '[ ! -d %s ]' % dashboard_supervise_path
        log_str = '[%s] Dashboard supervise `%s` check' %\
            (env.host, dashboard_supervise_path)
        sudo_and_chk(dashboard_supervise_chk, log_str,
                     err_flg, get_code_info())

        chk_supervise_process_cmd = 'ps -ef |grep "%s" |grep -v grep| wc -l' %\
            dashboard_supervise_path
        log_str = '[%s] Check dashboard supervise process `%s`' %\
            (env.host, chk_supervise_process_cmd)
        sudo_and_chk(chk_supervise_process_cmd, log_str,
                     err_flg, get_code_info(), 1, '0')

        dashboard_log_file = '%s/%s' % (gvar.CODIS_LOG_DIR,
                                        gvar.DASHBOARD_NAME)
        chk_dashboard_log_file = 'ls %s*' % dashboard_log_file
        log_str = '[%s] Dashboard log file `%s`' % (env.host,
                                                    chk_dashboard_log_file)
        ret = sudo_and_chk(chk_dashboard_log_file, log_str, [
                           0], get_code_info(), info_only=1)
        if ret:                                  
            f_name, f_lineno = get_code_info()
            f_lineno -= 4                
            gvar.LOGGER.error("[%s] %s:[line:%d] Dashboard have log error!" %
                              (env.host, f_name, f_lineno))                  
            err_flg[0] = 1               


        dashboard_pid_file = '%s/%s.pid' % (gvar.CODIS_TMP_DIR,
                                            gvar.DASHBOARD_NAME)
        chk_dashboard_pid = '[ ! -f %s ]' % dashboard_pid_file
        log_str = '[%s] Check dasboard pidfile `%s`' % (env.host,
                                                        dashboard_pid_file)
        sudo_and_chk(chk_dashboard_pid, log_str, err_flg, get_code_info())

        chk_dashboard_process_cmd =\
            'ps -ef |grep "%s.toml" |grep -v grep| wc -l' %\
            gvar.DASHBOARD_NAME
        log_str = '[%s] Check dasboard process `%s`' %\
            (env.host, chk_dashboard_process_cmd)
        sudo_and_chk(chk_dashboard_process_cmd, log_str,
                     err_flg, get_code_info(), 1, '0')

        port_chk = "[ `ss -lnt|awk '{print $4}'| grep %d|wc -l` -eq 0 ]" % dashboard_port
        log_str = '[%s] Check dashboard port %d whether free' %\
            (env.host, dashboard_port)
        sudo_and_chk(port_chk, log_str, err_flg, get_code_info())

    if err_flg[0]:
        return 0
    else:
        return 1


def chk_proxy_env(product_name, proxy_port_list):
    err_flg = [0]
    with settings(warn_only=True):
        proxy_supervise_path = '%s/%s' % (gvar.SUPERVISE_DIR,
                                          gvar.PROXY_NAME)
        proxy_supervise_chk = '[ ! -d %s ]' % proxy_supervise_path
        log_str = '[%s] proxy_supervise `%s` check' %\
            (env.host, proxy_supervise_path)
        sudo_and_chk(proxy_supervise_chk, log_str, err_flg, get_code_info())

        chk_supervise_process_cmd =\
            'ps -ef |grep "%s.toml" |grep -v grep| wc -l' %\
            gvar.PROXY_NAME
        log_str = '[%s] Check proxy supervise process `%s`' %\
            (env.host, chk_supervise_process_cmd)
        sudo_and_chk(chk_supervise_process_cmd, log_str,
                     err_flg, get_code_info(), 1, '0')

        proxy_log_file = '%s/%s' % (gvar.CODIS_LOG_DIR,
                                    gvar.PROXY_NAME)
        chk_proxy_log_file = 'ls %s*' % proxy_log_file
        log_str = '[%s] Proxy log file `%s`' % (env.host, chk_proxy_log_file)
        ret = sudo_and_chk(chk_proxy_log_file, log_str, [
                           0], get_code_info(), info_only=1)
        if ret:
            err_flg[0] = 1

        proxy_pid_file = '%s/%s.pid' % (gvar.CODIS_TMP_DIR,
                                        gvar.PROXY_NAME)
        chk_proxy_pid = '[ ! -f %s ]' % proxy_pid_file
        log_str = '[%s] Check proxy pidfile `%s`' % (env.host,
                                                     proxy_pid_file)
        sudo_and_chk(chk_proxy_pid, log_str, err_flg, get_code_info())

        chk_proxy_process_cmd = 'ps -ef |grep "%s" |grep -v grep| wc -l' %\
            proxy_supervise_path
        log_str = '[%s] Check proxy supervise process `%s`' %\
            (env.host, chk_proxy_process_cmd)
        sudo_and_chk(chk_proxy_process_cmd, log_str,
                     err_flg, get_code_info(), 1, '0')

        for each_proxy in proxy_port_list:
            for each_port in each_proxy:
                port_chk = "[ `ss -lnt|awk '{print $4}'| grep %d|wc -l` -eq 0 ]" % each_port
                log_str = '[%s] Check port %d whether free' %\
                    (env.host, each_port)
                sudo_and_chk(port_chk, log_str, err_flg, get_code_info())
    if err_flg[0]:
        return 0
    else:
        return 1


def chk_zk_node(zk_servers, product_name):
    try_times = 0

    """Check zookeeper whether exist."""
    try:
        f_name, f_lineno = get_code_info()
        f_lineno += 3
        zk = KazooClient(zk_servers)
        zk.start()
    except Exception as e:
        f_name, f_lineno = get_code_info()
        f_lineno -= 2
        gvar.LOGGER.error("%s:[line:%d] Failed to connect Zookeeper." %
                          (f_name, f_lineno))
        return 0

    """Check node whether exist."""
    node_path = '/codis3/%s' % product_name
    f_name, f_lineno = get_code_info()
    f_lineno += 2
    exists = zk.exists(node_path)
    zk.stop()
    if exists:
        gvar.LOGGER.error(
            "%s:[line:%d] Zookeeper node_path `%s` already exists!" %
            (f_name, f_lineno, node_path))
        return 0
    else:
        gvar.LOGGER.info(
            "%s:[line:%d] Zookeeper node_path `%s` not exists!" %
            (f_name, f_lineno, node_path))
        return 1
