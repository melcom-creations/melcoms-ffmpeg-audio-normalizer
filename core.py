# -*- coding: utf-8 -*-
"""
core.py
Handles core application state, configurations, file paths, and logging.
"""

import os
import sys
import configparser
import logging
from logging.handlers import RotatingFileHandler
import constants

def get_base_path():
    """Determines the root path of the application in both frozen and script states."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

class AppLogger:
    """Thread-safe logging manager with automatic file rotation to prevent excessive memory usage."""
    
    def __init__(self, log_size_kb: int, single_entry: bool):
        self.max_bytes = log_size_kb * 1024
        self.single_entry = single_entry
        self._loggers = {}

    def log(self, filename: str, message: str, mode: str = "a") -> None:
        log_path = os.path.join(get_base_path(), filename)
        
        if self.single_entry and mode == "w":
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(message)
            return

        if filename not in self._loggers:
            logger = logging.getLogger(filename)
            logger.setLevel(logging.INFO)
            logger.propagate = False
            
            if not logger.handlers:
                handler = RotatingFileHandler(
                    log_path, maxBytes=self.max_bytes, backupCount=1, encoding='utf-8'
                )
                handler.setFormatter(logging.Formatter('%(message)s'))
                logger.addHandler(handler)
            self._loggers[filename] = logger
            
        self._loggers[filename].info(message)

class Config:
    """Handles loading, saving, and validating application settings via an INI configuration file."""
    
    def __init__(self):
        self.ffmpeg_path = ""
        self.log_file_size_kb = 1024
        self.single_log_entry_enabled = True
        self.language = constants.DEFAULT_LANGUAGE_CODE
        self.theme_mode = constants.DEFAULT_THEME_MODE
        self.load_options()

    def load_options(self):
        parser = configparser.ConfigParser()
        config_path = os.path.join(get_base_path(), constants.CONFIG_FILE_NAME)
        
        if os.path.exists(config_path):
            parser.read(config_path, encoding='utf-8')
            settings = parser[constants.CONFIG_SECTION_SETTINGS] if constants.CONFIG_SECTION_SETTINGS in parser else {}
            self.ffmpeg_path = settings.get(constants.CONFIG_KEY_FFMPEG_PATH, self._find_ffmpeg_path())
            self.log_file_size_kb = settings.getint(constants.CONFIG_KEY_LOG_FILE_SIZE, 1024)
            self.single_log_entry_enabled = settings.getboolean(constants.CONFIG_KEY_SINGLE_LOG_ENTRY, True)
            self.language = settings.get(constants.CONFIG_KEY_LANGUAGE, constants.DEFAULT_LANGUAGE_CODE)
            self.theme_mode = settings.get(constants.CONFIG_KEY_THEME_MODE, constants.DEFAULT_THEME_MODE)
        else:
            self.ffmpeg_path = self._find_ffmpeg_path()
            
        self.ensure_log_size_valid()

    def _find_ffmpeg_path(self):
        program_path = get_base_path()
        if os.path.exists(os.path.join(program_path, constants.FFMPEG_EXECUTABLE_NAME)):
            return program_path
        return ""

    def save_options(self):
        parser = configparser.ConfigParser()
        parser[constants.CONFIG_SECTION_SETTINGS] = {
            constants.CONFIG_KEY_FFMPEG_PATH: self.ffmpeg_path,
            constants.CONFIG_KEY_LOG_FILE_SIZE: str(self.log_file_size_kb),
            constants.CONFIG_KEY_SINGLE_LOG_ENTRY: str(self.single_log_entry_enabled),
            constants.CONFIG_KEY_LANGUAGE: self.language,
            constants.CONFIG_KEY_THEME_MODE: self.theme_mode
        }
        config_path = os.path.join(get_base_path(), constants.CONFIG_FILE_NAME)
        with open(config_path, "w", encoding='utf-8') as f:
            parser.write(f)

    def ensure_log_size_valid(self):
        if not isinstance(self.log_file_size_kb, int) or self.log_file_size_kb <= 0:
            self.log_file_size_kb = 1024

# Global configuration and logging instances
app_config = Config()
app_logger = AppLogger(app_config.log_file_size_kb, app_config.single_log_entry_enabled)

def reinit_logger():
    """Reinitializes the global logger instance. Required after applying configuration changes."""
    global app_logger
    app_logger = AppLogger(app_config.log_file_size_kb, app_config.single_log_entry_enabled)