# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import sys
import argparse
import os
import re
import sqlite3
import requests
import bs4
from termcolor import colored

# Python2 compatibility
if sys.version_info[0] == 2:
    reload(sys)
    sys.setdefaultencoding('utf-8')

# Default database path is ~/.iSearch.
DEFAULT_PATH = os.path.join(os.path.expanduser('~'), '.iSearch')

CREATE_TABLE_WORD = '''
CREATE TABLE IF NOT EXISTS Word
(
name     TEXT PRIMARY KEY NOT NULL,
basic    TEXT,
expl     TEXT,
pr       INT DEFAULT 1,
aset     CHAR[1],
addtime  TIMESTAMP NOT NULL DEFAULT (DATETIME('NOW', 'LOCALTIME'))
)
'''
def get_info(soup, titleName, label, labelID, func):
    result = soup.find(label, id = labelID)
    wlist = []
    text = ''
    if result:
        for s in result.descendants:
            if isinstance(s, bs4.element.NavigableString):
                if s.strip():
                    wlist.append(s.strip())

        text = '\n\n' + titleName + '\n\n'
        text = func(wlist,text)
        text = re.sub('(\")', '\'', text)
    return text

def deal_word_group(wlist, text):
    if len(wlist) < 3:
        text = text + wlist[0] + ' ' + wlist[1] + '\n'
    else:
        for i, x in enumerate(wlist[:-3]):
            if i % 2:
                text = text + x + '\n'
            else:
                text = text + x + ' '
    return text

def deal_synonyms(wlist, text):
    tmp_flag = True
    for i in wlist:
        if '.' in i:
            if tmp_flag:
                tmp_flag = False
                text = text + '\n' + i + '\n'
            else:
                text = text + '\n\n' + i + '\n'
        else:
            text = text + i
    return text

def deal_discriminate(wlist, text):
    text += '-' * 40 + '\n' + format('↓ ' + wlist[0] + ' 的辨析 ↓', '^40s') + '\n' + '-' * 40 + '\n\n'

    for x in wlist[1:]:
        if x in '以上来源于':
            break
        if re.match(r'^[a-zA-Z]+$', x):
            text = text + x + ' >> '
        else:
            text = text + x + '\n\n'

    return text

def deal_collins(wlist, text):
    if wlist[1].startswith('('):
        # Phrase
        text = text + wlist[0] + '\n'
        line = ' '.join(wlist[2:])
    else:
        text = text + (' '.join(wlist[:2])) + '\n'
        line = ' '.join(wlist[3:])

    text += re.sub('例：', '\n例：', line)
    text = re.sub(r'(\d+\. )', r'\n\n\1', text)
    text = re.sub(r'(\s+?→\s+)', r'  →  ', text)
    text = re.sub('\s{10}\s+', '', text)
    return text

def deal_bilingual(ls5, text5):
    pt = re.compile(r'.*?\..*?\..*?|《.*》')

    for word in ls5:
        if not pt.match(word):
            if word.endswith(('（', '。', '？', '！', '。”', '）')):
                text5 = text5 + word + '\n\n'
                continue

            if u'\u4e00' <= word[0] <= u'\u9fa5':
                if word != '更多双语例句':
                    text5 += word
            else:
                text5 = text5 + ' ' + word
    return text5

def deal_fanyiToggle(ls6, text6):
    for word in ls6:
        if not word.startswith('以上为机器翻译结果'):
            text6 = text6 + word + '\n\n'
            continue
        break

    return text6



def get_text(url):
    my_headers = {
        'Accept': 'text/html, application/xhtml+xml, application/xml;q=0.9, image/webp, */*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN, zh;q=0.8',
        'Upgrade-Insecure-Requests': '1',
        'Host': 'dict.youdao.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) \
                       Chrome/48.0.2564.116 Safari/537.36'
    }
    res = requests.get(url, headers=my_headers)
    data = res.text
    soup = bs4.BeautifulSoup(data, 'html.parser')
    basic = ''
    expl = ''
    basic += get_info(soup, '【词组】', 'div', 'word_group', deal_word_group)
    basic += get_info(soup, '【同近义词】', 'div', 'synonyms', deal_synonyms)
    basic += get_info(soup, '【词语辨析】', 'div', 'discriminate', deal_discriminate)
    expl += get_info(soup, '【用例介绍】', 'div', 'collinsResult', deal_collins)
    expl += get_info(soup, '【双语例句】', 'div', 'bilingual', deal_bilingual)
    expl += get_info(soup, '【有道翻译】', 'div', 'fanyiToggle', deal_fanyiToggle)
    return basic,expl


