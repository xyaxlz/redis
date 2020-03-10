'''
#  ============================================================================
#       FileName: deploy_codis_instance.py
#           Desc:
#       HomePage:
#        Created: 2017-08-24 17:08:00
#        Version: 0.0.1
#     LastChange: 2017-10-20 14:02:48
#        History:
#  ============================================================================
'''

from jinja2 import Template
from fabric.api import settings, env, task, execute, settings
from fabric.network import disconnect_all
import time
import redis
import requests
import json

from utils.fab_cmd import sudo_and_chk, sudo_and_rechk, get_code_info
from utils.setting import GlobalVar as gvar
from utils.setting import DefaultScripts as scripts


@task
def deploy_codis_instance(redis_host_list, dashboard_host,
                          dashboard_port, dashboard_host_str, proxy_host_str,
                          proxy_port_list, proxy_seq,
                          sync_host_str, sync_port_pair,
                          sync_local_zk_servers, sync_remote_zk_servers,
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

        ret = execute(deploy_sync,
                      hosts=sync_host_str,
                      port_pair=sync_port_pair,
                      product_name=product_name,
                      dashboard_addr=dashboard_addr,
                      sync_local_zk_servers=sync_local_zk_servers,
                      sync_remote_zk_servers=sync_remote_zk_servers)
        for _, each_ret in ret.items():
            if not each_ret:
                return 315

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

        ret = execute(startup_sync,
                      hosts=sync_host_str,
                      port_pair=sync_port_pair)
        for _, each_ret in ret.items():
            if not each_ret:
                return 316
    disconnect_all()
    return 1


@task
def deploy_fe_instance(fe_host_str, fe_port, zk_servers):
    ret = execute(deploy_fe_supervise,
                  hosts=fe_host_str,
                  fe_port=fe_port,
                  zk_servers=zk_servers)
    for _, each_ret in ret.items():
        if not each_ret:
            return 312

    ret = execute(startup_fe,
                  hosts=fe_host_str,
                  fe_port=fe_port)
    for _, each_ret in ret.items():
        if not each_ret:
            return 313


def deploy_dashboard(zk_servers, dashboard_port, product_name):
    err_flg = [0]

    with settings(warn_only=True):
        config_path = "%s/dashboard/%s" % (gvar.CODIS_CONF_DIR,
                                           gvar.DASHBOARD_CFG_NAME)
        dashboard_cfg = scripts.dashboard_cfg % (zk_servers, product_name,
                                                 env.host, dashboard_port)
        create_cfg_cmd = '''cat << EOF > %s
%s
EOF''' % (config_path, dashboard_cfg)
        log_str = '[%s] Create dashbaord cfg `%s`' % (env.host, config_path)
        sudo_and_chk(create_cfg_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        dashboard_supervise_path = '%s/%s' % (gvar.SUPERVISE_DIR,
                                              gvar.DASHBOARD_NAME)
        mkdir_cmd = 'mkdir -p %s' % dashboard_supervise_path
        log_str = '[%s] Mkdir `%s`' % (env.host, dashboard_supervise_path)
        sudo_and_chk(mkdir_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        dashboard_supervise = scripts.dashboard_supervise.format(
            product_name=product_name)
        run_script_path = '%s/run' % dashboard_supervise_path
        create_run_script = '''cat << EOF > %s
%s
EOF''' % (run_script_path, dashboard_supervise)
        log_str = '[%s] Create dashboard supervise run script' % env.host
        sudo_and_chk(create_run_script, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        chown_cmd = 'chown -R web.web %s' % dashboard_supervise_path
        log_str = '[%s] Chown dashboard supervise' % env.host
        sudo_and_chk(chown_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        chmod_cmd = 'chmod +x %s' % run_script_path
        log_str = '[%s] Chmod dashboard supervise run script `%s`' %\
            (env.host, run_script_path)
        sudo_and_chk(chmod_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0
    return 1


def deploy_proxy(port_list, product_name, dashboard_addr, permission, seq=0):
    """
    port_list:
      syntax: [(proxy_port, admin_port), ...]
      example: [(19000, 21000), (19100, 21100)]

    seq:
      action: The start suffix of Supervise dir.
    """
    err_flg = [0]

    with settings(warn_only=True):
        proxy_cfg = Template(scripts.proxy_cfg).render(\
            product_name=product_name, permission=permission)

        config_path = "%s/proxy/%s" % (gvar.CODIS_CONF_DIR,
                                       gvar.PROXY_CFG_NAME)
        create_cfg_cmd = '''cat << EOF > %s
%s
EOF''' % (config_path, proxy_cfg)
        log_str = '[%s] Create proxy cfg `%s`' % (env.host, config_path)
        sudo_and_chk(create_cfg_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        num = len(port_list)
        for idx, suffix  in enumerate(range(seq, seq+num)):
            proxy_name = gvar.PROXY_NAME.format(suffix=suffix)
            proxy_supervise_path = '%s/%s' % (gvar.SUPERVISE_DIR,
                                              proxy_name)
            proxy_supervise = scripts.proxy_supervise.format(
                product_name=product_name, dashboard_addr=dashboard_addr,
                host=env.host, proxy_port=port_list[idx][0],
                admin_port=port_list[idx][1], suffix=suffix)
            run_script_path = '%s/run' % proxy_supervise_path

            mkdir_cmd = 'mkdir -p %s' % proxy_supervise_path
            log_str = '[%s] Mkdir `%s`' % (env.host, proxy_supervise_path)
            sudo_and_chk(mkdir_cmd, log_str, err_flg, get_code_info())
            if err_flg[0]:
                return 0

            create_run_script = '''cat << EOF > %s
%s
EOF''' % (run_script_path, proxy_supervise)
            log_str = '[%s] Create proxy supervise run script' % env.host
            sudo_and_chk(create_run_script, log_str, err_flg, get_code_info())
            if err_flg[0]:
                return 0

            chown_cmd = 'chown -R web.web %s' % proxy_supervise_path
            log_str = '[%s] Chown proxy supervise' % env.host
            sudo_and_chk(chown_cmd, log_str, err_flg, get_code_info())
            if err_flg[0]:
                return 0

            chmod_cmd = 'chmod +x %s' % run_script_path
            log_str = '[%s] Chmod proxy supervise run script `%s`' %\
                (env.host, run_script_path)
            sudo_and_chk(chmod_cmd, log_str, err_flg, get_code_info())
            if err_flg[0]:
                return 0
    return 1


def deploy_sync(port_pair, product_name, dashboard_addr, sync_local_zk_servers, sync_remote_zk_servers):
    err_flg = [0]

    with settings(warn_only=True):
        sync_cfg = Template(scripts.sync_cfg).render(\
            sync_local_zk_servers=sync_local_zk_servers,
            sync_remote_zk_servers=sync_remote_zk_servers,
            product_name=product_name)

        config_path = "%s/sync/%s" % (gvar.CODIS_CONF_DIR,
                                       gvar.SYNC_CFG_NAME)
        create_cfg_cmd = '''cat << EOF > %s
%s
EOF''' % (config_path, sync_cfg)
        log_str = '[%s] Create sync cfg `%s`' % (env.host, config_path)
        sudo_and_chk(create_cfg_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        sync_supervise_path = '%s/%s' % (gvar.SUPERVISE_DIR,
                                          gvar.SYNC_NAME)
        sync_supervise = scripts.sync_supervise.format(
            product_name=product_name, dashboard_addr=dashboard_addr,
            host=env.host, proxy_port=port_pair[0], admin_port=port_pair[1])
        run_script_path = '%s/run' % sync_supervise_path

        mkdir_cmd = 'mkdir -p %s' % sync_supervise_path
        log_str = '[%s] Mkdir `%s`' % (env.host, sync_supervise_path)
        sudo_and_chk(mkdir_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        create_run_script = '''cat << EOF > %s
%s
EOF''' % (run_script_path, sync_supervise)
        log_str = '[%s] Create sync supervise run script' % env.host
        sudo_and_chk(create_run_script, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        chown_cmd = 'chown -R web.web %s' % sync_supervise_path
        log_str = '[%s] Chown sync supervise' % env.host
        sudo_and_chk(chown_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        chmod_cmd = 'chmod +x %s' % run_script_path
        log_str = '[%s] Chmod sync supervise run script `%s`' %\
            (env.host, run_script_path)
        sudo_and_chk(chmod_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0
    return 1


def deploy_redis(redis_port, max_mem_size):
    err_flg = [0]

    with settings(warn_only=True):
        for port in redis_port:
            cfg = Template(scripts.redis_cfg).render(port=port,
                                                     max_mem_size=max_mem_size)
            cfg_path = '%s/%s.conf' % (gvar.REDIS_CONF_DIR, port)
            create_cfg_cmd = '''cat << EOF > %s
%s
EOF''' % (cfg_path, cfg)
            log_str = '[%s] Create redis cfg `%s`' % (env.host, cfg_path)
            sudo_and_chk(create_cfg_cmd, log_str, err_flg, get_code_info())
            if err_flg[0]:
                return 0

        chown_cmd = 'chown -R web.web %s' % gvar.REDIS_CONF_DIR
        log_str = '[%s] Chown redis conf' % env.host
        sudo_and_chk(chown_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0
    return 1


def config_redis_backup(redis_port, backup_invl):
    err_flg = [0]

    if backup_invl:
        with settings(warn_only=True):
            chk_script_cmd = '[ -f %s/%s ]' % (gvar.SCRIPT_DIR, gvar.BK_SCRIPT_NAME)
            log_str = '[%s] Check backup scripts' % env.host
            ret = sudo_and_chk(chk_script_cmd, log_str, [0],
                               get_code_info(), info_only=1)
            if not ret:
                get_script_cmd = 'mkdir -p %s && cd %s && wget %s' %\
                    (gvar.SCRIPT_DIR, gvar.SCRIPT_DIR, gvar.BK_SCRIPT_URL)
                log_str = '[%s] Get backup scripts' % env.host
                sudo_and_chk(get_script_cmd, log_str, err_flg, get_code_info())
                if err_flg[0]:
                    return 0

            for each_port in redis_port:
                chk_crontab_cmd = 'less /var/spool/cron/web |\
egrep -w "%s" |egrep -w "%s"' % (each_port, gvar.BK_SCRIPT_NAME)
                log_str = '[%s] Check crontab file whether exists entry `%d`' %\
                    (env.host, each_port)
                ret = sudo_and_chk(chk_crontab_cmd, log_str, [0],
                                   get_code_info(), info_only=1)
                if not ret:
                    add_crontab_cmd = 'echo "1 */%d * * * sh \
%s/%s %d > /dev/null 2>&1" >> /var/spool/cron/web' %\
                        (backup_invl, gvar.SCRIPT_DIR, gvar.BK_SCRIPT_NAME, each_port)
                    log_str = '[%s] Add [%d] crontab' % (env.host, each_port)
                    sudo_and_chk(add_crontab_cmd, log_str, err_flg,
                                 get_code_info())
                    if err_flg[0]:
                        return 0

            chown_cmd = 'chown web.web /var/spool/cron/web;chmod 644 /var/spool/cron/web'
            log_str = "[%s] Change crontab file's owner and mode " % env.host
            sudo_and_chk(chown_cmd, log_str, err_flg, get_code_info())

            chmod_cmd = 'chmod +x %s/%s' % (gvar.SCRIPT_DIR, gvar.BK_SCRIPT_NAME)
            log_str = '[%s] Chmod backup script' % env.host
            sudo_and_chk(chmod_cmd, log_str, err_flg, get_code_info())
            if err_flg[0]:
                return 0
    return 1


def startup_dashboard(dashboard_port):
    err_flg = [0]

    with settings(warn_only=True):
        dashboard_supervise_path = '%s/%s' % (gvar.SUPERVISE_DIR,
                                              gvar.DASHBOARD_NAME)
        startup_cmd = 'su - web -c \"%s %s &\"' % (gvar.SUPERVISE_CMD,
                                                   dashboard_supervise_path)
        log_str = '[%s] Startup dashboard' % env.host
        sudo_and_chk(startup_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        dashboard_url = '%s:%s/topom' % (env.host, dashboard_port)
        chk_dashboard_status_cmd =\
            'curl -s -w %%{http_code} -o /dev/null %s' % dashboard_url
        log_str = '[%s] Try get dashboard status' % env.host
        sudo_and_rechk(chk_dashboard_status_cmd, log_str,
                       err_flg, get_code_info(), 1, '200')
        if err_flg[0]:
            return 0
    return 1


def startup_redis(redis_port):
    err_flg = [0]

    for port in redis_port:
        for i in range(3):
            start_cmd = 'su - web -c "numactl --interleave=all %s/codis-server %s/%d.conf"' %\
                (gvar.CODIS_BIN_DIR, gvar.REDIS_CONF_DIR, port)
            log_str = '[%s] Redis %d startup startup command execute' %\
                (env.host, port)
            sudo_and_chk(start_cmd, log_str, err_flg, get_code_info())
            if err_flg[0]:
                return 0

            r = redis.Redis(host=env.host, port=port, db=0)

            time.sleep(1)

            success_flg = 0
            for j in range(3):
                try:
                    f_name, f_lineno = get_code_info()
                    f_lineno += 2
                    ret = r.ping()
                    if ret:
                        success_flg = 1
                        log_str = "%s:[line:%d] [%s] Redis `%d` startup succeed." %\
                            (f_name, f_lineno, env.host, port)
                    gvar.LOGGER.info(log_str)
                    break
                except Exception as e:
                    f_name, f_lineno = get_code_info()
                    f_lineno -= 9
                    gvar.LOGGER.warning("%s:[line:%d] [%s] %s" %
                                        (f_name, f_lineno, env.host, e))
                    if j < 2:
                        time.sleep(2)
            if success_flg:
                break

        if not success_flg:
            gvar.LOGGER.warning("%s:[line:%d] [%s:%d] Redis startup failed." %
                                (f_name, f_lineno, env.host, port))
            return 0
    return 1


def add_groups(dashboard_port, group_num, start_group=1):
    err_flg = [0]

    with settings(warn_only=True):
        codis_admin_cmd = '%s/codis-admin' % gvar.CODIS_BIN_DIR
        dashboard_addr = '%s:%d' % (env.host, dashboard_port)
        for gid in range(start_group, start_group+group_num):
            create_group_cmd = '%s --dashboard=%s --create-group --gid=%d' %\
                (codis_admin_cmd, dashboard_addr, gid)
            log_str = '[%s] Dashboard create group %d' % (env.host, gid)
            sudo_and_chk(create_group_cmd, log_str, err_flg, get_code_info())
            if err_flg[0]:
                return 0
        if err_flg[0]:
            return 0
    return 1


def add_servers(redis_port, dashboard_port, host_list, start_group=1, interval=0):
    err_flg = [0]

    with settings(warn_only=True):
        codis_admin_cmd = '%s/codis-admin' % gvar.CODIS_BIN_DIR
        dashboard_addr = '%s:%d' % (env.host, dashboard_port)
        group_num = start_group
        for host_group in host_list:
            for port in redis_port:
                for host in host_group:
                    server_addr = '%s:%d' % (host, port)
                    add_server_cmd =\
                        '%s --dashboard=%s --group-add --gid=%d --addr=%s' %\
                        (codis_admin_cmd, dashboard_addr, group_num, server_addr)
                    log_str = '[%s] Dashboard add server `%s`' % (env.host,
                                                                  server_addr)
                    sudo_and_chk(add_server_cmd, log_str, err_flg, get_code_info())
                    if err_flg[0]:
                        return 0
                group_num +=1
            time.sleep(interval)
        if err_flg[0]:
            return 0
    return 1


def rebalance_slots(dashboard_port):
    err_flg = [0]

    with settings(warn_only=True):
        codis_admin_cmd = '%s/codis-admin' % gvar.CODIS_BIN_DIR
        dashboard_addr = '%s:%d' % (env.host, dashboard_port)
        rebalance_cmd = '%s --dashboard=%s --rebalance --confirm' % (
            codis_admin_cmd, dashboard_addr)
        log_str = '[%s] Dashboard rebalance slots' % env.host
        sudo_and_chk(rebalance_cmd, log_str, err_flg, get_code_info())

        if err_flg[0]:
            return 0
    return 1


def startup_proxy(port_list, seq=0):
    """
    port_list:
      syntax: [(proxy_port, admin_port), ...]
      example: [(19000, 21000), (19100, 21100)]

    seq:
      action: The start suffix of Supervise dir.

    """
    err_flg = [0]

    with settings(warn_only=True):
        num = len(port_list)
        for idx, suffix in enumerate(range(seq, seq+num)):
            proxy_name = gvar.PROXY_NAME.format(suffix=suffix)
            proxy_supervise_path = '%s/%s' % (gvar.SUPERVISE_DIR,
                                              proxy_name)

            startup_cmd = 'su - web -c \"%s %s &\"' % (gvar.SUPERVISE_CMD,
                                                       proxy_supervise_path)
            log_str = '[%s] Startup proxy' % env.host
            sudo_and_chk(startup_cmd, log_str, err_flg, get_code_info())
            if err_flg[0]:
                return 0

            proxy_url = '%s:%s/proxy' % (env.host, port_list[idx][1])
            chk_proxy_status_cmd =\
                'curl -s -w %%{http_code} -o /dev/null %s' % proxy_url
            log_str = '[%s] Try get proxy status' % env.host
            sudo_and_rechk(chk_proxy_status_cmd, log_str,
                           err_flg, get_code_info(), 1, '200')
            if err_flg[0]:
                return 0
    return 1


def startup_sync(port_pair):
    err_flg = [0]

    with settings(warn_only=True):
        sync_name = gvar.SYNC_NAME
        sync_supervise_path = '%s/%s' % (gvar.SUPERVISE_DIR,
                                         sync_name)

        startup_cmd = 'su - web -c \"%s %s &\"' % (gvar.SUPERVISE_CMD,
                                                   sync_supervise_path)
        log_str = '[%s] Startup sync' % env.host
        sudo_and_chk(startup_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        sync_url = '%s:%s/proxy' % (env.host, port_pair[1])
        chk_sync_status_cmd =\
            'curl -s -w %%{http_code} -o /dev/null %s' % sync_url
        log_str = '[%s] Try get sync status' % env.host
        sudo_and_rechk(chk_sync_status_cmd, log_str,
                       err_flg, get_code_info(), 1, '200')
        if err_flg[0]:
            return 0
    return 1


def deploy_fe_supervise(fe_port, zk_servers):
    err_flg = [0]

    with settings(warn_only=True):
        fe_supervise_path = '%s/codis_fe' % gvar.SUPERVISE_DIR
        mkdir_cmd = 'mkdir -p %s' % fe_supervise_path
        log_str = '%s] Mkdir `%s`' % (env.host, fe_supervise_path)
        sudo_and_chk(mkdir_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        fe_supervise = scripts.fe_supervise.format(zk_servers=zk_servers,
                                                   fe_port=fe_port)
        run_script_path = '%s/run' % fe_supervise_path
        create_run_script = '''cat << EOF > %s
%s
EOF''' % (run_script_path, fe_supervise)
        log_str = '[%s] Create fe supervise run script' % env.host
        sudo_and_chk(create_run_script, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        chown_cmd = 'chown -R web.web %s' % fe_supervise_path
        log_str = '[%s] Chown fesupervise' % env.host
        sudo_and_chk(chown_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        chmod_cmd = 'chmod +x %s' % run_script_path
        log_str = '[%s] Chmod fe supervise run script `%s`' %\
            (env.host, run_script_path)
        sudo_and_chk(chmod_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0
    return 1


def startup_fe(fe_port):
    err_flg = [0]

    with settings(warn_only=True):
        fe_supervise_path = '%s/codis_fe' % gvar.SUPERVISE_DIR
        startup_cmd = 'su - web -c \"%s %s &\"' % (gvar.SUPERVISE_CMD,
                                                   fe_supervise_path)
        log_str = '[%s] Startup fe' % env.host
        sudo_and_chk(startup_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        fe_url = '%s:%s' % (env.host, fe_port)
        chk_fe_status_cmd =\
            'curl -s -w %%{http_code} -o /dev/null %s' % fe_url
        log_str = '[%s] Try get fe status' % env.host
        sudo_and_rechk(chk_fe_status_cmd, log_str,
                       err_flg, get_code_info(), 1, '200')
        if err_flg[0]:
            return 0

    return 1

#written by liyouwei (sentinel deploy)
def setup_redis_replication(dashboard_port):
    err_flg = [0]
    with settings(warn_only=True):
        dashboard_addr = '%s:%d' % (env.host, dashboard_port)
        dashboard_url = "http://%s/topom" % dashboard_addr
        chk_dashboard_status_cmd = 'curl -s -w %%{http_code} -o /dev/null %s' % dashboard_url
        log_str = '[%s] Try get dashboard status' % env.host
        sudo_and_rechk(chk_dashboard_status_cmd, log_str,
                       err_flg, get_code_info(), 1, '200')
        if err_flg[0]:
            return 0
        response = requests.get(dashboard_url)
        data = response.text
        datas = json.loads(data)
        models = datas['stats']['group']['models']

        for model in models:
            servers = model['servers']
            for i, server in enumerate(servers):
                if i == 0:
                    master_ip = server['server'].split(":")[0]
                    master_port = server['server'].split(":")[1]
                else:
                    slave_ip = server['server'].split(":")[0]
                    slave_port = int(server['server'].split(":")[1])
                    r = redis.Redis(host=slave_ip, port=slave_port)
                    # 最多尝试三次,一次成功退出
                    success_flg = 0
                    for j in range(3):
                        try:
                            f_name, f_lineno = get_code_info()
                            f_lineno += 2
                            ret = r.slaveof(master_ip, master_port)
                            if ret:
                                success_flg = 1
                                log_str = "%s:[line:%d] [%s] Redis %s Slaveof execute succeed." % \
                                          (f_name, f_lineno, slave_ip, slave_port)
                                gvar.LOGGER.info(log_str)
                                break
                        except Exception as e:
                            f_name, f_lineno = get_code_info()
                            f_lineno -= 9
                            gvar.LOGGER.warning("%s:[line:%d] [%s] %s" % \
                                                (f_name, f_lineno, slave_server, e))
                    if success_flg:
                        break
                    # else:
                    #     gvar.LOGGER.error("%s:[line:%d] [%s] %s" %
                    #                       (f_name, f_lineno, env.host, e))

                    if not success_flg:
                        gvar.LOGGER.warning("%s:[line:%d] [%s:%d] Slaveof execute failed." % \
                                            (f_name, f_lineno, slave_ip, slave_port))
                        return 0
    return 1


def deploy_sentinel(sentinel_port):
    err_flg = [0]

    with settings(warn_only=True):
        cfg = Template(scripts.sentinel_cfg).render(port=sentinel_port)
        cfg_path = '%s/sentinel-%s.conf' % (gvar.SENTINEL_CONF_DIR, sentinel_port)
        create_cfg_cmd = '''cat << EOF > %s
%s
EOF''' % (cfg_path, cfg)
        log_str = '[%s] Create sentinel cfg `%s`' % (env.host, cfg_path)
        sudo_and_chk(create_cfg_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0

        chown_cmd = 'chown -R web.web %s' % gvar.SENTINEL_CONF_DIR
        log_str = '[%s] Chown sentinel conf' % env.host
        sudo_and_chk(chown_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0
    return 1

def startup_sentinel(sentinel_port):
    err_flg = [0]

    for i in range(3):
        start_cmd = 'su - web -c "%s/codis-server %s/sentinel-%d.conf --sentinel"' % \
                    (gvar.CODIS_BIN_DIR, gvar.REDIS_CONF_DIR, sentinel_port)
        log_str = '[%s] Sentinel %d  startup command execute' % \
                  (env.host, sentinel_port)
        sudo_and_chk(start_cmd, log_str, err_flg, get_code_info())

        time.sleep(2)
        if err_flg[0]:
            return 0

        r = redis.Redis(host=env.host, port=sentinel_port)
        success_flg = 0
        for j in range(3):
            try:
                f_name, f_lineno = get_code_info()
                f_lineno += 2
                ret = r.ping()
                if ret:
                    success_flg = 1
                    log_str = "%s:[line:%d] [%s] Sentinel `%d` startup succeed." % \
                              (f_name, f_lineno, env.host, sentinel_port)
                    gvar.LOGGER.info(log_str)           # written by liyouwei
                    break                               # written by liyouwei
            except Exception as e:
                f_name, f_lineno = get_code_info()
                f_lineno -= 9
                gvar.LOGGER.warning("%s:[line:%d] [%s] %s" %
                                    (f_name, f_lineno, env.host, e))
        if success_flg:
            break
        # else:
        #     gvar.LOGGER.error("%s:[line:%d] [%s] %s" %
        #                       (f_name, f_lineno, env.host, e))

        if not success_flg:
            gvar.LOGGER.warning("%s:[line:%d] [%s:%d] Sentinel try startup failed %d." %
                            (f_name, f_lineno, env.host, sentinel_port, i))
            return 0
    return 1


def add_sentinel(sentinel_port,dashboard_port,host_list):
    err_flg = [0]

    with settings(warn_only=True):
        codis_admin_cmd = '%s/codis-admin' % gvar.CODIS_BIN_DIR
        dashboard_addr = '%s:%d' % (env.host, dashboard_port)
        for host in host_list:
            server_addr = '%s:%d' % (host, sentinel_port)
            add_sentinel_cmd =\
                '%s --dashboard=%s --sentinel-add --addr=%s' \
                %(codis_admin_cmd, dashboard_addr, server_addr)
            log_str = '[%s] Dashboard add sentinel `%s`' % (env.host,server_addr)
            sudo_and_chk(add_sentinel_cmd, log_str, err_flg, get_code_info())
            if err_flg[0]:
                return 0
        if err_flg[0]:
            return 0
    return 1


def resync_sentinel(dashboard_port):
    err_flg = [0]

    with settings(warn_only=True):
        codis_admin_cmd = '%s/codis-admin' % gvar.CODIS_BIN_DIR
        dashboard_addr = '%s:%d' % (env.host, dashboard_port)
        resync_sentinel_cmd =\
            '%s --dashboard=%s --sentinel-resync' \
            %(codis_admin_cmd, dashboard_addr)
        log_str = '[%s] Dashboard resync sentinel.' % (env.host)
        sudo_and_chk(resync_sentinel_cmd, log_str, err_flg, get_code_info())
        if err_flg[0]:
            return 0
    return 1
#end
