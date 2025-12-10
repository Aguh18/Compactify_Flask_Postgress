import os

class PathConfig:
    """
    Simplified PathConfig for R2 storage
    Since we use R2 only, this mostly provides module naming
    """

    def __init__(self):
        # R2 doesn't need local paths, but keep for compatibility
        self.base_path = ""
        self.upload_path = ""

    def get_module_path(self, module_name):
        """Get R2 module path"""
        return module_name

    def get_uploads_path(self, module_name):
        """Get R2 uploads path (same as module path)"""
        return module_name

    def get_downloads_path(self, module_name):
        """Get R2 downloads path (same as module path)"""
        return module_name

    def get_database_path(self, module_name, filename):
        """Get database path format for R2"""
        return f"{module_name}/{filename}"

    def get_full_file_path(self, relative_path):
        """
        Get full file path - for R2 this returns the key
        This method kept for compatibility with existing code
        """
        return relative_path

    def ensure_directories(self, module_name):
        """
        For R2, directories are created automatically
        This method kept for compatibility with existing code
        """
        return {
            'module_path': module_name,
            'uploads_path': module_name,
            'downloads_path': module_name
        }

def get_module_name(controller_name):
    """Extract module name from controller name"""
    return controller_name.lower().replace('controller', '')

# Global instance for backward compatibility
path_config = PathConfig()