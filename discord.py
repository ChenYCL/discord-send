import os, sys, requests, json, random, time
import pandas as pd
import threading

sys.path.append(os.getcwd())  # 根目录
from data import discord_info_file, discord_file, discord_fix_messages_file, discord_channel_messages_file, use_proxy, \
    dingding_id
from utils import try_except_code, dingding_notice
from formatdata import *


@try_except_code
def get_token(account, password, proxy):
    """获取登录的token"""
    # 关于验证码有点迷，测试结果不统一，有时候需要验证码，但有时候不用验证码反而可以。token也很迷，生成新的token后旧的token还可以用。。。
    # website_url = 'https://discord.com/login'
    # website_key = 'f5561ba9-8f1e-40ca-9b5b-a0b3f719ef34'
    # response = self.verify_website(website_url, website_key, 'hcaptcha')
    # print(response)
    proxies = {"http": proxy, "https": proxy}
    url = "https://discord.com/api/v9/auth/login"
    data = {
        "login": account,
        "password": password,
        # "captcha_key": response
    }
    headers = {
        'Content-Type': 'application/json'
    }
    if use_proxy is False:
        response = requests.post(url, json=data, headers=headers).json()
    else:
        response = requests.post(url, json=data, headers=headers, proxies=proxies).json()
    token = response['token']
    # 将token替换到文件里
    all_discord = pd.read_csv(discord_file, sep='|', engine='python')
    all_discord.loc[all_discord['discord_create_email'] == account, 'discord_token'] = token
    all_discord.to_csv(discord_file, index=False, sep='|')


