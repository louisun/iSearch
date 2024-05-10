import requests
import bs4
import re
from .display import colorful_print, normal_print
from .config import getConfig, PROXY_SETTING

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

    config = getConfig()
    if config[PROXY_SETTING]:
        proxies = {
            'http': config[PROXY_SETTING],
            'https': config[PROXY_SETTING]
        }
        res = requests.get(url, headers=my_headers, proxies=proxies)
    else:
        res = requests.get(url, headers=my_headers)

    data = res.text
    soup = bs4.BeautifulSoup(data, 'html.parser')
    expl = ''

    # -----------------collins-----------------------

    collins = soup.find('div', id="collinsResult")
    ls1 = []
    if collins:
        for s in collins.descendants:
            if isinstance(s, bs4.element.NavigableString):
                if s.strip():
                    ls1.append(s.strip())

        if ls1[1].startswith('('):
            # Phrase
            expl = expl + ls1[0] + '\n'
            line = ' '.join(ls1[2:])
        else:
            expl = expl + (' '.join(ls1[:2])) + '\n'
            line = ' '.join(ls1[3:])
        text1 = re.sub('例：', '\n\n例：', line)
        text1 = re.sub(r'(\d+\. )', r'\n\n\1', text1)
        text1 = re.sub(r'(\s+?→\s+)', r'  →  ', text1)
        text1 = re.sub('(\")', '\'', text1)
        text1 = re.sub('\s{10}\s+', '', text1)
        expl += text1

    # -----------------word_group--------------------

    word_group = soup.find('div', id='word_group')
    ls2 = []
    if word_group:
        for s in word_group.descendants:
            if isinstance(s, bs4.element.NavigableString):
                if s.strip():
                    ls2.append(s.strip())
        text2 = ''
        expl = expl + '\n\n' + '【词组】\n\n'
        if len(ls2) < 3:
            text2 = text2 + ls2[0] + ' ' + ls2[1] + '\n'
        else:
            for i, x in enumerate(ls2[:-3]):
                if i % 2:
                    text2 = text2 + x + '\n'
                else:
                    text2 = text2 + x + ' '
        text2 = re.sub('(\")', '\'', text2)
        expl += text2

    # ------------------synonyms---------------------

    synonyms = soup.find('div', id='synonyms')
    ls3 = []
    if synonyms:
        for s in synonyms.descendants:
            if isinstance(s, bs4.element.NavigableString):
                if s.strip():
                    ls3.append(s.strip())
        text3 = ''
        tmp_flag = True
        for i in ls3:
            if '.' in i:
                if tmp_flag:
                    tmp_flag = False
                    text3 = text3 + '\n' + i + '\n'
                else:
                    text3 = text3 + '\n\n' + i + '\n'
            else:
                text3 = text3 + i

        text3 = re.sub('(\")', '\'', text3)
        expl = expl + '\n\n' + '【同近义词】\n'
        expl += text3

    # ------------------discriminate------------------

    discriminate = soup.find('div', id='discriminate')
    ls4 = []
    if discriminate:
        for s in discriminate.descendants:
            if isinstance(s, bs4.element.NavigableString):
                if s.strip():
                    ls4.append(s.strip())

        expl = expl + '\n\n' + '【词语辨析】\n\n'
        text4 = '-' * 40 + '\n' + format('↓ ' + ls4[0] + ' 的辨析 ↓', '^40s') + '\n' + '-' * 40 + '\n\n'

        for x in ls4[1:]:
            if x in '以上来源于':
                break
            if re.match(r'^[a-zA-Z]+$', x):
                text4 = text4 + x + ' >> '
            else:
                text4 = text4 + x + '\n\n'

        text4 = re.sub('(\")', '\'', text4)
        expl += text4

    # ------------------else------------------

    # If no text found, then get other information

    examples = soup.find('div', id='bilingual')

    ls5 = []

    if examples:
        for s in examples.descendants:
            if isinstance(s, bs4.element.NavigableString):
                if s.strip():
                    ls5.append(s.strip())

        text5 = '\n\n【双语例句】\n\n'
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
        text5 = re.sub('(\")', '\'', text5)
        expl += text5

    return expl


def search_online(word, printer=True):
    '''search the word or phrase on http://dict.youdao.com.'''

    # interesting, either ' %s' or '%s' can be used
    url = 'http://dict.youdao.com/w/ %s' % word

    expl = get_text(url)

    if printer:
        colorful_print(expl)
    return expl


