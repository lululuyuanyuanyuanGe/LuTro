# This file defines tools to interact with vultr apis
import json
import os
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class VultrServer:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VultrServer, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Only initialize once
        if not VultrServer._initialized:
            VultrServer._initialized = True
            self.VULTR_API_KEY = os.getenv("VULTR_API_KEY")
            self.headers = {
                        "Authorization": f"Bearer {self.VULTR_API_KEY}",
                        "Content-Type": "application/json"
                    }
            server_instances = self.list_vps_instances()["instances"]
            if not server_instances:
                server_instance = self.create_instance()
                while True:
                    # Store the single server instance on our vps machine
                    self.server_instance = self.get_instance(instance_id=server_instance["server_id"])
                    self.server_instance = self.server_instance["instance"]
                    print(json.dumps(self.server_instance, indent=2))
                    if self.server_instance["status"] == "active":
                        self.server_instance["server_password"] = server_instance["password"]
                        with open("data/vultr_server_instance.json", "w") as f:
                            f.write(json.dumps(self.server_instance, indent=2))
                            print(self.server_instance)
                        break
            else:
                # Load existing server instance from JSON file
                with open("data/vultr_server_instance.json", "r") as f:  # ← Use "r" for READ mode
                    self.server_instance = json.load(f)  # ← Load JSON data from file
                    print(json.dumps(self.server_instance, indent=2))

            
            
            
    def _call_request(self, url: str = None, params: dict = {}, method: str = "GET"):
        try:
            if method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=params)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.headers, json=params)
            else:
                response = requests.get(url, headers=self.headers, params=params)
            
            # Check if request was successful
            if response.status_code in [200, 201, 202, 204]:  # 204 is common for successful actions
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


    def get_account_info(self):
        """
        Get account information from Vultr API
        """
        # Vultr API endpoint for account information
        url = "https://api.vultr.com/v2/account"
        
        
        return self._call_request(url=url)

    def list_vps_instances(self, label=None, main_ip=None, region=None):
        url = "https://api.vultr.com/v2/instances"
        
        # Build query parameters
        params = {}
        if label:
            params['label'] = label
        if main_ip:
            params['main_ip'] = main_ip
        if region:
            params['region'] = region
        
        return self._call_request(url=url, params=params)

    def reboot_vps_instance(self, instance_ids: list = []):
        """
        Reboot a VPS instance from vultr
        """
        url = "https://api.vultr.com/v2/instances/reboot" 

        if not instance_ids:
            print("instance_ids are empty")

        params = {"instance_ids": instance_ids}
        return self._call_request(url = url, params=params, method="POST")


    def delete_instance(self, instance_id: str = None):
        """
        Delete an instance
        """
        if not instance_id:
            print("instance_ids are empty")

        url = f"https://api.vultr.com/v2/instances/{instance_id}"

        return self._call_request(url = url, method="DELETE")

    def create_instance(self, region: str = "ord", plan: str = "vc2-1c-1gb", label:str = "LuTro", 
                            os_id:int = 2571, backups:str = "disabled", hostname:str = "Luyuan", trojan_password:str = "888"):
        """
        Args: os_id - 2571 - Ubuntu 25.04 x64
            regions - ord - Chicago
            plan - vc2-1c-1gb - 5$/month
        """
        
        url = "https://api.vultr.com/v2/instances"
        params = {
            "region" : region,
            "plan" : plan,
            "label": label,
            "os_id": os_id,
            "backups": backups,
            "hostname": hostname,
        }

        response = self._call_request(url=url, params=params, method = "POST")

        server_id = response["instance"]["id"]
        password = response["instance"]["default_password"]
        return {
            "server_id": server_id,
            "password":  password
        }
    
    def get_instance(self, instance_id:str = ""):
        """
        Get a vps instance info
        """
        if not instance_id:
            print("Please provide an instance id")
            return

        url = f"https://api.vultr.com/v2/instances/{instance_id}"
        return self._call_request(url=url, method="GET")



    def list_os(self):
        """
        List all the operating systems with it's ids
        """
        url = "https://api.vultr.com/v2/os"

        return self._call_request(url=url, method="GET")

    def list_regions(self):
        """
        List all the regions with it's ids
        """
        url = "https://api.vultr.com/v2/os"

        return self._call_request(url=url, method="GET")


vultrServer = VultrServer()

