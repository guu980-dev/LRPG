import yaml
import json


def load_yaml(path: str):
    with open(path, 'r', encoding='UTF8') as f:
        load_yaml = yaml.load(f, Loader=yaml.FullLoader)
    return load_yaml


def load_txt(path):
    with open(path, 'r', encoding='UTF8') as f:
        txt = f.read()
    return txt


def save_json(path, dict):
    with open(path, 'w', encoding='UTF8') as f:
        json.dump(dict, f, indent='\t', ensure_ascii=False)
    return