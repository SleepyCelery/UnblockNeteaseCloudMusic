from ruamel import yaml


def ConfigMerge():
    with open('config.yaml', mode='r', encoding='utf-8') as configfile:
        config = yaml.safe_load(configfile.read())
    for i in config['proxy-groups']:
        if i.get('proxies') == ['DIRECT'] and "网易云音乐" in i.get('name'):
            del i['proxies']
    with open('config.yaml', mode='w', encoding='utf-8') as configfile:
        yaml.dump(config, configfile, default_flow_style=False)


if __name__ == '__main__':
    ConfigMerge()