def colorful_print(raw):
    '''print colorful text in terminal.'''

    lines = raw.split('\n')
    colorful = True
    detail = False
    for line in lines:
        if line:
            if line.startswith('例'):
                print(line + '\n')
                continue
            elif line.startswith('【'):
                print(colored(line, 'white', 'on_blue') + '\n')
                detail = True
                continue
            elif colorful:
                aolorful = False
                print(colored(line, 'green', None) + '\n')
                continue

            if not detail:
                print(colored(line + '\n', 'yellow'))
            else:
                print(colored(line, 'cyan') + '\n')


def normal_print(raw):
    ''' no colorful text, for output.'''
    lines = raw.split('\n')
    for line in lines:
        if line:
            print(line + '\n')


def search_online(word, printer=True):
    '''search the word or phrase on http://dict.youdao.com.'''

    url = 'http://dict.youdao.com/w/ %s' % word

    basic, expl = get_text(url)

    if printer:
        colorful_print(basic)
        colorful_print(expl)
    return basic, expl


def search_database(word):
    '''offline search.'''

    conn = sqlite3.connect(os.path.join(DEFAULT_PATH, 'word.db'))
    curs = conn.cursor()
    curs.execute(r'SELECT basic, expl, pr FROM Word WHERE name LIKE "%s%%"' % word)
    res = curs.fetchall()
    if res:
        print(colored(word + ' 在数据库中存在', 'white', 'on_green'))
        print()
        print(colored('★ ' * res[0][2], 'red'), colored('☆ ' * (5 - res[0][2]), 'yellow'), sep='')
        colorful_print(res[0][0])
        colorful_print(res[0][1])
    else:
        print(colored(word + '提示: 不在本地，从有道词典查询', 'green', 'on_grey'))
        search_online(word)
        input_msg = '若请输入优先级(1~5)，否则默认为3\n>>> '
        if sys.version_info[0] == 2:
            add_in_db_pr = raw_input(input_msg)
        else:
            add_in_db_pr = input(input_msg)

        if add_in_db_pr and add_in_db_pr.isdigit():
            if(int(add_in_db_pr) >= 1 and int(add_in_db_pr) <= 5):
                add_word(word, int(add_in_db_pr))
                print(colored('单词 {word} 已加入数据库中,优先级为{num}'.format(word=word, \
                              num=int(add_in_db_pr)),'red', 'on_cyan'))
        else:
            add_word(word, 3)
            print(colored('单词 {word} 已加入数据库中,优先级为3'.format(word=word),\
                              'red', 'on_cyan'))
    curs.close()
    conn.close()


def add_word(word, default_pr):
    '''add the word or phrase to database.'''

    conn = sqlite3.connect(os.path.join(DEFAULT_PATH, 'word.db'))
    curs = conn.cursor()
    curs.execute('SELECT basic, expl, pr FROM Word WHERE name = "%s"' % word)
    res = curs.fetchall()
    if res:
        #update : 这里可以提示是否更新，如果有某个字段不一致或者上次查询时间比较旧
        print(colored(word + ' 在数据库中已存在，不需要添加', 'white', 'on_red'))
        sys.exit()

   #update: 这里可以添加模糊查询,通过某个参数指定，先显示近似查询，然后选择某一个后，再具体查询

    try:
        basic , expl = search_online(word, printer=False)
        curs.execute('insert into word(name, basic, expl, pr, aset) values ("%s","%s" ,"%s", %d, "%s")'\
                     % ( word,basic, expl, default_pr, word[0].upper()))
    except Exception as e:
        print(colored('something\'s wrong, you can\'t add the word', 'white', 'on_red'))
        print(e)
    else:
        conn.commit()
        print(colored('%s has been inserted into database' % word, 'green'))
    finally:
        curs.close()
        conn.close()


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
    curs.execute('SELECT basic, expl, pr FROM Word WHERE name = "%s"' % word)
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


def list_letter(aset, vb=False, output=False):
    '''list words by letter, from a-z (ingore case).'''

    conn = sqlite3.connect(os.path.join(DEFAULT_PATH, 'word.db'))
    curs = conn.cursor()
    try:
        if not vb:
            curs.execute('SELECT name, pr FROM Word WHERE aset = "%s"' % aset)
        else:
            curs.execute('SELECT expl, pr FROM Word WHERE aset = "%s"' % aset)
    except Exception as e:
        print(colored('something\'s wrong, catlog is from A to Z', 'red'))
        print(e)
    else:
        if not output:
            print(colored(format(aset, '-^40s'), 'green'))
        else:
            print(format(aset, '-^40s'))

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


