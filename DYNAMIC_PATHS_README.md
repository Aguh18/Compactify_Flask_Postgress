# Dynamic Path System Documentation

## Overview
Aplikasi ini menggunakan sistem path yang dinamis dan terpusat untuk semua operasi file. Sistem ini memudahkan pengelolaan direktori dan menghilangkan hard-coded paths.

## Architecture

### 1. Path Configuration Module (`app/config/paths.py`)
Centralized path management dengan class `PathConfig`:

```python
from app.config.paths import path_config

# Get module path
module_path = path_config.get_module_path('CompressImg')
# Output: /app/app/static/CompressImg

# Get uploads path
uploads_path = path_config.get_uploads_path('CompressImg')
# Output: /app/app/static/CompressImg/uploads

# Get downloads path
downloads_path = path_config.get_downloads_path('CompressImg')
# Output: /app/app/static/CompressImg/downloads
```

### 2. Base Controller (`app/controllers/base_controller.py`)
Class `BaseController` menyediakan fungsi-fungsi umum:

```python
from app.controllers.base_controller import BaseController

# Initialize
base_controller = BaseController('compressImgController')

# Setup directories
directories = base_controller.setup_directories()

# Save uploaded file
input_path, filename, uid = base_controller.save_uploaded_file(file, uid)

# Get download paths
paths = base_controller.get_download_paths(uid, filename)

# Save to database
db_path = base_controller.save_to_database(filename, uid)

# Download file
return base_controller.download_file(relative_path)
```

## Benefits

### ✅ **Dynamic & Flexible**
- Tidak ada hard-coded paths
- Mudah untuk modify struktur direktori
- Otomatis handle directory creation

### ✅ **Centralized Management**
- Semua path logic di satu tempat
- Konsistent naming convention
- Mudah maintenance

### ✅ **Error Resilient**
- Otomatis create directories
- Proper error handling
- Safe file operations

### ✅ **Container Ready**
- Compatible dengan Docker volumes
- Proper path resolution
- No manual path configuration

## Module Mappings

Setiap controller otomatis di-map ke module yang sesuai:

| Controller | Module | Directory |
|-----------|--------|-----------|
| compressImgController | CompressImg | /app/app/static/CompressImg |
| removeBgController | removeBackground | /app/app/static/removeBackground |
| imageToPdfController | imagetopdf | /app/app/static/imagetopdf |
| imageToGrayscaleController | imgtogray | /app/app/static/imgtogray |
| compressPdfController | CompressPdf | /app/app/static/CompressPdf |
| wordToPDFController | docToPdf | /app/app/static/docToPdf |
| zipController | zip | /app/app/static/zip |
| audiocompressController | CompressAudio | /app/app/static/CompressAudio |

## Directory Structure

```
/app/app/static/
├── CompressImg/
│   ├── uploads/
│   └── downloads/
├── removeBackground/
│   ├── uploads/
│   └── downloads/
├── imagetopdf/
│   ├── uploads/
│   └── downloads/
├── imgtogray/
│   ├── uploads/
│   └── downloads/
├── CompressPdf/
│   ├── uploads/
│   └── downloads/
├── docToPdf/
│   ├── uploads/
│   └── downloads/
├── zip/
│   ├── uploads/
│   └── downloads/
└── CompressAudio/
    ├── uploads/
    └── downloads/
```

## Usage Example

### Implementing New Controller

```python
from app.controllers.base_controller import BaseController

# Initialize
base_controller = BaseController('newModuleController')

def process_file():
    if request.method == "POST":
        try:
            # Setup directories
            directories = base_controller.setup_directories()

            # Save uploaded file
            input_path, filename, uid = base_controller.save_uploaded_file(file)

            # Process file
            output_path = f"{directories['downloads_path']}/{uid}processed_{filename}"
            # ... processing logic ...

            # Save to database
            file_db = base_controller.save_to_database(f"processed_{filename}", uid)

            return jsonify({"success": True, "file": file_db})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

def download_file(file):
    return base_controller.download_file(file)
```

### Database Storage

File paths disimpan di database sebagai relative path:
```
CompressImg/downloads/82783609-f166-4315-bc45-22ff6b272899processed_image.jpg
```

Saat download, path di-resolve menjadi:
```
/app/app/static/CompressImg/downloads/82783609-f166-4315-bc45-22ff6b272899processed_image.jpg
```

## Docker Integration

Path system ini sudah compatible dengan Docker volumes:

```yaml
volumes:
  - ./app/static/CompressImg:/app/app/static/CompressImg
  - ./app/static/removeBackground:/app/app/static/removeBackground
  # ... dan seterusnya
```

## Migration dari Hard-coded Paths

Jika Anda memiliki controller dengan hard-coded paths:

### Before:
```python
project_Path = "/app/app/static/CompressImg/"
if not os.path.exists(project_Path):
    os.makedirs(project_Path)
# ... manual path handling
```

### After:
```python
base_controller = BaseController('compressImgController')
directories = base_controller.setup_directories()
# ... automatic path handling
```

## Testing

Untuk test dynamic paths:

```python
from app.config.paths import path_config

# Test path resolution
print(path_config.get_module_path('CompressImg'))
print(path_config.get_uploads_path('CompressImg'))
print(path_config.get_downloads_path('CompressImg'))
```

## Troubleshooting

### Common Issues:

1. **Permission Denied**: Pastikan Docker volumes memiliki proper permissions
2. **Directory Not Found**: Path system otomatis create directories, tapi pastikan base path exists
3. **Module Name Mismatch**: Check `MODULE_MAPPING` di `paths.py` untuk proper naming

### Debug Mode:

Enable debug logging untuk path resolution:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- [ ] Support untuk custom base path configuration
- [ ] Auto-cleanup old files
- [ ] Path validation and security checks
- [ ] Support untuk multiple storage backends