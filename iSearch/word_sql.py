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

    # func word_dict_to_json
    # purpose: change list to json type, for saving
    # other: because of ’ can't exist, so change it to ASCII(%27)
    @staticmethod
    def word_dict_to_json(word_dict):
        word_dict["synonyms"]       = json.dumps(word_dict["synonyms"])
        word_dict["discriminate"]   = json.dumps(word_dict["discriminate"])
        word_dict["word_group"]     = json.dumps(word_dict["word_group"])
        word_dict["collins"]        = json.dumps(word_dict["collins"])
        word_dict["bilingual"]      = json.dumps(word_dict["bilingual"])
        word_dict["fanyiToggle"]    = json.dumps(word_dict["fanyiToggle"])
        for key, value in word_dict.items():
            if isinstance(value, str):
                word_dict[key] = re.sub('\'', '%27', value)

    # func json_to_word_dict
    # purpose: change list to json type, for saving
    # other: because of ’ can't exist, so change it to ASCII(%27)
    # return : word_dict dict 
    @staticmethod
    def json_to_word_dict(result):
        word_dict = {}
        word_dict["name"] = result[0]
        word_dict["synonyms"]       = json.loads(re.sub("%27", "\'", result[1]))
        word_dict["discriminate"]   = json.loads(re.sub("%27", "\'", result[2]))
        word_dict["word_group"]     = json.loads(re.sub("%27", "\'", result[3]))
        word_dict["collins"]        = json.loads(re.sub("%27", "\'", result[4]))
        word_dict["bilingual"]      = json.loads(re.sub("%27", "\'", result[5]))
        word_dict["fanyiToggle"]    = json.loads(re.sub("%27", "\'", result[6]))
        word_dict["pr"] = result[7]
    
        return word_dict

    def select_word(self, condition):
        word_dict = {}
        word_dict_list = []
        curs = self.__conn.cursor()
        curs.execute('SELECT name, synonyms, discriminate, word_group, collins,\
                     bilingual, fanyiToggle, pr FROM Word WHERE %s' % condition)
        res = curs.fetchall()
        if res:
            for result in res:
                word_dict = self.json_to_word_dict(result)
                word_dict_list.append(word_dict)
        
        return word_dict_list

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

    def insert_word(self, word_dict):
        try:
            curs = self.__conn.cursor()
            self.word_dict_to_json(word_dict)
            curs.execute('''insert into Word(name, synonyms, discriminate, word_group,
                         collins, bilingual, fanyiToggle, pr, aset)
                         values ('%s','%s','%s','%s','%s','%s','%s', %d, '%s')'''
                         % ( word_dict["name"], word_dict["synonyms"], word_dict["discriminate"], 
                            word_dict["word_group"], word_dict["collins"], word_dict["bilingual"], 
                            word_dict["fanyiToggle"], word_dict["pr"], word_dict["name"][0].upper()))
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















