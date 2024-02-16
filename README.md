# 功能
- 获取token
- 发送信息
- 双号互聊
- 钉钉机器人提醒

# 文件结构
```
discord.py
config.py
formatdata.py
utils.py
.gitignore
README.md
data
    discord.csv # discord账号
    ip.csv # 独立ip
    channel_messages.json # 发送内容 单条
    fix_messages.txt # 固定聊天内容
    discord_info.json # 项目的一些discord信息
```
参考结构：
<img width="275" alt="image" src="https://github.com/ChenYCL/discord-send/assets/25706676/d163c9ba-9431-45cd-9815-546555139ecd">



需要补齐的敏感数据文件

- discord.csv
  
关键使用token登陆，如何获取discord token，请自行搜索
你的discord账号.这个discord_token是需要程序获取的,会自动填充进来,可以留空，id必须按照顺序1,2,3,4...
### 小技巧：建议配合指纹浏览器手动获取token，长期使用
<img width="1280" alt="image" src="https://github.com/ChenYCL/discord-send/assets/25706676/73fb0996-caa6-48aa-a092-f3ed6c91190e">


```
discord_id|discord_create_email|discord_password|discord_username|discord_token
1|xxxxx|xxxxx|xxxxx|xxxxx
2|xxxxx|xxxxx|xxxxx|xxxxx
```

- ip.csv

你的独立ip数据
```
proxy_ip:proxy_port:proxy_username:proxy_password
xxxxx:xxxxx:xxxxx:xxxxx
xxxxx:xxxxx:xxxxx:xxxxx
```

- config.py
```
discord_file = './data/discord.csv'
discord_fix_messages_file = './data/fix_messages.txt'
discord_channel_messages_file = './data/channel_messages.json'
discord_info_file = './data/discord_info.json'
ip_file = './data/ip.csv'
use_proxy = False
# 钉钉机器人id
dingding_id = 'xxxxx'
```
- channel_messages.json
```
{
  "babylon": [
    "!faucet 领水地址",
    "!faucet 领水地址",
     // 账号多少个就多少个
  ]
}



```

# 钉钉机器人设置

https://open.dingtalk.com/document/orgapp/custom-robot-access

这个就是一个提醒功能.当别人@你让你回复时需要及时处理.所以加个提醒.

# 指纹浏览器多登，解决ip变更导致token被拦截问题
https://www.bitbrowser.cn/?code=761271 走我链接有优惠
<img width="1347" alt="image" src="https://github.com/ChenYCL/discord-send/assets/25706676/5b81d045-0e0f-4e78-b7ec-e0b960690d6e">

如何使用指纹浏览器，教程： 
Discord使用token一键登录教程
DC使用Token登录视频教程
https://youtu.be/NmTGtlTWseo

教程
1，安装比特浏览器（下载地址www.bitbrowser.cn）

2，在扩展中心安装插件Discord Token Login

3，以上全安装完成后打开登录界面www.discord.com/login打开插件粘贴Token登录

示例账号
ziurkadorzar@outlook.com:GtmKKrrL87:MTA3MTIxMTE2NjI3MTAyNTE4Mg.GAXswI.k0f-By--jCrtS5uAj3kCEBWlfgv3cEr24ZBeAw

格式
邮箱:密码:Token

Discord账号是ziurkadorzar@outlook.com

DC密码是GtmKKrrL87

邮箱账号是ziurkadorzar@outlook.com

邮箱密码是GtmKKrrL87

Token是MTA3MTIxMTE2NjI3MTAyNTE4Mg.GAXswI.k0f-By--jCrtS5uAj3kCEBWlfgv3cEr24ZBeAw

邮箱登录地址是outlook.com
DC密码和邮箱密码相同，也可使用邮箱和密码登录DC，在新的ip登录DC需要登录邮箱验证ip地址

若有收获，就点个赞吧

# 请我喝☕
<img width="200" alt="image" src="https://github.com/ChenYCL/discord-send/assets/25706676/ea44ff39-29c4-4446-88db-6eb5855e50a2">



# 效果
注意先安装python相关依赖
```
python3 discord.py

```
<img width="639" alt="image" src="https://github.com/ChenYCL/discord-send/assets/25706676/5da07061-5051-4a1b-a6a7-3e7e00844cb9">


