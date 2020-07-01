import json
import os
from log import write_log


def userconfig_exists():
    if os.path.exists(os.path.expanduser('~') + r'\NeteaseCloudMusicProxy\UserConfig.json'):
        return True
    return False


def add_config(key, value):
    if not os.path.exists(os.path.expanduser('~') + r'\NeteaseCloudMusicProxy'):
        os.mkdir(os.path.expanduser('~') + r'\NeteaseCloudMusicProxy')
    try:
        if userconfig_exists():
            with open(os.path.expanduser('~') + r'\NeteaseCloudMusicProxy\UserConfig.json', mode='r') as configfile:
                config = json.load(configfile)
                config[key] = value
                jsonfile = json.dumps(config)
            with open(os.path.expanduser('~') + r'\NeteaseCloudMusicProxy\UserConfig.json', mode='w') as configfile:
                configfile.write(jsonfile)
            return True
        else:

            config = {}
            with open(os.path.expanduser('~') + r'\NeteaseCloudMusicProxy\UserConfig.json', mode='w') as configfile:
                config[key] = value
                configfile.write(json.dumps(config))
            return True
    except Exception as e:
        write_log(e)
        return False


def read_config(key):
    try:
        if not userconfig_exists():
            return False
        with open(os.path.expanduser('~') + r'\NeteaseCloudMusicProxy\UserConfig.json', mode='r') as configfile:
            config = json.loads(configfile.read())
            return config[key]
    except Exception as e:
        write_log(e)
        return False


if __name__ == '__main__':
    # print(userconfig_exists())
    # print(add_config('NeteaseCloudMusicPath', r'D:\Apps\CloudMusic'))
    print(read_config('NeteaseCloudMusicPath'))
