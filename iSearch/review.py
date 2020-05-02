#!/usr/bin/env python
# coding=utf-8
import time

class Reviewer:
    def __init__(self):
        print("init reviewer")
        self.__interval_times = []

    # interval_time单位为s
    def add_interval_time(self, interval_time):
        self.__interval_times.append(interval_time)

    def del_interval_time(self, interval_time):
        self.__interval_times.remove(interval_time)

    # interval_time单位为day
    def add_interval_day(self, interval_day):
        self.__interval_times.append(interval_day * 24 * 3600)

    def del_interval_day(self, interval_day):
        self.__interval_times.remove(interval_day * 24 * 3600)

    def get_words(self, conn):
        cur_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        word_dict_list = []
        for interval_time in self.__interval_times:
            curs = conn.cursor()
            words = []
            begin_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - interval_time))
            curs.excute('SELECT * FROM word WHERE time between "%s" and "%s"' % (begin_time, cur_time))
            res = curs.fetchall()
            for result in res:
                word_dict = {}
                word_dict[""]




# 自测

def time_test():
    reviewer = Reviewer()
    localtime = time.localtime(time.time())
    print(localtime)
    add_time = time.time() - 3 * 24 * 3600
    print("3 day ago:", time.localtime(add_time))
    displaytime = time.asctime(time.localtime(time.time()))
    print("asctime=", displaytime)
    # 格式化成2016-03-20 11:45:39形式
    print (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    # 格式化成Sat Mar 28 22:24:24 2016形式
    print (time.strftime("%a %b %d %H:%M:%S %Y", time.localtime()))

    # 将格式字符串转换为时间戳
    a = "Sat Mar 28 22:24:24 2016"
    print (time.mktime(time.strptime(a,"%a %b %d %H:%M:%S %Y")))

#time_test()


