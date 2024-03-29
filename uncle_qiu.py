#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
# File: uncle_qiu.py
# Date: 2023/11/28
# Cron: 0 1,8 * * *
# new Env("丘大叔每日签到")
# export QDS_TOKEN=jWRdODlssffsdfafasfafsaffaf, 抓包丘大叔柠檬茶微信小程序, 获取https://webapi.qmai.cn/请求头中的Qm-User-Token.
import os
import random
import string
import sys
import time

import requests
from anti_useragent import UserAgent

ua = UserAgent()


class UncleQiuApp:

    def __init__(self):
        self.title = '丘大叔签到'
        self.base_url = 'https://webapi.qmai.cn/'
        token = os.getenv('QDS_TOKEN', None)
        if not token:
            print('未配置QDS_TOKEN, 跳过执行!')
            sys.exit(1)

        headers = {
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/116.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI "
                          "MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a1b)XWEB/9165",
            'Qm-User-Token': token,
            "multi-store-id": "97702",
            "store-id": "202338",
            "qm-from-type": "catering",
            "scene": "1145",
            "referer": "https://servicewechat.com/wx01d44c5a2232d2d0/264/page-frame.html",
            'qm-from': 'wechat',
        }
        self.http = requests.Session()
        self.http.headers.update(headers)

    def send(self, title, content):
        try:
            from notify import send
            send(title, content)
        except ModuleNotFoundError as _:
            print('未找到通知模块!')

    def get_sign_days(self):
        url = self.base_url + '/web/catering/integral/sign/detail'
        params = {
            "appid": 'wx' + ''.join(random.sample(string.ascii_lowercase + string.digits, 12)),
        }
        try:
            data = self.http.post(url, json=params).json()
            return data['data']['continuityTotal']
        except Exception as _:
            return -1

    def signin(self):
        is_signin_ok = False
        try:
            url = self.base_url + 'web/catering/integral/sign/signIn'
            params = {
                "activityId": "100820000000000642",
                "mobilePhone": "138" + ''.join(random.sample(string.digits, 8)),
                "userName": "微信用户",
                "appid": 'wx' + ''.join(random.sample(string.ascii_lowercase + string.digits, 12)),
            }
            data = self.http.post(url, json=params).json()
            if not data['status'] and '已签到' not in data['message']:
                msg = f'签到失败, {data["message"]}'
            else:
                time.sleep(1)
                sign_days = self.get_sign_days()
                if sign_days:
                    msg = f'签到成功!\n已连续签到{sign_days}天!'
                else:
                    msg = '签到成功, 但获取签到天数失败!'
                is_signin_ok = True
        except Exception as e:
            msg = f"签到失败, 错误:{e.args}"

        return is_signin_ok, msg

    def get_my_points(self):
        """
        获取当前积分
        :return:
        """
        url = self.base_url + '/web/catering/crm/total-points'
        params = {
            "appid": "wx01d44c5a2232d2d0"
        }
        try:
            data = self.http.post(url, json=params).json()
            if data['status']:
                return data['data']
            return -1
        except Exception as _:
            return -1

    def get_goods(self, points):
        goods_list = []
        try:
            url = self.base_url + '/web/catering/mall/goods?categoryId=0&page=1&pageSize=10&appid=wx01d44c5a2232d2d0'
            data = self.http.get(url).json()
            if not data['status']:
                return goods_list
            for item in data['data']['data']:
                if points >= item['pointsPrice']:
                    if not item['cashPrice']:
                        goods_list.append(item['goodsName'] + f"({item['pointsPrice']}积分)")
                    else:
                        goods_list.append(item['goodsName'] + f"({item['pointsPrice']}积分+{item['cashPrice']}元)")
            return goods_list
        except Exception as _:
            return goods_list

    def start(self):
        is_signin_ok, msg = self.signin()
        if not is_signin_ok:
            self.send(self.title, msg)
            return

        points = self.get_my_points()
        if points < 0:
            msg += '\n查询积分信息失败!'
            self.send(self.title, msg)
            return

        msg += f'\n当前剩余总积分:{points}!'
        goods_list = self.get_goods(points)
        if not goods_list:
            msg += '\n暂无可兑换商品|查询商品信息失败!'
        else:
            msg += '\n可兑换商品如下:'
            for goods in goods_list:
                msg += f'\n\t{goods}'

        self.send(self.title, msg)


if __name__ == '__main__':
    app = UncleQiuApp()
    app.start()