class DiscordUtil():

    @try_except_code
    def get_message_from_channel(self, token, from_channel_list, proxy, amount=1000):
        """原理从你加入的channel_lis里选一个channel,获取到历史消息保存到文件中备用.
        熊市消息少,可能很久才有一条消息,api一直请求会超出限制。实际这个功能是在牛市刷项目用的

        Attributes:
            token:discord的账号token
            from_channel_list:获取消息的频道列表
            proxy: 代理
            amount: 获取的最大消息数
        return:
            message: 随机获取到的一条消息
        """
        while True:
            with open(discord_channel_messages_file) as f:
                channel_messages = f.read().splitlines()
            if len(channel_messages) >= amount:
                break

            channel_id = random.choice(from_channel_list)
            # before、after、around可获取某个message ID之前、之后、周围的消息
            url = "https://discord.com/api/v9/channels/" + channel_id + "/messages?limit=100"
            headr = {
                "Authorization": str(token),
                "Content-Type": "application/json",
            }
            proxies = {"http": proxy, "https": proxy}
            if use_proxy is False:
                response = requests.get(url=url, headers=headr).json()
            else:
                response = requests.get(url=url, headers=headr, proxies=proxies).json()

            for context in response:
                if ('<') not in context['content']:
                    if ('@') not in context['content']:
                        if ('http') not in context['content']:
                            if ('?') not in context['content']:
                                print(context['content'])
                                # 去重
                                if context['content'] not in channel_messages:
                                    with open(discord_channel_messages_file, "a") as f:
                                        f.write(context['content'] + '\n')

    def get_account_id_with_retry(self, token, proxy, max_retries=5):
        retries = 0
        while retries < max_retries:
            try:
                account_id, account_username = self.get_account_id(token, proxy)
                return account_id, account_username
            except TypeError:
                # 暂停2秒后重试
                time.sleep(2)
                retries += 1
                print(f"Retry {retries}/{max_retries}...")
        print("Max retries exceeded.")
        return None, None

    # @try_except_code
    def send_message(self, token, proxy, message, to_channel, guild_id='', reply_message_id='', reply_account_id='',
                     reply_rate=0.4):
        """发送或者回复聊天
        如何确定发送还是回复。初始肯定是发送，给reply_message_id先赋值空字符串
        回复时如何得到回复id
        如何确定自己的不回复
        如何确定token和proxy的关联性
        Attributes:
            token:discord账户token
            account_username: discord账户名
            proxy: 代理
            message:要发送的消息
            to_channel:发送消息的频道id
            guild_id: 服务器id.可选,默认''.回复消息才用到的参数
            reply_message_id: 要回复的消息id.可选,默认''.回复消息才用到的参数
            reply_account_id: 要回复的消息的账户id.可选,默认''.回复消息才用到的参数
            reply_rate: 回复消息的概率,默认4成
        """
        account_id, account_username = self.get_account_id_with_retry(token, proxy)
        header = {
            "Authorization": str(token),
            "Content-Type": "application/json",
        }
        msg = {
            "content": message,
            "nonce": "82329451214{}33232234".format(random.randrange(0, 1000)),
            "tts": False,
        }
        # 如果有要回复的消息并且消息的发送者不是自己，那么根据回复概率回复消息。回复消息比普通发送消息多一个message_reference参数
        if self.is_reply(reply_rate) and reply_message_id and (account_id != reply_account_id):
            msg['message_reference'] = {
                'channel_id': to_channel,
                'guild_id': guild_id,
                'message_id': reply_message_id
            }
        url = f'https://discord.com/api/v9/channels/{to_channel}/messages'
        proxies = {"http": proxy, "https": proxy}
        if use_proxy is False:
            response = requests.post(url=url, headers=header, json=msg).json()
        else:
            response = requests.post(url=url, headers=header, json=msg, proxies=proxies).json()

        if 'code' in response:
            print(f'信息发送失败: ', response['message'])
            if response['message'] == 'Missing Permissions':
                print('没有权限发送消息')
            if response['message'] == 'This action cannot be performed due to slowmode rate limit':
                print('慢速模式速率限制,稍后重试')
            return False # 跳过去下个账号
        else:
            message_id = response['id']
            print(f'信息发送成功,msg_id:{message_id}')
            return True # 成功去下个账号

    @try_except_code
    def get_account_id(self, token, proxy):
        header = {
            "Authorization": str(token),
            "Content-Type": "application/json",
        }
        url = 'https://discord.com/api/v9/users/@me'
        proxies = {"http": proxy, "https": proxy}
        if use_proxy is False:
            response = requests.get(url=url, headers=header).json()
        else:
            response = requests.get(url=url, headers=header, proxies=proxies).json()
        account_id = response['id']
        account_username = response['username']
        return account_id, account_username

    def is_reply(self, reply_rate=0.4):
        """回复概率。1表示回复消息,0表示发送消息,0.1-0.9表示回复消息的概率
        """
        if reply_rate == 1:
            return True
        elif reply_rate == 0:
            return False
        else:
            return random.randint(0, 9) < reply_rate * 10

    @try_except_code
    def listening(self, token, account_id, account_username, channel_id, proxy, mods, keywords, from_email, to_email):
        """信息监听，及时处理，防止被判定为机器人
        """
        # before、after、around可获取某个message ID之前、之后、周围的消息
        url = "https://discord.com/api/v9/channels/" + channel_id + "/messages?limit=100"
        headr = {
            "Authorization": str(token),
            "Content-Type": "application/json",
        }
        proxies = {"http": proxy, "https": proxy}
        if use_proxy is False:
            response = requests.get(url=url, headers=headr).json()
        else:
            response = requests.get(url=url, headers=headr, proxies=proxies).json()

        # print(response)
        for data in response:
            # print(data)
            # 监听到@全员的信息 或者 监听到@自己的信息 或者 监听到mod发言并且包含关键字，比如停止说话等
            if (data['mention_everyone'] == True) or (account_id in data['content']) or (
                    (data['author']['id'] in mods) and (keyword for keyword in keywords if keyword in data['content'])):
                # 信息发送到邮箱
                content = f"discord账户{account_username}请处理提及自己的信息,避免被判定为机器人\n{data['author']['username']}提及了我\n提及内容:{data['content']}"
                dingding_notice(content)
                return True

    @try_except_code
    def chat(self, account_info, from_channel_list, to_channel, from_email, to_email, guild_id='', reply_rate=0.4,
             interval_time=60, is_channel_message=True, mods=[], keywords=[]):
        """发送聊天

        Attributes:
            account_info:discord账户的token和proxy
            from_channel_list:获取消息的频道列表
            to_channel:发送消息的频道
            guild_id: 服务器id.可选,默认''.回复消息才用到的参数
            reply_rate: 1表示回复消息,0表示发送消息,0.1-0.9表示回复消息的概率。默认0.4,4成概率回复消息
            interval_time: 休眠时间,有些频道会设置慢速模式,隔多久才能说话一次.默认一分钟
            is_channel_message: 控制消息来源。is_channel_message=True时使用从频道中获取到的消息,is_channel_message=False时使用自己准备好的吹水话术
            mods: 管理员列表
            keywords: 关键字列表
        """
        with open(discord_channel_messages_file) as f:
            # splitlines去除换行符
            channel_messages = f.read().splitlines()
        with open(discord_fix_messages_file) as f:
            fix_messages = f.read().splitlines()
        # 先赋值空字符串，避免参数提前引用的错误
        reply_message_id = ''
        reply_account_id = ''
        while True:
            # 获取消息
            if is_channel_message:
                message = random.choice(channel_messages)
            else:
                message = random.choice(fix_messages)
            # 双号互聊，随机选择一个账号。一个账号包括token和proxy
            account_ = random.choice(account_info)
            token = account_['discord_token']
            proxy = account_['proxy']
            # 当前账户的id，通过token获得
            account_id, account_username = self.get_account_id(token, proxy)
            # 监听消息，有跟自己相关的消息先处理，比如别人@你让你回复，否则可能被举报是机器人
            mentioned = self.listening(token, account_id, account_username, to_channel, proxy, mods, keywords,
                                       from_email, to_email)
            if mentioned == True:
                break
            # 发送消息或者回复消息。根据回复概率决定要不要回复消息
            reply_message_id, reply_account_id = self.send_message(token, account_id, proxy, message, to_channel,
                                                                   guild_id, reply_message_id, reply_account_id,
                                                                   reply_rate)
            # 休眠
            time.sleep(random.randrange(interval_time, interval_time + 10))


