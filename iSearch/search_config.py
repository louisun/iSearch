#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 birdfss <ffhbird@gmail.com>
#
# Distributed under terms of the MIT license.

import json, os

# purpose : 用户可以设置一些默认配置，不需要每次通过命令行
#           输入，方便使用
# config  : 请参考config/default-000.json 
class iSearchConfig():
    def __init__(self, ConfigPath):
        if os.path.isfile(ConfigPath):
            with open(ConfigPath, "r") as fr:
                self.__config = json.loads(fr.read())

        self.default_maps = ["priority"]
        
    def get_default_config(self, key):
        if key in self.__config["default"]:
            return self.__config["default"][key]
        else:
            return None

    def get_display_config(self):
        if "display" in self.__config:
            return self.__config["display"]
        else:
            return {}


