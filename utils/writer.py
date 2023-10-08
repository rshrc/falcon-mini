from typing import NoReturn
import yaml

def generate_config(user_id: int, filename: str='data.yaml') -> NoReturn:
    data = {
        'user': {
            'id': user_id,
        }
    }

    with open(filename, 'w') as file:
        yaml.safe_dump(data, file, default_flow_style=False)

if __name__=='__main__':    
    generate_config(123)