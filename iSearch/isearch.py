# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import sys
import argparse
import os
import sqlite3
from display import Displayer
from termcolor import colored
from parser import Parser

# Python2 compatibility
if sys.version_info[0] == 2:
    reload(sys)
    sys.setdefaultencoding('utf-8')

# Default database path is ~/.iSearch.
DEFAULT_PATH = os.path.join(os.path.expanduser('~'), '.iSearch')
ISCOLORED = 1

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

def search_online(word, word_parser):
    '''search the word or phrase on http://dict.youdao.com.'''

    url = 'http://dict.youdao.com/w/ %s' % word

    word_dict = word_parser.get_text(url)
    return word_dict

def search_database(word, conn, word_parser):
    '''offline search.'''
    word_dict = {}
    curs = conn.cursor()
    #模糊查询
    if '#' in word:
        curs.execute('SELECT name, synonyms, discriminate, word_group, collins, \
            bilingual, fanyiToggle, pr FROM Word WHERE name LIKE "%%%s%%"' % word)
    #具体查询
    else:
        curs.execute('SELECT name, synonyms, discriminate, word_group, collins, \
            bilingual, fanyiToggle, pr FROM Word WHERE name LIKE "%s"' % word)
    res = curs.fetchall()
    if res:
        print(colored(word + ' 在数据库中存在', 'white', 'on_green'))
        for result in res:
            print(colored('★ ' * result[7], 'red'), colored('☆ ' * (5 - result[7]), 'yellow'), sep='')
            word_dict = word_parser.json_to_word_dict(result)
    
    return word_dict

def search_word(word, word_parser, displayer):
    conn = sqlite3.connect(os.path.join(DEFAULT_PATH, 'word.db'))
    word_dict = search_database(word, conn, word_parser)
    curs = conn.cursor()
    if word_dict:
        displayer.show(word_dict)
    else:
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
                add_word(word, word_dict, word_parser, int(add_in_db_pr))
            elif 0 == int(add_in_db_pr):
                print("won't insert %s into database" %(word))
            elif 6 == int(add_in_db_pr):
                add_word_self(word, word_dict, word_parser, 6)

        else:
            add_word(word,word_dict, word_parser, 3)

    curs.close()
    conn.close()

def add_word_self(word, word_dict, word_parser, default_pr):
    '''add the word or phrase to database.'''
    input_msg = "please input word meaning\n"
    update_flag = 0
    if sys.version_info[0] == 2:
        word_basic = raw_input(input_msg)
    else:
        word_basic = input(input_msg)

    try:
        if add_word(word, word_dict, word_parser, default_pr):
            curs.execute('UPDATE word SET user_defined="%s", pr=%d, \
                     aset="%s" WHERE name="%s"' % ( word_basic, default_pr, 
                     word[0].upper(), name))

    except Exception as e:
        print(colored('something\'s wrong, you can\'t add the word', 'white', 'on_red'))
        print(e)
    else:
        conn.commit()
        print(colored('%s:%s has been inserted into database' % (word, word_basic), 'green'))
    finally:
        curs.close()
        conn.close()

def add_word(word, word_dict, word_parser, default_pr):
    '''add the word or phrase to database.'''
    conn = sqlite3.connect(os.path.join(DEFAULT_PATH, 'word.db'))
    curs = conn.cursor()
    curs.execute('SELECT synonyms, discriminate, word_group, collins, bilingual, fanyiToggle, pr FROM Word WHERE name = "%s"' % word)
    res = curs.fetchall()
    if res:
        #update : 这里可以提示是否更新，如果有某个字段不一致或者上次查询时间比较旧
        print(colored(word + ' 在数据库中已存在，不需要添加', 'white', 'on_red'))
        sys.exit()

   #update: 这里可以添加模糊查询,通过某个参数指定，先显示近似查询，然后选择某一个后，再具体查询

    try:
        word_parser.word_dict_to_json(word_dict)

        curs.execute('''insert into word(name, synonyms, discriminate, word_group,
                     collins, bilingual, fanyiToggle, pr, aset)
                     values ('%s','%s','%s','%s','%s','%s','%s', %d, '%s')'''
                     % ( word, word_dict["synonyms"], word_dict["discriminate"], word_dict["word_group"], 
                        word_dict["collins"], word_dict["bilingual"], word_dict["fanyiToggle"]
                        , default_pr, word[0].upper()))

    except Exception as e:
        print(colored('something\'s wrong, you can\'t add the word', 'white', 'on_red'))
        print(e)
        return False
    else:
        conn.commit()
        print(colored('%s has been inserted into database, 优先级为%d' % (word, default_pr), 'green'))
    finally:
        curs.close()
        conn.close()
        return True


