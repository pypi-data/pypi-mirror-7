.. :changelog:

Release History
---------------

0.1.23 (2014-03-21)
++++++++++++++++++

- 添加日志过滤器：RequireInSAE，RequireNotInSAE

0.1.21 (2014-03-20)
++++++++++++++++++

- 删除扩展命令：sae_schemamigration（因为此命令不需要链接SAE数据库）

0.1.18 (2014-03-19)
++++++++++++++++++

- 添加扩展命令：upgrade_requirements

0.1.13 (2014-03-18)
++++++++++++++++++

- 重命名扩展命令： updatepackages -> compress_site_packages，
- 添加扩展命令：sae_migrate, sae_schemamigration, sae_syncdb

0.1.11 (2014-03-17)
++++++++++++++++++

- commands（扩展命令）: updatepackages（更新依赖库并压缩为site-packages.zip）

0.1.1 (2014-03-16)
++++++++++++++++++

- patches: 自动设置
- conf: SAE平台的默认设置

0.1.0 (2014-03-15)
++++++++++++++++++

- db: 通用模型和读写分离
- cache: 缓存模型
- utils: 时间戳模块和装饰模块
- tasks: 用于执行任务