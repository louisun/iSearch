import sys
import os
import re
import requests
import bs4
from bs4 import BeautifulSoup
import sqlite3
from termcolor import colored
import argparse

# Set your own path of database
db_path = '/backup/Use/SearchWord/' 

def colorfulPrint(raw):
	lines = raw.split('\n')
	highlight = True
	detail = False
	for line in lines:
		if line:
			if highlight:
				highlight = False
				print(colored(line,'white','on_green')+'\n')
				continue
			elif line.startswith('例'):
				print(line+'\n')
				continue
			elif line.startswith('【'):
				highlight = True
				print(colored(line,'white','on_green')+'\n')
				highlight = False
				detail = True
				continue

			if not detail:
				print(colored(line+'\n','yellow'))
			else:
				print(colored(line,'cyan')+'\n')

def normalPrint(raw):
	lines = raw.split('\n')
	firstLine = True
	for line in lines:
		if line:
			print(line+'\n')


def search_online(word,printer=True):
	url = 'http://dict.youdao.com/w/%s'%(word)

	myHeaders = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Accept-Encoding': 'gzip, deflate, sdch',
		'Accept-Language': 'zh-CN,zh;q=0.8',
		'Upgrade-Insecure-Requests': '1',
		'Host': 'dict.youdao.com',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
	}
	res = requests.get(url, headers=myHeaders)
	data = res.text
	soup = BeautifulSoup(data, 'lxml')
	expl = ''

	# -----------------collins-----------------------
	collins = soup.find('div', id="collinsResult")
	ls1 = []
	if collins:
		for s in collins.descendants:
			if isinstance(s, bs4.element.NavigableString):
				if s.strip():
					ls1.append(s.strip())

		expl = expl + (' '.join(ls1[:2])) + '\n'

		line = ' '.join(ls1[4:])
		text1 = re.sub('例：', '\n\n例：', line)
		text1 = re.sub(r'(\d+\. )', r'\n\n\1', text1)
		text1 = re.sub(r'(\s+?→\s+)',r'  →  ',text1)
		text1 = re.sub('(\")','\'',text1)
		text1 = re.sub('\s{10}\s+','',text1)
		expl = expl + text1



	# --------------wordGroup-----------------------
	wordGroup = soup.find('div',id='wordGroup')
	ls2 = []
	if wordGroup:
		for s in wordGroup.descendants:
			if isinstance(s,bs4.element.NavigableString):
				if s.strip():
					ls2.append(s.strip())
		text2 = ''
		expl = expl + '\n\n'+'【词组】\n\n'
		if(len(ls2) < 3):
			 text2 = text2 + ls2[0]+ ' '+ls2[1]+'\n'
		else:
			for i,x in enumerate(ls2[:-3]):
				if i%2:
					text2 = text2 + x+'\n'
				else:
					text2 = text2 + x+' '
		text2 = re.sub('(\")','\'',text2)
		expl = expl + text2

	# ----------------synoyms-----------------------
	synoyms = soup.find('div',id='synonyms')
	ls3 = []
	if synoyms:
		for s in synoyms.descendants:
			if isinstance(s,bs4.element.NavigableString):
				if s.strip():
					ls3.append(s.strip())
		text3 = ''
		tmp_flag = True
		for i in ls3:
			if '.' in i:
				if tmp_flag:
					tmp_flag = False
					text3 = text3 +'\n' + i+'\n'
				else:
					text3 = text3 +'\n\n' + i+'\n'
			else:
				text3 = text3 + i

		text3 = re.sub('(\")','\'',text3)
		expl = expl + '\n\n'+'【同近义词】\n'
		expl = expl + text3


	# --------------discriminate----------------------
	discriminate = soup.find('div',id='discriminate')
	ls4 = []
	if discriminate:
		for s in discriminate.descendants:
			if isinstance(s,bs4.element.NavigableString):
				if s.strip():
					ls4.append(s.strip())

		expl = expl + '\n\n'+'【词语辨析】\n\n'
		text4 = '-'*40+'\n'+ls4[0]+'\n'+'-'*40+'\n\n'

		for x in ls4[1:]:
			if x in '以上来源于':
				break
			if re.match(r'^[a-zA-Z]+$',x):
				text4 = text4 + x + ' >> '
			else:
				text4 = text4 + x + '\n\n'

		text4 = re.sub('(\")','\'',text4)
		expl = expl + text4


	if printer:
		colorfulPrint(expl)
	return expl




