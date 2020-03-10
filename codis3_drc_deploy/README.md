# Codis3_deploy
## 功能
自动安装codis3
## 目录结构
```
├── check_env.py                // 检查远端机器是否可以安装codis3
├── deploy_codis_env.py         // 部署codis的环境(如codis的可执行文件等)
├── deploy_codis_instance.py    // 部署codis的实例的相关函数
├── fabfile.py                  // 这是一个汇总的fabfile文件，执行所有fab命令，都要走这个文件，因为去掉了配置文件，导致调用脚本的时候比较困难，这里的call开都的函数都是为了解决调用问题的临时函数，后续集成到自动化平台时，调用格式如call函数中调用各个自动化流程一样。
├── deploy_sepical_scenes.py    // 自动化相关的各个场景的对外调用的函数，未来直接调用这里的函数实现自动化部署
├── conf                        // 配置文件目录
│   └── log.ini                 // 日志的配置文件，在这里修改日志级别等
├── log                         // 日志目录，执行时会在这里生成一个install.log文件
└── utils                       // 相关的一些基础命令目录
    ├── config_handler.py       // 对安装配置文件进行解析，并进行处理。
    ├── _exceptions.py          // 错误码对应的错误，这个是为了merge到cmdb写的
    ├── fab_cmd.py              // 封装了fab的sudo命令，使编写安装更方便简洁
    ├── __init__.py
    └── setting.py              // 全局变量文件，里面设置了一些诸如日志的LOGGER、全局的目录结构、脚本
```

## 具体函数说明
`chk_and_deploy_codis_cluster`  // 检查安装环境，并部署codis软件(如果需要)，并部署codis实例
`deploy_fe`                     // 部署codis软件(如果需要)，并部署codis实例
`deploy_and_startup_dashboard`  // 仅部署并启动dashboard
`deploy_and_startup_redis`      // 仅部署并启动redis
`deploy_and_startup_proxy`      // 仅部署并启动proxy
`config_special_dashboard`      // 配置指定的codis的group和server

后四步逐步执行可部署一个完整的codis集群，后续如有需求，可以单独写一个初始化就将集群初始化在多个(2个以上)server上。目前可用于扩容和迁移。
