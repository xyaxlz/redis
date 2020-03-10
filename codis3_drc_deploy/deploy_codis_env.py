'''
#  ============================================================================
#       FileName: deploy_codis_env.py
#           Desc:
#       HomePage:
#        Created: 2017-08-22 17:34:17
#        Version: 0.0.1
#     LastChange: 2017-09-28 16:52:42
#        History:
#  ============================================================================
'''
from fabric.api import settings, task, execute, env
from fabric.network import disconnect_all

from utils.fab_cmd import sudo_and_chk, get_code_info, sudo_and_get_result
from utils.setting import GlobalVar as gvar


@task
def deploy_codis_env(host_str):
    """Install Codis package"""
    with settings(parallel=True):
        ret = execute(install_codis3_pkg,
                      hosts=host_str)
        for _, each_ret in ret.items():
            if not each_ret:
                return 202

        ret = execute(chk_codis3_dir,
                      hosts=host_str,
                      info_only=0)

        for _, each_ret in ret.items():
            if not each_ret:
                return 202
        disconnect_all()
        print("Deploy codis env success.")
    return 1


def chk_codis3_dir(info_only):
    err_flg = [0]

    with settings(warn_only=True):
        codis_cmd = 'codis-admin,codis-dashboard,codis-fe,codis-proxy,\
codis-server,redis-cli'
        chk_cmd = 'ls %s/bin/{%s}' % (gvar.CODIS_DIR, codis_cmd)
        log_str = '[%s] Codis command files `%s`' % (env.host, chk_cmd)
        sudo_and_chk(chk_cmd, log_str, err_flg,
                     get_code_info(), info_only=info_only)
        if err_flg[0]:
            return 0
        else:
            return 1


def install_codis3_pkg():
    err_flg = [0]

    with settings(warn_only=True):
        get_ver_cmd = "rpm -q centos-release|awk -F '-' '{print $3}'"
        log_str = '[%s] Get OS version' % env.host
        ret = sudo_and_get_result(get_ver_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        if ret == "6":
            codis_urls = gvar.CENTOS6_URL
        elif ret == "7":
            codis_urls = gvar.CENTOS7_URL
        else:
            gvar.LOGGER.error("[%s] %s:[line:%d] OS version not in 6 or 7!" %
                              (env.host, f_name, f_lineno))                  
            return 0

        wget_cmd = 'cd /data/install;rm -rf %s;wget %s' % (
            gvar.CODIS_PKG_NAME, codis_urls)
        log_str = '[%s] Wget codis package' % env.host
        sudo_and_chk(wget_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        unpack_cmd = 'cd /data/install;tar xf %s -C /data/server' % gvar.CODIS_PKG_NAME
        log_str = '[%s] Unpack codis3 package' % env.host
        sudo_and_chk(unpack_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        chown_cmd = 'chown -R web.web %s' % gvar.CODIS_DIR
        log_str = '[%s] Chown `%s`' % (env.host, gvar.CODIS_DIR)
        sudo_and_chk(chown_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        chk_crontab_cmd = 'grep "find /data/server/codis3_drc/log -mtime +3 -exec rm -rf {}" /var/spool/cron/root'
        log_str = '[%s] Check crontab file whether exists entry' % (env.host)
        ret = sudo_and_chk(chk_crontab_cmd, log_str, [
                           0], get_code_info(), info_only=1)
        if not ret:
           add_crontab_cmd = 'echo "0 3 * * * find /data/server/codis3_drc/log -mtime +3 -exec rm -rf {} \;" >> /var/spool/cron/root'
           log_str = '[%s] Add crontab' % (env.host)
           sudo_and_chk(add_crontab_cmd, log_str, err_flg,
                        get_code_info())
           if err_flg[0]:
               return 0

        return 1
