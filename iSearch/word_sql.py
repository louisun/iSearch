#!/usr/bin/env python
# coding=utf-8
import json
import re
import sqlite3
import os
from termcolor import colored

DEFAULT_PATH = os.path.join(os.path.expanduser('~'), '.iSearch')

CREATE_TABLE_WORD = '''
CREATE TABLE IF NOT EXISTS Word
(
name            TEXT PRIMARY KEY NOT NULL,
user_defined    TEXT,
voice           TEXT,
basic           TEXT,
synonyms        TEXT,
discriminate    TEXT,
word_group      TEXT,
collins         TEXT,
bilingual       TEXT,
fanyiToggle     TEXT,
pr              INT DEFAULT 1,
aset            CHAR[1],
addtime         TIMESTAMP NOT NULL DEFAULT (DATETIME('NOW', 'LOCALTIME'))
)
'''

ORDER_ARR = ["name", "user_defined" ,"voice", "basic", "synonyms", "discriminate",
             "word_group", "collins", "bilingual", "fanyiToggle", "pr"]
# 没有通过json串存放的元素的下标
exception_arr = [0, 1, 10]

class Word_sql:
    def __init__(self):
        if not os.path.exists(DEFAULT_PATH):
            os.mkdir(DEFAULT_PATH)
        if not os.path.exists(os.path.join(DEFAULT_PATH, 'word.db')):
            with open(os.path.join(DEFAULT_PATH, 'word_list.txt'), 'w') as f:
                pass
        self.__conn = sqlite3.connect(os.path.join(DEFAULT_PATH, 'word.db'))
        curs = self.__conn.cursor()
        curs.execute(CREATE_TABLE_WORD)
        self.__conn.commit()

    def __del__(self):
        self.__conn.close()

    # func word_dict_to_json
    # purpose: change list to json type, for saving
    # other: because of ’ can't exist, so change it to ASCII(%27)
    @staticmethod
    def word_dict_to_json(word_dict):
        for key, value in word_dict.items():
            if isinstance(value, list) or isinstance(value, dict):
                word_dict[key] = re.sub('\'', '%27', json.dumps(value))

    # func json_to_word_dict
    # purpose: change list to json type, for saving
    # other: because of ’ can't exist, so change it to ASCII(%27)
    # return : word_dict dict 
    @staticmethod
    def json_to_word_dict(result):
        word_dict = {}
        for index in range(len(ORDER_ARR)):
            if index in exception_arr:
                # word name
                word_dict[ORDER_ARR[index]] = result[index]
            else:
                if result[index]:
                    word_dict[ORDER_ARR[index]] = json.loads(re.sub("%27", "\'", result[index]))

        return word_dict

    def delete_word(self, condition):
        try:
            curs = self.__conn.cursor()
            curs.execute('DELETE FROM Word WHERE %s' % condition)
        except Exception as e:
            print(e)
            return False
        else:
            print(colored('delete word where %s ' % condition, 'green'))
            self.__conn.commit()
            return True

    def update_word(self, set_part, condition):
        try:
            curs = self.__conn.cursor()
            curs.execute('UPDATE Word SET %s WHERE %s' % (set_part, condition))
        except Exception as e:
            print(colored('something\'s wrong, you can\'t set %s' % (set_part), 'white', 'on_red'))
            print(e)
            return False
        else:
            self.__conn.commit()
            print("set %s success" % set_part)
            return True

    def select_word(self, condition):
        word_dict = {}
        word_dict_list = []
        curs = self.__conn.cursor()
        split = ","
        select_str = split.join(ORDER_ARR)
        curs.execute('SELECT %s FROM Word WHERE %s' % (select_str,condition))
        res = curs.fetchall()
        if res:
            for result in res:
                word_dict = self.json_to_word_dict(result)
                word_dict_list.append(word_dict)
        
        return word_dict_list

    def insert_word(self, word_dict):
        try:
            curs = self.__conn.cursor()
            self.word_dict_to_json(word_dict)
            split = ","
            insert_str = split.join(ORDER_ARR)
            for index in range(len(ORDER_ARR)):
                if 0 == index:
                    value_str = "'%s'" % word_dict[ORDER_ARR[index]]
                    #print(value_str)
                else:
                    # 如果有元素不存在于字典中，那么加入一个空值,避免报错
                    if ORDER_ARR[index] not in word_dict:
                        word_dict[ORDER_ARR[index]] = ""
                    value_str = "%s,'%s'" % (value_str,word_dict[ORDER_ARR[index]]) 
                    #print(value_str)
            curs.execute('''insert into Word(%s,aset)
                         values (%s, '%s')'''
                         % ( insert_str, value_str, word_dict["name"][0].upper()))
        except Exception as e:
            print(colored('something\'s wrong, you can\'t add the word', 'white', 'on_red'))
            print(e)
            return False
        else:
            self.__conn.commit()
            print(colored('%s has been inserted into database, 优先级为%d' 
                          % (word_dict["name"], word_dict["pr"]), 'green'))
            return True
        
    def count_word(self, condition):
        curs = self.__conn.cursor()
        curs.execute('SELECT count(*) FROM Word WHERE %s' % condition)
        res = curs.fetchone()
        if res:
            return res[0]

        return 0















