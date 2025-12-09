"""
Dynamic Path Configuration Module
Centralized path management for all file operations
"""

import os

class PathConfig:
    def __init__(self):
        # Base paths
        self.base_path = "/app/app/static"
        self.upload_path = "/app"

    def get_module_path(self, module_name):
        """
        Get the full path for a specific module

        Args:
            module_name (str): Name of the module (e.g., 'CompressImg', 'removeBackground')

        Returns:
            str: Full path to the module directory
        """
        return f"{self.base_path}/{module_name}"

    def get_uploads_path(self, module_name):
        """
        Get the uploads path for a specific module

        Args:
            module_name (str): Name of the module

        Returns:
            str: Full path to the uploads directory
        """
        return f"{self.base_path}/{module_name}/uploads"

    def get_downloads_path(self, module_name):
        """
        Get the downloads path for a specific module

        Args:
            module_name (str): Name of the module

        Returns:
            str: Full path to the downloads directory
        """
        return f"{self.base_path}/{module_name}/downloads"

    def get_database_path(self, module_name, filename):
        """
        Get the database storage path (relative path)

        Args:
            module_name (str): Name of the module
            filename (str): Name of the file

        Returns:
            str: Relative path for database storage
        """
        return f"{module_name}/downloads/{filename}"

    def get_full_file_path(self, relative_path):
        """
        Get the full file path from relative path

        Args:
            relative_path (str): Relative path from database

        Returns:
            str: Full path to the file
        """
        return f"{self.upload_path}/{relative_path}"

    def ensure_directories(self, module_name):
        """
        Create necessary directories for a module

        Args:
            module_name (str): Name of the module
        """
        module_path = self.get_module_path(module_name)
        uploads_path = self.get_uploads_path(module_name)
        downloads_path = self.get_downloads_path(module_name)

        # Create directories if they don't exist
        os.makedirs(module_path, exist_ok=True)
        os.makedirs(uploads_path, exist_ok=True)
        os.makedirs(downloads_path, exist_ok=True)

        return {
            'module_path': module_path,
            'uploads_path': uploads_path,
            'downloads_path': downloads_path
        }

# Create global instance
path_config = PathConfig()

# Module name mapping (optional: for different naming conventions)
MODULE_MAPPING = {
    'compressimg': 'CompressImg',
    'compressimgcontroller': 'CompressImg',
    'removebg': 'removeBackground',
    'removebgcontroller': 'removeBackground',
    'imagetopdf': 'imagetopdf',
    'imagetopdfcontroller': 'imagetopdf',
    'imgtogray': 'imgtogray',
    'imgtograycontroller': 'imgtogray',
    'compresspdf': 'CompressPdf',
    'compresspdfcontroller': 'CompressPdf',
    'wordtopdf': 'docToPdf',
    'wordtopdfcontroller': 'docToPdf',
    'zip': 'zip',
    'zipcontroller': 'zip',
    'compressaudio': 'CompressAudio',
    'audiocompresscontroller': 'CompressAudio'
}

def get_module_name(controller_name):
    """
    Get module name from controller name

    Args:
        controller_name (str): Name of the controller

    Returns:
        str: Module name
    """
    return MODULE_MAPPING.get(controller_name.lower(), controller_name)