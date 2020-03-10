'''
#  ============================================================================
#       FileName: deploy_redis_instance.py
#           Desc:
#       HomePage:
#        Created: 2017-09-13 10:55:49
#        Version: 0.0.1
#     LastChange: 2017-09-22 10:16:21
#        History:
#  ============================================================================
'''
from fabric.api import settings, env, task, execute, settings
from fabric.network import disconnect_all
import time
import redis

from utils.fab_cmd import sudo_and_chk, sudo_and_rechk, get_code_info
from utils.setting import GlobalVar as gvar


@task
def deploy_redis_replica(master_host, slave_host, redis_host_str, redis_port,
                         backup_invl, pkg_urls, redis_cfg):
    with settings(parallel=True):
        ret = execute(create_user,
                      hosts=redis_host_str)
        for _, each_ret in ret.items():
            if not each_ret:
                return 300

        ret = execute(deploy_redis,
                      hosts=redis_host_str,
                      redis_port=redis_port,
                      redis_cfg=redis_cfg)
        for _, each_ret in ret.items():
            if not each_ret:
                return 301

        if backup_invl:
            ret = execute(config_redis_backup,
                          hosts=redis_host_str,
                          redis_port=redis_port,
                          script_url=pkg_urls['bk_script'],
                          backup_invl=backup_invl)
            for _, each_ret in ret.items():
                if not each_ret:
                    return 302

        ret = execute(startup_redis,
                      hosts=redis_host_str,
                      redis_port=redis_port)
        for _, each_ret in ret.items():
            if not each_ret:
                return 303

        ret = slaveof(slave_host, redis_port,
                      master_host, redis_port)
        if not ret:
            return 304

        ret = execute(deploy_ha_scripts,
                      hosts=redis_host_str,
                      master_host=master_host,
                      slave_host=slave_host,
                      redis_port=redis_port,
                      pkg_urls=pkg_urls)
        for _, each_ret in ret.items():
            if not each_ret:
                return 306

    disconnect_all()
    gvar.LOGGER.info("Init replica succeed.")
    return 1


def create_user():
    err_flg = [0]

    with settings(warn_only=True):
        chk_cmd = 'egrep "^web:" /etc/passwd'
        log_str = '[%s] Check user whether exists' % env.host
        ret = sudo_and_chk(chk_cmd, log_str, [0],
                           get_code_info(), info_only=1)
        if not ret:
            create_cmd = 'useradd web'
            log_str = '[%s] Add user web' % env.host
            sudo_and_chk(create_cmd, log_str, err_flg, get_code_info())
            if err_flg[0]:
                return 0
    return 1


