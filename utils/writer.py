from typing import NoReturn, Dict, Any
import yaml
import os

dir = os.getcwd()

def generate_config(user_id: int, filename: str=f'{dir}/data.yaml') -> NoReturn:
    data = {
        'user': {
            'id': user_id,
        }
    }

    with open(filename, 'w') as file:
        yaml.safe_dump(data, file, default_flow_style=False)

def read_config() -> Dict[str, Any]:
    file: str = '{dir}/data.yaml'

    with open(file, 'r') as f:
        data: Dict[str, Any] = yaml.safe_load(f)

    return data

if __name__=='__main__':    
    # generate_config(123)

    print(read_config())