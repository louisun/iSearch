# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import sys
import argparse
import os
import sqlite3
from display import Displayer, Display_mode
from termcolor import colored
from parser import Parser
from review import Reviewer
from word_sql import Word_sql

# Python2 compatibility
if sys.version_info[0] == 2:
    reload(sys)
    sys.setdefaultencoding('utf-8')

# Default database path is ~/.iSearch.
ISCOLORED = 1
DEFAULT_PATH = os.path.join(os.path.expanduser('~'), '.iSearch')


def search_online(word, word_parser):
    '''search the word or phrase on http://dict.youdao.com.'''

    url = 'http://dict.youdao.com/w/ %s' % word

    word_dict = word_parser.get_text(url)
    word_dict["name"] = word
    return word_dict

def search_database(word, word_sql, displayer):
    '''offline search.'''
    #模糊查询
    if '#' in word:
        word_dict_list = word_sql.select_word('name LIKE "%%%s%%"' % (word))
        if word_dict_list:
            for word_dict in word_dict_list:
                displayer.show(word_dict, Display_mode.NAME)
        else:
            # 这里需要加个是否需要网络查询的判断
            return False
    #具体查询
    else:
        word_dict_list = word_sql.select_word('name LIKE "%s"' % word)
        if word_dict_list:
            print(colored(word + ' 在数据库中存在', 'white', 'on_green'))
            for word_dict in word_dict_list:
                print(colored('★ ' * word_dict["pr"], 'red'), colored('☆ ' * (5 - word_dict["pr"]), 'yellow'), sep='')
                displayer.show(word_dict)
        else:
            return False

    return True
    

def search_word(word, word_parser, word_sql, displayer):
    flag = search_database(word, word_sql, displayer)
    if False == flag:
        print(colored(word + '提示: 不在本地，从有道词典查询', 'green', 'on_grey'))
        word_dict = search_online(word, word_parser)
        displayer.show(word_dict)

        input_msg = '请输入,放弃保存0，优先级(1~5)(默认为3)，6自定义\n>>> '
        if sys.version_info[0] == 2:
            add_in_db_pr = raw_input(input_msg)
        else:
            add_in_db_pr = input(input_msg)

        if add_in_db_pr and add_in_db_pr.isdigit():
            if int(add_in_db_pr) >= 1 and int(add_in_db_pr) <= 5:
                add_word(word, word_dict, word_sql, int(add_in_db_pr))
            elif 0 == int(add_in_db_pr):
                print("won't insert %s into database" %(word))
            elif 6 == int(add_in_db_pr):
                add_word_self(word, word_dict, word_sql, word_parser, 6)

        else:
            add_word(word, word_dict, word_sql, 3)


def add_word_self(word, word_dict, word_sql, word_parser, default_pr):
    '''add the word or phrase to database.'''
    input_msg = "please input word meaning\n"
    update_flag = 0
    if sys.version_info[0] == 2:
        word_basic = raw_input(input_msg)
    else:
        word_basic = input(input_msg)

    if add_word(word, word_dict, word_sql, default_pr):
        word_sql.update_word("user_defined='%s', pr=%d" % (word_basic, default_pr), 
                                "name='%s'" % (word))

def add_word(word, word_dict, word_sql, default_pr):
    '''add the word or phrase to database.'''
    count = word_sql.count_word("name = '%s'" % word)
    if count > 0:
        #update : 这里可以提示是否更新，如果有某个字段不一致或者上次查询时间比较旧
        print(colored(word + ' 在数据库中已存在，不需要添加', 'white', 'on_red'))
        sys.exit()

    if "name" not in word_dict:
        word_dict["name"] = word
    if "pr" not in word_dict:
        word_dict["pr"] = default_pr
    #update: 这里可以添加模糊查询,通过某个参数指定，先显示近似查询，然后选择某一个后，再具体查询
    return word_sql.insert_word(word_dict)


def delete_word(word, word_sql):
    '''delete the word or phrase from database. fix bug'''
    count = word_sql.count_word("name='%s'" % word)
    if count:
        word_sql.delete_word("name='%s'" % word)
    else:
        print(colored('%s not exists in the database' % word, 'white', 'on_red'))


def set_priority(word, pr, word_sql):
    '''
    set the priority of the word.
    priority(from 1 to 5) is the importance of the word.
    '''
    count = word_sql.count_word("name='%s'" % word)
    if count:
        if word_sql.update_word("pr=%d", "name='%s'" % (pr, word)):
            print(colored('the priority of  %s has been reset to  %s' % (word, pr), 'green'))
        else:
            print(colored('something\'s wrong, you can\'t reset priority', 'white', 'on_red'))
    else:
        print(colored('%s not exists in the database' % word, 'white', 'on_red'))

def list_priority(pr, word_sql, displayer, vb=False, output=False):
    '''
    list words by priority, like this:
    1   : list words which the priority is 1,
    2+  : list words which the priority is lager than 2,
    3-4 : list words which the priority is from 3 to 4.
    '''
    word_dict_list = []
    if len(pr) == 1:
        word_dict_list = word_sql.select_word("pr == %d ORDER by pr, name" % (int(pr[0])))
    elif len(pr) == 2 and pr[1] == '+':
        word_dict_list = word_sql.select_word("pr >= %d ORDER by pr, name" % (int(pr[0])))
    elif len(pr) == 3 and pr[1] == '-':
        word_dict_list = word_sql.select_word("pr >= %d AND pr <= %d ORDER by pr, name" % (int(pr[0]), int(pr[2])))

    for word_dict in word_dict_list:
        displayer.show(word_dict)


