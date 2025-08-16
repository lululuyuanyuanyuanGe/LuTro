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
        print("Setting up trojan server with proper execution order...")
        domain_name = os.getenv("DOMAIN_NAME")
        
        # Step 1: Initialize trojan (must run first)
        print("Step 1: Initializing trojan server...")
        init_result = vultrSSH.execute_script_from_file_concurrent(
            script_file_path="src/utils/bash_scripts/init_trojan.bash",
            replacements={
                "{{VPS_PUBLIC_IP}}": vps_ip,
                "{{PASSWORD}}": 888
            }
        )
        
        if not init_result['success']:
            error_msg = init_result.get('error', 'Unknown error')
            if init_result.get('stderr'):
                error_msg = init_result['stderr'][:200] + "..." if len(init_result['stderr']) > 200 else init_result['stderr']
            print(f"❌ init_trojan.bash failed - Error: {error_msg}")
            return
        
        print("✅ init_trojan.bash completed successfully")
        
        # Step 2: Run certificate and webpage setup concurrently
        print("Step 2: Setting up certificate and webpage concurrently...")
        concurrent_configs = [
            {
                'file_path': "src/utils/bash_scripts/install_certificate.bash",
                'replacements': {
                    "{{DOMAIN}}": domain_name
                }
            },
            {
                'file_path': "src/utils/bash_scripts/host_webpage.bash",
                'replacements': {}
            }
        ]
        
        concurrent_results = vultrSSH.execute_scripts_concurrently(concurrent_configs)
        
        # Check concurrent scripts results
        concurrent_success = True
        for i, result in enumerate(concurrent_results):
            script_name = concurrent_configs[i]['file_path'].split('/')[-1]
            if result['success']:
                print(f"✅ {script_name} completed successfully")
            else:
                error_msg = result.get('error', 'Unknown error')
                if result.get('stderr'):
                    error_msg = result['stderr'][:200] + "..." if len(result['stderr']) > 200 else result['stderr']
                print(f"❌ {script_name} failed - Error: {error_msg}")
                concurrent_success = False
        
        # Step 3: Start trojan server (only if all previous steps succeeded)
        if concurrent_success:
            print("Step 3: Starting trojan server...")
            trojan_result = vultrSSH.execute_script_from_file_concurrent(
                script_file_path="src/utils/bash_scripts/run_trojan.bash",
                replacements={}
            )
            
            if trojan_result['success']:
                print("✅ run_trojan.bash completed successfully")
                print("🎉 Trojan server setup completed successfully!")
            else:
                error_msg = trojan_result.get('error', 'Unknown error')
                if trojan_result.get('stderr'):
                    error_msg = trojan_result['stderr'][:200] + "..." if len(trojan_result['stderr']) > 200 else trojan_result['stderr']
                print(f"❌ run_trojan.bash failed - Error: {error_msg}")
        else:
            print("❌ Certificate/webpage setup failed. Trojan server not started.")

    
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
