# Compactify - All-in-One File Processing Tool

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🌟 Apa itu Compactify?

**Compactify** adalah aplikasi web gratis yang menyediakan berbagai tools untuk memproses file secara online. Dengan antarmuka yang modern dan intuitif, Compactify memungkinkan Anda untuk mengkompress, mengkonversi, dan memanipulasi berbagai jenis file tanpa perlu menginstall software tambahan.

### 🎯 Mengapa Compactify?

- **Gratis & Open Source** - Sepenuhnya gratis tanpa batasan
- **Mudah Digunakan** - Interface drag-and-drop yang intuitif
- **Aman & Privat** - File diproses secara lokal, tidak disimpan di server
- **Multi-Format** - Support berbagai format file populer
- **Modern UI** - Dibangun dengan teknologi web terkini
- **Cross-Platform** - Berjalan di semua sistem operasi

## 🚀 Fitur Utama

### 📸 Image Processing
- **Image Compression** - Kompres gambar dengan kualitas terjaga
- **Image to Grayscale** - Konversi gambar berwarna ke hitam putih
- **Background Removal** - Hapus background gambar secara otomatis
- **Image to PDF** - Gabungkan multiple gambar menjadi satu PDF

### 📄 Document Processing
- **PDF Compression** - Kurangi ukuran file PDF
- **Word to PDF** - Konversi dokumen Word (.docx) ke PDF

### 🎵 Audio Processing
- **Audio Compression** - Kompres file audio dengan kontrol kualitas

### 📦 Archive Tools
- **ZIP Creation** - Buat arsip ZIP dari multiple files

## 🛠️ Teknologi yang Digunakan

**Backend:**
- **Flask** - Python web framework yang lightweight
- **Pillow (PIL)** - Library untuk image processing
- **OpenCV** - Computer vision untuk advanced image processing
- **rembg** - AI-powered background removal
- **PyPDF2** - PDF manipulation
- **python-docx** - Word document processing

**Frontend:**
- **HTML5 & CSS3** - Struktur dan styling modern
- **Tailwind CSS** - Utility-first CSS framework
- **Alpine.js** - Minimal JavaScript framework
- **FontAwesome** - Icon library

**Infrastructure:**
- **PostgreSQL** - Database (optional)
- **Docker** - Containerization
- **Gunicorn** - WSGI HTTP server

## 📋 Prerequisites

