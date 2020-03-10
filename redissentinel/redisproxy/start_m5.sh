#!/bin/bash

if [ $# -ne 3 ];then
    echo "Uage: $0 redis_proxy_port redis_proxy_http_port redis_namespace"
    echo "Uage: $0 第一个参数redisproxy的端口，第二个参数redisproxy http的端口，第三个参数redis MQ的namespace"
    echo "e.g.: $0 8355 18355 test_namespace"
    exit 1
fi



LOG_PATH=/data/logs/redisproxy
WORK_PATH=/data/www/redisproxy
BIN_PATH=${WORK_PATH}/bin
VERSION=`cat version|awk '{printf "%s",$1}'`

export IDC=m5
export ZK_ADDRS=10.100.21.122:4181,10.100.21.123:4181,10.100.21.124:4181,10.100.21.125:4181,10.100.21.126:4181
export PROXY_PORT=$1
export PROXY_HTTPPORT=$2
export NAMESPACE=$3

function run(){
	init;
	supervisor;
}

function init(){
    if [ ! -d ${LOG_PATH} ]; then
		mkdir -p ${LOG_PATH}
	fi

    if [ ! -d ${WORK_PATH} ]; then
		mkdir -p ${WORK_PATH}
	fi

    if [ ! -d ${BIN_PATH} ]; then
		mkdir -p ${BIN_PATH}
	fi

    new_bin="${BIN_PATH}/redisproxy_${VERSION}"
    old_bin="${BIN_PATH}/redisproxy"

    \cp -f supervisord.conf "${WORK_PATH}/supervisord_${PROXY_PORT}_${VERSION}.conf"
    \cp -f redisproxy ${new_bin}


    if [ ! -f ${old_bin} ]; then
        ln -s "${BIN_PATH}/redisproxy_${VERSION}" ${BIN_PATH}/redisproxy

        if [ $? != 0 ]; then
            echo "升级失败"
            exit 1
        fi

        return 0
    fi

    if [[ -L "$old_bin" && -f "$old_bin" ]]; then
        ln -snf $new_bin $old_bin
        if [ $? != 0 ]; then
            echo "版本替换失败"
            exit 1
        fi
        return 0
    fi

    if [ -f ${old_bin} ]; then
        rm -rf $old_bin
        if [ $? != 0 ]; then
            echo "删除${BIN_PATH}/redisproxy失败"
            exit 1
        fi
        ln -s "${BIN_PATH}/redisproxy_${VERSION}" ${BIN_PATH}/redisproxy
	fi
}

function supervisor(){
	cd  ${WORK_PATH}

    conf_path="${WORK_PATH}/supervisord_${PROXY_PORT}_${VERSION}.conf"
    
    sed -i  "s/IDC/${IDC}/g" $conf_path
    sed -i  "s/ZK_ADDRS/${ZK_ADDRS}/g" $conf_path
    sed -i  "s/PROXY_PORT/${PROXY_PORT}/g" $conf_path
    sed -i  "s/PROXY_HTTPPORT/${PROXY_HTTPPORT}/g" $conf_path
    sed -i  "s/NAMESPACE/${NAMESPACE}/g" $conf_path

	supervisord -c $conf_path
    ps -ef|grep redisproxy|grep ${PROXY_PORT}|grep -v grep|grep -v supervisord
}

run;
