import os

SHOW_SAVE_DB_CONFIRM_MESSAGE = "SHOW_SAVE_DB_CONFIRM_MESSAGE"
DEFAULT_SAVE_DB_LEVEL = "DEFAULT_SAVE_DB_LEVEL"
PROXY = "PROXY"

DEFAULT_CONFIG = {
    SHOW_SAVE_DB_CONFIRM_MESSAGE : False,
    DEFAULT_SAVE_DB_LEVEL: "3",
    PROXY: None
}

CONFIG_FILE_DIRECTORIES = [
    os.curdir, 
    os.path.join(os.path.expanduser('~'), '.iSearch'), # default path
    os.path.join(os.path.expanduser('~'), '.config', 'iSearch'), 
    "/etc/iSearch", 
    os.getenv("ISEARCH_CONF", "NotFound") # add fault tolerance
]

config = None

'''
    simple parser to parse key-value format file to avoid introduce new library
    eg.
        skipSaveDbConfirmMessage=True
        defaultSaveDbLevel=3
'''
def parseConfigFile(configFile):
    global config
    config = {}
    with open(configFile, 'r') as reader:
        rawConfig = reader.read()
        lines = rawConfig.split("\n")
        for line in lines:
            if line.startswith("#") or len(line) == 0:
                continue
            key, value = map(str.strip, line.split("="))
            config[key] = True if value.lower() == "true" else False if value.lower() == "false" else value
    
    config = setDefaultConfig(config)
    return config

def setDefaultConfig(config):
    if SHOW_SAVE_DB_CONFIRM_MESSAGE not in config:
        config[SHOW_SAVE_DB_CONFIRM_MESSAGE] = DEFAULT_CONFIG[SHOW_SAVE_DB_CONFIRM_MESSAGE]
    if DEFAULT_SAVE_DB_LEVEL not in config:
        config[DEFAULT_SAVE_DB_LEVEL] = DEFAULT_CONFIG[DEFAULT_SAVE_DB_LEVEL]
    if PROXY not in config:
        config[PROXY] = None
    return config

def getConfig():
    global config
    if config is not None:
        return config

    # https://stackoverflow.com/questions/7567642/where-to-put-a-configuration-file-in-python
    for loc in CONFIG_FILE_DIRECTORIES:
        try: 
            return parseConfigFile(os.path.join(loc, "iSearch.txt")) # return the first found config file
        except IOError:
            pass
        except FileNotFoundError:
            pass
            
    return DEFAULT_CONFIG

# test code
# print(getConfig())