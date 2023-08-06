#! /usr/bin/env bash
set -eu

# Variables
export OVERC_DB_NAME=${OVERC_DB_NAME:-"overc"}
export OVERC_DB_USER=${OVERC_DB_USER:-"overc"}
export OVERC_DB_PASS=${OVERC_DB_PASS:-"overc"}
export OVERC_DB_HOST=${OVERC_DB_HOST:-"localhost"}
export OVERC_DB_PORT=${OVERC_DB_PORT:-"3306"}
if [ ! -z "$OVERC_DB_LINK" ] ; then
    eval export OVERC_DB_HOST=\$${OVERC_DB_LINK}_TCP_ADDR
    eval export OVERC_DB_PORT=\$${OVERC_DB_LINK}_TCP_PORT
fi

# Logging
#rm -f /var/run/{nginx,php5-fpm,zabbix/zabbix_server}.pid
#LOGFILES=$(echo /var/log/{nginx/error,nginx/http.error,php5-fpm,supervisord,zabbix-server/zabbix_server}.log)
#( umask 0 && truncate -s0 $LOGFILES ) && tail --pid $$ -n0 -F $LOGFILES &

# Launch
export OVERC_CONFIG=/etc/overc/server.ini
export OVERC_DATABASE=mysql://$OVERC_DB_USER:$OVERC_DB_PASS@$OVERC_DB_HOST:$OVERC_DB_PORT/$OVERC_DB_NAME
exec uwsgi /etc/uwsgi/overc.yml
