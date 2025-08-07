# Compactify - All-in-One File Processing Tool

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Compactify** is a powerful, free-to-use web application that provides comprehensive file processing tools. Built with Flask and modern web technologies, it offers an intuitive interface for various file operations including compression, conversion, and processing.

## 🚀 Features

### Image Processing
- **Image Compression** - Reduce image file sizes while maintaining quality
- **Image to Grayscale** - Convert colorful images to grayscale
- **Background Removal** - Remove backgrounds from images automatically
- **Image to PDF** - Convert multiple images into a single PDF document

### Document Processing
- **PDF Compression** - Compress PDF files to reduce size
- **Word to PDF** - Convert Word documents (.docx) to PDF format

### Audio Processing
- **Audio Compression** - Reduce audio file sizes with quality control

### Archive Tools
- **ZIP Creation** - Create compressed ZIP archives from multiple files

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, Tailwind CSS, Alpine.js
- **Image Processing**: Pillow (PIL)
- **Database**: PostgreSQL (optional)
- **Containerization**: Docker & Docker Compose

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.9 or higher
- pip (Python package manager)
- Git
- Docker (optional, for containerized deployment)

## 🔧 Installation

### Method 1: Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Aguh18/Compactify_Flask_Postgress.git
   cd Compactify_Flask_Postgress
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python server.py
   ```

5. **Access the application**
   Open your browser and go to `http://localhost:5000`

### Method 2: Docker Installation (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/Aguh18/Compactify_Flask_Postgress.git
   cd Compactify_Flask_Postgress
   ```

2. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   Open your browser and go to `http://localhost:5000`

### Method 3: Manual Docker Build

1. **Build the Docker image**
   ```bash
   docker build -t compactify-flask .
   ```

2. **Run the container**
   ```bash
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
     compactify-flask
   ```

## 🐳 Docker Commands

### Basic Docker Operations
```bash
# Build the image
docker build -t compactify-flask .

# Run the container
docker run -p 5000:5000 compactify-flask

# Run in background
docker run -d -p 5000:5000 compactify-flask
```

### Docker Compose Operations
```bash
# Build and start
docker-compose up --build

# Run in background
docker-compose up -d

# Stop the application
docker-compose down

# View logs
docker-compose logs -f

# Rebuild without cache
docker-compose build --no-cache
```

## 📁 Project Structure

```
Compactify_Flask_Postgress/
├── app/
│   ├── controllers/         # Route handlers
│   ├── models/             # Data models and validation
│   ├── static/             # CSS, JS, images, uploads
│   ├── templates/          # HTML templates
│   ├── service/            # Business logic
│   └── config/             # Configuration files
├── migrations/             # Database migrations
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
├── requirements.txt        # Python dependencies
├── server.py              # Application entry point
└── README.md              # This file
```

## 🚀 Usage

1. **Visit the homepage** at `http://localhost:5000`
2. **Choose a tool** from the available options
3. **Upload your files** using the drag-and-drop interface
4. **Process your files** with one click
5. **Download the results** instantly

## 🔒 Security Features

- File type validation
- Size limitations
- Secure file handling
- Input sanitization
- Error handling

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

If you have any questions or need help, please:
- Open an issue on GitHub
- Contact the maintainer

## 🎯 Roadmap

- [ ] Batch file processing
- [ ] Advanced compression algorithms
- [ ] Cloud storage integration
- [ ] API endpoints
- [ ] Mobile app support

---

**Made with ❤️ for easy file processing**