def search_database(word):
	conn = sqlite3.connect(db_path+'word.db')
	curs = conn.cursor()
	curs.execute('SELECT expl, pr FROM Word WHERE name = "%s"'% (word))
	res = curs.fetchall()
	if res:
		print(colored(word+' 在数据库中存在','white','on_green'))
		print()
		print(colored('★ ' * res[0][1],'red'),colored('☆ ' * (5 - res[0][1]),'yellow'),sep='')
		colorfulPrint(res[0][0])
	else:
		print(colored(word+' 不在数据库中，从有道词典查询','white','on_red'))
		search_online(word)
	curs.close()
	conn.close()

def add_word(word):
	conn = sqlite3.connect(db_path+'word.db')
	curs = conn.cursor()
	try:
		expl = search_online(word,printer=False)
		curs.execute("insert into word(name,expl,pr,aset) values (\"%s\",\"%s\",%d,\"%s\")"%(word,expl,1,word[0].upper()))
	except Exception as e:
		print(colored('something\'s wrong, you can\'t add the word','white','on_red'))
		print(e)
	else:
		conn.commit()
		print(colored('%s has been inserted into database'%(word),'green'))
	finally:
		curs.close()
		conn.close()


def delete_word(word):
	conn = sqlite3.connect(db_path+'word.db')
	curs = conn.cursor()
	# search fisrt
	curs.execute('SELECT expl, pr FROM Word WHERE name = "%s"'% (word))
	res = curs.fetchall()

	
	if res:
		try:
			curs.execute('DELETE FROM Word WHERE name = "%s"'% (word))
		except Exception as e:     
			print(e)
		else:
			print(colored('%s has been deleted from database'%(word),'green'))
			conn.commit()
		finally:
			curs.close()
			conn.close()
	else:
		print(colored('%s not exists in the database'%(word),'white','on_red'))

	  
	

def set_priority(word,pr):
	conn = sqlite3.connect(db_path+'word.db')
	curs = conn.cursor()
	curs.execute('SELECT expl, pr FROM Word WHERE name = "%s"'% (word))
	res = curs.fetchall()
	if res:
		try:
			curs.execute('UPDATE Word SET pr=%d WHERE name = "%s"'% (pr,word))
		except Exception as e:
			print(colored('something\'s wrong, you can\'t reset priority','white','on_red'))
			print(e)
		else:
			print(colored('the priority of %s has been reset to %s'%(word,pr),'green'))
			conn.commit()
		finally:
			curs.close()
			conn.close()
	else:
		print(colored('%s not exists in the database'%(word),'white','on_red'))

def list_letter(aset,vb=False,output=False):
	conn = sqlite3.connect(db_path+'word.db')
	curs = conn.cursor()
	try:
		if not vb:
			curs.execute('SELECT name, pr FROM Word WHERE aset = "%s"'% (aset))
		else:
			curs.execute('SELECT expl, pr FROM Word WHERE aset = "%s"'% (aset))
	except Exception as e:
		print(colored('something\'s wrong, catlog is from A to Z','red'))
		print(e)
	else:
		if not output:
			print(colored(format(aset,'-^40s'),'green'))
		else:
			print(format(aset,'-^40s'))

		for line in curs.fetchall():
			expl = line[0]
			pr = line[1]
			print('\n'+'='*40+'\n')
			if not output:
				print(colored('★ ' * pr,'red',),colored('☆ ' * (5-pr),'yellow'),sep='')
				colorfulPrint(expl)
			else:
				print('★ ' * pr+'☆ ' * (5-pr))
				normalPrint(expl)
	finally:
		curs.close()
		conn.close()

