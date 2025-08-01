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
```bash
chmod +x startup.sh
./startup.sh
```

### 3. Access the System
- http://localhost:8080/login

## Setting Develop Environment:
```
1. Install and Start Ollama
2. Install MariaDB v10.11 and create database accounts. The account credentials must match those defined in env.
3. Initialize the database      : Execute all SQL files under the init-db directory.
4. Set up environment variables : Copy env.example to .env and place it in the project root directory.
5. Create working directories   : documents faiss_data logs models
6. Upgrade Python pip           : pip install --upgrade pip
7. Install Python dependencies: : pip install -r requirements.txt
8. Start FastAPI server         : uvicorn app.app:app --host 127.0.0.1 --port 8080
```

### Overview
| note | Photo |
|------|-------|
|**Login**   |<img width="1920" height="951" alt="image" src="https://github.com/user-attachments/assets/68358aaf-95d5-43b0-8400-49a0e70f7bd0" />|
|**Register**|<img width="1917" height="994" alt="image" src="https://github.com/user-attachments/assets/eff2f0f3-0d80-46ec-899e-e4c5ba58e35e" />|
|**Chat**    |<img width="1913" height="944" alt="image" src="https://github.com/user-attachments/assets/36fdd090-08dd-4afe-b2fa-cd58bd26568c" />|
|**File Upload And Index Build**                          |<img width="1918" height="636" alt="image" src="https://github.com/user-attachments/assets/3cc5cde7-3323-4059-9f2f-b86d5539e388" />|
|**backend setting `system prompt word embedding ollama`**|<img width="1919" height="993" alt="image" src="https://github.com/user-attachments/assets/e365ffe5-8bfe-487b-9938-73b17994cd90" />|
|**basic account setting**                                |<img width="1918" height="764" alt="image" src="https://github.com/user-attachments/assets/109338bc-05d5-4a99-b31a-dfa63a1a6e9a" />|
|**basic user panel**                                     |<img width="297" height="476" alt="image" src="https://github.com/user-attachments/assets/71d6d8ba-8a12-4125-85be-140ba794c90f" />|





