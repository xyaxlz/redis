'''
#  ============================================================================
#       FileName: fab_cmd.py
#           Desc:
#       HomePage:
#        Created: 2017-08-22 15:21:20
#        Version: 0.0.1
#     LastChange: 2017-09-28 16:52:53
#        History:
#  ============================================================================
'''
from fabric.api import sudo, local
import time
import sys
import os

from utils.setting import GlobalVar as gvar


def get_code_info():
    return (
        os.path.basename(sys._getframe().f_back.f_code.co_filename),
        sys._getframe().f_back.f_lineno)


def sudo_and_chk(cmd, log_str, err_flg, code_info,
                 ret_chk=0, ret_restrict=None, info_only=0):
    ret = sudo(cmd)
    log_str = "%s[line:%d] %s" % (code_info[0], code_info[1], log_str)
    if ret.failed:
        if info_only:
            gvar.LOGGER.info("%s failed." % log_str)
            err_flg[0] = 1
            return 0
        else:
            gvar.LOGGER.error("%s failed!" % log_str)
            err_flg[0] = 1
            return None
    else:
        gvar.LOGGER.info("%s succeed." % log_str)
    if ret_chk:
        if ret == ret_restrict:
            gvar.LOGGER.info("%s return value is right." % log_str)
        else:
            if info_only:
                gvar.LOGGER.info("%s return value is wrong!" % log_str)
                return 0
            else:
                gvar.LOGGER.error("%s return value is wrong!" % log_str)
                err_flg[0] = 1
                return None
    return 1


def sudo_and_rechk(cmd, log_str, err_flg, code_info,
                   ret_chk=0, ret_restrict=None):
    log_str = "%s[line:%d] %s" % (code_info[0], code_info[1], log_str)
    for i in range(3):
        ret = sudo(cmd)
        if ret.failed:
            gvar.LOGGER.warning("%s execute failed!" % log_str)
            time.sleep(5)
            continue
        else:
            gvar.LOGGER.info("%s execute succeed." % log_str)
            if ret_chk:
                if ret == ret_restrict:
                    gvar.LOGGER.info("%s return value is right." % log_str)
                    return None
                else:
                    gvar.LOGGER.warning("%s return value is wrong!" % log_str)
                    time.sleep(5)
                    continue
            return None
    err_flg[0] = 1
    gvar.LOGGER.error("%s failed 3 times!" % log_str)


def sudo_and_get_result(cmd, log_str, err_flg, code_info):
    ret = sudo(cmd)
    log_str = "%s[line:%d] %s" % (code_info[0], code_info[1], log_str)
    if ret.failed:
        gvar.LOGGER.error("%s failed!" % log_str)
        err_flg[0] = 1
        return None
    else:
        gvar.LOGGER.info("%s succeed." % log_str)
        return ret


def local_and_chk(cmd, log_str, err_flg, code_info,
                  ret_chk=0, ret_restrict=None, info_only=0):
    ret = local(cmd, 1)
    log_str = "%s[line:%d] %s" % (code_info[0], code_info[1], log_str)
    if ret.failed:
        if info_only:
            gvar.LOGGER.info("%s failed." % log_str)
            err_flg[0] = 1
            return 0
        else:
            gvar.LOGGER.error("%s failed!" % log_str)
            err_flg[0] = 1
            return None
    else:
        gvar.LOGGER.info("%s succeed." % log_str)
    if ret_chk:
        if ret == ret_restrict:
            gvar.LOGGER.info("%s return value is right." % log_str)
        else:
            if info_only:
                gvar.LOGGER.info("%s return value is wrong!" % log_str)
                return 0
            else:
                gvar.LOGGER.error("%s return value is wrong!" % log_str)
                err_flg[0] = 1
                return None
    return 1


def local_and_get_result(cmd, log_str, err_flg, code_info):
    ret = local(cmd, 1)
    log_str = "%s[line:%d] %s" % (code_info[0], code_info[1], log_str)
    if ret.failed:
        gvar.LOGGER.error("%s failed!" % log_str)
        err_flg[0] = 1
        return None
    else:
        gvar.LOGGER.info("%s succeed." % log_str)
        return ret
