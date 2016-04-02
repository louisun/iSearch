# -*- coding: utf-8 -*-
from __future__ import print_function

import sys
import argparse
from util import *




# If you want to use another path, set USER_PATH in util.py.
if USER_PATH:
    default_path = USER_PATH


def main():
	parser = argparse.ArgumentParser(description='Search words')

	parser.add_argument(dest='word',help='the word you want to search.',nargs='*')


	parser.add_argument('-f', '--file', dest='file',
						action='store', help='add words list from text file.')

	parser.add_argument('-a', '--add', dest='add',
						action='store', nargs='+',help='insert word into database.')

	parser.add_argument('-d', '--delete', dest='delete',
						action='store', nargs='+',help='delete word from database.')

	parser.add_argument('-s', '--set', dest='set',
						action='store',help='set priority.')

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
	elif args.file:
		input_file_path = args.file
		if input_file_path.endswith('.txt'):
			superInsert(input_file_path)
		elif input_file_path=='default':
			superInsert(os.path.join(default_path,'word_list.txt'))
		else:
			print(colored('please use a correct path of text file','white','on_red'))
	elif args.word:
		if not os.path.exists(os.path.join(default_path,'word.db')):
			os.mkdir(default_path)
			with open(os.path.join(default_path,'word_list.txt'),'w') as f:
				pass
			conn = sqlite3.connect(os.path.join(default_path,'word.db'))
			curs = conn.cursor()
			curs.execute(CREATE_TABLE_WORD)
			conn.commit()
			curs.close()
			conn.close()
		word = ' '.join(args.word)
		search_database(word)


if __name__ == '__main__':
	main()