def delete_word(word):
    '''delete the word or phrase from database.'''

    conn = sqlite3.connect(os.path.join(DEFAULT_PATH, 'word.db'))
    curs = conn.cursor()
    # search fisrt
    curs.execute('SELECT basic FROM Word WHERE name = "%s"' % word)
    res = curs.fetchall()

    if res:
        try:
            curs.execute('DELETE FROM Word WHERE name = "%s"' % word)
        except Exception as e:
            print(e)
        else:
            print(colored('%s has been deleted from database' % word, 'green'))
            conn.commit()
        finally:
            curs.close()
            conn.close()
    else:
        print(colored('%s not exists in the database' % word, 'white', 'on_red'))


def set_priority(word, pr):
    '''
    set the priority of the word.
    priority(from 1 to 5) is the importance of the word.
    '''

    conn = sqlite3.connect(os.path.join(DEFAULT_PATH, 'word.db'))
    curs = conn.cursor()
    curs.execute('SELECT synonyms, discriminate, word_group, collins, bilingual, fanyiToggle, pr FROM Word WHERE name = "%s"' % word)
    res = curs.fetchall()
    if res:
        try:
            curs.execute('UPDATE Word SET pr= %d WHERE name = "%s"' % (pr, word))
        except Exception as e:
            print(colored('something\'s wrong, you can\'t reset priority', 'white', 'on_red'))
            print(e)
        else:
            print(colored('the priority of  %s has been reset to  %s' % (word, pr), 'green'))
            conn.commit()
        finally:
            curs.close()
            conn.close()
    else:
        print(colored('%s not exists in the database' % word, 'white', 'on_red'))


def list_letter(aset, displayer, card=False, vb=False, output=False):
    '''list words by letter, from a-z (ingore case).'''

    conn = sqlite3.connect(os.path.join(DEFAULT_PATH, 'word.db'))
    curs = conn.cursor()
    try:
        if vb:
            curs.execute('SELECT name, pr, synonyms, discriminate, word_group, collins, bilingual, fanyiToggle  FROM Word WHERE aset = "%s"' % aset)
        elif card:
            curs.execute('SELECT name, pr, basic FROM Word WHERE aset = "%s"' % aset)
        else:
            curs.execute('SELECT name, pr FROM Word WHERE aset = "%s"' % aset)
    except Exception as e:
        print(colored('something\'s wrong, catlog is from A to Z', 'red'))
        print(e)
    else:
        if not output:
            print(colored(format(aset, '-^40s'), 'green'))
        else:
            print(format(aset, '-^40s'))

        for line in curs.fetchall():
            name = line[0]
            pr = line[1]
            print('\n' + '=' * 40 + '\n')
            if not output:
                print(colored('★ ' * pr, 'red', ), colored('☆ ' * (5 - pr), 'yellow'), sep='')
                displayer.show_core(name, ISCOLORED)
                if vb:
                    basic = line[2]
                    expl = line[3]
                    colorful_print(basic)
                    colorful_print(expl)
                elif card:
                    basic = line[2]
                    colorful_print(basic)
            else:
                print('★ ' * pr + '☆ ' * (5 - pr))
                normal_print(name)
    finally:
        curs.close()
        conn.close()


