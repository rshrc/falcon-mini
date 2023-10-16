import os
from typing import Any, Dict, NoReturn
import requests as r
import yaml

dir = os.getcwd()

def get_configuration(url, device_uuid):
    url = f"{url}/api/j3devices/{device_uuid}/"
    response = r.get(url)

    return response


def generate_config(user_id: int) -> NoReturn:
    data = {
        'user': {
            'id': user_id,
        }
    }

    with open(f"{dir}/utils/data.yaml", 'w') as file:
        yaml.safe_dump(data, file, default_flow_style=False)

def read_config() -> Dict[str, Any]:
    file: str = f'{dir}/utils/data.yaml'

    with open(file, 'r') as f:
        data: Dict[str, Any] = yaml.safe_load(f)

    return data

if __name__=='__main__':    
    # generate_config(123)

    print(read_config())