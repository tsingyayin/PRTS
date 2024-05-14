![](https://img.shields.io/badge/Project-Visindigo-purple)
![](https://img.shields.io/badge/Python-3.8%2B-blue)
![](https://img.shields.io/badge/PySide6-6.5%2B-darkgreen)
![](https://img.shields.io/badge/PySide2-5.15%2B-darkgreen)

PRTS是一个轻量化的，适用于网站后台、应用后台等的权限、角色和令牌管理系统，即Permission-Role-Token System

PRTS使用Python内置的sqlite3模块操作数据库，且使用的SQL语句均为标准语句。因此如有需要，可以直接将PRTS的数据库操作实现向其他数据库迁移。

使用注意事项只有一点：PRTS是单例的，第二次尝试创建PRTS对象时会抛出异常。
# 主要功能

- 角色（用户）管理
  - 基本的注册、登录等功能
  - STMP邮箱绑定
  - 用户昵称设置等
  - 自由配置的其他用户信息
- 权限管理
  - 采用字符串表示的权限系统
  - 权限组和权限继承
  - 带有有效期标识的权限
- 令牌管理
  - 生成和验证令牌
  - 带有有效期标识的令牌
- 产品激活秘钥管理
  - 生成和验证激活秘钥
  - 按秘钥携带的todo信息执行不同的操作
  - 可批量使用的秘钥
  - 带有有效期标识的秘钥
- 定期计划设施
  - 可以用通配符以较为复杂的方式指定计划时间
  - 内置一个每10分钟清理一次数据库的计划`PRTSClearExpiredSchedule`
  - 内置一个作为样例的服务器守护器，每分钟向特定的URL发送一个请求`PRTSServerGuardian`
  - **值得注意的是，定期计划设施内部采用了多线程，因此在使用时需要注意线程安全问题**
  
# ProductKey TODO
PRTS的产品秘钥管理系统可以用于软件的激活，而且为了方便根据不同的秘钥激活不同的产品（反正就是按需执行不同操作），PRTS的秘钥管理系统会在每个秘钥中携带一个TODO信息，其内容是任意字符串，在激活时，可以根据TODO信息执行不同的操作。

例如，您可以使用`PRTS.TempStringManager.generatProductKey()`生成一个秘钥，要调用此函数，需要如下参数：
- todo: str，秘钥携带的TODO信息
- count: int，此秘钥可以被使用的次数
- ttl: int，此秘钥的有效期，单位为秒

然后此函数会返回作为秘钥的字符串。

要验证秘钥，您可以使用`PRTS.TempStringManager.verifyProductKey()`，此函数需要如下参数：
- key: str，要验证的秘钥
- username: str，要验证的用户
  
此函数会返回一个bool值，表示秘钥是否有效，如果有效，此函数会尝试调用TODO解析函数，此函数需要您继承`PRTS.ProductKeyTODOHandler`类，并实现其中的`handle()`方法，此方法需要如下参数：
- key: str，要验证的秘钥
- username: str，激活此秘钥的用户
- todo: str，秘钥携带的TODO信息
- count: int，此秘钥可以被使用的次数
- ttl: int，此秘钥的有效期，单位为秒
- spawn_time: int，此秘钥的生成时间，单位为秒

此函数需要返回一个bool值，表示是否执行成功。

要将TODOHandler连接到PRTS，只需调用`PRTS.ProductKeyManager.setTODOHandler()`即可。

# 辅助调试的功能
当可以使用PySide2或PySide6时，您可以使用PRTS.GUI进行可视化操作。
> 需要注意的是，PRTS.GUI仅用于调试，不应该在生产环境中使用。与此同时，导入PySide2的代码默认被注释掉了，如果您的Python版本不支持Qt6，您应该在`PRTS.GUI._QtGeneral.py`中取消注释PySide2的导入。

# 致谢
此项目的源码从[ECS](http://ecs.yxgeneral.cn)项目中的登录系统源码演变而来，在需求和实现上也参考了部分[C_SAT](https://c-sat.processsafetytool.com/#/login)项目的实现。
（这俩玩意都是我写的，所以我谢谢我自己 XD ）


