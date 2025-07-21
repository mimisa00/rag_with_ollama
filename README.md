# RAG (Retrieval-Augmented Generation) 系統

本專案實作增強型檢索系統，並採用了 Ollama 框架作為 LLM 平台核心。系統具備以下功能：
帳號管理：提供簡易的使用者註冊與登入功能
檔案上傳與擷取：可上傳檔案並進行內容擷取
索引建立：建立語意檢索所需的資料索引
後台參數調整：可調整系統運作所需的參數設定
歡迎提供寶貴建議，您可以留言或來信與我們聯繫！


## 🏗️ 專案結構

```
rag/
├── app/                      # Python 應用程式
│   ├── app.py                # FastAPI 主應用
│   └── model_docling.py      # 文檔處理模組
├── backend/                  # backend 配置
│   ├── Dockerfile            # 容器配置
│   ├── requirements.txt      # Python 依賴
│   └── test_db_connection.py # 啟動時DB測試
├── documents/                # 索引文件放置
├── faiss_data/               # 向量資料存取
├── frontend/                 # 前端文件
│   └── static/               # 靜態文件 (HTML, CSS, JS)
├── init-db/                  # 初始化 DB 文件
├── logs/                     # 日誌文件
├── mariadb_data/             # 資料庫儲存
├── models/                   # 模型儲存位置
├── ollama/                   # ollama 快取
├── ollama_modelfile/         # ollama 自訂 modelfile
├── docker-compose.yml        # Docker 服務配置
├── env.example               # 環境變數範例
├── README.md                 # 詳細文檔
├── startup.ps1.sh            # Windows 環境啟動腳本
└── startup.sh                # Linux   啟動腳本
```

## 🚀 快速開始

### 前置需求
- Docker
- Git
- 至少 8GB RAM
- NVIDIA GPU (可選，用於加速)

### 1. Clone 專案

```bash
git clone https://github.com/mimisa00/rag_with_ollama.git
cd rag_with_ollama
```

### 2. 環境設置

#### Linux/macOS:
```bash
chmod +x startup.sh
./startup.sh
```

#### Windows PowerShell:
```powershell
請查閱 .\setup.ps1 說明
```

### 3. 啟動服務

```bash
docker compose up -d
```

### 4. 訪問系統
- 主界面: http://localhost:8080/login


## 📄 授權
本專案採用 MIT 授權條款。