def list_priority(pr, displayer, vb=False, output=False):
    '''
    list words by priority, like this:
    1   : list words which the priority is 1,
    2+  : list words which the priority is lager than 2,
    3-4 : list words which the priority is from 3 to 4.
    '''

    conn = sqlite3.connect(os.path.join(DEFAULT_PATH, 'word.db'))
    curs = conn.cursor()

    try:
        if not vb:
            if len(pr) == 1:
                curs.execute('SELECT name, pr FROM Word WHERE pr ==  %d ORDER by pr, name' % (int(pr[0])))
            elif len(pr) == 2 and pr[1] == '+':
                curs.execute('SELECT name, pr FROM Word WHERE pr >=  %d ORDER by pr, name' % (int(pr[0])))
            elif len(pr) == 3 and pr[1] == '-':
                curs.execute('SELECT name, pr FROM Word WHERE pr >=  %d AND pr<=  % d ORDER by pr, name' % (
                    int(pr[0]), int(pr[2])))
        else:
            if len(pr) == 1:
                curs.execute('SELECT expl, pr FROM Word WHERE pr ==  %d ORDER by pr, name' % (int(pr[0])))
            elif len(pr) == 2 and pr[1] == '+':
                curs.execute('SELECT expl, pr FROM Word WHERE pr >=  %d ORDER by pr, name' % (int(pr[0])))
            elif len(pr) == 3 and pr[1] == '-':
                curs.execute('SELECT expl, pr FROM Word WHERE pr >=  %d AND pr<=  %d ORDER by pr, name' % (
                    int(pr[0]), int(pr[2])))
    except Exception as e:
        print(colored('something\'s wrong, priority must be 1-5', 'red'))
        print(e)
    else:
        for line in curs.fetchall():
            expl = line[0]
            pr = line[1]
            print('\n' + '=' * 40 + '\n')
            if not output:
                print(colored('★ ' * pr, 'red', ), colored('☆ ' * (5 - pr), 'yellow'), sep='')
                colorful_print(expl)
            else:
                print('★ ' * pr + '☆ ' * (5 - pr))
                normal_print(expl)
    finally:
        curs.close()
        conn.close()


def list_latest(limit, card=False, vb=False, output=False):
    '''list words by latest time you add to database.'''

    conn = sqlite3.connect(os.path.join(DEFAULT_PATH, 'word.db'))
    curs = conn.cursor()
    try:
        if vb:
            curs.execute('SELECT name, pr, addtime, synonyms, discriminate, word_group, collins, bilingual, fanyiToggle FROM Word ORDER by datetime(addtime) DESC LIMIT  %d' % limit)
        elif card:
            curs.execute('SELECT name, pr, addtime, basic FROM Word ORDER by datetime(addtime) DESC LIMIT  %d' % limit)
        else:
            curs.execute('SELECT name, pr, addtime FROM Word ORDER by datetime(addtime) DESC LIMIT  %d' % limit)
    except Exception as e:
        print(e)
        print(colored('something\'s wrong, please set the limit', 'red'))
    else:
        for line in curs.fetchall():
            name = line[0]
            pr = line[1]
            print('\n' + '=' * 40 + '\n')
            if not output:
                print(colored('★ ' * pr, 'red'), colored('☆ ' * (5 - pr), 'yellow'), sep='')
                colorful_print(name)
                if vb:
                    colorful_print(line[3])
                    colorful_print(line[4])
                elif card:
                    colorful_print(line[3])
            else:
                print('★ ' * pr + '☆ ' * (5 - pr))
                normal_print(name)
                if vb:
                    normal_print(line[3])
                    normal_print(line[4])
                elif card:
                    normal_print(line[3])
    finally:
        curs.close()
        conn.close()


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


