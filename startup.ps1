# 需手動執行 

1.啟動 ollama
2.安裝 mariadb 資料庫 v10.11 並建立 DB 帳號，帳號密碼需與 env.example 一致
  root/root_password_2024
  rag_user/rag_password_2024
3.初始化資料庫     : 執行 init-db 底下所有 sql
4.建立環境變數     : 複製 env.example > .env 並放到專案目錄下
5.建立工作目錄     : documents faiss_data logs mariadb_data models ollama
5.更新 python lib : pip install --upgrade pip
6.安裝 python lib : pip install -r requirements.txt
7.啟動 FastApi    : uvicorn app.app:app --host 127.0.0.1 --port 8080