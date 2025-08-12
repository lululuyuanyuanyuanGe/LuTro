import os
import requests
import json
from dotenv import load_dotenv
from utils.vultr import *

load_dotenv()

VULTR_API_KEY = os.getenv("VULTR_API_KEY")


def main():
    
    print("Fetching Vultr account information...")

    response = vultr_create_instance()
    
    if response:
        print(json.dumps(response, indent=2))

if __name__ == "__main__":
    main()
