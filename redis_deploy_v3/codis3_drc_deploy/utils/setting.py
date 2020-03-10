'''
#  ============================================================================
#       FileName: setting.py
#           Desc:
#       HomePage:
#        Created: 2017-08-22 15:54:57
#        Version: 0.0.1
#     LastChange: 2018-01-16 10:12:53
#        History:
#  ============================================================================
'''
import logging
import logging.config


class GlobalVar:

    CODIS_DIR = "/data/server/codis3_drc"
    CODIS_CONF_DIR = "%s/config" % CODIS_DIR
    CODIS_SCRIPTS_DIR = "%s/scripts" % CODIS_DIR
    CODIS_BIN_DIR = "%s/bin" % CODIS_DIR
    CODIS_LOG_DIR = "%s/log" % CODIS_DIR
    CODIS_TMP_DIR = "%s/tmp" % CODIS_DIR

    REDIS_DIR = "%s/redis" % CODIS_DIR
    REDIS_CONF_DIR = "%s/conf" % REDIS_DIR
    REDIS_DATA_DIR = "%s/data" % REDIS_DIR
    REDIS_LOG_DIR = "%s/log" % REDIS_DIR
    REDIS_TMP_DIR = "%s/tmp" % REDIS_DIR

    SCRIPT_DIR = "/data/scripts"

    SUPERVISE_DIR = "%s/supervise" % SCRIPT_DIR
    SUPERVISE_CMD = "/usr/bin/supervise"

    DASHBOARD_NAME = "%s_dashboard"
    PROXY_NAME = "%s_proxy_{suffix}"
    SYNC_NAME = "%s_sync"
    WATCHER_NAME = "%s_watcher"

    PROXY_CFG_NAME = "%s_proxy.toml"
    SYNC_CFG_NAME = "%s_sync.toml"

    CODIS_PKG_NAME = "codis3_drc.tar.bz2"
    BK_SCRIPT_NAME = "codis3_drc_backup.sh"

    CENTOS6_URL = "%s/codis/codis3/ncodis/centos6/{pkg_name}".format(pkg_name=CODIS_PKG_NAME)
    CENTOS7_URL = "%s/codis/codis3/ncodis/centos7/{pkg_name}".format(pkg_name=CODIS_PKG_NAME)
    BK_SCRIPT_URL = "%s/codis/codis3/{script_name}".format(script_name=BK_SCRIPT_NAME)

    # written by liyouwei
    SENTINEL_DIR = REDIS_DIR
    SENTINEL_CONF_DIR = REDIS_CONF_DIR

    # end

    @staticmethod
    def set_logger():
        logging.config.fileConfig("conf/log.ini")
        logging.getLogger("paramiko").setLevel(logging.WARNING)
        GlobalVar.LOGGER = logging.getLogger("root")

    @staticmethod
    def set_names(product_name):
        GlobalVar.DASHBOARD_NAME = GlobalVar.DASHBOARD_NAME % product_name
        GlobalVar.PROXY_NAME = GlobalVar.PROXY_NAME % product_name
        GlobalVar.SYNC_NAME = GlobalVar.SYNC_NAME % product_name
        GlobalVar.WATCHER_NAME = GlobalVar.WATCHER_NAME % product_name

        GlobalVar.DASHBOARD_CFG_NAME = "%s.toml" % GlobalVar.DASHBOARD_NAME
        GlobalVar.PROXY_CFG_NAME = GlobalVar.PROXY_CFG_NAME % product_name
        GlobalVar.SYNC_CFG_NAME = GlobalVar.SYNC_CFG_NAME % product_name
        GlobalVar.WATCHER_CFG_NAME = "%s.toml" % GlobalVar.WATCHER_NAME

    @staticmethod
    def set_urls(repo_url):
        GlobalVar.CENTOS6_URL = GlobalVar.CENTOS6_URL % repo_url
        GlobalVar.CENTOS7_URL = GlobalVar.CENTOS7_URL % repo_url
        GlobalVar.BK_SCRIPT_URL = GlobalVar.BK_SCRIPT_URL % repo_url