def deploy_redis(redis_port, redis_cfg):
    err_flg = [0]

    with settings(warn_only=True):
        mkdir_cmd = "mkdir -p %s/{log,etc,pid,data}" % gvar.REDIS_DIR
        log_str = '[%s] Make redis dir' % env.host
        sudo_and_chk(mkdir_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        cfg_name = gvar.REDIS_CFG_NAME % (redis_port)
        cfg_path = '%s/%s' % (gvar.REDIS_CONF_DIR, cfg_name)
        create_cfg_cmd = '''cat << EOF > %s
%s
EOF''' % (cfg_path, redis_cfg)
        log_str = '[%s] Create redis cfg `%s`' % (env.host, cfg_path)
        sudo_and_chk(create_cfg_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        chown_cmd = "chown -R web.web %s/{log,etc,pid,data}" % gvar.REDIS_DIR
        log_str = '[%s] Chown redis dir' % env.host
        sudo_and_chk(chown_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

    return 1


def config_redis_backup(redis_port, script_url, backup_invl):
    err_flg = [0]

    with settings(warn_only=True):
        chk_script_cmd = '[ -f %s/backup_redis.sh ]' % gvar.SCRIPT_DIR
        log_str = '[%s] Check backup scripts' % env.host
        ret = sudo_and_chk(chk_script_cmd, log_str, [0],
                           get_code_info(), info_only=1)
        if not ret:
            get_script_cmd = 'mkdir -p %s && cd %s && wget %s ' %\
                (gvar.SCRIPT_DIR, gvar.SCRIPT_DIR, script_url)
            log_str = '[%s] Get backup scripts' % env.host
            sudo_and_chk(get_script_cmd, log_str, err_flg, get_code_info())
            if err_flg[0]:
                return 0

        chk_cron_cmd = 'less /var/spool/cron/web |\
egrep -w "%s" |egrep -w "backup_redis.sh"' % redis_port
        log_str = '[%s] Check crontab file whether exists entry' % env.host
        ret = sudo_and_chk(chk_cron_cmd, log_str, [0],
                           get_code_info(), info_only=1)
        if not ret:
            add_crontab_cmd = 'echo "1 */%d * * * sh \
%s/backup_redis.sh %d > /dev/null 2>&1" >> /var/spool/cron/web' % (
                backup_invl, gvar.SCRIPT_DIR, redis_port)
            log_str = '[%s] Add crontab' % env.host
            sudo_and_chk(add_crontab_cmd, log_str, err_flg,
                         get_code_info())
            if err_flg[0]:
                return 0

        chmod_cmd = 'chmod +x %s/backup_redis.sh' % gvar.SCRIPT_DIR
        log_str = '[%s] Chmod backup script' % env.host
        sudo_and_chk(chmod_cmd, log_str, err_flg, get_code_info())

        web_cron = '/var/spool/cron/web'
        chg_priv_cmd = 'chmod 600 %s;chown web.web %s' % (web_cron, web_cron)
        log_str = '[%s] Chmod and chown web crontab file' % env.host
        sudo_and_chk(chg_priv_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0
    return 1


def startup_redis(redis_port):
    err_flg = [0]

    for i in range(3):
        start_cmd = 'su - web -c "%s/redis-server %s/redis-%d.conf"' %\
            (gvar.REDIS_BIN_DIR, gvar.REDIS_CONF_DIR, redis_port)
        log_str = '[%s] Redis startup startup command execute' % env.host
        sudo_and_chk(start_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        r = redis.Redis(host=env.host, port=redis_port, db=0)

        time.sleep(5)

        success_flg = 0
        for j in range(3):
            try:
                f_name, f_lineno = get_code_info()
                f_lineno += 2
                ret = r.ping()
                if ret:
                    success_flg = 1
                log_str = "%s:[%d] Redis %s startup succeed." %\
                    (f_name, f_lineno, env.host)
                gvar.LOGGER.info(log_str)
                break
            except Exception as e:
                f_name, f_lineno = get_code_info()
                f_lineno -= 9
                gvar.LOGGER.warning("%s[line:%d] [%s] %s" %
                                    (f_name, f_lineno, env.host, e))
                if j < 2:
                    time.sleep(2)
        if success_flg:
            break
        else:
            gvar.LOGGER.error("%s[line:%d] [%s] %s" %
                              (f_name, f_lineno, env.host, e))

        return 0
    return 1


def slaveof(slave_host, slave_port, master_host, master_port):
    r = redis.Redis(host=slave_host, port=slave_port, db=0)
    r.slaveof(master_host, master_port)
    role = r.info()['role']
    f_name, f_lineno = get_code_info()
    f_lineno -= 2
    if role == 'slave':
        gvar.LOGGER.info("%s[line:%d] Slaveof execute succed." %
                         (f_name, f_lineno))
        return 1
    else:
        gvar.LOGGER.error("%s[line:%d] Slaveof execute failed." %
                          (f_name, f_lineno))
        return 0

def deploy_ha_scripts(master_host, slave_host, redis_port, pkg_urls):
    err_flg = [0]

    with settings(warn_only=True):
        scripts = ['redis_master', 'redis_backup', 'redis_fault', 'redis_stop']
        for each in scripts:
            chk_script_cmd = '[ -f %s/%s.sh ]' % (gvar.SCRIPT_DIR, each)
            log_str = '[%s] Check backup scripts' % env.host
            ret = sudo_and_chk(chk_script_cmd, log_str, [0],
                               get_code_info(), info_only=1)

            if not ret:
                get_script_cmd = "cd %s && wget %s" %\
                    (gvar.SCRIPT_DIR, pkg_urls[each])
                log_str = '[%s] Get %s scripts' % (env.host, each)
                sudo_and_chk(get_script_cmd, log_str, err_flg, get_code_info())
                if err_flg[0]:
                    return 0
        if env.host == master_host:
            change_host = slave_host
        else:
            change_host = master_host

        redis_master_chk = 'less %s/redis_master.sh |\
egrep -w "SLAVEOF" |egrep -w "%d"' % (gvar.SCRIPT_DIR, redis_port)
        log_str = '[%s] Check redis_backup file whether exists entry' % env.host
        ret = sudo_and_chk(redis_master_chk, log_str, [0],
                           get_code_info(), info_only=1)
        if not ret:
            add_redis_master =\
                'echo "\\\\$REDISCli -p %d SLAVEOF NO ONE >> \\\\$LOGFILE \
2>&1" >> %s/redis_master.sh' % (redis_port, gvar.SCRIPT_DIR)
            log_str = '[%s] Add entry into redis_master script.' % env.host
            sudo_and_chk(add_redis_master, log_str, err_flg,
                         get_code_info())
            if err_flg[0]:
                return 0

        redis_backup_chk = 'less %s/redis_backup.sh |\
egrep -w "%s" |egrep -w "%s"' % (gvar.SCRIPT_DIR, change_host, redis_port)
        log_str = '[%s] Check redis_backup file whether exists entry' % env.host
        ret = sudo_and_chk(redis_backup_chk, log_str, [0],
                           get_code_info(), info_only=1)
        if not ret:
            add_redis_backup = 'echo "\\\\$REDISCli -p %d SLAVEOF %s %d >> \
\\\\$LOGFILE 2>&1" >> %s/redis_backup.sh' % (redis_port, change_host,
                                                redis_port, gvar.SCRIPT_DIR)
            log_str = '[%s] Add entry into redis_backup script.' % env.host
            sudo_and_chk(add_redis_backup, log_str, err_flg,
                         get_code_info())
            if err_flg[0]:
                return 0

    return 1
