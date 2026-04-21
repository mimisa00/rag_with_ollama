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

## QUICK VIEW
| Advance repo | this repo |
|------|-------|
![7814](https://github.com/user-attachments/assets/c731f5f6-96fc-456d-b55d-257c7c9c5c45)|![7813](https://github.com/user-attachments/assets/b52c251e-72b2-42c8-be00-22558b612d52)|


### ADVANCE REPO 
| note | Photo |
|------|-------|
|**login** |<img width="800" alt="image" src="https://github.com/user-attachments/assets/9aeeaf5f-b149-4a61-996f-43f3d60aec9a" />|
|**register**|<img width="800" alt="image" src="https://github.com/user-attachments/assets/5dc10f0e-92de-4f48-8535-0b8c0dc5c82d" />|
|**chat window** |<img width="300" alt="image" src="https://github.com/user-attachments/assets/4c26596c-9ba6-432d-af4a-867b625f0ea0" /><img width="300" alt="image" src="https://github.com/user-attachments/assets/d3540b13-9e63-4682-a9f2-947dc8f36fe1" /><img width="300" alt="image" src="https://github.com/user-attachments/assets/1c938baf-5fec-4f3a-a0e9-5e6fcd1598bd" />|
|**quick view setting**|<img width="800" alt="image" src="https://github.com/user-attachments/assets/c1578e68-2edf-4096-baf5-3eb75e1bd712" />|
|**rag setting** |<img width="160" alt="image" src="https://github.com/user-attachments/assets/5f6167e5-abe8-471b-b0da-f0c4de3c5990" /><img width="160" alt="image" src="https://github.com/user-attachments/assets/c9f89155-9bda-4f19-9a74-ea5095432352" /><img width="160" alt="image" src="https://github.com/user-attachments/assets/fbb1cd7c-f54b-4c22-8b63-c299d470cf83" /><img width="160" alt="image" src="https://github.com/user-attachments/assets/3aa59e23-5454-4c36-8fc3-59ba451affef" /><img width="160" alt="image" src="https://github.com/user-attachments/assets/927cf07a-48d8-45dc-b1f6-8c07fb0db71d" />|
|**organization setting**|<img width="220" alt="image" src="https://github.com/user-attachments/assets/49305ba1-1a02-4759-9ee2-6c3b22ca5b08" /><img width="220" alt="image" src="https://github.com/user-attachments/assets/3a1abda8-52c4-47cc-8d90-cd71f6cbe647" /><img width="220" alt="image" src="https://github.com/user-attachments/assets/fc6cd051-ca55-43c7-897c-e3ce9306b970" /><img width="220" alt="image" src="https://github.com/user-attachments/assets/2775f43d-0d46-4436-96fc-1745de42f0e4" />|
|**permission setting** |<img width="400" alt="image" src="https://github.com/user-attachments/assets/030f728d-e478-4089-b5d3-9c681c853de2" /><img width="400" alt="image" src="https://github.com/user-attachments/assets/0be79baa-3f94-4d68-8c01-17f9a1d62e8b" />|

### THIS REPO
| note | Photo |
|------|-------|
|**login** |<img width="800" alt="image" src="https://github.com/user-attachments/assets/68358aaf-95d5-43b0-8400-49a0e70f7bd0" />|
|**register**|<img width="800" alt="image" src="https://github.com/user-attachments/assets/eff2f0f3-0d80-46ec-899e-e4c5ba58e35e" />|
|**chat window** |<img width="800" alt="image" src="https://github.com/user-attachments/assets/36fdd090-08dd-4afe-b2fa-cd58bd26568c" />|
|**index** |<img width="800" alt="image" src="https://github.com/user-attachments/assets/3cc5cde7-3323-4059-9f2f-b86d5539e388" />|
|**setting**|<img width="800" alt="image" src="https://github.com/user-attachments/assets/e365ffe5-8bfe-487b-9938-73b17994cd90" />|
|**account manager** |<img width="800" alt="image" src="https://github.com/user-attachments/assets/109338bc-05d5-4a99-b31a-dfa63a1a6e9a" />|
|**user panel** |<img width="800" alt="image" src="https://github.com/user-attachments/assets/9bd40207-fd7d-4645-884f-d7234870c8ce" />|





