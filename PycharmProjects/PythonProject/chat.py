import itchat


def send_messages_to_group(group_name, message):

    username = '810705504'
    password = 'google'
    # 登录微信
    itchat.auto_login(hotReload=True)

    # 获取目标群聊
    group = itchat.search_chatrooms(name=group_name)
    if not group:
        print(f"未找到群聊: {group_name}")
        return

    group = group[0]  # 获取第一个匹配的群聊
    group_username = group['UserName']

    # 发送消息
    itchat.send(message, toUserName=group_username)
    print(f"消息已发送到群聊: {group_name}")

    # 退出登录
    itchat.logout()


if __name__ == '__main__':
    group_name = '家庭股票交流'  # 目标群聊名称
    message = '大家好，这是群发的测试消息！'  # 待发送的消息
    send_messages_to_group(group_name, message)