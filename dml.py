#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
# File: dml.py
# Cron: 0 1,8 * * *
# new Env("达美乐抽奖")
# export DML_OPENID=""   多个OPENID用@隔开
import requests
import os
import time


class DmlApp:

    def __init__(self, openid=""):
        self.base_url = 'https://game.dominos.com.cn'
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/116.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI '
                          'MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a1b)XWEB/9185',

        }
        self.openid = openid
        self.http = requests.Session()
        self.http.headers.update(headers)

    def share_game(self):
        try:
            url = f'{self.base_url}/musangking/game/sharingDone'
            params = {
                'openid': self.openid,
                'from': 1,
                'target': 0,
            }
            response = self.http.post(url, data=params)
            return response.json()
        except Exception as e:
            print(e.args)
            return {
                'statusCode': 9999, 'errorMessage': '系统错误了!'}

    def game_done(self):
        try:
            url = f'{self.base_url}/musangking/game/gameDone'
            params = {
                'openid': self.openid,
                'score': 'rLb9yLbutb293b4lmxxEsQud7a4XK6mWSKhF82It9KkAos3yauwWZ8WQdWc7ca5DiaQzCiFWQ91tx6K7JGyC5huxqhr3AovA9WOKl39JBcdtbRa0KX2AaDzVlP2LACrhvdtPXaVrPnrwe1U/wHxj4nxM9MTYdmO3aBpYVZUyIIE3OXxjSwagjePBNpmTl9lMf7BaiW7KUolDTlAMHZ7zaVLBa8ZU7vJHwArNBQtkvynvURuhTfMPQTHgipwVvwah86z5ifKkeDG/geJ6yenuWN/T0K82MKACVn1JwsxI0DUL2DndY8khc6JL6uQsknSkQyZucHE7tlEUiQnTU9Mm+A==',
                'tempId': 'null'
            }
            response = self.http.post(url, data=params)
            return response.json()
        except Exception as e:
            print(e.args)
            return {
                'statusCode': 9999, 'errorMessage': '系统错误了!'}

    def send(self, title, content):
        try:
            from notify import send
            send(title, content)
        except ModuleNotFoundError as _:
            print('未找到通知模块!')

    def run(self):
        for i in range(5):
            res = self.share_game()
            time.sleep(1)
            if res['statusCode'] != 0:
                print(f'{self.openid} {res["errorMessage"]}')
                break

        content = ''
        for i in range(10):
            res = self.game_done()
            if res['statusCode'] != 0:
                print(f'{self.openid} {res["errorMessage"]}')
                break
            time.sleep(1)
            print(res)
            content += f"{self.openid} {res['content']['name']}\n"

        if content:
            self.send('达美乐', content)


if __name__ == '__main__':
    openid_list = os.getenv('DML_OPENID', '').split('@')
    openid_list = [i for i in openid_list if i.strip() != '']
    if len(openid_list) < 1:
        print('未设置DML_OPENID, 程序退出运行!')
    else:
        for openid in openid_list:
            dml = DmlApp(openid)
            dml.run()
