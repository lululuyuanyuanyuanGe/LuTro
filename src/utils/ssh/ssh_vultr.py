import paramiko
import time

from vultr.vultr import vultrServer

class VultrSSH:
    def __init__(self):
        self.ssh_client = None
    
    def connect(self):
        """
        Establish SSH connection to the server
        """
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            password = vultrServer.server_instance["server_password"]
            host = vultrServer.server_instance["main_ip"]

            if password:
                # Connect using password
                self.ssh_client.connect(host, username="root", password=password, timeout=30)
            else:
                raise ValueError("Password must be provided")
            
            print(f"✅ SSH connection established to {host}")
            return True
            
        except Exception as e:
            print(f"❌ SSH connection failed: {e}")
            return False
    
    def execute_script(self, script_content, timeout=300):
        """
        Execute a bash script on the remote server
        
        Args:
            script_content (str): The bash script content to execute
            timeout (int): Script execution timeout in seconds
            
        Returns:
            dict: {'success': bool, 'stdout': str, 'stderr': str, 'exit_code': int}
        """
        self.connect()
        if not self.ssh_client:
            return {'success': False, 'error': 'No SSH connection established'}
        
        try:
            print("📤 Executing script on remote server...")
            
            # Execute the script
            stdin, stdout, stderr = self.ssh_client.exec_command(script_content, timeout=timeout)
            
            # Wait for completion and get results
            exit_code = stdout.channel.recv_exit_status()
            stdout_data = stdout.read().decode('utf-8')
            stderr_data = stderr.read().decode('utf-8')
            
            result = {
                'success': exit_code == 0,
                'stdout': stdout_data,
                'stderr': stderr_data,
                'exit_code': exit_code
            }
            
            if result['success']:
                print("✅ Script executed successfully")
            else:
                print(f"❌ Script execution failed with exit code: {exit_code}")
                if stderr_data:
                    print(f"Error output: {stderr_data}")
            
            return result
            
        except Exception as e:
            print(f"❌ Script execution error: {e}")
            return {'success': False, 'error': str(e)}
    
    def execute_script_from_file(self, script_file_path, replacements=None, timeout=300):
        """
        Read and execute a bash script from file with optional placeholder replacements
        
        Args:
            script_file_path (str): Path to the bash script file
            replacements (dict): Dictionary of placeholder replacements {placeholder: value}
            timeout (int): Script execution timeout in seconds
            
        Returns:
            dict: {'success': bool, 'stdout': str, 'stderr': str, 'exit_code': int}
        """
        try:
            # Read the script file
            with open(script_file_path, 'r') as file:
                script_content = file.read()
                print(script_content)
            
            # Apply replacements if provided
            if replacements:
                for placeholder, value in replacements.items():
                    script_content = script_content.replace(placeholder, str(value))
                print(f"📝 Applied {len(replacements)} placeholder replacements")
            
            # Execute the modified script
            return self.execute_script(script_content, timeout)
            
        except FileNotFoundError:
            return {'success': False, 'error': f'Script file not found: {script_file_path}'}
        except Exception as e:
            return {'success': False, 'error': f'Error reading script file: {e}'}
    
    def wait_for_ssh_ready(self, host, username='root', password=None, private_key_path=None, 
                          max_attempts=20, delay=30):
        """
        Wait for SSH service to become available on the server
        
        Args:
            host (str): Server IP address
            username (str): SSH username
            password (str): SSH password (if using password auth)
            private_key_path (str): Path to private key (if using key auth)
            max_attempts (int): Maximum connection attempts
            delay (int): Delay between attempts in seconds
            
        Returns:
            bool: True if SSH becomes available, False if timeout
        """
        print(f"⏳ Waiting for SSH to become available on {host}...")
        
        for attempt in range(1, max_attempts + 1):
            print(f"🔄 SSH connection attempt {attempt}/{max_attempts}")
            
            if self.connect(host, username, password, private_key_path, timeout=10):
                self.disconnect()
                return True
            
            if attempt < max_attempts:
                print(f"⏳ Waiting {delay} seconds before next attempt...")
                time.sleep(delay)
        
        print("❌ SSH connection timeout - server may not be ready")
        return False
    
    def disconnect(self):
        """Close the SSH connection"""
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
            print("🔌 SSH connection closed")

# Convenience function for quick script execution
def execute_remote_script(host, script_file_path, username='root', password=None, 
                         private_key_path=None, replacements=None):
    """
    Convenience function to quickly execute a script on a remote server
    
    Args:
        host (str): Server IP address
        script_file_path (str): Path to bash script file
        username (str): SSH username
        password (str): SSH password
        private_key_path (str): Path to private key file
        replacements (dict): Placeholder replacements
        
    Returns:
        dict: Execution result
    """
    ssh = VultrSSH()
    
    # Wait for SSH to be ready
    if not ssh.wait_for_ssh_ready(host, username, password, private_key_path):
        return {'success': False, 'error': 'SSH service not available'}
    
    # Connect and execute script
    if ssh.connect(host, username, password, private_key_path):
        result = ssh.execute_script_from_file(script_file_path, replacements)
        ssh.disconnect()
        return result
    
    return {'success': False, 'error': 'Failed to establish SSH connection'}

