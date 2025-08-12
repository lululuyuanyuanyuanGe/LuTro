# This file defines tools to interact with vultr apis
from json import load
import re
import requests

from main import VULTR_API_KEY

headers = {
        "Authorization": f"Bearer {VULTR_API_KEY}",
        "Content-Type": "application/json"
    }

def _call_request(url: str = None, params: dict = {}, method: str = "GET"):
    try:
        if method.upper() == "POST":
            response = requests.post(url, headers=headers, json=params)
        if method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, json=params)
        else:
            response = requests.get(url, headers=headers, params=params)
        
        # Check if request was successful
        if response.status_code in [200, 204]:  # 204 is common for successful actions
            if response.content:  # Check if there's content to parse
                return response.json()
            else:
                return {"success": True}
        else:
            print(f"Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def vultr_get_account_info():
    """
    Get account information from Vultr API
    """
    # Vultr API endpoint for account information
    url = "https://api.vultr.com/v2/account"
    
    
    return _call_request(url=url)

def vultr_list_vps_instances(label=None, main_ip=None, region=None):
    url = "https://api.vultr.com/v2/instances"
    
    # Build query parameters
    params = {}
    if label:
        params['label'] = label
    if main_ip:
        params['main_ip'] = main_ip
    if region:
        params['region'] = region
    
    return _call_request(url=url, params=params)

def vultr_reboot_vps_instance(instance_ids: list = []):
    """
    Reboot a VPS instance from vultr
    """
    url = "https://api.vultr.com/v2/instances/reboot" 

    if not instance_ids:
        print("instance_ids are empty")

    params = {"instance_ids": instance_ids}
    return _call_request(url = url, params=params, method="POST")


# def vultr_reinstall_vps_instance(instance_id: str = None):
#     """
#     Reinstall the operating system of a vps isntance
#     """
#     if not instance_id:
#         print("instance_id is empty")

#     params = 


def vultr_delete_instance(instance_id: str = None):
    """
    Delete an instance
    """
    if not instance_id:
        print("instance_ids are empty")

    url = f"https://api.vultr.com/v2/instances/{instance_id}"

    return _call_request(url = url, method="DELETE")

def vultr_create_instance(region: str = "ord", plan: str = "vc2_1c_1gb", label:str = "LuTro", 
                          os_id:str = "2571", backups:str = "disable", hostname:str = "Luyuan"):
    """
    Args: os_id - 2571 - Ubuntu 25.04 x64
          regions - ord - Chicago
    """

    url = "https://api.vultr.com/v2/instances"
    params = {
        "region" : region,
        "plan" : plan,
        "label": label,
        "os_id": os_id,
        "backups": backups,
        "hostname": hostname
    }

    return _call_request(url=url, params=params, method = "POST")
def vultr_list_os():
    """
    List all the operating systems with it's ids
    """
    url = "https://api.vultr.com/v2/os"

    return _call_request(url=url, method="GET")

def vultr_list_regions():
    """
    List all the regions with it's ids
    """
    url = "https://api.vultr.com/v2/os"

    return _call_request(url=url, method="GET")