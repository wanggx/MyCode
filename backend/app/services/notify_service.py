# -*- coding: utf-8 -*-
"""
通知服务：企业微信消息发送
"""

from app.utils.notify import sendMsg as _sendMsg, sendGroupFile as _sendGroupFile


def send_text(msg):
    """发送文本消息"""
    _sendMsg(msg)


def send_file(filepath):
    """发送文件"""
    return _sendGroupFile(filepath)
