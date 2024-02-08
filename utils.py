"""
常用小功能集锦
"""
import os, sys, traceback, requests, json
sys.path.append(os.getcwd())  # 根目录
from data import dingding_id



def try_except_code(function):
    """处理python的异常,以及requests请求异常。在需要的函数名前面使用装饰器语法@try_except_code调用
    捕获requests异常时,需要在使用地方的响应后面加一句response.raise_for_status()来检查响应的状态码,如果状态码表明请求失败,则抛出一个HTTPError异常,然后就可以用此函数捕获异常。如果状态码表明请求成功,则什么也不会发生,函数会直接返回
    """

    def wrapper(*args, **kwargs):
        try:
            result = function(*args, **kwargs)
        except Exception as e:
            # 获取异常信息
            exc_type, exc_obj, exc_tb = sys.exc_info()
            # 获取文件名和行号
            file_name = traceback.extract_tb(exc_tb)[-1][0]
            line_number = traceback.extract_tb(exc_tb)[-1][1]
            # 输出错误信息
            print("出错文件:", file_name)
            print("出错位置:", line_number, '行')
            print("出错类型:", exc_type.__name__)
            print("错误信息:", str(e))
            result = None
        except requests.exceptions.RequestException:
            # 处理 requests 异常
            exc_type, exc_obj, exc_tb = sys.exc_info()
            # 获取文件名和行号
            file_name = traceback.extract_tb(exc_tb)[-1][0]
            line_number = traceback.extract_tb(exc_tb)[-1][1]
            # 输出错误信息
            print("出错文件:", file_name)
            print("出错位置:", line_number, '行')
            print("出错类型:", exc_type.__name__)
            print("错误信息:", str(exc_obj))
            result = None
        except requests.exceptions.HTTPError as e:
            # 处理 HTTP 异常
            exc_type, exc_obj, exc_tb = sys.exc_info()
            # 获取文件名和行号
            file_name = traceback.extract_tb(exc_tb)[-1][0]
            line_number = traceback.extract_tb(exc_tb)[-1][1]
            # 输出错误信息
            print("出错文件:", file_name)
            print("出错位置:", line_number, '行')
            print("出错类型:", exc_type.__name__)
            print("错误信息:", str(e))
            result = None
        return result

    return wrapper


@try_except_code
def dingding_notice(content, robot_id=dingding_id):
    """钉钉提醒"""
    url = f'https://oapi.dingtalk.com/robot/send?access_token={robot_id}'
    msg = {
        "msgtype": "text",
        "text": {"content": content}
    }
    headers = {"Content-Type": "application/json;charset=utf-8"}
    response = requests.post(url=url, json=msg, headers=headers, timeout=10).json()
    return response
