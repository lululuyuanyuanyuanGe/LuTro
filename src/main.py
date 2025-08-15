import os
import requests
import json
from dotenv import load_dotenv
# from vultr.vultr import vultrServer
from utils.ssh.ssh_vultr import VultrSSH
from cloudflare.api import Cloudflare
from vultr.api import VultrServer


def main(mode):
    if mode == "on":
        print("========Starting to set up trojan on your vps server========")
        print("Delete the existing vps server...")
        print("Setting up the DNS record for your domain name to your VPS server...")
        vultrServer = VultrServer()
        vps_ip = vultrServer.server_instance["main_ip"]
        server_password = vultrServer.server_instance["server_password"]
        print(vps_ip)
        cloudflare = Cloudflare(vps_ip=vps_ip)
        cloudflare.update_or_create_record(vps_ip=vps_ip)
        cloudflare.wait_for_dns_resolution()
        vultrSSH = VultrSSH(vps_ip=vps_ip, vps_password=server_password)
        print("Setting up trojan server with all components...")
        domain_name = os.getenv("DOMAIN_NAME")
        
        # First run the setup scripts concurrently
        setup_configs = [
            {
                'file_path': "src/utils/bash_scripts/init_trojan.bash",
                'replacements': {
                    "{{VPS_PUBLIC_IP}}": vps_ip,
                    "{{PASSWORD}}": 888
                }
            },
            
            {
                'file_path': "src/utils/bash_scripts/host_webpage.bash",
                'replacements': {}
            }
        ]
        
        print("Running setup scripts concurrently...")
        setup_results = vultrSSH.execute_scripts_concurrently(setup_configs)
        
        # Check if all setup scripts succeeded
        all_setup_successful = True
        for i, result in enumerate(setup_results):
            script_name = setup_configs[i]['file_path'].split('/')[-1]
            if result['success']:
                print(f"✅ {script_name} completed successfully")
            else:
                error_msg = result.get('error', 'Unknown error')
                if result.get('stderr'):
                    error_msg = result['stderr'][:200] + "..." if len(result['stderr']) > 200 else result['stderr']
                print(f"❌ {script_name} failed - Error: {error_msg}")
                all_setup_successful = False
        
        # Only run trojan if all setup scripts succeeded
        if all_setup_successful:
            print("All setup complete. Starting trojan server...")
            trojan_result = vultrSSH.execute_script_from_file_concurrent(
                script_file_path="src/utils/bash_scripts/run_trojan.bash",
                replacements={}
            )
            
            if trojan_result['success']:
                print("✅ Trojan server started successfully")
            else:
                print(f"❌ Trojan server failed to start: {trojan_result.get('error', 'Unknown error')}")
        else:
            print("❌ Setup failed. Trojan server not started.")

    
    elif mode == "off":
        vultrServer = VultrServer()
        vultrServer.delete_instance()
    
    
    # response = vultrServer.instance
    
    # if response:
    #     print(json.dumps(response, indent=2))

if __name__ == "__main__":
    main("on")
    # main("off")

    # result = vultrSSH.execute_script_from_file(script_file_path="src//utils//bash_scripts//init.bash")
    # print(result)
