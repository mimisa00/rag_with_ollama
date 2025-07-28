# Lightweight Retrieval-Augmented Generation System (RAG)

This project implements an enhanced retrieval system using the Ollama framework as the core platform for LLM operations. The system offers the following features:
- Account Management: Simple user registration and login functionalities
- File Upload and Extraction: Upload files and extract their contents
- Index Building: Create data indexes for semantic retrieval
- Backend Parameter Configuration: Adjustable parameters for system operation
We welcome your valuable feedback! Feel free to leave a comment or contact us via email.


##  Structure

```
rag/
├── app/                      # Python application
│   ├── app.py                # FastAPI main app
│   ├── auth.py               # Authorization control
│   ├── dao.py                # Database access
│   └── model_docling.py      # Document processing module
├── backend/                  # Backend configuration
│   ├── Dockerfile            # Container configuration
│   ├── requirements.txt      # Python dependencies
│   └── test_db_connection.py # DB connection test at startup
├── documents/                # Indexed documents storage
├── faiss_data/               # Vector data storage
├── frontend/                 # Frontend files
│   └── static/               # Static files (HTML, CSS, JS)
├── init-db/                  # DB initialization scripts
├── logs/                     # Log files
├── mariadb_data/             # Database storage
├── models/                   # Model storage
├── ollama/                   # Ollama cache
├── ollama_modelfile/         # Custom Ollama modelfiles
├── docker-compose.yml        # Docker service configuration
├── env.example               # Environment variable example
├── README.md                 # Project documentation
├── startup.ps1.sh            # Windows startup script
└── startup.sh                # Linux startup script
```

##  Getting Started

### Prerequisites
- Docker
- Git
- At least CPU 4 Core 2.2 ghz 8GB RAM
- NVIDIA GPU (optional, for acceleration)

### 1. Clone the Repository

```bash
git clone https://github.com/mimisa00/rag_with_ollama.git
cd rag_with_ollama
```

### 2. Set Up the Environment

#### Linux/macOS:
```bash
chmod +x startup.sh
./startup.sh
```

#### Windows base environment:
```powershell
1. Install and Start Ollama
2. Install MariaDB v10.11 and create database accounts. The account credentials must match those defined in env.
3. Initialize the database      : Execute all SQL files under the init-db directory.
4. Set up environment variables : Copy env.example to .env and place it in the project root directory.
5. Create working directories   : documents faiss_data logs models
6. Upgrade Python pip           : pip install --upgrade pip
7. Install Python dependencies: : pip install -r requirements.txt
8. Start FastAPI server         : uvicorn app.app:app --host 127.0.0.1 --port 8080
```

### 3. Access the System
- http://localhost:8080/login


