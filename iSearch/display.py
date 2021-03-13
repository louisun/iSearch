#!/usr/bin/env python
# coding=utf-8

import json
from termcolor import colored

type_to_chinese = {
    "voice":"【发音】",
    "user_defined":"【自定义】",
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
    def __init__(self, config):
        if "type" not in config:
            config["type"] = Display_mode.SHORT
        
        for part in ["text", "title"]:
            if part not in config:
                config[part] = {}

            if "color" not in config[part]:
                config[part]["color"] = "blue"

            if "backcolor" not in config[part]:
                config[part]["backcolor"] = "on_white"

        self.__config = config
    
    def title_print(self, title):
        print(colored(title, self.__config["title"]["color"], self.__config["title"]["backcolor"]))

    def show_core(self, text):
        print(colored(text, self.__config["text"]["color"], self.__config["text"]["backcolor"]))

    '''
    1. 因为固定顺序，所以不使用key,value in *.item()形式遍历
    2. 其中，根据标记，提前返回
    '''
    def show(self, word_dict, mode=Display_mode.MIDDLE):
        if not word_dict:
            return False

        if "name" in word_dict:
            self.show_core(word_dict["name"])

        if "user_defined" in word_dict and word_dict["user_defined"]:
            self.title_print(type_to_chinese["user_defined"])
            self.show_core(word_dict["user_defined"])

        if "voice" in word_dict and word_dict["voice"]:
            self.title_print(type_to_chinese["voice"])
            for item in word_dict["voice"]:
                self.show_core(item)

        if "basic" in word_dict and word_dict["basic"]:
            self.title_print(type_to_chinese["basic"])
            for item in word_dict["basic"]:
                self.show_core(item)

        if mode & Display_mode.NAME:
            return True

        #标准是数组
        if "synonyms" in word_dict and word_dict["synonyms"]:
            self.title_print(type_to_chinese["synonyms"])
            for item in word_dict["synonyms"]:
                self.show_core(item)

        if "discriminate" in word_dict and word_dict["discriminate"]:
            self.title_print("\n" + type_to_chinese["discriminate"])
            for item in word_dict["discriminate"]:
                self.show_core(item)

        if mode & Display_mode.SHORT:
            return True

        if "word_group" in word_dict and  word_dict["word_group"]:
            self.title_print("\n" + type_to_chinese["word_group"])
            for item in word_dict["word_group"]:
                self.show_core(item)

        if mode & Display_mode.MIDDLE:
            return True
    
        if "collins" in word_dict and word_dict["collins"]:
            self.title_print("\n" + type_to_chinese["collins"])
            for item in word_dict["collins"]:
                self.show_core(item)

        if "bilingual" in word_dict and word_dict["bilingual"]:
            self.title_print("\n" + type_to_chinese["bilingual"])
            for item in word_dict["bilingual"]:
                self.show_core(item)

        if "fanyiToggle" in word_dict and word_dict["fanyiToggle"]:
            self.title_print("\n" + type_to_chinese["fanyiToggle"])
            for item in word_dict["fanyiToggle"]:
                self.show_core(item)

        return True


    def display_basic(self, data, title_color, text_color):
        for dataItem in data:
            if dataItem:
                if is_title(dataItem):
                    if(self.__config["type"] & Mode.COLORED):
                        print(colored(dataItem, title_color.backcolor, title_color.textcolor))
                    else:
                        print(dataItem)
                else:
                    if(self.__config["type"] & Mode.COLORED):
                        print(colored(dataItem, text_color.backcolor, title_color.textcolor))
                    else:
                        print(dataItem)