def list_priority(pr,vb=False,output=False):
	conn = sqlite3.connect(db_path+'word.db')
	curs = conn.cursor()

	try:
		if not vb:
			if len(pr)==1:
				curs.execute('SELECT name, pr FROM Word WHERE pr == %d ORDER by pr,name'% (int(pr[0])))
			elif len(pr)==2 and pr[1]=='+':
				curs.execute('SELECT name, pr FROM Word WHERE pr >= %d ORDER by pr,name'% (int(pr[0])))
			elif len(pr)==3 and pr[1]=='-':
				curs.execute('SELECT name, pr FROM Word WHERE pr >= %d AND pr<= %d ORDER by pr,name'% (int(pr[0]),int(pr[2])))
		else:
			if len(pr)==1:
				curs.execute('SELECT expl, pr FROM Word WHERE pr == %d ORDER by pr,name'% (int(pr[0])))
			elif len(pr)==2 and pr[1]=='+':
				curs.execute('SELECT expl, pr FROM Word WHERE pr >= %d ORDER by pr,name'% (int(pr[0])))
			elif len(pr)==3 and pr[1]=='-':
				curs.execute('SELECT expl, pr FROM Word WHERE pr >= %d AND pr<= %d ORDER by pr,name'% (int(pr[0]),int(pr[2])))
	except Exception as e:
		print(colored('something\'s wrong, priority must be 1-5','red'))
		print(e)
	else:
		for line in curs.fetchall():
			expl = line[0]
			pr = line[1]
			print('\n'+'='*40+'\n')
			if not output:
				print(colored('★ ' * pr,'red',),colored('☆ ' * (5-pr),'yellow'),sep='')
				colorfulPrint(expl)
			else:
				print('★ ' * pr+'☆ ' * (5-pr))
				normalPrint(expl)
	finally:
		curs.close()
		conn.close()


def list_latest(limit,vb=False,output=False):
	conn = sqlite3.connect(db_path+'word.db')
	curs = conn.cursor()
	try:
		if not vb:
			curs.execute('SELECT name,pr,addtime FROM Word ORDER by datetime(addtime) DESC LIMIT %d'%(limit))
		else:
			curs.execute('SELECT expl,pr,addtime FROM Word ORDER by datetime(addtime) DESC LIMIT %d'%(limit))
	except Exception as e:
		print(e)
		print(colored('something\'s wrong, please set the limit','red'))
	else:
		for line in curs.fetchall():
			expl = line[0]
			pr = line[1]
			print('\n'+'='*40+'\n')
			if not output:
				print(colored('★ ' * pr,'red'),colored('☆ ' * (5-pr),'yellow'),sep='')
				colorfulPrint(expl)
			else:
				print('★ ' * pr+'☆ ' * (5-pr))
				normalPrint(expl)
	finally:
		curs.close()
		conn.close()

def main():
	parser = argparse.ArgumentParser(description='Search words')

	parser.add_argument(dest='word',help='the word you want to search',nargs='*')

	parser.add_argument('-a', '--add', dest='add',
						action='store', nargs='+',help='insert word into database')

	parser.add_argument('-d', '--delete', dest='delete',
						action='store', nargs='+',help='delete word from database')

	parser.add_argument('-s', '--set', dest='set',
						action='store',help='set priority')

	parser.add_argument('-v', '--verbose', dest='verbose',
						action='store_true', help='verbose mode')

	parser.add_argument('-o', '--output', dest='output',
						action='store_true', help='output mode')

	parser.add_argument('-p', '--priority', dest='priority',
						action='store', help='list words by priority')	

	parser.add_argument('-t', '--time', dest='time',
						action='store', help='list words by time')

	parser.add_argument('-l', '--letter', dest='letter',
						action='store', help='list words by letter')

	args = parser.parse_args()
	is_verbose = args.verbose
	is_output = args.output
	if args.add:
		add_word(' '.join(args.add))
	elif args.delete:
		delete_word(' '.join(args.delete))
	elif args.set:
		priority = int(args.set)
		if args.word:
			set_priority(' '.join(args.word),priority)
		else:
			print(colored('please set the priority','white','on_red'))

	elif args.letter:
		list_letter(args.letter[0].upper(),vb=is_verbose,output=is_output)
	elif args.time:
		limit = int(args.time)
		list_latest(limit,vb=is_verbose,output=is_output)
	elif args.priority:
			list_priority(args.priority,vb=is_verbose,output=is_output)

	elif args.word:
		if not os.path.exists(db_path+'word.db'):
			conn = sqlite3.connect(db_path+'word.db')
			curs = conn.cursor()
			curs.execute('create table if not exists Word(name text Primary Key, expl text,pr int default 1,aset char[1],addtime TIMESTAMP NOT NULL DEFAULT (datetime(\'now\', \'localtime\')))')
			conn.commit()
			curs.close()
			conn.close()
		word = ' '.join(args.word)
		search_database(word)
if __name__ == '__main__':
	main()
