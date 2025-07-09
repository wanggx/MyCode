import os
import requests
from requests_toolbelt import MultipartEncoder

def uploadGroupFile(filepath):
    upload_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key=2d426b1f-4b3e-4905-b403-f69222c947cd&type=file'
    headers = {"Accept": "application/json, text/plain, */*", "Accept-Encoding": "gzip, deflate",
                   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36"}
    filename = os.path.basename(filepath)
    try:
        multipart = MultipartEncoder(
            fields={'filename': filename, 'filelength': '', 'name': 'media', 'media': (filename, open(filepath, 'rb'), 'application/octet-stream')},
            boundary='-------------------------acebdf13572468')
        headers['Content-Type'] = multipart.content_type
        resp = requests.post(upload_url, headers=headers, data=multipart)
        json_res = resp.json()
        if json_res.get('media_id'):
            # print(f"企业微信机器人上传文件成功，file:{filepath}")
            return json_res.get('media_id')
    except Exception as e:
        # print(f"企业微信机器人上传文件失败，file: {filepath}, 详情：{e}")
        print("企业微信机器人上传文件失败,详细信息:" + str(e))
        return ""


def sendGroupFile(filepath):
    headers = {
        "content-type": "application/json"
    }
    media_id = uploadGroupFile(filepath)
    msg = {"msgtype": "file", "file": {"media_id": media_id}}
    # 发送请求
    try:
        url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=2d426b1f-4b3e-4905-b403-f69222c947cd'
        result = requests.post(url, headers=headers, json=msg)
        return True
    except Exception as e:
        print("企业微信机器人发送文件失败,详细信息:" + str(e))
        return False


def sendMsg(msg):
    requests.post(
        'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=2d426b1f-4b3e-4905-b403-f69222c947cd',
        json={
            'msgtype': 'text',
            'mentioned_mobile_list': ['13554216385'],
            'text': {
                'content': msg
            }
        }
    )