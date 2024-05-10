import os
import sqlite3
from termcolor import colored
from iSearch.display import colorful_print, normal_print
from iSearch.webio import get_text, search_online

# Default database path is ~/.iSearch.
DEFAULT_DB_DIRECTORY_PATH = os.path.join(os.path.expanduser('~'), '.iSearch')

CREATE_TABLE_WORD = '''
CREATE TABLE IF NOT EXISTS Word
(
name     TEXT PRIMARY KEY,
expl     TEXT,
pr       INT DEFAULT 1,
aset     CHAR[1],
addtime  TIMESTAMP NOT NULL DEFAULT (DATETIME('NOW', 'LOCALTIME'))
)
'''


def search_database(word, config):
    '''offline search.'''

    conn = sqlite3.connect(os.path.join(DEFAULT_DB_DIRECTORY_PATH, 'word.db'))
    curs = conn.cursor()
    curs.execute(r'SELECT expl, pr FROM Word WHERE name LIKE "%s%%"' % word)
    res = curs.fetchall()
    if res:
        print(colored(word + ' 在数据库中存在', 'white', 'on_green'))
        print()
        print(colored('★ ' * res[0][1], 'red'), colored('☆ ' * (5 - res[0][1]), 'yellow'), sep='')
        colorful_print(res[0][0])
    else:
        print(colored(word + ' 不在本地，从有道词典查询', 'white', 'on_red'))
        search_online(word)
        if config[SHOW_SAVE_DB_CONFIRM_MESSAGE] == True:
            input_msg = '若存入本地，请输入优先级(1~5) ，否则 Enter 跳过\n>>> '
            if sys.version_info[0] == 2:
                add_in_db_pr = raw_input(input_msg)
            else:
                add_in_db_pr = input(input_msg)
        else:
            add_in_db_pr = config[DEFAULT_SAVE_DB_LEVEL]

        if add_in_db_pr and add_in_db_pr.isdigit():
            if(int(add_in_db_pr) >= 1 and int(add_in_db_pr) <= 5):
                add_word(word, int(add_in_db_pr))
                print(colored('单词 {word} 已加入数据库中'.format(word=word), 'white', 'on_red'))
    curs.close()
    conn.close()


def add_word(word, default_pr):
    '''add the word or phrase to database.'''

    conn = sqlite3.connect(os.path.join(DEFAULT_DB_DIRECTORY_PATH, 'word.db'))
    curs = conn.cursor()
    curs.execute('SELECT expl, pr FROM Word WHERE name = "%s"' % word)
    res = curs.fetchall()
    if res:
        print(colored(word + ' 在数据库中已存在，不需要添加', 'white', 'on_red'))
        sys.exit()

    try:
        expl = search_online(word, printer=False)
        curs.execute('insert into word(name, expl, pr, aset) values ("%s", "%s", %d, "%s")' % (
            word, expl, default_pr, word[0].upper()))
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

    conn = sqlite3.connect(os.path.join(DEFAULT_DB_DIRECTORY_PATH, 'word.db'))
    curs = conn.cursor()
    # search fisrt
    curs.execute('SELECT expl, pr FROM Word WHERE name = "%s"' % word)
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

    conn = sqlite3.connect(os.path.join(DEFAULT_DB_DIRECTORY_PATH, 'word.db'))
    curs = conn.cursor()
    curs.execute('SELECT expl, pr FROM Word WHERE name = "%s"' % word)
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

    conn = sqlite3.connect(os.path.join(DEFAULT_DB_DIRECTORY_PATH, 'word.db'))
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

    conn = sqlite3.connect(os.path.join(DEFAULT_DB_DIRECTORY_PATH, 'word.db'))
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

    conn = sqlite3.connect(os.path.join(DEFAULT_DB_DIRECTORY_PATH, 'word.db'))
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
    log_file_path = os.path.join(DEFAULT_DB_DIRECTORY_PATH, 'log.txt')
    baseurl = 'http://dict.youdao.com/w/'
    word_list = open(input_file_path, 'r', encoding='utf-8')
    log_file = open(log_file_path, 'w', encoding='utf-8')

    conn = sqlite3.connect(os.path.join(DEFAULT_DB_DIRECTORY_PATH, 'word.db'))
    curs = conn.cursor()

    for line in word_list.readlines():
        word = line.strip()
        print(word)
        url = baseurl + word
        expl = get_text(url)
        try:
            # insert into database.
            curs.execute("INSERT INTO Word(name, expl, pr, aset) VALUES (\"%s\", \"%s\", %d, \"%s\")" \
                         % (word, expl, 1, word[0].upper()))
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

    conn = sqlite3.connect(os.path.join(DEFAULT_DB_DIRECTORY_PATH, 'word.db'))
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
