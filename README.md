### 项目介绍
> 英语学习记录

> 使用postgreSQL数据库，redis内存库

> sanic构建异步web服务

### 目录结构

```
├── api_test                # 接口测试
├── conf                    # 配置目录
├── model                   # 数据库配置操作目录
├── sys_manager             # 系统管理模块
├── views                   # 蓝图目录
├── words                   # 单词相关模块
├── model                   # 所有model
├── template                # <前端>html目录
│   ├── account             # <前端>账号相关html
│   └── words               # <前端>单词相关html
├── static                  # <前端>静态文件，包括js和css
│   ├── assets              # <前端>公共静态文件
│   ├── account             # <前端>账号相关静态文件
│   └── words               # <前端>单词相关静态文件
├── english_server          # sanic服务
└── util                    # 工具类，函数目录
```

### 开发流程
> 2018.01.24: 项目初始化

> 2018.02.26: 增加登录和编辑模块