def list_priority(pr, vb=False, output=False):
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


def list_latest(limit, vb=False, output=False):
    '''list words by latest time you add to database.'''

    conn = sqlite3.connect(os.path.join(DEFAULT_PATH, 'word.db'))
    curs = conn.cursor()
    try:
        if not vb:
            curs.execute('SELECT name, pr, addtime FROM Word ORDER by datetime(addtime) DESC LIMIT  %d' % limit)
        else:
            curs.execute('SELECT expl, pr, addtime FROM Word ORDER by datetime(addtime) DESC LIMIT  %d' % limit)
    except Exception as e:
        print(e)
        print(colored('something\'s wrong, please set the limit', 'red'))
    else:
        for line in curs.fetchall():
            expl = line[0]
            pr = line[1]
            print('\n' + '=' * 40 + '\n')
            if not output:
                print(colored('★ ' * pr, 'red'), colored('☆ ' * (5 - pr), 'yellow'), sep='')
                colorful_print(expl)
            else:
                print('★ ' * pr + '☆ ' * (5 - pr))
                normal_print(expl)
    finally:
        curs.close()
        conn.close()


def super_insert(input_file_path):
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
        basic, expl = get_text(url)
        try:
            # insert into database.
            curs.execute("INSERT INTO Word(name, basic, expl, pr, aset) VALUES \
                         (\"%s\", \"%s\", \"%s\", %d, \"%s\")" \
                         % (word, basic, expl, 1, word[0].upper()))
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


def main():
    parser = argparse.ArgumentParser(description='Search words')

    parser.add_argument(dest='word', help='the word you want to search.', nargs='*')

    parser.add_argument('-f', '--file', dest='file',
                        action='store', help='add words list from text file.')

    parser.add_argument('-a', '--add', dest='add',
                        action='store', nargs='+', help='insert word into database.')

    parser.add_argument('-d', '--delete', dest='delete',
                        action='store', nargs='+', help='delete word from database.')

    parser.add_argument('-s', '--set', dest='set',
                        action='store', help='set priority.')

    parser.add_argument('-v', '--verbose', dest='verbose',
                        action='store_true', help='verbose mode.')

    parser.add_argument('-o', '--output', dest='output',
                        action='store_true', help='output mode.')

    parser.add_argument('-p', '--priority', dest='priority',
                        action='store', help='list words by priority.')

    parser.add_argument('-t', '--time', dest='time',
                        action='store', help='list words by time.')

    parser.add_argument('-l', '--letter', dest='letter',
                        action='store', help='list words by letter.')

    parser.add_argument('-c', '--count', dest='count',
                        action='store', help='count the word.')

    args = parser.parse_args()
    is_verbose = args.verbose
    is_output = args.output

    #设置参数，可以每次打开，可以根据查询次数，对单词进行权重排序，提示复习
    #或者手动输入命令更新优先级
    #应该能支持不同显示版本

    if args.add:
        default_pr = 1 if not args.set else int(args.set)
        add_word(' '.join(args.add), default_pr)

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
        list_letter(args.letter[0].upper(), is_verbose, is_output)

    elif args.time:
        limit = int(args.time)
        list_latest(limit, is_verbose, is_output)

    elif args.priority:
        list_priority(args.priority, is_verbose, is_output)

    elif args.file:
        input_file_path = args.file
        if input_file_path.endswith('.txt'):
            super_insert(input_file_path)
        elif input_file_path == 'default':
            super_insert(os.path.join(DEFAULT_PATH, 'word_list.txt'))
        else:
            print(colored('please use a correct path of text file', 'white', 'on_red'))
    elif args.count:
        count_word(args.count)

    elif args.word:
        if not os.path.exists(os.path.join(DEFAULT_PATH, 'word.db')):
            os.mkdir(DEFAULT_PATH)
            with open(os.path.join(DEFAULT_PATH, 'word_list.txt'), 'w') as f:
                pass
            conn = sqlite3.connect(os.path.join(DEFAULT_PATH, 'word.db'))
            curs = conn.cursor()
            curs.execute(CREATE_TABLE_WORD)
            conn.commit()
            curs.close()
            conn.close()
        word = ' '.join(args.word)
        search_database(word)


if __name__ == '__main__':
    main()