class DefaultScripts:
    redis_cfg = '''protected-mode no
daemonize yes
pidfile "/data/server/codis3_drc/redis/tmp/{{port}}.pid"
port {{port}}
databases 1
timeout 216000
tcp-keepalive 0
loglevel notice
logfile "/data/server/codis3_drc/redis/log/redis-{{port}}.log"
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename "redis-{{port}}-dump.rdb"
dir "/data/server/codis3_drc/redis/data"
slave-serve-stale-data yes
slave-read-only yes
repl-disable-tcp-nodelay no
slave-priority 100
appendonly no
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
lua-time-limit 5000
slowlog-log-slower-than 20000
slowlog-max-len 128
notify-keyspace-events ""
hash-max-ziplist-entries 512
hash-max-ziplist-value 256
list-max-ziplist-entries 512
list-max-ziplist-value 64
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
activerehashing yes
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit slave 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60
hz 10
aof-rewrite-incremental-fsync yes
repl-backlog-size 20mb
{% if max_mem_size -%}
maxmemory {{max_mem_size}}gb
maxmemory-policy allkeys-lru
{% endif -%}

################################ DQ  ##########################################
#
# DQ is the short write for disk queue.
dq yes

# DQ data file size.
dq-data-file-size 100mb

# Soft and hard limit of dq write buffer. If buffer size is larger than soft limit,
# a warning would be logged and replied to clients. If buffer size is large than
# hard limit, dq writing is not allowed.
dq-write-buf-limit-soft 100mb
dq-write-buf-limit-hard 1gb

# Limit of dq subscribe buffer. Enlarging this buffer can send more data per
# second to subscriber client.
dq-sub-buf-limit 10mb'''

    dashboard_cfg = '''
# Quick Start
coordinator_name = "zookeeper"
coordinator_addr = "%s"

# Set Codis Product Name/Auth.
product_name = "%s"
product_auth = ""

# Set bind address for admin(rpc), tcp only.
admin_addr = "%s:%d"

# Set arguments for data migration (only accept 'sync' & 'semi-async').
migration_method = "semi-async"
migration_parallel_slots = 100
migration_async_maxbulks = 200
migration_async_maxbytes = "32mb"
migration_async_numkeys = 500
migration_timeout = "30s"'''

    proxy_cfg = '''# Set bind address for proxy, proto_type can be "tcp", "tcp4", "tcp6", "unix" or "unixpacket".
proto_type = "tcp4"

# Set Codis Product Name/Auth.
product_name = "{{product_name}}"
product_auth = ""

# Set auth for client session
#   1. product_auth is used for auth validation among codis-dashboard,
#      codis-proxy and codis-server.
#   2. session_auth is different from product_auth, it requires clients
#      to issue AUTH <PASSWORD> before processing any other commands.
session_auth = ""

# Set datacenter of proxy.
proxy_datacenter = ""

# Set max number of alive sessions.
proxy_max_clients = 10000

# Set max offheap memory size. (0 to disable)
proxy_max_offheap_size = "1024mb"

# Set heap placeholder to reduce GC frequency.
proxy_heap_placeholder = "256mb"

# Proxy will ping backend redis (and clear 'MASTERDOWN' state) in a predefined interval. (0 to disable)
backend_ping_period = "5s"

# Set backend recv buffer size & timeout.
backend_recv_bufsize = "128kb"
backend_recv_timeout = "30s"

# Set backend send buffer & timeout.
backend_send_bufsize = "128kb"
backend_send_timeout = "30s"

# Set backend pipeline buffer size.
backend_max_pipeline = 20480

# Set backend never read replica groups, default is false
backend_primary_only = false

# Set backend parallel connections per server
backend_primary_parallel = 1
backend_replica_parallel = 1

# Set backend tcp keepalive period. (0 to disable)
backend_keepalive_period = "75s"

# Set number of databases of backend.
backend_number_databases = 1

# Set max request size
session_max_req_size = "20mb"

# If there is no request from client for a long time, the connection will be closed. (0 to disable)
# Set session recv buffer size & timeout.
session_recv_bufsize = "128kb"
session_recv_timeout = "30m"

# Set session send buffer size & timeout.
session_send_bufsize = "64kb"
session_send_timeout = "30s"

# Make sure this is higher than the max number of requests for each pipeline request, or your client may be blocked.
# Set session pipeline buffer size.
session_max_pipeline = 20000

# Set session tcp keepalive period. (0 to disable)
session_keepalive_period = "75s"

# Set session to be sensitive to failures. Default is false, instead of closing socket, proxy will send an error response to client.
session_break_on_failure = false

# Set session slow log threshold
session_slow_threshold = "20ms"'''

    sync_cfg = '''##################################################
#                                                #
#                   Codis-Sync                   #
#                                                #
##################################################
# Set drc
local_drc_zk = "{{sync_local_zk_servers}}"
remote_drc_zk = "{{sync_remote_zk_servers}}"
dq_max_lag = "10mb"
apply_strategy = "sync"
sync_apply_workers = 30
remote_recv_bufsize = "128kb"
remote_recv_timeout = "30s"
remote_send_bufsize = "128kb"
remote_send_timeout = "30s"
remote_max_pipeline = 20480

##################################################
#                                                #
#                  Codis-Proxy                   #
#                                                #
##################################################

# Set Codis Product Name/Auth.
product_name = "{{product_name}}"
product_auth = ""

# Set auth for client session
#   1. product_auth is used for auth validation among codis-dashboard,
#      codis-proxy and codis-server.
#   2. session_auth is different from product_auth, it requires clients
#      to issue AUTH <PASSWORD> before processing any other commands.
session_auth = ""

# Set jodis address & session timeout
#   1. jodis_name is short for jodis_coordinator_name, only accept "zookeeper" & "etcd".
#   2. jodis_addr is short for jodis_coordinator_addr
#   3. proxy will be registered as node:
#        if jodis_compatible = true (not suggested):
#          /zk/codis/db_{PRODUCT_NAME}/proxy-{HASHID} (compatible with Codis2.0)
#        or else
#          /jodis/{PRODUCT_NAME}/proxy-{HASHID}
jodis_name = ""
jodis_addr = ""
jodis_timeout = "20s"
jodis_compatible = false

# Set datacenter of proxy.
proxy_datacenter = ""

# Set max number of alive sessions.
proxy_max_clients = 1000

# Set max offheap memory size. (0 to disable)
proxy_max_offheap_size = "1024mb"

# Set heap placeholder to reduce GC frequency.
proxy_heap_placeholder = "256mb"

# Set backend wait until write is acknowledged by at least n slaves, default is 0
backend_wait_slaves = 0

# Proxy will ping backend redis (and clear 'MASTERDOWN' state) in a predefined interval. (0 to disable)
backend_ping_period = "5s"

# Set backend recv buffer size & timeout.
backend_recv_bufsize = "128kb"
backend_recv_timeout = "30s"

# Set backend send buffer & timeout.
backend_send_bufsize = "128kb"
backend_send_timeout = "30s"

# Set backend pipeline buffer size.
backend_max_pipeline = 20480

# Set backend never read replica groups, default is false
backend_primary_only = false

# Set backend parallel connections per server
backend_primary_parallel = 1
backend_replica_parallel = 1

# Set backend tcp keepalive period. (0 to disable)
backend_keepalive_period = "75s"

# Set number of databases of backend.
backend_number_databases = 1

# Set max request size
session_max_req_size = "20mb"

# If there is no request from client for a long time, the connection will be closed. (0 to disable)
# Set session recv buffer size & timeout.
session_recv_bufsize = "128kb"
session_recv_timeout = "30m"

# Set session send buffer size & timeout.
session_send_bufsize = "64kb"
session_send_timeout = "30s"

# Make sure this is higher than the max number of requests for each pipeline request, or your client may be blocked.
# Set session pipeline buffer size.
session_max_pipeline = 10000

# Set session tcp keepalive period. (0 to disable)
session_keepalive_period = "75s"

# Set session to be sensitive to failures. Default is false, instead of closing socket, proxy will send an error response to client.
session_break_on_failure = false

# Set session slow log threshold
session_slow_threshold = "20ms"

# Set metrics server (such as http://localhost:28000), proxy will report json formatted metrics to specified server in a predefined period.
metrics_report_server = ""
metrics_report_period = "1s"

# Set influxdb server (such as http://localhost:8086), proxy will report metrics to influxdb.
metrics_report_influxdb_server = ""
metrics_report_influxdb_period = "1s"
metrics_report_influxdb_username = ""
metrics_report_influxdb_password = ""
metrics_report_influxdb_database = ""

# Set statsd server (such as localhost:8125), proxy will report metrics to statsd.
metrics_report_statsd_server = ""
metrics_report_statsd_period = "1s"
metrics_report_statsd_prefix = ""
'''

