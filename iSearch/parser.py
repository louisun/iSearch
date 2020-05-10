#!/usr/bin/env python
# coding=utf-8

import requests
import bs4
import re

# func get_info
# purpose: find div content by id, and call func to deal with it
# return callback return  -> word part info list
def get_info(soup, label, label_attr, func):
    result = soup.find(label, attrs=label_attr)
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

    for index in range(len(word_group_list)):
        word_group_list[index] = re.sub(r'(\s+)', r' ', word_group_list[index])

    return word_group_list

def deal_basic(wlist):
    synonyms_list = []
    tmp_text = ''
    for i in wlist:
        if '.' in i or '[' in i:
            #下一个元素，保存当前元素
            if '' != tmp_text:
                synonyms_list.append(tmp_text)
            tmp_text = i
        else:
            tmp_text = tmp_text + i

    if '' != tmp_text:
        synonyms_list.append(tmp_text)

    for index in range(len(synonyms_list)):
        synonyms_list[index] = re.sub(r'(\s+)', r' ', synonyms_list[index])

    return synonyms_list

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

    for index in range(len(synonyms_list)):
        synonyms_list[index] = re.sub(r'(\n\s+)', r'\n', synonyms_list[index])

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

# 方法类
# 提供解析的各种方法
# 常见命名：word_parser
class Parser:
    @staticmethod
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
        word_dict["basic"]          = get_info(soup, 'div', {'class':'trans-container'}, deal_basic)
        word_dict["voice"]          = get_info(soup, 'div', {'class':'baav'}, deal_synonyms)
        word_dict['synonyms']       = get_info(soup, 'div', {'id':'synonyms'}, deal_synonyms)
        word_dict['discriminate']   = get_info(soup, 'div', {'id':'discriminate'}, deal_discriminate)
        word_dict['word_group']     = get_info(soup, 'div', {'id':'wordGroup'}, deal_word_group)
        word_dict['collins']        = get_info(soup, 'div', {'id':'collinsResult'}, deal_collins)
        word_dict['bilingual']      = get_info(soup, 'div', {'id':'bilingual'}, deal_bilingual)
        word_dict['fanyiToggle']    = get_info(soup, 'div', {'id':'fanyiToggle'}, deal_fanyiToggle)
        return word_dict