def list_latest(limit, word_sql, displayer, card=False, vb=False, output=False):
    '''list words by latest time you add to database.'''
    
    word_dict_list = word_sql.select_word("name is not NULL ORDER BY datatime(addtime) DESC LIMIT %d" % limit)
    for word_dict in word_dict_list:
        displayer.show(word_dict)


def list_review(word_sql, displayer, reviewer, is_card, is_output):
    reviewer.add_interval_day(1)
    reviewer.add_interval_day(3)
    reviewer.add_interval_day(7)
    
    return reviewer.get_words(word_sql, displayer)




def super_insert(input_file_path, word_parser):
    log_file_path = os.path.join(DEFAULT_PATH, 'log.txt')
    baseurl = 'http://dict.youdao.com/w/'
    word_list = open(input_file_path, 'r', encoding='utf-8')
    log_file = open(log_file_path, 'w', encoding='utf-8')

    conn = sqlite3.connect(os.path.join(DEFAULT_PATH, 'word.db'))
    curs = conn.cursor()

    for line in word_list.readlines():
        word = line.strip()
        print(word)
        url = baseurl + word
        word_dict = word_parser.get_text(url)
        try:
            # insert into database.
            curs.execute("INSERT INTO Word(name, synonyms, discriminate, word_group, collins, bilingual, fanyiToggle, pr, aset) VALUES \
                         (\"%s\", \"%s\", \"%s\", %d, \"%s\")" \
                         % (word, synonyms, discriminate, word_group, collins, bilingual, fanyiToggle, 1, word[0].upper()))
        except Exception as e:
            print(word, "can't insert into database")
            # save the error in log file.
            print(e)
            log_file.write(word + '\n')
    conn.commit()
    curs.close()
    conn.close()
    log_file.close()
    word_list.close()


def register_argument(parser):
    parser.add_argument(dest='word', help='the word you want to search.', nargs='*')

    parser.add_argument('-a', '--add', dest='add',
                        action='store', nargs='+', help='insert word into database.')

    parser.add_argument('-d', '--delete', dest='delete',
                        action='store', nargs='+', help='delete word from database.')

    parser.add_argument('-c', '--card', dest='card',
                        action='store_true', help='card mode.')

    parser.add_argument('-f', '--file', dest='file',
                        action='store', help='add words list from text file.')

    parser.add_argument('-s', '--set', dest='set',
                        action='store', help='set priority.')

    parser.add_argument('-v', '--verbose', dest='verbose',
                        action='store_true', help='verbose mode.')

    parser.add_argument('-o', '--output', dest='output',
                        action='store_true', help='output mode.')

    parser.add_argument('-p', '--priority', dest='priority',
                        action='store', help='list words by priority.')

    parser.add_argument('-r', '--review', dest='review',
                        action='store_true', help='review words by time class')

    parser.add_argument('-t', '--time', dest='time',
                        action='store', help='list words by time.')



def main():
    # 显示模式设置
    displayer = Displayer()
    # 设置解析模式
    word_parser = Parser()
    # 设置复习模式
    reviewer = Reviewer()
    # 数据库连接
    word_sql = Word_sql()

    parser = argparse.ArgumentParser(description='Search words')

    register_argument(parser)

    args = parser.parse_args()
    is_verbose = args.verbose
    is_output = args.output
    is_card = args.card

    #设置参数，可以每次打开，可以根据查询次数，对单词进行权重排序，提示复习
    #或者手动输入命令更新优先级
    #应该能支持不同显示版本

    if args.add:
        #这个用于导入批量单词，基本还是用查询
        default_pr = 1 if not args.set else int(args.set)
        #add_word(' '.join(args.add), None, default_pr)

    elif args.delete:
        delete_word(' '.join(args.delete), word_sql)

    elif args.set:
        number = args.set
        if not number.isdigit():
            print(colored('you forget to set the number', 'white', 'on_red'))
            sys.exit()
        priority = int(number)
        if args.word:
            set_priority(' '.join(args.word), priority, word_sql)
        else:
            print(colored('please set the priority', 'white', 'on_red'))

    elif args.time:
        limit = int(args.time)
        list_latest(limit, word_sql, displayer, is_card, is_verbose, is_output)

    elif args.review:
        list_review(word_sql, displayer, reviewer, is_card, is_output)


    elif args.priority:
        list_priority(args.priority, word_sql, displayer, is_verbose, is_output)

    elif args.file:
        input_file_path = args.file
        if input_file_path.endswith('.txt'):
            super_insert(input_file_path, word_parser)
        elif input_file_path == 'default':
            super_insert(os.path.join(DEFAULT_PATH, 'word_list.txt'), word_parser)
        else:
            print(colored('please use a correct path of text file', 'white', 'on_red'))

    elif args.word:
        word = ' '.join(args.word)
        search_word(word, word_parser, word_sql, displayer)


if __name__ == '__main__':
    main()
