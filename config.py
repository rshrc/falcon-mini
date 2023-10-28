import os
from dataclasses import asdict, dataclass
from typing import Any, Dict, NoReturn, Union

import requests as r
import yaml

dir = os.getcwd()

@dataclass
class UserInfo:
    uuid: str
    name: str
    address: str

@dataclass
class SubscriptionInfo:
    plan_name: str
    description: str
    price: str
    duration_months: int
    start_date: str
    end_date: str
    is_active: bool

@dataclass
class APILimits:
    daily_limit: int
    remaining_calls: int

@dataclass
class GoogleCloudSecurityFile:
    type: str
    content: Any

@dataclass
class UpdateInfo:
    update_available: bool
    update_method: str
    update_link: str

@dataclass
class Memory:
    context_limit: int

@dataclass
class Voice:
    url: str

@dataclass
class DeviceConfig:
    user_info: UserInfo
    subscription_info: SubscriptionInfo
    api_limits: APILimits
    google_cloud_security_file: GoogleCloudSecurityFile
    update_info: UpdateInfo
    memory: Memory
    voice: Voice

    @classmethod
    def from_dict(cls, data: dict):
        data = data['device_config']

        return cls(
            user_info=UserInfo(**data['user_info']),
            subscription_info=SubscriptionInfo(**data['subscription_info']),
            api_limits=APILimits(**data['api_limits']),
            google_cloud_security_file=GoogleCloudSecurityFile(**data['google_cloud_security_file']),
            update_info=UpdateInfo(**data['update_info']),
            memory=Memory(**data['memory']),
            voice=Voice(**data['voice']) 

        )

    def to_dict(self):
        return {
            "user_info": asdict(self.user_info),
            "subscription_info": asdict(self.subscription_info),
            "api_limits": asdict(self.api_limits),
            "google_cloud_security_file": asdict(self.google_cloud_security_file),
            "update_info": asdict(self.update_info),
            "memory": asdict(self.memory),
            "voice": asdict(self.voice) 

        }



def get_configuration(url: str, device_uuid: Union[str, None]) -> Union[str, DeviceConfig]:
    if device_uuid is None:
        return "No Device Set Yet!"

    url = f"{url}api/j3devices/{device_uuid}/"
    response = r.get(url)

    return DeviceConfig.from_dict(response.json())


def generate_config(user_id: int) -> NoReturn:
    data = {
        'user': {
            'id': user_id,
        }
    }

    with open(f"{dir}/utilities/data.yaml", 'w') as file:
        yaml.safe_dump(data, file, default_flow_style=False)

def read_config() -> Dict[str, Any]:
    file: str = f'{dir}/utilities/data.yaml'

    with open(file, 'r') as f:
        data: Dict[str, Any] = yaml.safe_load(f)

    return data

if __name__=='__main__':    
    # generate_config(123)

    print(read_config())