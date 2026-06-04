# -*- coding: utf-8 -*-
"""
企业微信机器人通知工具
"""

from app.core.config import settings
import requests
from requests_toolbelt import MultipartEncoder
import os


def _get_webhook_url():
    """构建 webhook URL（从 settings 读取 key）"""
    return f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={settings.WECHAT_WEBHOOK_KEY}"


def _get_upload_url():
    """构建上传 URL（从 settings 读取 key）"""
    return f"https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={settings.WECHAT_WEBHOOK_KEY}&type=file"


def uploadGroupFile(filepath):
    """上传文件到企业微信，返回 media_id"""
    url = _get_upload_url()
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    filename = os.path.basename(filepath)
    try:
        multipart = MultipartEncoder(
            fields={
                "filename": filename,
                "filelength": "",
                "name": "media",
                "media": (
                    filename,
                    open(filepath, "rb"),
                    "application/octet-stream",
                ),
            },
            boundary="-------------------------acebdf13572468",
        )
        headers["Content-Type"] = multipart.content_type
        resp = requests.post(url, headers=headers, data=multipart)
        json_res = resp.json()
        if json_res.get("media_id"):
            return json_res.get("media_id")
    except Exception as e:
        print(f"企业微信机器人上传文件失败,详细信息:{str(e)}")
        return ""


def sendGroupFile(filepath):
    """发送文件到企业微信群"""
    media_id = uploadGroupFile(filepath)
    if not media_id:
        return False
    msg = {"msgtype": "file", "file": {"media_id": media_id}}
    try:
        url = _get_webhook_url()
        requests.post(url, headers={"content-type": "application/json"}, json=msg)
        return True
    except Exception as e:
        print(f"企业微信机器人发送文件失败,详细信息:{str(e)}")
        return False


def sendMsg(msg):
    """发送文本消息到企业微信群"""
    url = _get_webhook_url()
    requests.post(
        url,
        json={
            "msgtype": "text",
            "mentioned_mobile_list": ["13554216385"],
            "text": {"content": msg},
        },
    )
