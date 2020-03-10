'''
#  ============================================================================
#       FileName: _exceptions.py
#           Desc:
#       HomePage:
#        Created: 2017-08-31 11:52:17
#        Version: 0.0.1
#     LastChange: 2017-10-20 12:18:00
#        History:
#  ============================================================================
'''


class Deploy_err(Exception):
    err_code = {
    
        101: '102 Error: Redis environment is not clean.',
        102: '103 Error: Dashboard environment is not clean.',
        103: '104 Error: Proxy environment is not clean.',
        104: '105 Error: Zookeeper environment is not clean.',
    
        201: '201 Error: Codis package install failed.',
    
        301: '301 Error: Deploy dashboard failed.',
        302: '302 Error: Deploy proxy failed.',
        303: '303 Error: Deploy watcher failed.',
        304: '304 Error: Deploy redis failed.',
        305: '305 Error: Deploy startup redis script failed.',
        306: '306 Error: Config redis backup failed.',
        307: '307 Error: Startup dashboard failed.',
        308: '308 Error: Startup redis failed.',
        309: '309 Error: Startup watcher failed.',
        310: '308 Error: Config dashboard failed.',
        311: '309 Error: Startup proxy failed.',
        312: '310 Error: Deploy fe supervise failed',
        313: '311 Error: Startup fe failed.'
    }
        self.value = value
    def __str__(self):
        return repr(Deploy_err.err_code[self.value])