if __name__ == '__main__':

    data = my_format_data(start_num=1, end_num=25)
    # project babylon
    project_channel = project_info('babylon')

    # # 获取token,自动填充到discord.csv文件
    # for d in data:
    #     get_token(d['discord_create_email'], d['discord_password'], d['proxy'])
    # exit()

    for d in data:
        print(f'第 {d["discord_id"]} 个账户')
        discord = DiscordUtil()
        message = get_discord_messages("babylon", int(d['discord_id']) - 1)
        # print(d['discord_token'], d['proxy'], message, project_channel['to_channel'])
        result = discord.send_message(d['discord_token'], d['proxy'], message, project_channel['to_channel'])
        if not result:  # 假设 send_message 在失败时返回 False
            print(f"处理账号 {d['discord_id']} 时发生错误，跳过此账号")
            continue  # 发生错误时跳过当前账号，继续下一个账号
    exit()

    # # 多线程。多个账号同时聊天。一个线程两个账号
    # # # 将数据2个一组分成若干组
    # data = my_format_data(start_num=1, end_num=4)
    # step = 2
    # group_data = [data[i:i+step] for i in range(0,len(data),step)]

    # guild_id, from_channel_list, to_channel, mods, keywords = project_info('project1')

    # # 用来获取频道历史消息
    # discord = DiscordUtil()
    # # token, from_channel_list, proxy, amount=1000
    # discord.get_message_from_channel(data[0]['discord_token'], from_channel_list, data[0]['proxy'], 300)
    # exit()

    # 双号互聊
    # threads = []
    # for d in group_data:
    #     # print(d)
    #     discord = DiscordUtil()
    #     # account_info, from_channel_list, to_channel, from_email, to_email, guild_id='', reply_rate=0.4（回复消息概率）, interval_time=60（两个消息发送间隔）, is_channel_message=True（控制消息来源，True为频道历史消息，False为自备消息）mods=[], keywords=[]
    #     th = threading.Thread(target=discord.chat,args=(d, from_channel_list, to_channel, from_email, to_email, guild_id, 0.4, 1, True, mods, keywords))
    #     threads.append(th)
    # for th in threads:
    #     th.start()
    #     time.sleep(2)
    # for th in threads:
    #     th.join()
