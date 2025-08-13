import os
import requests
import json
from dotenv import load_dotenv
# from vultr.vultr import vultrServer
from utils.ssh.ssh_vultr import *


def main():
    
    print("Invoking api calls .........")

    # response = vultrServer.instance
    
    # if response:
    #     print(json.dumps(response, indent=2))

if __name__ == "__main__":
    vultrSSH = VultrSSH()
    # result = vultrSSH.execute_script_from_file(script_file_path="src//utils//bash_scripts//init.bash")
    # print(result)
