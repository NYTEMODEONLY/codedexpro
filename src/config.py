import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        # Load environment variables from .env file if it exists
        load_dotenv()
        
        # Camera settings
        self.camera_index = int(os.environ.get('CAMERA_INDEX', '0'))
        
        # App settings
        self.debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
        
        # Auto detection settings
        self.auto_detect = os.environ.get('AUTO_DETECT', 'True').lower() == 'true'
        self.scan_interval = int(os.environ.get('SCAN_INTERVAL', '500'))  # milliseconds
        self.scan_cooldown = float(os.environ.get('SCAN_COOLDOWN', '2.0'))  # seconds
                
    def update_setting(self, key, value):
        """
        Update a configuration setting.
        
        Args:
            key: Setting key
            value: Setting value
        """
        # Camera settings
        if key == 'camera_index':
            self.camera_index = int(value)
            env_key = 'CAMERA_INDEX'
        # App settings
        elif key == 'debug_mode':
            self.debug_mode = str(value).lower() == 'true'
            env_key = 'DEBUG'
        # Auto detection settings 
        elif key == 'auto_detect':
            self.auto_detect = str(value).lower() == 'true'
            env_key = 'AUTO_DETECT'
        elif key == 'scan_interval':
            self.scan_interval = int(value)
            env_key = 'SCAN_INTERVAL'
        elif key == 'scan_cooldown':
            self.scan_cooldown = float(value)
            env_key = 'SCAN_COOLDOWN'
        else:
            return False
            
        # Update .env file
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
        
        # Read existing content if file exists
        env_content = {}
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if '=' in line:
                        k, v = line.strip().split('=', 1)
                        env_content[k] = v
        
        # Update setting
        env_content[env_key] = str(value)
        
        # Write back to file
        with open(env_path, 'w') as f:
            for k, v in env_content.items():
                f.write(f"{k}={v}\n")
                
        return True 