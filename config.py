import yaml

import config

app_conf = None
if not app_conf:
    app_conf = {}
    with open(r'configs/application.yaml', encoding='utf-8') as f:
        config.app_conf = yaml.safe_load(f.read())


def init():
    pass
