# Lightweight Retrieval-Augmented Generation System (RAG)

This project was built using **Claude Code** and implements an enhanced retrieval system, with the **Ollama** framework serving as the core platform for LLM operations.

## Features

The system offers a range of features designed for efficient document retrieval and management:

- **Account Management**: Simple user registration and login functionalities.
- **File Upload & Extraction**: Seamlessly upload files and extract their contents.
- **Index Building**: Create data indexes optimized for semantic retrieval.
- **Backend Configuration**: Adjustable parameters for basic system operations.

---

##  Comparison: Open Source vs. Advance Edition

The following table highlights the differences between the public repository and our internal/Advance version:

| Feature | Open Source Edition | Advance Edition (Private) |
| :--- | :---: | :---: |
| **Account Management** | ✔️ | ✔️ |
| **File Processing** | ✔️ | ✔️ |
| **Semantic Indexing** | ✔️ | ✔️ |
| **Organization Management** | ❌ | ✔️ |
| **Granular Access Control (RBAC)** | ❌ | ✔️ |
| **Advanced RAG Configuration** | ❌ | ✔️ |
| **Full System Administration** | ❌ | ✔️ |

### Advanced Module Details

For our advance version, we have implemented several high-level modules to meet professional requirements:

* **Organization Management**: Multi-tenant support to manage various organizations and departments.
* **Permission Control**: Role-Based Access Control (RBAC) to ensure data security and compliance.
* **Comprehensive RAG Pipeline**: Full suite of parameters for retrieval optimization, including custom chunking strategies and re-ranking.
* **Global System Settings**: Advanced backend controls for infrastructure and environment monitoring.


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

## Quick View
| Advance Edition | Open Source Edition |
|------|-------|
![7814](https://github.com/user-attachments/assets/c731f5f6-96fc-456d-b55d-257c7c9c5c45)|![7813](https://github.com/user-attachments/assets/b52c251e-72b2-42c8-be00-22558b612d52)|

### Advance Edition 
| Feature | Screenshot |
|:---|:---|
|**Login & Registration** |<img width="250" src="https://github.com/user-attachments/assets/9aeeaf5f-b149-4a61-996f-43f3d60aec9a" /> <img width="250" src="https://github.com/user-attachments/assets/5dc10f0e-92de-4f48-8535-0b8c0dc5c82d" />|
|**Chat Interface** |<img width="180" src="https://github.com/user-attachments/assets/4c26596c-9ba6-432d-af4a-867b625f0ea0" /> <img width="180" src="https://github.com/user-attachments/assets/d3540b13-9e63-4682-a9f2-947dc8f36fe1" /> <img width="180" src="https://github.com/user-attachments/assets/1c938baf-5fec-4f3a-a0e9-5e6fcd1598bd" />|
|**Quick View Settings**|<img width="600" src="https://github.com/user-attachments/assets/c1578e68-2edf-4096-baf5-3eb75e1bd712" />|
|**RAG Settings** |<img width="110" src="https://github.com/user-attachments/assets/5f6167e5-abe8-471b-b0da-f0c4de3c5990" /> <img width="110" src="https://github.com/user-attachments/assets/c9f89155-9bda-4f19-9a74-ea5095432352" /> <img width="110" src="https://github.com/user-attachments/assets/fbb1cd7c-f54b-4c22-8b63-c299d470cf83" /> <img width="110" src="https://github.com/user-attachments/assets/3aa59e23-5454-4c36-8fc3-59ba451affef" /> <img width="110" src="https://github.com/user-attachments/assets/e7ad7edf-3402-465f-92cf-639c8e1d48b3" />|
|**Organization Settings**|<img width="140" src="https://github.com/user-attachments/assets/49305ba1-1a02-4759-9ee2-6c3b22ca5b08" /> <img width="140" src="https://github.com/user-attachments/assets/3a1abda8-52c4-47cc-8d90-cd71f6cbe647" /> <img width="140" src="https://github.com/user-attachments/assets/fc6cd051-ca55-43c7-897c-e3ce9306b970" /> <img width="140" src="https://github.com/user-attachments/assets/2775f43d-0d46-4436-96fc-1745de42f0e4" /> <img width="140" src="https://github.com/user-attachments/assets/c1dd4790-22ee-44e3-9239-e063836fd98f" /> <img width="140" src="https://github.com/user-attachments/assets/b6f27a5c-126f-451f-8d3d-cb21a5890a7d" /> <img width="140" src="https://github.com/user-attachments/assets/7fe474c0-929e-4343-b1e7-714a35b99c1f" /> <img width="140" src="https://github.com/user-attachments/assets/ebc1e798-b316-4ea1-959e-7d2f152fb021" />|
|**Permissions Management** |<img width="250" src="https://github.com/user-attachments/assets/030f728d-e478-4089-b5d3-9c681c853de2" /> <img width="250" src="https://github.com/user-attachments/assets/0be79baa-3f94-4d68-8c01-17f9a1d62e8b" />|
|**Account Management**|<img width="110" src="https://github.com/user-attachments/assets/a1bdf1bf-3531-41b7-affa-d651b44cd0c9" /> <img width="110" src="https://github.com/user-attachments/assets/5c3b7051-bda5-4a4e-acd8-57032f0826ab" /> <img width="110" src="https://github.com/user-attachments/assets/faea3262-7a35-40de-9e88-1c3c0dd763fb" /> <img width="110" src="https://github.com/user-attachments/assets/a843934b-903b-4f04-a636-c3bca5a142fd" /> <img width="110" src="https://github.com/user-attachments/assets/542da936-53e3-4de9-bedf-9a5c0ac609d8" />|

### Open Source Edition
| Feature | Screenshot |
|:---|:---|
|**Login & Registration** |<img width="250" src="https://github.com/user-attachments/assets/68358aaf-95d5-43b0-8400-49a0e70f7bd0" /> <img width="250" src="https://github.com/user-attachments/assets/eff2f0f3-0d80-46ec-899e-e4c5ba58e35e" />|
|**Chat Interface** |<img width="600" src="https://github.com/user-attachments/assets/36fdd090-08dd-4afe-b2fa-cd58bd26568c" />|
|**RAG Settings**|<img width="250" src="https://github.com/user-attachments/assets/3cc5cde7-3323-4059-9f2f-b86d5539e388" /> <img width="250" src="https://github.com/user-attachments/assets/e365ffe5-8bfe-487b-9938-73b17994cd90" />|
|**Account Management** |<img width="600" src="https://github.com/user-attachments/assets/109338bc-05d5-4a99-b31a-dfa63a1a6e9a" />|


