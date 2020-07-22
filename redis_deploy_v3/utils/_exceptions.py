'''
#  ============================================================================
#       FileName: _exceptions.py
#           Desc:
#       HomePage:
#        Created: 2017-09-22 15:42:17
#        Version: 0.0.1
#     LastChange: 2017-09-22 15:50:36
#        History:
#  ============================================================================
'''

err_code = {
    101: '101 Error: Redis version check failed.',
    102: '102 Error: Redis environment is not clean.',
    103: '103 Error: Redis command not exists but dir exists.',
    104: '104 Error: Redis main not exists.',

    201: '201 Error: Redis package install failed.',

    300: '300 Error: Create web user failed.',
    301: '301 Error: Deploy redis configure failed.',
    302: '302 Error: Config redis backup failed.',
    303: '303 Error: Startup redis failed.',
    304: '304 Error: Subordinateof execute failed.',
    305: '305 Error: Orgin main not exists',
    306: '305 Error: Deploy redis ha script failed.'
}

class DeployErr(Exception):
        self.value = err_code[error_code]
    def __str__(self):
        return repr(self.value)
