# Redis deploy
## 功能

1. 部署一套redis主从
2. 指定向一台机器安装redis
3. 部署一个redis的slave节点
4. 部署一套redis主从，并建立同指定的redis复制关系(可用于迁移场景)

## 目录结构
```
├── check_env.py                    // 包含检查redis版本的、检查redis目录是否存在、reids环境的功能
├── deploy_redis_env.py             // 部署reids的软件包 这里写死了安装路径，为/data/server/redis
├── deploy_redis_instance.py        // 包含部署配置文件、配置备份、启动redis、配置slaveof的功能
├── deploy_sepical_scenes.py        // 外部调用自动化的文件，提供了仅向指定机器部署redis软件包、检查并部署一个redis实例的从库、部署一套redis主从的功能、部署一套redis主从并同指定redis复制的功能
├── fabfile.py                      // 就是fabric的一个总的文件，类似于头文件里面把所有对外函数进行了汇总，并在这里设置所有自动化交互时输入的密码和日志初始化的位置
├── log                             // 日志目录，如果执行会在这里生成一个`install.log`的文件，这个与cmdb结合后可能会被删掉，日志由cmdb来处理
├── README.md
├── conf                            // 配置文件目录，目前仅保留了配置日志的配置文件，未来也会被删除掉，由cmdb使用
│   └── log.ini
└── utils                           // 一些相关库
    ├── _exceptions.py              // 错误码文件，用以cmdb报错调用
    ├── fab_cmd.py                  // fab命令的封装
    ├── __init__.py
    ├── parm_parse.py               // 参数解析处理
    └── setting.py                  // 全局变量和默认配置文件
```
