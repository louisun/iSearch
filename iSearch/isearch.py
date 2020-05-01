# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import sys
import argparse
import os
import re
import sqlite3
import requests
import bs4
import json
from display import Displayer
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

# func word_dict_to_json
# purpose: change list to json type, for saving
# other: because of ’ can't exist, so change it to ASCII(%27)
def word_dict_to_json(word_dict):
    word_dict["synonyms"]       = json.dumps(word_dict["synonyms"])
    word_dict["discriminate"]   = json.dumps(word_dict["discriminate"])
    word_dict["word_group"]     = json.dumps(word_dict["word_group"])
    word_dict["collins"]        = json.dumps(word_dict["collins"])
    word_dict["bilingual"]      = json.dumps(word_dict["bilingual"])
    word_dict["fanyiToggle"]    = json.dumps(word_dict["fanyiToggle"])
    for key, value in word_dict.items():
        word_dict[key] = re.sub('\'', '%27', value)

# func json_to_word_dict
# purpose: change list to json type, for saving
# other: because of ’ can't exist, so change it to ASCII(%27)
def json_to_word_dict(result):
    word_dict = {}
    word_dict["synonyms"]       = json.loads(re.sub("%27", "\'", result[1]))
    word_dict["discriminate"]   = json.loads(re.sub("%27", "\'", result[2]))
    word_dict["word_group"]     = json.loads(re.sub("%27", "\'", result[3]))
    word_dict["collins"]        = json.loads(re.sub("%27", "\'", result[4]))
    word_dict["bilingual"]      = json.loads(re.sub("%27", "\'", result[5]))
    word_dict["fanyiToggle"]    = json.loads(re.sub("%27", "\'", result[6]))

    return word_dict


def get_info(soup, titleName, label, labelID, func):
    result = soup.find(label, id = labelID)
    wlist = []
    if result:
        for s in result.descendants:
            if isinstance(s, bs4.element.NavigableString):
                if s.strip():
                    wlist.append(s.strip())

    return func(wlist)

def deal_word_group(wlist):
    word_group_list = []
    for i, x in enumerate(wlist):
        if i % 2:
            word_group_list[len(word_group_list) - 1] = word_group_list[len(word_group_list) - 1] + ' ' + x
        else:
            word_group_list.append(x) 

    return word_group_list

def deal_synonyms(wlist):
    synonyms_list = []
    tmp_text = ''
    for i in wlist:
        if '.' in i:
            #下一个元素，保存当前元素
            if '' != tmp_text:
                synonyms_list.append(tmp_text)
            #这里添加例子如下 adj. 温柔的；柔软的；脆弱的；幼稚的；难对付的
            tmp_text = i + '\n'
        else:
            #这里添加近义词 
            #2->adj. 温柔的；柔软的；脆弱的；幼稚的；难对付的\nsoft
            #2->adj. 温柔的；柔软的；脆弱的；幼稚的；难对付的\nsoft,
            #2->adj. 温柔的；柔软的；脆弱的；幼稚的；难对付的\nsoft,fond
            tmp_text = tmp_text + i

    if '' != tmp_text:
        synonyms_list.append(tmp_text)

    return synonyms_list

def deal_discriminate(wlist):
    discriminate_list = []
    if 0 == len(wlist):
        return discriminate_list

    discriminate_list.append(wlist[0])
    text = ""

    for x in wlist[1:]:
        if x in '以上来源于':
            break
        if re.match(r'^[a-zA-Z]+$', x):
            text = text + x + ' : '
        else:
            text = text + x
            discriminate_list.append(text)
            text = ""

    return discriminate_list

def deal_collins(wlist):
    text = ""
    if len(wlist) < 2:
        return text

    if wlist[1].startswith('('):
        # Phrase
        text = text + wlist[0] + '\n'
        line = ' '.join(wlist[2:])
    else:
        text = text + (' '.join(wlist[:2])) + '\n'
        line = ' '.join(wlist[3:])

    text += re.sub('例：', '\n例：', line)
    text = re.sub(r'(\d+\. )', r'\n\1', text)
    text = re.sub(r'(\s+?→\s+)', r'  →  ', text)
    text = re.sub('\s{10}\s+', '', text)

    return text.split('\n')

