# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LuTro is a Python-based VPN automation tool that manages Vultr VPS instances and configures them with Trojan proxy servers. The project automates the entire lifecycle from VPS creation to SSH-based configuration deployment.

## Development Commands

- **Run the application**: `python src/main.py`
- **Install dependencies**: `uv sync` (uses uv package manager)
- **Activate environment**: Dependencies are managed via uv.lock

## Architecture

### Core Components

**VultrServer (`src/vultr/vultr.py`)**
- Singleton class managing Vultr API interactions
- Handles VPS lifecycle: creation, monitoring, deletion
- Stores active server instance in `vultr_server_instance.json`
- Auto-creates new instances if none exist, otherwise loads from JSON

**VultrSSH (`src/utils/ssh/ssh_vultr.py`)**
- SSH client wrapper using paramiko
- Executes bash scripts on remote VPS instances
- Supports script execution from files with placeholder replacements
- Main method: `execute_script_from_file()` for deploying configuration scripts

**Main Application (`src/main.py`)**
- Entry point that coordinates VultrServer and VultrSSH
- Currently executes `init.bash` script on the VPS instance

### Configuration Flow

1. VultrServer checks for existing instances via API
2. If none exist, creates new Ubuntu 25.04 VPS in Chicago (ord region)
3. Waits for VPS to become active and saves instance data to JSON
4. VultrSSH connects using stored credentials and executes deployment script
5. The `init.bash` script downloads and configures Trojan proxy server

### Key Files

- `vultr_server_instance.json`: Stores active VPS instance metadata and credentials
- `src/utils/init.bash`: Trojan server installation and configuration script
- `trojan_linux_amd64/`: Contains Trojan proxy binary distribution

### Environment Variables

- `VULTR_API_KEY`: Required for Vultr API authentication (loaded via python-dotenv)

### Dependencies

- `requests`: Vultr API communication
- `paramiko`: SSH client functionality  
- `dotenv`: Environment variable management
- `uv`: Package manager (replaces pip/poetry)

## Security Notes

The codebase handles VPS deployment and proxy configuration. Server passwords are stored in JSON files and should be treated as sensitive data.