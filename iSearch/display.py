#!/usr/bin/env python
# coding=utf-8

import json
from termcolor import colored

type_to_chinese = {
    "basic":"【基本含义】",
    "synonyms":"【同近义词】",
    "discriminate":"【词语辨析】",
    "word_group":"【词组】",
    "collins":"【用例介绍】",
    "bilingual":"【双语例句】",
    "fanyiToggle":"【有道翻译】"
}

def is_title(dataItem):
    if dataItem.startswith('例') or dataItem.startswith('【'):
        return true
    else:
        return false

class Display_mode():
    COLORED = 1
    NAME = 2
    SHORT = 4
    MIDDLE = 8
    LONG = 16


class Displayer:
    def __init__(self, mode=Display_mode.SHORT, isColored=1):
        self.__mode = Display_mode.SHORT 
        self.__colored = isColored
        self.__text_color = 'blue'
        self.__text_backcolor = 'on_white'
        self.__title_color = 'white'
        self.__title_backcolor = 'on_blue'
        #print("mode = %d" %(self.__mode))

    #def __del__(self):
        #将配置写入文件中

    def set_mode(self, mode):
        self.__mode = mode
    def get_mode(self):
        return self.__mode
    
    def title_print(self, title):
        print(colored(title, self.__title_color, self.__title_backcolor))

    def show_core(self, text, isColored=1):
        if 1 == isColored:
            print(colored(text, self.__text_color, self.__text_backcolor))
        else:
            print(text)

    '''
    1. 因为固定顺序，所以不使用key,value in *.item()形式遍历
    2. 其中，根据标记，提前返回
    '''
    def show(self, word_dict, mode=Display_mode.MIDDLE):
        if "name" in word_dict:
            self.show_core(word_dict["name"], self.__colored)

        if "basic" in word_dict and word_dict["basic"]:
            self.title_print(type_to_chinese["basic"])
            for item in word_dict["basic"]:
                self.show_core(item, self.__colored)

        if mode & Display_mode.NAME:
            return True

        #标准是数组
        if "synonyms" in word_dict and word_dict["synonyms"]:
            self.title_print(type_to_chinese["synonyms"])
            for item in word_dict["synonyms"]:
                self.show_core(item, self.__colored)

        if "discriminate" in word_dict and word_dict["discriminate"]:
            self.title_print("\n" + type_to_chinese["discriminate"])
            for item in word_dict["discriminate"]:
                self.show_core(item, self.__colored)

        if mode & Display_mode.SHORT:
            return True

        if "word_group" in word_dict and  word_dict["word_group"]:
            self.title_print("\n" + type_to_chinese["word_group"])
            for item in word_dict["word_group"]:
                self.show_core(item, self.__colored)

        if mode & Display_mode.MIDDLE:
            return True
    
        if "collins" in word_dict and word_dict["collins"]:
            self.title_print("\n" + type_to_chinese["collins"])
            for item in word_dict["collins"]:
                self.show_core(item, self.__colored)

        if "bilingual" in word_dict and word_dict["bilingual"]:
            self.title_print("\n" + type_to_chinese["bilingual"])
            for item in word_dict["bilingual"]:
                self.show_core(item, self.__colored)

        if "fanyiToggle" in word_dict and word_dict["fanyiToggle"]:
            self.title_print("\n" + type_to_chinese["fanyiToggle"])
            for item in word_dict["fanyiToggle"]:
                self.show_core(item, self.__colored)

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