def deal_bilingual(ls5):
    pt = re.compile(r'.*?\..*?\..*?|《.*》')
    text5 = ""

    for word in ls5:
        if not pt.match(word):
            if word.endswith(('（', '。', '？', '！', '。”', '）')):
                text5 = text5 + word + '\n'
                continue

            if u'\u4e00' <= word[0] <= u'\u9fa5':
                if word != '更多双语例句':
                    text5 += word
            else:
                text5 = text5 + ' ' + word

    return text5.split("\n")

def deal_fanyiToggle(ls6):
    fanyiToggle_list = []
    for word in ls6:
        if not word.startswith('以上为机器翻译结果'):
            fanyiToggle_list.append(word)
            continue
        break
    
    return fanyiToggle_list



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
    word_dict = {}
    word_dict['synonyms'] = get_info(soup, '【词语解析与近义词】', 'div', 'synonyms', deal_synonyms)
    word_dict['discriminate'] = get_info(soup, '【词语辨析】', 'div', 'discriminate', deal_discriminate)
    word_dict['word_group'] = get_info(soup, '【词组】', 'div', 'wordGroup', deal_word_group)
    word_dict['collins'] = get_info(soup, '【用例介绍】', 'div', 'collinsResult', deal_collins)
    word_dict['bilingual'] = get_info(soup, '【双语例句】', 'div', 'bilingual', deal_bilingual)
    word_dict['fanyiToggle'] = get_info(soup, '【有道翻译】', 'div', 'fanyiToggle', deal_fanyiToggle)
    return word_dict


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


def search_online(word):
    '''search the word or phrase on http://dict.youdao.com.'''

    url = 'http://dict.youdao.com/w/ %s' % word

    word_dict = get_text(url)
    return word_dict


def search_database(word, displayer):
    '''offline search.'''

    conn = sqlite3.connect(os.path.join(DEFAULT_PATH, 'word.db'))
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
            word_dict = json_to_word_dict(result)
            displayer.show(word_dict)

    else:
        print(colored(word + '提示: 不在本地，从有道词典查询', 'green', 'on_grey'))
        word_dict = search_online(word)
        displayer.show(word_dict)
        input_msg = '请输入,放弃保存0，优先级(1~5)(默认为3)，6自定义\n>>> '
        if sys.version_info[0] == 2:
            add_in_db_pr = raw_input(input_msg)
        else:
            add_in_db_pr = input(input_msg)

        if add_in_db_pr and add_in_db_pr.isdigit():
            if int(add_in_db_pr) >= 1 and int(add_in_db_pr) <= 5:
                add_word(word, word_dict, int(add_in_db_pr))
            elif 0 == int(add_in_db_pr):
                print("won't insert %s into database" %(word))
            elif 6 == int(add_in_db_pr):
                add_word_self(word, 6)

        else:
            add_word(word,word_dict, 3)

    curs.close()
    conn.close()

def add_word_self(word, word_dict, default_pr):
    '''add the word or phrase to database.'''
    input_msg = "please input word meaning\n"
    update_flag = 0
    if sys.version_info[0] == 2:
        word_basic = raw_input(input_msg)
    else:
        word_basic = input(input_msg)

    try:
        if add_word(word, word_dict, default_pr):
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

def add_word(word, word_dict, default_pr):
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
        print(word_dict["synonyms"])
        word_dict_to_json(word_dict)
        print("---------------")
        print(word_dict["synonyms"])
        print(word_dict["discriminate"])
        print(word_dict["word_group"])
        print(word_dict["collins"])
        print(word_dict["bilingual"])
        print(word_dict["fanyiToggle"])
        print("---------------")

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


def list_letter(aset, card=False, vb=False, output=False):
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
                colorful_print(name)
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
        word_dict = get_text(url)
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


def main():
    # 显示模式设置
    displayer = Displayer()

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

    parser.add_argument('-c', '--count', dest='count',
                        action='store', help='count the word.')

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
        list_letter(args.letter[0].upper(), is_card, is_verbose, is_output)

    elif args.time:
        limit = int(args.time)
        list_latest(limit, is_card, is_verbose, is_output)

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
        search_database(word, displayer)


if __name__ == '__main__':
    main()
