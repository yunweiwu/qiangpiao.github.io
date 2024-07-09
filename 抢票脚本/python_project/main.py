# author：

import configparser
from datetime import datetime
import os
import pickle
from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

"""
1. 由于可能票源紧张，本程序默认抢购一张
2. 程序启动之前，先同步下电脑的时间，避免本地和网络时间相差较大
"""
# cfg = configparser.ConfigParser()
cfg = configparser.RawConfigParser()
conf_path = "./config.conf"
cfg.read([conf_path], encoding='utf-8')


class Book_Ticket(object):

    def __init__(self):
        # 首页url
        self.damai_url = "https://www.damai.cn/"
        # 登录界面
        self.login_url = "https://passport.damai.cn/login?ru=https%3A%2F%2Fwww.damai.cn%2F"
        # 购票界面url
        self.book_url = cfg.get("ticket_info", "book_url").strip()

        self.price_list = cfg.get("ticket_info", "price").strip().split(",")  # 抢票的价格挡位，从左向右
        self.price = list(map(int, self.price_list))
        self.name_num = int(cfg.get("ticket_info", "name_num").strip())  # 在订单界面选择给第几个实名用户购买，默认给第一个用户购买

        self.driver_path = cfg.get("other", "driver_path").strip()

        self.status = 0  # 是否登录的状态 0是未登录，1是登录

        self.current_num = 1  # 当前抢票第几次
        self.num = int(cfg.get("ticket_info", "num").strip())  # 抢票总次数

        self.datetime = cfg.get("ticket_info", "date_time").strip()  # 抢票时间点
        self.rush_time = time.strptime(self.datetime, '%Y-%m-%d %H:%M:%S')

        # 设置无头浏览器 无界面浏览器
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--disable-gpu')
        # self.driver = webdriver.Chrome(executable_path=self.driver_path, options=self.chrome_options)  # 此项稳定版打开
        chrome_options = Options()
        self.driver = webdriver.Chrome(options=chrome_options)  # 默认谷歌浏览器, 指定下驱动的位置
        # self.driver = webdriver.Chrome()  # 默认谷歌浏览器
        self.driver.maximize_window()

    def get_cookie(self):
        try:
            # 先进入登录页面进行登录
            print("------开始登录------")
            self.driver.get(self.login_url)
            # time.sleep(2)  # 不加好像也可以
            self.driver.switch_to.frame(0)
            # login_methods = self.driver.find_elements_by_class_name("login-tabs-tab")

            # inputTag = driver.find_element_by_id("value")  # 利用ID查找
            # 改为：
            login_methods = self.driver.find_elements(By.CLASS_NAME, "login-tabs-tab")

            login_methods[2].click()
            print("------请扫码------")
            # while self.driver.title != '大麦登录':
            #     time.sleep(0.5)

            while self.driver.title != '大麦网-全球演出赛事官方购票平台-100%正品、先付先抢、在线选座！':
                time.sleep(1)
            print("------扫码成功------")
            pickle.dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))
            print("------Cookie保存成功------")
        except Exception as e:
            raise e

    def set_cookie(self):
        try:
            cookies = pickle.load(open("cookies.pkl", "rb"))  # 载入cookie
            for cookie in cookies:
                cookie_dict = {
                    'domain': '.damai.cn',  # 必须有，不然就是假登录
                    'name': cookie.get('name'),
                    'value': cookie.get('value'),
                    "expires": "",
                    'path': '/',
                    'httpOnly': False,
                    'HostOnly': False,
                    'Secure': False}
                self.driver.add_cookie(cookie_dict)
            print('------载入Cookie------')
        except Exception as e:
            print("------cookie 设置失败，原因：%s------" % str(e))

    def login(self):
        if not os.path.exists('cookies.pkl'):  # 如果不存在cookie.pkl,就登录获取一下
            self.get_cookie()
        else:  # 存在就设置下cookie
            self.driver.get(self.damai_url)
            self.set_cookie()

    def select_price(self):
        try:
            """
            选择票价挡位
            :return: 
            """
            price_list = self.driver.find_elements(By.XPATH, "//div[@class='select_right_list']/div")  # 根据优先级选择一个可行票价
            # 不知道为啥多出两个标签，前两个标签不是, 所以去除前两个
            price_list = price_list[2:]
            print("------票价档次数量：%s------" % len(price_list))
            num = 0
            for i in self.price:
                # j = price_list[i - 1].get_attribute('class')
                print("------正在抢购第 %s 挡位票------" % i)
                try:
                    span = price_list[i - 1].find_element(By.TAG_NAME, "span")
                    print("------第 %s 档票已经售完------" % i)
                    num += 1
                    if num < len(self.price):
                        continue
                except:
                    price_list[i - 1].click()
                    break
                if num == len(self.price):
                    print("------你想抢的票已售完------")
                    raise Exception("你想抢的票已售完")
        except Exception as e:
            raise e

    def select_buy_name(self):
        try:
            # 先判断是否有选择购买人的标签
            buy_name_label = self.driver.find_elements(By.CLASS_NAME, "dm-ticket-buyer")
            if not buy_name_label:
                return

            buy_name_click = self.driver.find_element(By.XPATH, "//div[@class='next-row next-row-no-padding buyer-list']/div[%s]" % self.name_num)
            click_1 = True
            while click_1:
                try:
                    buy_name_click.click()
                    click_1 = False
                except Exception as e:
                    pass
        except Exception as e:
            raise e

    def submit(self):
        try:
            submit_click = self.driver.find_element(By.ID, 'dmOrderSubmitBlock_DmOrderSubmitBlock')
            click_2 = True
            while click_2:
                try:
                    submit_click.click()
                    click_2 = False
                except Exception as e:
                    pass
        except Exception as e:
            raise e

    def quit(self):
        while self.driver.title != "支付宝 - 网上支付 安全快速！":
            time.sleep(1)
        self.driver.quit()

    def rush_ticket(self):
        try:
            # 直接来到演唱会购票界面
            self.driver.get(self.book_url)

            # 选择票价
            self.select_price()

            # 点击立即预定
            click_book = self.driver.find_element(By.CLASS_NAME, "buy-link")
            click_book.click()

            # 选择购买人
            # self.select_buy_name()

            # 其他默认

            # 点击提交订单
            self.submit()

        except Exception as e:
            raise e

    def run(self):
        try:
            # 登录
            self.login()
            # 判断抢票时间是否到达
            print("------等待抢票时间点到来，进行抢票------")
            while time.mktime(self.rush_time) - time.time() > 0.5:  # 提前0.2-0.5秒开始抢
                time.sleep(0.4)

            start_time = time.time()
            print("------开始抢票，时间点：%s------" % datetime.now())

            # 抢票
            loop = 1
            for i in range(self.num):
                try:
                    print("------正在进行第 %s 轮抢票------" % (i + 1))
                    self.rush_ticket()
                    break
                except Exception as e:
                    if loop == self.num:
                        raise e
                    loop += 1
                    pass
            # self.rush_ticket()

            end_time = time.time()
            print("抢票结束，时间点：%s" % datetime.now())
            print("抢票总时长：%s， 此时长不包括登录时间" % (end_time - start_time))
            print("抢票成功，抓紧去订单中付款！！")

            # 关闭浏览器
            self.quit()

            time.sleep(20)

        except Exception as e:
            self.driver.quit()
            print("******抢票失败，原因：%s******" % str(e))


if __name__ == '__main__':
    book = Book_Ticket()
    book.run()
