#!/usr/bin/env python
# coding=utf-8

import json
from termcolor import colored

def is_title(dataItem):
    if dataItem.startswith('例') or dataItem.startswith('【'):
        return true
    else:
        return false

class Mode():
    COLORED = 1
    SHORT = 2
    MIDDLE = 4
    LONG = 8


class Displayer:
    def __init__(self):
        self.__mode = Mode.COLORED | Mode.SHORT 
        self.__text_color = 'blue'
        self.__text_backcolor = 'on_white'
        self.__title_color = 'white'
        self.__title_backcolor = 'on_blue'
        print("mode = %d" %(self.__mode))

    def __del__(self):
        #将配置写入文件中
        print("mode=%d" % (self.__mode))

    def set_mode(self, mode):
        self.__mode = mode
    def get_mode(self):
        return self.__mode
    
    def title_print(self, title):
        print(colored(title, self.__title_color, self.__title_backcolor))

    def show(self, word_dict):
        #标准是数组
        self.title_print("【词语解析与近义词】")
        for item in word_dict["synonyms"]:
            print(colored(item, self.__text_color, self.__text_backcolor))

        self.title_print("\n【词语辨析】")
        for item in word_dict["discriminate"]:
            print(colored(item, self.__text_color, self.__text_backcolor))

        self.title_print("\n【词组】")
        for item in word_dict["word_group"]:
            print(colored(item, self.__text_color, self.__text_backcolor))

        self.title_print("\n【用例介绍】")
        for item in word_dict["collins"]:
            print(colored(item, self.__text_color, self.__text_backcolor))

        self.title_print("\n【双语例句】")
        for item in word_dict["bilingual"]:
            print(colored(item, self.__text_color, self.__text_backcolor))

        self.title_print("\n【有道翻译】")
        for item in word_dict["fanyiToggle"]:
            print(colored(item, self.__text_color, self.__text_backcolor))
        return True


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







