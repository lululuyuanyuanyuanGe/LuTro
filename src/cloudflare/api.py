import os
from urllib import request, response
from dotenv import load_dotenv
import requests
import json
import time
import socket

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
            self.vps_ip = ""

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
                return response.json()
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return response.json()

    def get_domain_info(self, domain_name:str = ""):
        """
        Get the id of the domain_name
        """
        
        url = "https://api.cloudflare.com/client/v4/zones"
        params = {"name": domain_name}
        response = self._call_request(url = url, params = params, method = "GET")
        return response["result"]
    
    def get_zone_id(self, domain_name:str = ""):
        domain_info = self.get_domain_info(domain_name=domain_name)
        for domain in domain_info:
            if domain["name"] == domain_name:
                return domain["id"]
        return None

    def get_existing_records(self, zone_id, record_type="A"):
        """Get all existing DNS records of a specific type"""
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
        print("url", url)
        params = {"type": record_type}
        response = self._call_request(url = url, params=params, method = "GET")
        formatted_response = json.dumps(response, indent=2)
        print("存在的的DNS记录", formatted_response)

        return response["result"]


    def delete_dns_record(self, zone_id, record_id):
        """Delete a specific DNS record"""
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
        
        response = self._call_request(url=url, method="DELETE")
        if response:
            return True
        return False

    def create_dns_record(self, zone_id, record_name:str = "", record_type:str = "A", vps_ip:str = ""):
        """Create a DNS record"""
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
        vps_ip = self.vps_ip
        if not record_name:
            record_name = "@"
        data = {
            "type": record_type,
            "name": record_name,
            "content": vps_ip,
            "ttl": 300
        }
        response = self._call_request(url=url, params=data, method="POST")
        formated_response = json.dumps(response, indent=2)
        print("create_dns_record返回：", formated_response)

        
        return response

    def update_or_create_record(self, domain_name:str ="", record_type:str = "A", vps_ip:str = ""):
        """
        Delete existing record if it exists, then create new one
        """
        self.vps_ip = vps_ip
        if not domain_name:
            domain_name = self.domain_name
        zone_id = self.get_zone_id(domain_name=domain_name)
        # Get existing records
        existing_records = self.get_existing_records(zone_id, record_type)
        
        # Find and delete matching records
        for record in existing_records:
            if record["name"] == domain_name or record["name"] == f"{domain_name}.{self.domain_name}":
                print(f"🗑️  Found existing {record_type} record for {domain_name}, deleting...")
                print()
                self.delete_dns_record(zone_id, record["id"])
        
        # Create the new record
        response = self.create_dns_record(zone_id, domain_name, record_type, vps_ip)
        if response["success"]:
            return True
        return False

    def wait_for_dns_resolution(self, domain:str = "", vps_ip: str = "", timeout=1800, interval=5):
        """
        Block execution until DNS resolution works
        
        Args:
            domain: Domain to test (e.g., "geluyuan.com")
            vps_ip: Expected IP address (e.g., "216.128.148.99")
            timeout: Maximum wait time in seconds (default: 30 minutes)
            interval: Time between tests in seconds (default: 30 seconds)
        
        Returns:
            True if DNS resolution successful, False if timeout
        """
        vps_ip = self.vps_ip
        if not domain:
            domain = self.domain_name
        print(f"⏳ Waiting for DNS resolution: {domain} → {vps_ip}")
        
        start_time = time.time()
        test_counter = 1
        while time.time() - start_time < timeout:
            try:
                print("Test count: ", test_counter)
                resolved_ip = socket.gethostbyname(domain)
                
                if resolved_ip == vps_ip:
                    elapsed = time.time() - start_time
                    print(f"✅ DNS resolution successful! ({elapsed:.1f} seconds)")
                    return True
                else:
                    print(f"⏳ DNS not ready: {domain} → {resolved_ip} (expected: {vps_ip})")
                    test_counter += 1
            except socket.gaierror as e:
                print(f"⏳ DNS lookup failed: {e}")
            
            time.sleep(interval)
        
        print(f"❌ DNS resolution timeout after {timeout/60:.1f} minutes")
        return False

# Initiate the single instance        
cloudflare = Cloudflare()

if __name__ == "__main__":
    
    zone_id = cloudflare.get_zone_id(domain_name="geluyuan.com")
    print("zone_id: ", zone_id)
    formatted_zone_id = json.dumps(zone_id, indent=2)
    print("zone_id: ", formatted_zone_id)
    dns_record = cloudflare.update_or_create_record(domain_name="geluyuan.com", 
                                                    vps_ip="216.128.148.99")
    formatted_dns_record = json.dumps(dns_record, indent=2)
    print("dns_record: ", formatted_dns_record)
    cloudflare.wait_for_dns_resolution()
    # cloudflare.delete_dns_record(zone_id=zone_id, record_id="ca2722b7f47edeaee78af589648fc0c2")