Pastikan sistem Anda sudah terinstall:
- **Python 3.9+** ([Download Python](https://python.org/downloads))
- **Git** ([Download Git](https://git-scm.com/downloads))
- **Docker** (opsional, untuk containerized deployment)

## � Quick Start & Tutorial

### Method 1: Local Development Setup (Recommended untuk Development)

#### Step 1: Clone Repository
```bash
# Clone project dari GitHub
git clone https://github.com/Aguh18/Compactify_Flask_Postgress.git

# Masuk ke direktori project
cd Compactify_Flask_Postgress
```

#### Step 2: Setup Python Virtual Environment
```bash
# Buat virtual environment
python -m venv venv

# Aktivasi virtual environment
# Untuk Linux/macOS:
source venv/bin/activate

# Untuk Windows:
venv\Scripts\activate
```

#### Step 3: Install Dependencies
```bash
# Install semua package yang diperlukan (67 dependencies)
pip install -r requirements.txt

# Verify installation
pip list | grep Flask
```

#### Step 4: Run the Application
```bash
# Jalankan aplikasi
python server.py

# Atau menggunakan Flask command dengan debug mode
flask --app server run --debug --host=0.0.0.0 --port=5000
```

#### Step 5: Access Application
Buka browser dan akses: **http://localhost:5000**

---

### Method 2: Docker Setup (Recommended untuk Production)

#### Step 1: Clone Repository
```bash
git clone https://github.com/Aguh18/Compactify_Flask_Postgress.git
cd Compactify_Flask_Postgress
```

#### Step 2: Build Docker Image
```bash
# PENTING: Command harus include titik (.) di akhir untuk build context
docker build -t compactify .

# Build dengan tag spesifik
docker build -t compactify:v1.0 .

# Jika mendapat error permission denied, jalankan:
sudo usermod -aG docker $USER
# Kemudian logout/login kembali atau:
newgrp docker
```

#### Step 3: Run Docker Container
```bash
# Run container sederhana
docker run -p 5000:5000 compactify

# Run dengan volume mapping (recommended untuk persistent storage)
docker run -p 5000:5000 \
  -v $(pwd)/app/static/uploads:/app/app/static/uploads \
  -v $(pwd)/app/static/CompressImg:/app/app/static/CompressImg \
  -v $(pwd)/app/static/CompressPdf:/app/app/static/CompressPdf \
  -v $(pwd)/app/static/docToPdf:/app/app/static/docToPdf \
  -v $(pwd)/app/static/imagetopdf:/app/app/static/imagetopdf \
  -v $(pwd)/app/static/imgtogray:/app/app/static/imgtogray \
  -v $(pwd)/app/static/removeBackground:/app/app/static/removeBackground \
  -v $(pwd)/app/static/zip:/app/app/static/zip \
  -v $(pwd)/app/static/CompressAudio:/app/app/static/CompressAudio \
  compactify

# Run in background (detached mode)
docker run -d -p 5000:5000 --name compactify-app compactify
```

---

### Method 3: Docker Compose (Easiest & Fastest)

#### Step 1: One Command Setup
```bash
# Clone repository
git clone https://github.com/Aguh18/Compactify_Flask_Postgress.git
cd Compactify_Flask_Postgress

# Build dan jalankan sekaligus
docker-compose up --build

# Atau run in background
docker-compose up -d --build
```

#### Step 2: Management Commands
```bash
# Stop aplikasi
docker-compose down

# Lihat logs real-time
docker-compose logs -f

# Restart aplikasi
docker-compose restart

# Rebuild tanpa cache
docker-compose build --no-cache
```

## 🔧 Development Commands

### Local Development Workflow
```bash
# Aktivasi virtual environment
source venv/bin/activate  # Linux/macOS
# atau
venv\Scripts\activate     # Windows

# Install new dependencies
pip install package-name
pip freeze > requirements.txt

# Run dengan debug mode
export FLASK_ENV=development  # Linux/macOS
set FLASK_ENV=development     # Windows
python server.py
```

### Docker Development
```bash
# Build ulang setelah code changes
docker build -t compactify .

# Run dengan bind mount untuk live code changes
docker run -p 5000:5000 \
  -v $(pwd):/app \
  -e FLASK_ENV=development \
  compactify

# Masuk ke container untuk debugging
docker exec -it compactify-app bash
```

## � Troubleshooting

### Common Issues & Solutions

#### ❌ Issue 1: Port sudah digunakan
```bash
# Error: "Port 5000 is already in use"
# Solution: Gunakan port lain
python server.py --port 8000
# atau
docker run -p 8000:5000 compactify
```

#### ❌ Issue 2: Docker permission denied
```bash
# Error: "permission denied while trying to connect to the Docker daemon"
# Solution: Add user to docker group
sudo usermod -aG docker $USER
newgrp docker  # Apply tanpa logout
```

#### ❌ Issue 3: Build context error
```bash
# Error: "docker buildx build requires 1 argument"
# Solution: Pastikan ada titik (.) di akhir command
docker build -t compactify .  # CORRECT
# bukan: docker build -t compactify  # WRONG
```

#### ❌ Issue 4: Python dependencies error
```bash
# Error: ModuleNotFoundError
# Solution: Install missing dependencies
pip install -r requirements.txt

# Atau update pip first
pip install --upgrade pip
```

#### ❌ Issue 5: File upload permission error
```bash
# Error: Permission denied saat upload files
# Solution: Set correct permissions
chmod -R 755 app/static/
```

## 🧪 Testing Your Installation

### Manual Testing Checklist
Setelah aplikasi berjalan, test fitur-fitur berikut:

- [ ] **Homepage** - Akses http://localhost:5000 berhasil
- [ ] **Image Compression** - Upload gambar, compress, dan download
- [ ] **PDF Compression** - Upload PDF, compress, dan download
- [ ] **Document Conversion** - Upload .docx, convert ke PDF
- [ ] **Background Removal** - Upload gambar, remove background
- [ ] **Image to Grayscale** - Convert gambar ke hitam putih
- [ ] **Image to PDF** - Multiple gambar jadi satu PDF
- [ ] **Audio Compression** - Compress file audio
- [ ] **ZIP Creation** - Buat archive dari multiple files

### Performance Test
```bash
# Test dengan gunicorn (production server)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 server:app

# Monitor resource usage
docker stats compactify-app  # untuk Docker
top -p $(pgrep python)       # untuk local
```

## 📁 Project Structure

```
Compactify_Flask_Postgress/
├── app/
│   ├── controllers/         # Route handlers untuk setiap fitur
│   │   ├── compressImgController.py      # Image compression
│   │   ├── compressPdfController.py      # PDF compression  
│   │   ├── removeBgController.py         # Background removal
│   │   ├── imageToGrayscaleController.py # Grayscale conversion
│   │   ├── imageToPdfController.py       # Image to PDF
│   │   ├── wordToPDFController.py        # Word to PDF
│   │   ├── audiocompressController.py    # Audio compression
│   │   └── zipController.py              # ZIP creation
│   ├── models/             # Data models dan validation
│   │   ├── fileModel.py                  # File handling model
│   │   └── validate/                     # Input validation
│   ├── static/             # Frontend assets
│   │   ├── src/                          # Source CSS/JS
│   │   ├── image/                        # UI images
│   │   └── uploads/                      # User uploaded files
│   ├── templates/          # HTML templates (Jinja2)
│   │   ├── home.html                     # Landing page
│   │   ├── master/layout.html            # Base template
│   │   ├── CompressImg/                  # Image compression UI
│   │   ├── CompressPdf/                  # PDF compression UI
│   │   └── ... (other feature templates)
│   ├── service/            # Business logic
│   └── config/             # Database configuration
├── migrations/             # Alembic database migrations
├── Dockerfile              # Container configuration
├── docker-compose.yml      # Multi-service orchestration
├── requirements.txt        # 67 Python dependencies
├── server.py              # Flask application entry point
└── README.md              # Documentation lengkap
```

## 🎯 Cara Menggunakan Compactify

### 1. Akses Aplikasi
Buka browser dan kunjungi `http://localhost:5000`

### 2. Pilih Tool yang Diinginkan
Dari homepage, pilih salah satu dari 8 tools yang tersedia:
- **Compress Image** - Kurangi ukuran file gambar
- **Compress PDF** - Kurangi ukuran file PDF
- **Remove Background** - Hapus background gambar otomatis
- **Image to Grayscale** - Ubah gambar berwarna jadi hitam putih
- **Image to PDF** - Gabung multiple gambar jadi PDF
- **Word to PDF** - Convert dokumen Word ke PDF
- **Compress Audio** - Kurangi ukuran file audio
- **Create ZIP** - Buat arsip ZIP dari multiple files

### 3. Upload Files
- **Drag & Drop** file ke area upload
- Atau **klik** untuk browse dan pilih file
- Support multiple file selection (untuk beberapa tools)

### 4. Process Files
- Klik tombol **"Process"** atau **"Compress"**
- Tunggu proses selesai (ada progress indicator)
- File akan diproses sesuai tool yang dipilih

### 5. Download Results
- Setelah selesai, tombol **"Download"** akan muncul
- Klik untuk download hasil processed file
- File tersimpan dengan nama yang sudah diformat

## 🔒 Keamanan & Privasi

### File Security
- **Validasi Format** - Hanya file dengan ekstensi yang diizinkan
- **Size Limitation** - Ada batasan ukuran file upload
- **Temporary Storage** - File dihapus setelah proses selesai
- **Input Sanitization** - Semua input divalidasi dan dibersihkan

### Privacy Protection
- **No Cloud Storage** - File diproses lokal, tidak disimpan di cloud
- **Auto Cleanup** - File temporary dihapus otomatis
- **No User Tracking** - Tidak ada tracking user data
- **GDPR Compliant** - Tidak menyimpan data personal

## 🤝 Contributing

Kami welcome kontribusi dari siapa saja! Jika ingin berkontribusi:

1. **Fork repository** ini
2. **Create feature branch** (`git checkout -b feature/FiturBaru`)
3. **Commit changes** (`git commit -m 'Add: Fitur baru yang amazing'`)
4. **Push ke branch** (`git push origin feature/FiturBaru`)
5. **Open Pull Request** dengan deskripsi yang jelas

### Development Setup untuk Contributors
```bash
# Clone your fork
git clone https://github.com/your-username/Compactify_Flask_Postgress.git
cd Compactify_Flask_Postgress

# Add upstream remote
git remote add upstream https://github.com/Aguh18/Compactify_Flask_Postgress.git

# Create development branch
git checkout -b development

# Setup development environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Areas yang Butuh Kontribusi
- [ ] **UI/UX Improvements** - Better design dan user experience
- [ ] **New Features** - Additional file processing tools
- [ ] **Performance** - Optimization untuk large files
- [ ] **Testing** - Unit tests dan integration tests
- [ ] **Documentation** - Improve docs dan tutorials
- [ ] **Internationalization** - Support multiple languages

## 📞 Support & Contact

Jika ada pertanyaan, bug reports, atau butuh bantuan:

### GitHub Issues
- **Bug Reports**: [Create Issue](https://github.com/Aguh18/Compactify_Flask_Postgress/issues/new?template=bug_report)
- **Feature Requests**: [Create Issue](https://github.com/Aguh18/Compactify_Flask_Postgress/issues/new?template=feature_request)
- **Questions**: [Discussions](https://github.com/Aguh18/Compactify_Flask_Postgress/discussions)

### Quick Help
```bash
# Check application status
curl http://localhost:5000/health  # (if health endpoint exists)

# View application logs
docker logs compactify-app

# Debug mode
export FLASK_DEBUG=True
python server.py
```

## 📈 Performance & Analytics

### System Requirements
**Minimum:**
- RAM: 512MB
- Storage: 1GB free space
- Python: 3.9+

**Recommended:**
- RAM: 2GB+
- Storage: 5GB+ free space  
- CPU: 2+ cores
- SSD storage untuk better I/O performance

### Monitoring
```bash
# Monitor Docker container
docker stats compactify-app

# Monitor Python process
htop -p $(pgrep -f "python server.py")

# Check disk usage
df -h app/static/
```

## 🔮 Future Roadmap

### Version 2.0 (Planned)
- [ ] **Batch Processing** - Process multiple files sekaligus
- [ ] **Advanced Compression** - Algorithm lebih canggih
- [ ] **Cloud Integration** - Google Drive, Dropbox support
- [ ] **API Endpoints** - RESTful API untuk developers
- [ ] **User Accounts** - Save preferences dan history

### Version 2.5 (Future)
- [ ] **Mobile App** - React Native atau Flutter
- [ ] **Real-time Collaboration** - Multiple users
- [ ] **AI Features** - Smart compression dengan AI
- [ ] **Plugin System** - Extensible architecture
- [ ] **Multi-language Support** - Indonesian, English, dll

## 📄 License

Project ini menggunakan **MIT License** - lihat file [LICENSE](LICENSE) untuk detail lengkap.

```
MIT License - Bebas digunakan untuk personal maupun commercial use
```

## 🏆 Credits & Acknowledgments

### Built With Love By
- **Aguh18** - Main Developer & Maintainer

### Special Thanks To
- **Flask Community** - Amazing web framework
- **Tailwind CSS** - Utility-first CSS framework  
- **Alpine.js** - Lightweight JavaScript framework
- **Open Source Community** - Untuk semua libraries yang digunakan

### Libraries & Dependencies
Compactify menggunakan 67+ open source libraries (lihat `requirements.txt`)

---

## ⭐ Star This Project

Jika Compactify berguna untuk Anda, jangan lupa beri **⭐ Star** di GitHub!

**Made with ❤️ in Indonesia untuk memudahkan file processing**

---

### Quick Commands Reference
```bash
# Local Development
git clone https://github.com/Aguh18/Compactify_Flask_Postgress.git
cd Compactify_Flask_Postgress
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt && python server.py

# Docker (Fastest)
git clone https://github.com/Aguh18/Compactify_Flask_Postgress.git
cd Compactify_Flask_Postgress && docker-compose up --build

# Access: http://localhost:5000
```
