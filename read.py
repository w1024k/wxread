# coding : utf-8
# @Author: wangyang
# @time  : 2020/5/22 9:33

import sys
import time
import random
import threading
import argparse
import itertools
from selenium import webdriver


class Reader(object):
    def __init__(self, go_signal, name="流畅的python", driver="./chromedriver", duration=60):
        self.signal = go_signal
        self.name = name
        self.duration = duration
        self.browser = webdriver.Chrome(executable_path=driver)
        self.browser.implicitly_wait(3)
        self.browser.get("https://weread.qq.com/")
        self.pull_js = "var q=document.documentElement.scrollTop=%s"
        self.pull_distance = 0

    def login(self):
        if not self.browser.find_elements_by_class_name("navBar_link_Login"):
            return True
        self.browser.find_element_by_class_name("navBar_link_Login").click()
        print("请在20秒内登陆")
        self.slow_function(d=20)
        if self.browser.find_elements_by_class_name("navBar_link_Login"):
            return False
        return True

    def find_book(self):
        self.browser.find_element_by_class_name("navBar_home_inputText").send_keys(self.name)
        self.browser.find_element_by_class_name("search_input_right").click()
        self.browser.find_elements_by_class_name("search_result_global_bookInfo")[0].click()

    def slow_function(self, d, go=True):
        f = "{:0>%sd} s" % str(len(str(d)))
        write, flush = sys.stdout.write, sys.stdout.flush
        print("倒计时")
        for char in itertools.cycle('|/-\\'):
            status = char + ' ' + f.format(d)
            write(status)
            flush()
            write('\x08' * len(status))
            if d == 0:
                break
            time.sleep(1)
            d -= 1
        if not go:
            self.signal.go = False

    def run(self):
        is_login = self.login()
        if not is_login:
            print("未登录")
        else:
            self.find_book()
            read = threading.Thread(target=self.read_page)
            print("ready reading..")
            read.start()
            print("start reading..")
            self.slow_function(d=self.duration * 60, go=False)
            read.join()
            print("down..")
        self.browser.close()

    def pull_page(self):
        move = random.randint(1000, 2000)
        self.pull_distance += move
        pull_js = self.pull_js % str(self.pull_distance)
        self.browser.execute_script(pull_js)

    def read_page(self):
        while True:
            pull_times = random.randint(10, 20)
            for _ in range(pull_times):
                if not self.signal.go:
                    return
                self.pull_page()
                wait = random.randint(3, 5)
                # print("%s s后下拉 " % wait)
                time.sleep(wait)
            self.browser.find_element_by_class_name("readerFooter_button").click()

            # print("翻页")
            self.pull_distance = 0


class Signal:
    go = True


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    go_signal = Signal()
    driver = "./chromedriver"
    ap.add_argument("-d", "--duration", required=False, help="阅读时长", type=int)
    ap.add_argument("-n", "--name", required=False, help="书名")
    args = vars(ap.parse_args())
    duration = int(args.get("duration") or 60)
    name = args.get("name") or "流畅的python"

    print("即将自动阅读%s %s 分钟" % (name, duration))
    reader = Reader(go_signal=go_signal, name=name, duration=duration)
    reader.run()
    print("end...")
