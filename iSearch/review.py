#!/usr/bin/env python
# coding=utf-8
import time
import sys

DAY_TO_SECOND = 24 * 3600

class Reviewer:
    def __init__(self, config):
        print("init reviewer")
        self.__interval_times = self.day2time(config["review"]["day"])
    
    # 将间隔日期转化为时间
    def day2time(dayList):
        ret = []
        for day in dayList:
            ret.append(day * DAY_TO_SECOND)
        return ret

    def review(self, word_sql, displayer):
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
                msg = input(input_msg)
                if "quit" == msg or "q" == msg:
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


