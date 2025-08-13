import os
from urllib import request, response
from dotenv import load_dotenv
import requests

load_dotenv()

class Cloudflare:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Cloudflare, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not Cloudflare._initialized:
            Cloudflare._initialized = True
            self.cludflare_api_key = os.getenv("CLOUDFLARE_API_KEY")
            self.headers = {
                "Authorization": f"Bearer {self.cludflare_api_key}",
                "Content-Type": "application/json"
            }
            self.domain_name = os.getenv("DOMAIN_NAME")

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

    def get_domain_id(self, domain_name:str = ""):
        """
        Get the id of the domain_name
        """
        
        url = "https://api.cloudflare.com/client/v4/zones"
        params = {"name": domain_name}
        response = self._call_request(url = url, params = params, method = "GET")
        return response["result"]

    def get_existing_records(self, zone_id, record_type="A"):
        """Get all existing DNS records of a specific type"""
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
        params = {"type": record_type}
        response = self._call_request(url = url, params=params, method = "GET")

        return response["result"]


    def delete_dns_record(self, zone_id, record_id, record_name):
        """Delete a specific DNS record"""
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
        
        response = requests.delete(url, headers=self.headers)
        
        if response.status_code == 200:
            print(f"✅ Successfully deleted existing A record for {record_name}")
            return True
        else:
            print(f"❌ Error deleting record for {record_name}: {response.text}")
            return False

    def create_dns_record(self, zone_id, record_name, record_type, content):
        """Create a DNS record"""
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
        
        data = {
            "type": record_type,
            "name": record_name,
            "content": content,
            "ttl": 300
        }
        response = self._call_request(url=url, params=data, method="POST")

        
        return response["result"]

    def update_or_create_record(self, zone_id, record_name, record_type, content):
        """Delete existing record if it exists, then create new one"""
        
        # Get existing records
        existing_records = self.get_existing_records(zone_id, record_type)
        
        # Find and delete matching records
        for record in existing_records:
            if record["name"] == record_name or record["name"] == f"{record_name}.{self.domain_name}":
                print(f"🗑️  Found existing {record_type} record for {record_name}, deleting...")
                self.delete_dns_record(zone_id, record["id"], record_name)
        
        # Create the new record
        return self.create_dns_record(zone_id, record_name, record_type, content)