
import requests

requests.post(
    'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=2d426b1f-4b3e-4905-b403-f69222c947cd',
    json={
        'msgtype': 'text',
        'mentioned_mobile_list': ['13554216385'],
        'text': {
            'content': '测试 at'
        }
    }
)