def count_word(arg):
    '''count the number of words'''

    conn = sqlite3.connect(os.path.join(DEFAULT_PATH, 'word.db'))
    curs = conn.cursor()
    if arg[0].isdigit():
        if len(arg) == 1:
            curs.execute('SELECT count(*) FROM Word WHERE pr ==  %d' % (int(arg[0])))
        elif len(arg) == 2 and arg[1] == '+':
            curs.execute('SELECT count(*) FROM Word WHERE pr >=  %d' % (int(arg[0])))
        elif len(arg) == 3 and arg[1] == '-':
            curs.execute('SELECT count(*) FROM Word WHERE pr >=  %d AND pr<=  % d' % (int(arg[0]), int(arg[2])))
    elif arg[0].isalpha():
        if arg == 'all':
            curs.execute('SELECT count(*) FROM Word')
        elif len(arg) == 1:
            curs.execute('SELECT count(*) FROM Word WHERE aset == "%s"' % arg.upper())
    res = curs.fetchall()
    print(res[0][0])
    curs.close()
    conn.close()

def register_argument(parser):
    parser.add_argument(dest='word', help='the word you want to search.', nargs='*')

    parser.add_argument('-a', '--add', dest='add',
                        action='store', nargs='+', help='insert word into database.')

    parser.add_argument('-d', '--delete', dest='delete',
                        action='store', nargs='+', help='delete word from database.')

    parser.add_argument('-c', '--count', dest='count',
                        action='store', help='count the word.')

    parser.add_argument('-f', '--file', dest='file',
                        action='store', help='add words list from text file.')

    parser.add_argument('-s', '--set', dest='set',
                        action='store', help='set priority.')

    parser.add_argument('-v', '--verbose', dest='verbose',
                        action='store_true', help='verbose mode.')

    parser.add_argument('-ca', '--card', dest='card',
                        action='store_true', help='card mode.')

    parser.add_argument('-o', '--output', dest='output',
                        action='store_true', help='output mode.')

    parser.add_argument('-p', '--priority', dest='priority',
                        action='store', help='list words by priority.')

    parser.add_argument('-t', '--time', dest='time',
                        action='store', help='list words by time.')

    parser.add_argument('-l', '--letter', dest='letter',
                        action='store', help='list words by letter.')




def main():
    # 显示模式设置
    displayer = Displayer()
    # 设置解析模式
    word_parser = Parser()

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
        delete_word(' '.join(args.delete))

    elif args.set:
        number = args.set
        if not number.isdigit():
            print(colored('you forget to set the number', 'white', 'on_red'))
            sys.exit()
        priority = int(number)
        if args.word:
            set_priority(' '.join(args.word), priority)
        else:
            print(colored('please set the priority', 'white', 'on_red'))

    elif args.letter:
        list_letter(args.letter[0].upper(), displayer, is_card, is_verbose, is_output)

    elif args.time:
        limit = int(args.time)
        list_latest(limit, is_card, is_verbose, is_output)

    elif args.priority:
        list_priority(args.priority, displayer, is_verbose, is_output)

    elif args.file:
        input_file_path = args.file
        if input_file_path.endswith('.txt'):
            super_insert(input_file_path, word_parser)
        elif input_file_path == 'default':
            super_insert(os.path.join(DEFAULT_PATH, 'word_list.txt'), word_parser)
        else:
            print(colored('please use a correct path of text file', 'white', 'on_red'))
    elif args.count:
        count_word(args.count)

    elif args.word:
        if not os.path.exists(DEFAULT_PATH):
            os.mkdir(DEFAULT_PATH)
        if not os.path.exists(os.path.join(DEFAULT_PATH, 'word.db')):
            with open(os.path.join(DEFAULT_PATH, 'word_list.txt'), 'w') as f:
                pass
            conn = sqlite3.connect(os.path.join(DEFAULT_PATH, 'word.db'))
            curs = conn.cursor()
            curs.execute(CREATE_TABLE_WORD)
            conn.commit()
            curs.close()
            conn.close()
        word = ' '.join(args.word)
        search_word(word, word_parser, displayer)


if __name__ == '__main__':
    main()
