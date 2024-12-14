from termcolor import colored

def colorful_print(raw):
    '''print colorful text in terminal.'''

    lines = raw.split('\n')
    colorful = True
    detail = False
    for line in lines:
        if line:
            if colorful:
                colorful = False
                print(colored(line, 'white', 'on_green') + '\n')
                continue
            elif line.startswith('例'):
                print(line + '\n')
                continue
            elif line.startswith('【'):
                print(colored(line, 'white', 'on_green') + '\n')
                detail = True
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
