import json 
from typing import Dict 

def read_conf(fpath:str, development_state:str='local-development') -> Dict: 
    with open(fpath, 'r') as file: 
        conf = json.load(file) 
    for opts in ['dropbox_fpath', 'auth_config_fpath', 'secrets_env_fpath']: 
        conf[opts] = conf[development_state][opts] 
    for state in ['local-development', 'render-development', 'production']: 
        if state in conf: 
            del conf[state] 
    return conf