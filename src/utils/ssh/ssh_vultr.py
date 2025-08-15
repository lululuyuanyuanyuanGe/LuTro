import paramiko
import time
import asyncio
import asyncssh


class VultrSSH:
    def __init__(self, vps_ip, vps_password):
        self.ssh_client = None
        self.vps_ip = vps_ip
        self.vps_password = vps_password
    
    def connect(self):
        """
        Establish SSH connection to the server
        """
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            password = self.vps_password
            host = self.vps_ip

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
            
            # Apply replacements if provided
            if replacements:
                for placeholder, value in replacements.items():
                    script_content = script_content.replace(placeholder, str(value))
            
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
    
    async def _create_async_ssh_connection(self):
        """Create an async SSH connection using asyncssh"""
        try:
            conn = await asyncssh.connect(
                self.vps_ip,
                username='root',
                password=self.vps_password,
                known_hosts=None,
                connect_timeout=30
            )
            return conn
        except Exception as e:
            print(f"❌ Async SSH connection failed: {e}")
            return None
    
    async def execute_script_async(self, script_content, script_file_path, timeout=300):
        """
        Execute a bash script on the remote server asynchronously
        
        Args:
            script_content (str): The bash script content to execute
            timeout (int): Script execution timeout in seconds
            
        Returns:
            dict: {'success': bool, 'stdout': str, 'stderr': str, 'exit_code': int}
        """
        conn = await self._create_async_ssh_connection()
        if not conn:
            return {'success': False, 'error': 'No SSH connection established'}
        
        try:
            print(f"📤 Executing script {script_file_path} on remote server (async)...")
            
            # Execute the script
            result = await conn.run(script_content, timeout=timeout)
            
            return_data = {
                'success': result.exit_status == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'exit_code': result.exit_status
            }
            
            if not return_data['success']:
                if result.stderr:
                    return_data['error'] = result.stderr
            
            return return_data
            
        except Exception as e:
            print(f"❌ Script execution error (async): {e}")
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    async def execute_script_from_file_async(self, script_file_path, replacements=None, timeout=300):
        """
        Read and execute a bash script from file with optional placeholder replacements (async)
        
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
            
            # Apply replacements if provided
            if replacements:
                for placeholder, value in replacements.items():
                    script_content = script_content.replace(placeholder, str(value))
            
            # Execute the modified script
            return await self.execute_script_async(script_content, script_file_path, timeout)
            
        except FileNotFoundError:
            return {'success': False, 'error': f'Script file not found: {script_file_path}'}
        except Exception as e:
            return {'success': False, 'error': f'Error reading script file: {e}'}
    
    async def execute_multiple_scripts_async(self, script_configs):
        """
        Execute multiple scripts concurrently
        
        Args:
            script_configs (list): List of script configurations
                [{'file_path': str, 'replacements': dict, 'timeout': int}, ...]
                
        Returns:
            list: List of execution results in the same order as input
        """
        tasks = []
        for config in script_configs:
            task = self.execute_script_from_file_async(
                config['file_path'],
                config.get('replacements'),
                config.get('timeout', 300)
            )
            tasks.append(task)
        
        print(f"🔄 Executing {len(tasks)} scripts concurrently...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions that occurred
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                results[i] = {'success': False, 'error': str(result)}
        
        return results
    
    def execute_scripts_concurrently(self, script_configs):
        """
        Synchronous wrapper for executing multiple scripts concurrently
        
        Args:
            script_configs (list): List of script configurations
                [{'file_path': str, 'replacements': dict, 'timeout': int}, ...]
                
        Returns:
            list: List of execution results in the same order as input
        """
        return asyncio.run(self.execute_multiple_scripts_async(script_configs))
    
    def execute_script_from_file_concurrent(self, script_file_path, replacements=None, timeout=300):
        """
        Synchronous wrapper for executing a single script asynchronously
        
        Args:
            script_file_path (str): Path to the bash script file
            replacements (dict): Dictionary of placeholder replacements {placeholder: value}
            timeout (int): Script execution timeout in seconds
            
        Returns:
            dict: {'success': bool, 'stdout': str, 'stderr': str, 'exit_code': int}
        """
        return asyncio.run(self.execute_script_from_file_async(script_file_path, replacements, timeout))
