import __init__
import os
import configparser
from pathlib import Path

class MIRA_SYS_CONFIG():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.MIRA_SYS_CONFIG_PATH = self.config.read(Path(__init__.MIRA_SYS_CONFIG_PATH).resolve())    
        
    def update_ini_file(self, section: str, key_word: str, new_value: str):
        """
        Update a specific key_word in an INI file.

        Args:
            file_path (str): Path to the INI file.
            section (str): Section name in the INI file.
            key_word (str): Key to be updated in the specified section.
            new_value (str): New value to set for the key_word.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        # Initialize the configparser
        config = configparser.ConfigParser()
        config.read(self.MIRA_SYS_CONFIG_PATH)

        # Check if the section exists
        if section in config:
            # Check if the key_word exists in the section
            if key_word in config[section]:
                # Update the existing key_word with the new value
                config[section][key_word] = new_value
            else:
                # If the key_word does not exist, add it
                config.set(section, key_word, new_value)
        else:
            # If the section does not exist, add it and the key_word
            config.add_section(section)
            config.set(section, key_word, new_value)

        # Save the updated configuration back to the INI file
        with open(str(self.MIRA_SYS_CONFIG_PATH), "w") as config_file:
            config.write(config_file)

        return True


