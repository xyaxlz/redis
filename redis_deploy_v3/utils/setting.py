'''
#  ============================================================================
#       FileName: setting.py
#           Desc:
#       HomePage:
#        Created: 2017-09-12 14:54:12
#        Version: 0.0.1
#     LastChange: 2017-09-12 15:34:20
#        History:
#  ============================================================================
'''
import logging
import logging.config


class GlobalVar:

    REDIS_DIR = "/data/server/redis"
    REDIS_SRC_DIR = "%s/src" % REDIS_DIR
    REDIS_BIN_DIR = "%s/bin" % REDIS_DIR
    REDIS_CONF_DIR = "%s/etc" % REDIS_DIR
    REDIS_DATA_DIR = "%s/data" % REDIS_DIR
    REDIS_LOG_DIR = "%s/log" % REDIS_DIR
    REDIS_PID_DIR = "%s/pid" % REDIS_DIR
    REDIS_CMD = 'redis-benchmark,redis-check-aof,\
redis-cli,redis-sentinel,redis-server'
    REDIS_CFG_NAME = "redis-%d.conf"

    SCRIPT_DIR = "/data/scripts"

    @staticmethod
    def set_logger():
        logging.config.fileConfig("conf/log.ini")
        logging.getLogger("paramiko").setLevel(logging.WARNING)
        GlobalVar.LOGGER = logging.getLogger("root")


class Cfg:
    #protected-mode no
    #bind 127.0.0.1
    redis_cfg = '''daemonize yes
pidfile "/data/server/redis/pid/redis-{{port}}.pid"
port {{port}}
timeout 216000
tcp-keepalive 0
loglevel notice
logfile "/data/server/redis/log/redis-{{port}}.log"
databases 16
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename "redis-{{port}}-dump.rdb"
appendfilename "redis-{{port}}.aof"
dir "/data/server/redis/data"
slave-serve-stale-data yes
slave-read-only no
repl-disable-tcp-nodelay no
slave-priority 100
{% if aof -%}
appendonly yes
appendfsync everysec
{% if aof_rewrite -%}
auto-aof-rewrite-percentage 100
{% else -%}
auto-aof-rewrite-percentage 0
{% endif -%}
{% else -%}
appendonly no
{% endif -%}
no-appendfsync-on-rewrite yes
auto-aof-rewrite-min-size 64mb
lua-time-limit 5000
slowlog-log-slower-than 10000
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
{% endif -%}'''
