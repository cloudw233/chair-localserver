import tomlkit, os

from core.path import config_path

def config(key:str):
    with open(os.path.join(config_path,'config.toml')) as f:
        _config = tomlkit.parse(f.read())
    return _config[key]