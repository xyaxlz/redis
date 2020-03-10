from fabric.api import settings, env, task, settings, local

from utils.setting import GlobalVar as gvar
from utils.fab_cmd import local_and_chk, get_code_info, local_and_get_result
from utils._exceptions import Deploy_err

@task
    err_flg = [0]

    with settings(warn_only=True):
        for broker in m5_brokers:
                broker, product_name)
            log_str = 'Init topic with `%s`' % broker
            if err_flg[0]:
                continue
            break
        if err_flg[0]:
            raise Deploy_err(100)

        for broker in lugu_brokers:
                broker, product_name)
            log_str = 'Init topic with `%s`' % broker
            if err_flg[0]:
                continue
            break
        if err_flg[0]:
            raise Deploy_err(100)

@task
def consumer_chk(m5_brokers, lugu_brokers, m5_sync_hosts, lugu_sync_hosts, product_name):
    err_flg = [0]

    with settings(warn_only=True):
        for broker in m5_brokers:
            log_str = 'Get consumer info from %s`' % broker
            if err_flg[0]:
                continue
            for each in ret.split('\n'):
                partition, consumer =  each.split('\t')
                assert consumer in lugu_sync_hosts, "%s not in lugu sync hosts."
            break
        if err_flg[0]:
            raise Deploy_err(100)
        for broker in lugu_brokers:
            log_str = 'Get consumer info from %s`' % broker
            if err_flg[0]:
                continue
            for each in ret.split('\n'):
                partition, consumer =  each.split('\t')
                assert consumer in m5_sync_hosts, "%s not in m5 sync hosts."
            break
        if err_flg[0]:
            raise Deploy_err(100)
