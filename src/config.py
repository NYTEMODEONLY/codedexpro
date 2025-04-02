import os
import json

class Config:
    def __init__(self):
        # Default configuration
        self.defaults = {
            "debug": False,
            "camera_index": 0,
            "auto_detect": True,
            "scan_interval": 350,
            "scan_cooldown": 1.5
        }
        
        # Load settings from config file if it exists
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
        self.load_config()
        
    def load_config(self):
        """Load configuration from JSON file or use defaults"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                    
                # Set configuration from file, with fallback to defaults
                self.debug_mode = config_data.get('debug', self.defaults['debug'])
                self.camera_index = config_data.get('camera_index', self.defaults['camera_index'])
                self.auto_detect = config_data.get('auto_detect', self.defaults['auto_detect'])
                self.scan_interval = config_data.get('scan_interval', self.defaults['scan_interval'])
                self.scan_cooldown = config_data.get('scan_cooldown', self.defaults['scan_cooldown'])
            else:
                # Use defaults and create config file
                self.debug_mode = self.defaults['debug']
                self.camera_index = self.defaults['camera_index']
                self.auto_detect = self.defaults['auto_detect']
                self.scan_interval = self.defaults['scan_interval']
                self.scan_cooldown = self.defaults['scan_cooldown']
                self.save_config()
        except Exception as e:
            print(f"Error loading configuration: {e}")
            # Use defaults as fallback
            self.debug_mode = self.defaults['debug']
            self.camera_index = self.defaults['camera_index']
            self.auto_detect = self.defaults['auto_detect']
            self.scan_interval = self.defaults['scan_interval']
            self.scan_cooldown = self.defaults['scan_cooldown']
                
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
        # App settings
        elif key == 'debug_mode':
            self.debug_mode = bool(value)
        # Auto detection settings 
        elif key == 'auto_detect':
            self.auto_detect = bool(value)
        elif key == 'scan_interval':
            self.scan_interval = int(value)
        elif key == 'scan_cooldown':
            self.scan_cooldown = float(value)
        else:
            return False
            
        # Save the updated configuration
        self.save_config()
        return True
    
    def save_config(self):
        """Save current configuration to JSON file"""
        config_data = {
            'debug': self.debug_mode,
            'camera_index': self.camera_index,
            'auto_detect': self.auto_detect,
            'scan_interval': self.scan_interval,
            'scan_cooldown': self.scan_cooldown
        }
        
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            print(f"Error saving configuration: {e}") 