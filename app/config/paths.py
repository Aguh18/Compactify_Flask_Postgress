import os

class PathConfig:
    def __init__(self):
        self.base_path = "/app/app/static"
        self.upload_path = "/app"

    def get_module_path(self, module_name):
        return f"{self.base_path}/{module_name}"

    def get_uploads_path(self, module_name):
        return f"{self.base_path}/{module_name}/uploads"

    def get_downloads_path(self, module_name):
        return f"{self.base_path}/{module_name}/downloads"

    def get_database_path(self, module_name, filename):
        return f"{module_name}/downloads/{filename}"

    def get_full_file_path(self, relative_path):
        return f"{self.upload_path}/{relative_path}"

    def ensure_directories(self, module_name):
        module_path = self.get_module_path(module_name)
        uploads_path = self.get_uploads_path(module_name)
        downloads_path = self.get_downloads_path(module_name)

        os.makedirs(module_path, exist_ok=True)
        os.makedirs(uploads_path, exist_ok=True)
        os.makedirs(downloads_path, exist_ok=True)

        return {
            'module_path': module_path,
            'uploads_path': uploads_path,
            'downloads_path': downloads_path
        }

path_config = PathConfig()

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
    return MODULE_MAPPING.get(controller_name.lower(), controller_name)