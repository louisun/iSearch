#!/usr/bin/env python
# coding=utf-8

import json
from termcolor import colored

class Mode():
    COLORED = 1
    SHORT = 2
    MIDDLE = 4
    LONG = 8

class Displayer:
    def __init__(self):
        self.__mode = Mode.COLORED | Mode.SHORT 
        print("mode = %d" %(self.__mode))

    def __del__(self):
        #将配置写入文件中
        print("mode=%d" % (self.__mode))

    def set_mode(self, mode):
        self.__mode = mode
    def get_mode(self):
        return self.__mode

    def is_title(dataItem):
        if dataItem.startswith('例') or dataItem.startswith('【'):
            return true
        else:
            return false
    
    def display_basic(self, data, title_color, text_color):
        for dataItem in data:
            if dataItem:
                if is_title(dataItem):
                    if(self.__mode & Mode.COLORED):
                        print(colored(dataItem, title_color.backcolor, title_color.textcolor))
                    else:
                        print(dataItem)
                else:
                    if(self.__mode & Mode.COLORED):
                        print(colored(dataItem, text_color.backcolor, title_color.textcolor))
                    else:
                        print(dataItem)







