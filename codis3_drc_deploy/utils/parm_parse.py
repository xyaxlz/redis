'''
#  ============================================================================
#       FileName: parm_parse.py
#           Desc:
#       HomePage:
#        Created: 2017-09-25 12:14:56
#        Version: 0.0.1
#     LastChange: 2018-01-16 15:56:19
#        History:
#  ============================================================================
'''

import re

from utils.setting import GlobalVar as gvar


class ParmError(Exception):
        self.value = value
        self.err_code = {
            1: "Missing user or ssh_port parameters.",
            2: "Missing Package parameters.",
            3: "Get wrong parameter. The redis_port's value must be `[start_port, end_port]`,\
start_port must less than end_port.",
            4: "Get wrong paremeter. The redis_port's value must be a list.",
        }
    def __str__(self):
        return repr(self.err_code[self.value])

class ParmParse():
        """
        Args:
            Essential parameters:
                user
                ssh_port
            Non-essential parameters:
                '.*host$'               The parameter with host suffix, be used to defined as different role with prefix.
                proxy_host              The host be defined as a proxy role.
                redis_host_list         The redis_host_list is list with redis group.
                                        Example: [('main1', 'subordinate1'), ('main2', 'subordinate'2),...].
                repo_url                Get packages from this url.
                codis3_package_name     Codis3 package name in repo.
                bk_script_name          Backup script name in repo.
                redis_port              Redis port list, the format is [start_port, end_port].
                                        Example: Redis port list is [6300, 6302], redis port are 6300, 6301 and 6302.

                *                       If parameter is different with above parameters, which will be assignd to self.
        """
        self.kwargs = kwargs

        self.host_parse(**self.kwargs)
        self.pkg_parse(**self.kwargs)
        self.redis_port_parse(**self.kwargs)

        # To handle other parameters.
        for each in self.kwargs:
            setattr(self, each, kwargs[each])

    def host_parse(self, **kwargs):
        """
        To handle host parameters.
        """
        if 'user' in kwargs and 'ssh_port' in kwargs:
            self.user = kwargs['user']
            self.kwargs.pop('user')
            self.ssh_port = kwargs['ssh_port']
            self.kwargs.pop('ssh_port')
        else:
            raise ParmError(1)

        pattern = re.compile(r'.*host$')
        for each in kwargs:
            if pattern.match(each):
                setattr(self, each, kwargs[each])
                setattr(self, '%s_str' % each, '%s@%s:%d' %
                    (self.user, kwargs[each], self.ssh_port))
                self.kwargs.pop(each)
            elif each == 'proxy_hosts':
                self.proxy_host_str = []
                for each_host in kwargs[each]:
                    self.proxy_host_str.append("%s@%s:%d" %\
                        (self.user, each_host, self.ssh_port))
                self.kwargs.pop(each)
# written by liyouwei
            elif each == 'sentinel_hosts':
                self.sentinel_host_str = []
                self.sentinel_hosts = kwargs[each]
                for each_host in kwargs[each]:
                    self.sentinel_host_str.append("%s@%s:%d" % \
                                                  (self.user, each_host, self.ssh_port))
                self.kwargs.pop(each)
#end
            elif each == 'sync_hosts':
                self.sync_host_str = []
                for each_host in kwargs[each]:
                    self.sync_host_str.append("%s@%s:%d" %\
                        (self.user, each_host, self.ssh_port))
                self.kwargs.pop(each)
            elif each == 'redis_host_list':
                self.redis_host_str = []
                self.redis_host_list = kwargs[each]
                # Every host in redis_host_list is a part of redis_host_str.
                for each_group in self.redis_host_list:
                    for each_host in each_group:
                        self.redis_host_str.append('%s@%s:%d' % (self.user, each_host, self.ssh_port))
                self.kwargs.pop(each)

        self.codis_host_str = []
        if 'dashboard_host' in kwargs:
            self.codis_host_str.append(self.dashboard_host_str)

        if 'proxy_hosts' in kwargs:
            self.codis_host_str += self.proxy_host_str[:]

        if hasattr(self, 'redis_host_str'):
            tmp_host_str = self.redis_host_str
            self.codis_host_str += tuple(set(tmp_host_str))

        if hasattr(self, 'sentinel_host_str'):
            tmp_host_str = self.sentinel_host_str
            self.codis_host_str += tuple(set(tmp_host_str))

        self.codis_host_str = tuple(set(self.codis_host_str))

    def pkg_parse(self, **kwargs):
        if 'repo_url' in kwargs:
            self.repo_url = kwargs['repo_url']
            self.kwargs.pop('repo_url')

            #gvar.BK_SCRIPT_URL = gvar.BK_SCRIPT_URL % self.repo_url
            #gvar.CENTOS6_URL = gvar.CENTOS6_URL % self.repo_url
            #gvar.CENTOS7_URL = gvar.CENTOS7_URL % self.repo_url


    def redis_port_parse(self, **kwargs):
        if 'redis_port' in kwargs:
            redis_port = kwargs['redis_port']
            if isinstance(redis_port, list):
                if redis_port[0] > redis_port[1]:
                    raise ParmError(3)
                else:
                    self.redis_port = range(redis_port[0], redis_port[1]+1)
                    self.kwargs.pop('redis_port')
            else:
                raise ParmError(4)
