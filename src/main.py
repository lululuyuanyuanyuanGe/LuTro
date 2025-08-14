import os
import requests
import json
from dotenv import load_dotenv
# from vultr.vultr import vultrServer
from utils.ssh.ssh_vultr import vultrSSH
from cloudflare.api import Cloudflare
from vultr.api import vultrServer


def main():
    print("========Starting to set up trojan on your vps server========")
    print("Step 1 Delete the existing vps server")
    print("Step 2 Setting up the DNS record for your domain name to your VPS server")
    vps_ip = vultrServer.server_instance["main_ip"]
    print(vps_ip)
    cloudflare = Cloudflare(vps_ip=vps_ip)
    cloudflare.update_or_create_record(vps_ip=vps_ip)
    dns_ready = cloudflare.wait_for_dns_resolution()
    
    
    # response = vultrServer.instance
    
    # if response:
    #     print(json.dumps(response, indent=2))

if __name__ == "__main__":
    main()

    # result = vultrSSH.execute_script_from_file(script_file_path="src//utils//bash_scripts//init.bash")
    # print(result)
