#!/usr/bin/env python
# coding=utf-8

class Reviewer:
    def __init__(self):
        print("init reviewer")
        self.__times = []

    def add_time(self, time):
        self.__times.append(time)

    def del_time(self, time):
        self.__times.remove(time)

    def get_words(self, conn):
        for time in self.__times:
            curs = conn.cursor()
            words = []
            curs.excute('SELECT * FROM word WHERE time="%s"' % (time))
            res = curs.fetchall()


