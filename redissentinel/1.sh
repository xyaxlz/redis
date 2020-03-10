
chown web.web -R /data/www
chown web.web /data/logs -R

su - web -c  "cd /data/install/redisproxy; sh start_m5.sh   8888 18888 arch.testSentinel_redis.tcp"
