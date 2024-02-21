#Buff - Searcher
##鸣谢
* DCZ_666
* 钢铁小麦
* 小鸟游一铭
* Yubadboy
* Youutaku
##使用方法
###1. 设置Session与CSRF Token
* 打开 buff.163.com 
* 打开 开发工具->网络 后登录
* 找到notification一项后点击
* 在响应标头中找到两个Set-Cookie
* 将它们第一个分号前 第一个等于号后的值填入config
* 注意: 如果不勾选十日内免登录 当浏览器关闭后Cookie会自动失效
###2. 使用功能
* 打开程式
* 使用上下箭头选中后键入回车
* 注意: 请务必使用程式内提供的Exit退出 否则你在这次程序的配置是一次性的
* ####启动功能
    * 启动后 底部显示RUNNING
* ####日志功能
    * 使用箭头选择需要查看的日志
    * 键入回车 打开日志
    * 在日志功能内 使用退格键(BACKSPACE)返回上一页
    * 当日志数量达到100 将自动删除所有日志
## 配置文件详解
```json
{
    "sort_by": "Int类型 0到2对应 默认 最近发布 价格递增",
    "max_page": "Int类型 默认值为2 数字越大单次搜寻的范围越大 可能耽误搜寻",
    "cookies": {
        "csrf_token": "cookie内获取",
        "session": "cookie内获取"
    },
    "weapons": [
        {
            "id": "Int类型 武器ID",
            "range": [
                "最小价格",
                "最大价格"
            ],
            "pw_range": [
                "最小磨损",
                "最大磨损"
            ],
            "name": "武器名称"
        }
    ]
}
```
## 所需Python库
* requests
* json
* time
* threading
* os
* msvcrt
* sys
## 关于作者
* Bilibili: YusuiiNe
* Twitter: @HeyYubadboy
