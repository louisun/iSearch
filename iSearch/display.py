#!/usr/bin/env python
# coding=utf-8

import json
from termcolor import colored

def is_title(dataItem):
    if dataItem.startswith('例') or dataItem.startswith('【'):
        return true
    else:
        return false

def display_basic(data, mode, title_color, text_color):
    for dataItem in data:
        if dataItem:
            if is_title(dataItem):
                print(colored(dataItem, title_color.backcolor, title_color.textcolor))
            else:
                print(colored(dataItem, text_color.backcolor, title_color.textcolor))







