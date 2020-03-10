'''
#  ============================================================================
#       FileName: parm_parse.py
#           Desc:
#       HomePage:
#        Created: 2017-09-19 11:54:35
#        Version: 0.0.1
#     LastChange: 2017-11-13 15:43:33
#        History:
#  ============================================================================
'''


class parm_parse():
        self.user = parm['user']
        parm.pop('user')
        self.ssh_port = int(parm['ssh_port'])
        parm.pop('ssh_port')

        if 'repo_url' in parm.keys():
            self.repo_url = parm['repo_url']
            parm.pop('repo_url')
            self.pkg_urls = {}

            if 'redis_pkg_name' in parm.keys():
                self.redis_pkg_name = parm['redis_pkg_name']
                self.pkg_urls['redis'] = '%s/%s' % (
                    self.repo_url, self.redis_pkg_name)
                self.redis_unpack_dir = self.redis_pkg_name.split('.tar')[0]
                self.redis_ver = self.redis_unpack_dir.split('redis-')[1]
                parm.pop('redis_pkg_name')

            self.pkg_urls['bk_script'] = '%s/backup_redis.sh' % self.repo_url

            redis_scripts = ['redis_master', 'redis_backup', 'redis_fault', 'redis_stop']
            for each in redis_scripts:
                self.pkg_urls[each] = '%s/%s.sh' % (self.repo_url, each)

        for each in parm.keys():
            if 'host' in each:
                exec("self.%s = '%s'" % (each, parm[each]))
                exec("self.%s_str = '%s@%s:%d'" %
                     (each, self.user, parm[each], self.ssh_port))
            else:
                value = parm[each]
                if isinstance(value, int):
                    exec("self.%s = %s" % (each, parm[each]))
                else:
                    exec("self.%s = '%s'" % (each, parm[each]))