# written by liyouwei
    sentinel_cfg = '''port {{port}}
daemonize yes
protected-mode no
pidfile "/data/server/codis3_drc/redis/tmp/sentinel-{{port}}.pid"
logfile "/data/server/codis3_drc/redis/log/sentinel-{{port}}.log"
dir "/data/server/codis3_drc/redis/data/"
'''
# end

    dashboard_supervise = '''#!/bin/bash
%s/codis-dashboard --config=%s/dashboard/{product_name}_dashboard.toml --log=%s/{product_name}_dashboard.log --log-level=INFO --pidfile=%s/{product_name}_dashboard.pid >> %s/{product_name}_dashboard.out 2>&1''' % (GlobalVar.CODIS_BIN_DIR, GlobalVar.CODIS_CONF_DIR, GlobalVar.CODIS_LOG_DIR, GlobalVar.CODIS_TMP_DIR, GlobalVar.CODIS_LOG_DIR)

    proxy_supervise = '''#!/bin/bash
%s/codis-proxy --config=%s/proxy/{product_name}_proxy.toml --dashboard={dashboard_addr} --proxy-addr={host}:{proxy_port} --admin-addr={host}:{admin_port} --log=%s/{product_name}_proxy_{suffix}.log --log-level=INFO --ncpu=8 --pidfile=%s/{product_name}_proxy_{suffix}.pid 2>>%s/{product_name}_proxy_{suffix}.out''' % (GlobalVar.CODIS_BIN_DIR, GlobalVar.CODIS_CONF_DIR, GlobalVar.CODIS_LOG_DIR, GlobalVar.CODIS_TMP_DIR, GlobalVar.CODIS_LOG_DIR)

