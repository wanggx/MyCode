
# 导入 requests 包
import requests

# 发送请求
x = requests.get('https://www.runoob.com/')

# 返回网页内容
print(x.ok)

l = lambda c: c + 1

print(l(3))

if __name__ == '__main__':
    print(__name__)
    print(__doc__)