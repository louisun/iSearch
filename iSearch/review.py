#!/usr/bin/env python
# coding=utf-8
import time
import sys

DAY_TO_SECOND = 24 * 3600

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
        self.__interval_times.append(interval_day * DAY_TO_SECOND)

    def del_interval_day(self, interval_day):
        self.__interval_times.remove(interval_day * DAY_TO_SECOND)

    def get_words(self, word_sql, displayer):
        word_dict_list = []
        for interval_time in self.__interval_times:
            words = []
            cur_time = time.time()
            begin_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(cur_time - interval_time))
            end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(cur_time - interval_time + DAY_TO_SECOND))
            word_dict_list = word_sql.select_word("addtime between '%s' and '%s'" %(begin_time, end_time))
            print("----%d day ago--review_num=%d----" % (interval_time / DAY_TO_SECOND, len(word_dict_list)))
            for word_dict in word_dict_list:
                displayer.show(word_dict)
                input_msg = '------------按任意键继续, 输入quit退出----------'
                if sys.version_info[0] == 2:
                    msg = raw_input(input_msg)
                else:
                    msg = input(input_msg)

                if "quit" == msg:
                    break


        return True

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