#%s/codis-proxy --config=%s/proxy/{product_name}_proxy.toml --dashboard={dashboard_addr} --proxy_addr={host}:{proxy_port} --admin_addr={host}:{admin_port} --log=%s/{product_name}_proxy_{suffix}.log --log-level=INFO --ncpu=8 --pidfile=%s/{product_name}_proxy_{suffix}.pid > %s/{product_name}_proxy_{suffix}.out 2>&1''' % (GlobalVar.CODIS_BIN_DIR, GlobalVar.CODIS_CONF_DIR, GlobalVar.CODIS_LOG_DIR, GlobalVar.CODIS_TMP_DIR, GlobalVar.CODIS_LOG_DIR)

    sync_supervise = '''#!/bin/bash
%s/codis-sync --config=%s/sync/{product_name}_sync.toml --dashboard={dashboard_addr} --proxy-addr={host}:{proxy_port} --admin-addr={host}:{admin_port} --log=%s/{product_name}_sync.log --log-level=INFO --ncpu=8 --pidfile=%s/{product_name}_sync.pid >> %s/{product_name}_sync.out 2>&1''' % (GlobalVar.CODIS_BIN_DIR, GlobalVar.CODIS_CONF_DIR, GlobalVar.CODIS_LOG_DIR, GlobalVar.CODIS_TMP_DIR, GlobalVar.CODIS_LOG_DIR)

    watcher_supervise = '''#!/bin/bash
%s/codis-watcher --config=%s/watcher/{product_name}_watcher.toml --log=%s/{product_name}_watcher.log --log-level=INFO > %s/{product_name}_watcher.out 2>&1''' % (GlobalVar.CODIS_BIN_DIR, GlobalVar.CODIS_CONF_DIR, GlobalVar.CODIS_LOG_DIR, GlobalVar.CODIS_LOG_DIR)

    fe_supervise = '''#!/bin/bash
%s/codis-fe --assets-dir=%s/assets --zookeeper={zk_servers} --log=%s/codis_fe.log --pidfile=%s/codis-fe.pid --log-level=INFO --listen=0.0.0.0:{fe_port} >> %s/codis-fe.out 2>&1''' % (GlobalVar.CODIS_BIN_DIR, GlobalVar.CODIS_DIR, GlobalVar.CODIS_LOG_DIR, GlobalVar.CODIS_TMP_DIR, GlobalVar.CODIS_LOG_DIR)

