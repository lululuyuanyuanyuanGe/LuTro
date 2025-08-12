import os
import requests
import json
from dotenv import load_dotenv
from utils.vultr import *

load_dotenv()

VULTR_API_KEY = os.getenv("VULTR_API_KEY")


def main():
    
    print("Invoking api calls .........")

    response = vultr_list_os()
    
    if response:
        print(json.dumps(response, indent=2))

if __name__ == "__main__":
    main()
