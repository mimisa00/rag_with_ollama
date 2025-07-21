import os
import mimetypes
import shutil
import json
import numpy as np
import traceback
import torch
import ollama
import faiss
import urllib.parse
import time

from typing import Optional, List

from fastapi import (
    FastAPI,
    HTTPException,
    Response,
    status,
    Depends,
    UploadFile,
    File,
    Form,
    Body,
)
from fastapi.responses import (
    HTMLResponse,
    StreamingResponse,
    JSONResponse,
    FileResponse,
    RedirectResponse,
)

from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# 匯入整個模組
from app.model_docling import convert_file_via_docling
from app.dao import config_dao, conversation_dao, user_dao, llm_request_dao
from app.auth import (
    auth_manager,
    require_admin,
    get_current_user,
    get_current_user_optional,
)

app = FastAPI()
loaded = load_dotenv()
# /backend/app
BASE_DIR = os.path.dirname(__file__)
# /backend/frontend/static
STATIC_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend", "static")
# /backend/frontend/static/index.html
HTML_PATH_DASHBOARD = os.path.join(STATIC_DIR, "dashboard.html")
HTML_PATH_DASHBOARD_ADMIN = os.path.join(STATIC_DIR, "dashboard_admin.html")
HTML_PATH_LOGIN = os.path.join(STATIC_DIR, "login.html")
HTML_PATH_REGISTER = os.path.join(STATIC_DIR, "register.html")
HTML_PATH_SHOWINDEX = os.path.join(STATIC_DIR, "showindex.html")
HTML_PATH_MD_VIEWER = os.path.join(STATIC_DIR, "md_viewer.html")
HTML_PATH_MD_VIEWER_IDX = os.path.join(STATIC_DIR, "md_viewer_idx.html")
# /backend/documents
DOC_PATH = os.path.join(os.path.dirname(BASE_DIR), "documents")
# /backend/documents/markdown
MD_PATH = os.path.join(DOC_PATH, "markdown")
# /backend/faiss_data
FAISS_DIR = os.getenv("FAISS_DIR")
TEXTS_PATH = os.path.join(FAISS_DIR, "texts.json")
INDEX_PATH = os.path.join(FAISS_DIR, "faiss.index")


config = {}
embedding_model = None
current_embedding_model = None
index = None
texts = []
reranker_tokenizer = None
reranker_model = None
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

OLLAMA_HOST = os.getenv("OLLAMA_API_HOST", "http://localhost:11434")
ollama_client = ollama.Client(host=OLLAMA_HOST)


# Pydantic 模型
class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str


class AdminPasswordChangeRequest(BaseModel):
    new_password: str


# 前後端傳輸Json物件架構
class QueryTo(BaseModel):
    question: str
    keyword: Optional[str] = ""
    conv_id: Optional[str] = ""
    think: Optional[bool] = False


class AdminUserUpdate(BaseModel):
    role: str


@app.get("/", response_class=HTMLResponse)
def root(current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)):
    """主頁面 - 根據登入狀態導向 dashboard 或 login"""
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=302)
    else:
        return RedirectResponse(url="/login", status_code=302)


# 認證相關端點
@app.get("/login", response_class=HTMLResponse)
def login(current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)):
    """登入頁面"""
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=302)
    else:
        return FileResponse(
            HTML_PATH_LOGIN,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )


@app.get("/register", response_class=HTMLResponse)
def register(
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
):
    """註冊頁面"""
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=302)
    else:
        return FileResponse(
            HTML_PATH_REGISTER,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(current_user: Dict[str, Any] = Depends(get_current_user)):
    """主儀表板頁面"""
    # 讀取原始 index.html 內容作為問答內容
    try:
        if current_user["role"] == "admin":
            with open(HTML_PATH_DASHBOARD_ADMIN, "r", encoding="utf-8") as f:
                return f.read()
        else:
            with open(HTML_PATH_DASHBOARD, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/auth/login")
def api_login(login_data: LoginRequest, response: Response):
    """用戶登入"""
    user = auth_manager.authenticate_user(login_data.username, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用戶名或密碼錯誤"
        )

    # 創建 JWT token
    token = auth_manager.create_access_token(
        data={"sub": str(user["id"]), "username": user["username"]}
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=60 * 60 * 24,  # 例如一天
        secure=True,  # 若有 https 就開啟
        samesite="lax",
    )

    return {
        "user": {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
        },
    }


@app.post("/api/auth/register")
def api_register(register_data: RegisterRequest):
    """用戶註冊"""
    # 檢查用戶名是否已存在
    existing_user = user_dao.get_user_by_username(register_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用戶名已存在"
        )
    # 檢查是否為第一個用戶（設為管理員）
    all_users = user_dao.get_all_users()
    role = "admin" if len(all_users) == 0 else "user"
    # 加密密碼
    password_hash = auth_manager.get_password_hash(register_data.password)
    # 創建用戶
    user_id = user_dao.create_user(register_data.username, password_hash, role)
    return {"message": "註冊成功", "user_id": user_id, "role": role}


@app.get("/api/logout")
def api_logout(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """登出並清除 token"""
    # 清除認證 cookie
    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    return response


@app.post("/api/auth/change-password")
def api_change_password(
    password_data: PasswordChangeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """用戶變更密碼"""
    # 驗證舊密碼
    if not auth_manager.verify_password(
        password_data.old_password, current_user["password_hash"]
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="舊密碼錯誤"
        )

    # 生成新密碼雜湊
    new_password_hash = auth_manager.get_password_hash(password_data.new_password)

    # 更新資料庫
    success = user_dao.update_user_password(current_user["id"], new_password_hash)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="密碼更新失敗"
        )

    return {"message": "密碼變更成功"}


@app.get("/api/auth/current-user")
def api_get_current_user(current_user: Dict[str, Any] = Depends(get_current_user)):
    """獲取當前用戶資訊"""
    return {
        "id": current_user["id"],
        "username": current_user["username"],
        "role": current_user["role"],
    }


# 管理員
@app.get("/api/admin/users")
def api_get_all_users(current_user: Dict[str, Any] = Depends(get_current_user)):
    """獲取所有用戶（管理員功能）"""
    require_admin(current_user)
    users = user_dao.get_all_users()
    return users


@app.put("/api/admin/users/{user_id}/admin")
def api_update_user_admin_status(
    user_id: int,
    admin_data: AdminUserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """更新用戶管理員狀態（管理員功能）"""
    require_admin(current_user)

    success = user_dao.update_user_role(user_id, admin_data.role)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="更新失敗"
        )

    return {"message": "更新成功"}


@app.put("/api/admin/users/{user_id}/deactivate")
def deactivate_user(
    user_id: int, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """停用用戶（管理員功能）"""
    require_admin(current_user)
    success = user_dao.deactivate_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="停用失敗"
        )

    return {"message": "用戶已停用"}


@app.put("/api/admin/users/{user_id}/activate")
def activate_user(
    user_id: int, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """啟用用戶（管理員功能）"""
    require_admin(current_user)
    success = user_dao.activate_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="啟用失敗"
        )
    return {"message": "用戶已啟用"}


@app.post("/api/admin/users/{user_id}/change-password")
def api_admin_change_password(
    user_id: int,
    password_data: AdminPasswordChangeRequest = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """管理員變更任意用戶密碼"""
    require_admin(current_user)
    # 檢查用戶是否存在
    user = user_dao.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用戶不存在")
    # 生成新密碼雜湊
    new_password_hash = auth_manager.get_password_hash(password_data.new_password)
    # 更新資料庫
    success = user_dao.update_user_password(user_id, new_password_hash)
    if not success:
        raise HTTPException(status_code=500, detail="密碼更新失敗")
    return {"message": "密碼變更成功"}


@app.get("/showindex", response_class=HTMLResponse)
def showindex(current_user: Dict[str, Any] = Depends(get_current_user)):
    require_admin(current_user)
    with open(HTML_PATH_SHOWINDEX, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/md_viewer", response_class=HTMLResponse)
def md_viewer(current_user: Dict[str, Any] = Depends(get_current_user)):
    require_admin(current_user)
    with open(HTML_PATH_MD_VIEWER, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/md_viewer_idx", response_class=HTMLResponse)
def md_viewer_idx(current_user: Dict[str, Any] = Depends(get_current_user)):
    require_admin(current_user)
    with open(HTML_PATH_MD_VIEWER_IDX, "r", encoding="utf-8") as f:
        return f.read()


@app.on_event("startup")
def on_startup():
    load_config()
    ensure_faiss_dir_exists()
    load_existing_index()
    load_embedding_model()
    load_reranker_model()


def load_config():
    global config
    try:
        config.update(config_dao.get_all_configs())
        print("[DEBUG] 配置已從資料庫載入", flush=True)
    except Exception as e:
        print(f"[ERROR] 載入配置失敗: {e}", flush=True)


def ensure_faiss_dir_exists():
    os.makedirs(os.path.join(BASE_DIR, "faiss_data"), exist_ok=True)


def load_existing_index():
    global index
    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
        load_text_chunks()


def load_embedding_model():
    global embedding_model
    get_embedding_model()
    try:
        # 嘗試跑 warmup
        embedding_model.embed_query("warmup")
        print("[DEBUG] 模型 warmup 成功", flush=True)
    except Exception as e:
        print(f"[ERROR] 模型 warmup 失敗: {e}", flush=True)


def load_reranker_model():
    global reranker_tokenizer, reranker_model  # ✅ 宣告使用全域變數

    print("[DEBUG] 正在載入 BGE Reranker 模型...", flush=True)
    reranker_tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-reranker-v2-m3")
    reranker_model = AutoModelForSequenceClassification.from_pretrained(
        "BAAI/bge-reranker-v2-m3"
    )
    reranker_model.to(device)
    reranker_model.eval()
    print("[DEBUG] BGE Reranker 模型載入完成", flush=True)


def get_embedding_model():
    global embedding_model, current_embedding_model
    requested_model_name = config["embedding_model"]
    # 判斷是否需要重建（第一次載入或模型名稱不同）
    if embedding_model is None or current_embedding_model != requested_model_name:
        print(
            f"[DEBUG] 需要載入新的 embedding 模型: {requested_model_name}", flush=True
        )
        embedding_model = HuggingFaceEmbeddings(
            model_name=requested_model_name, model_kwargs={"device": device}
        )
        current_embedding_model = requested_model_name
    else:
        print(
            f"[DEBUG] 使用快取中的 embedding 模型: {current_embedding_model}",
            flush=True,
        )
    return embedding_model


# 儲存與載入 index 對應的文字內容
def save_text_chunks():
    with open(TEXTS_PATH, "w", encoding="utf-8") as f:
        json.dump(texts, f, ensure_ascii=False)


def load_text_chunks():
    global texts
    if os.path.exists(TEXTS_PATH):
        with open(TEXTS_PATH, "r", encoding="utf-8") as f:
            texts = json.load(f)


# 共用建索引 function
def process_documents_and_update_index(doc_texts):
    global texts, index

    print("[DEBUG] process_documents_and_update_index: 開始", flush=True)
    print("[DEBUG] 原始文件數量:", len(doc_texts), flush=True)

    print(
        "[DEBUG] use split chunk_size / use split chunk_overlap: ",
        int(config["chunk_size"]),
        "/",
        int(config["chunk_overlap"]),
        flush=True,
    )
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=int(config["chunk_size"]), chunk_overlap=int(config["chunk_overlap"])
    )
    new_chunks = []
    for doc in doc_texts:
        # doc: {content, source_file, markdown_file}
        chunks = splitter.split_text(doc["content"])
        for chunk in chunks:
            new_chunks.append(
                {
                    "content": chunk,
                    "source_file": doc["source_file"],
                    "markdown_file": doc["markdown_file"],
                }
            )
    print("[DEBUG] 產生 chunk 數量:", len(new_chunks), flush=True)
    texts.extend(new_chunks)

    print("[DEBUG] 開始批次計算向量", flush=True)
    try:
        embedding_model = get_embedding_model()
        vectors = embedding_model.embed_documents(
            [chunk["content"] for chunk in new_chunks]
        )
        vectors = np.array(vectors).astype("float32")
        print("[DEBUG] 向量 shape:", vectors.shape, flush=True)
    except Exception as e:
        print("[ERROR] 向量產生失敗:", str(e), flush=True)
        raise

    if index is None:
        print("[DEBUG] 尚未初始化 index，建立新 index", flush=True)
        dimension = vectors.shape[1]
        index = faiss.IndexFlatL2(dimension)
    else:
        print("[DEBUG] 使用現有 index", flush=True)
    index.add(vectors)
    print("[DEBUG] 新向量已加入 index", flush=True)
    try:
        os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)  # 建立資料夾（保險）
        faiss.write_index(index, INDEX_PATH)
        print("[DEBUG] Index 已寫入檔案:", INDEX_PATH, flush=True)
    except Exception as e:
        print("[ERROR] 寫入 index 時失敗:", str(e), flush=True)
    try:
        save_text_chunks()
        print("[DEBUG] texts.json 已儲存，共", len(texts), "筆", flush=True)
    except Exception as e:
        print("[ERROR] 儲存 texts.json 失敗:", str(e), flush=True)

    return len(new_chunks)


def save_config(data):
    try:
        config_dao.update_configs(data)
        print("[DEBUG] 配置已儲存到資料庫", flush=True)
    except Exception as e:
        print(f"[ERROR] 儲存配置失敗: {e}", flush=True)


@app.get("/get_config")
def get_config(current_user: Dict[str, Any] = Depends(get_current_user)):
    require_admin(current_user)
    try:
        return config_dao.get_all_configs()
    except Exception as e:
        print(f"[ERROR] 取得配置失敗: {e}", flush=True)
        return {}


@app.get("/isEnableThink")
def isEnableThink(current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        val = config_dao.get_config_by_key("is_enable_think")
        return val.lower() == "true" if val else False
    except Exception as e:
        print(f"[ERROR] 取得配置 is_enable_think 失敗: {e}", flush=True)
        return {}


@app.post("/update_config")
def update_config(
    new_config: dict, current_user: Dict[str, Any] = Depends(get_current_user)
):
    require_admin(current_user)
    global config
    try:
        config.update(new_config)
        save_config(new_config)
        load_config()
        update_ollama_model_options()
        return {"status": "參數已儲存"}
    except Exception as e:
        print(f"[ERROR] 更新配置失敗: {e}", flush=True)
        return {"status": "參數儲存失敗", "error": str(e)}


def update_ollama_model_options():
    """
    更新ollama model的參數
    """
    ollama_client.generate(
        model=config["llm_model"],
        prompt="TEST",
        options={
            "num_ctx": int(config["num_ctx"]),
            "repeat_last_n": int(config["repeat_last_n"]),
            "repeat_penalty": float(config["repeat_penalty"]),
            "temperature": float(config["temperature"]),
            "seed": int(config["seed"]),
            "stop": [config["stop"]],
            "num_predict": int(config["num_predict"]),
            "top_k": int(config["top_k"]),
            "top_p": float(config["top_p"]),
            "min_p": float(config["min_p"]),
        },
        stream=False,
    )


@app.get("/list_files")
def list_files(current_user: Dict[str, Any] = Depends(get_current_user)):
    require_admin(current_user)
    try:
        files = []
        for filename in os.listdir(DOC_PATH):
            full_path = os.path.join(DOC_PATH, filename)
            # if (
            #    filename.endswith(".pdf")
            #    or filename.endswith(".docx")
            #    or filename.endswith(".xlsx")
            # ):
            #    if os.path.isfile(full_path):
            #        files.append(filename)
            if os.path.isfile(full_path):
                files.append(filename)
        return {"files": files}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# 上傳檔案
@app.post("/upload_file")
def upload_file(
    files: List[UploadFile] = File(...),
    overwrite: bool = Form(False),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    require_admin(current_user)
    results = []
    for file in files:
        file_path = os.path.join(DOC_PATH, file.filename)
        exists = os.path.exists(file_path)
        if exists and not overwrite:
            results.append(
                {"filename": file.filename, "status": "exists", "message": "檔案已存在"}
            )
            continue
        try:
            with open(file_path, "wb") as f:
                f.write(file.file.read())
            results.append(
                {"filename": file.filename, "status": "success", "message": "上傳成功"}
            )
        except Exception as e:
            results.append(
                {"filename": file.filename, "status": "error", "message": str(e)}
            )
    return {"results": results}


@app.post("/check_file_exists")
def check_file_exists(
    filenames: List[str],
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    require_admin(current_user)
    result = {}
    for filename in filenames:
        file_path = os.path.join(DOC_PATH, filename)
        result[filename] = os.path.exists(file_path)
    return result


# 依照選擇的檔案建立索引
@app.post("/prepare_file")
def api_prepare_files(
    filenames: List[str] = Form(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    require_admin(current_user)
    results = []
    print("[DEBUG] filenames: ", filenames, flush=True)
    for filename in filenames:
        full_path = os.path.join(DOC_PATH, filename)
        if not os.path.exists(full_path):
            results.append(
                {"filename": filename, "status": "error", "message": "檔案不存在"}
            )
            continue
        try:
            result = convert_file_via_docling(full_path, filename)
            print("[DEBUG] result: ", result, flush=True)
            if not result:
                results.append(
                    {"filename": filename, "status": "error", "message": "無法擷取內容"}
                )
                continue
            chunk_count = process_documents_and_update_index([result])
            print("[DEBUG] chunk_count: ", chunk_count, flush=True)
            results.append(
                {"filename": filename, "status": "success", "chunks": chunk_count}
            )
        except Exception as e:
            traceback.print_exc()
            results.append({"filename": filename, "status": "error", "message": str(e)})
    return {"results": results}


# 建立目錄裡全部檔案索引
@app.post("/prepare_index")
def api_prepare_index(current_user: Dict[str, Any] = Depends(get_current_user)):
    require_admin(current_user)
    global texts, index
    try:
        docs = []
        for filename in os.listdir(DOC_PATH):
            full_path = os.path.join(DOC_PATH, filename)
            if not os.path.isfile(full_path):
                continue

            result = convert_file_via_docling(full_path, filename)
            if result:
                docs.append(result)

        texts.clear()
        index = None
        chunk_count = process_documents_and_update_index(docs)
        return {"status": "success", "chunks": chunk_count}
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500, content={"status": "error", "message": str(e)}
        )


# 顯示索引前100筆內容
@app.get("/show_index_summary_100")
def index_summary_100(current_user: Dict[str, Any] = Depends(get_current_user)):
    require_admin(current_user)
    try:
        # 從 texts 中提取出所有的 content
        content_chunks = [
            item["content"] for item in texts[:100]
        ]  # 最多顯示前100筆內容
        return {
            "count": len(texts),
            "chunks": content_chunks,
            "index_exists": os.path.exists(INDEX_PATH),
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# 顯示索引完整內容
@app.get("/show_index_summary_all")
def index_summary(current_user: Dict[str, Any] = Depends(get_current_user)):
    require_admin(current_user)
    try:
        # 從 texts 中提取出所有的 content
        content_chunks = [item["content"] for item in texts]  # 顯示全部內容
        return {
            "count": len(texts),
            "chunks": content_chunks,
            "index_exists": os.path.exists(INDEX_PATH),
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# 清除索引
@app.post("/clear_index")
def clear_index(current_user: Dict[str, Any] = Depends(get_current_user)):
    require_admin(current_user)
    try:
        if os.path.exists(INDEX_PATH):
            os.remove(INDEX_PATH)
        if os.path.exists(TEXTS_PATH):
            os.remove(TEXTS_PATH)
        # 清除 MD_PATH 底下所有檔案
        if os.path.exists(MD_PATH):
            for filename in os.listdir(MD_PATH):
                file_path = os.path.join(MD_PATH, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # 如果是目錄，遞迴刪除

        globals()["index"] = None
        globals()["texts"] = []
        return {"status": "cleared"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# 檢查索引與檔案內容是否一致
@app.get("/validate_index")
def validate_index(current_user: Dict[str, Any] = Depends(get_current_user)):
    require_admin(current_user)
    if index is None or not texts:
        return {"status": "invalid", "reason": "index 或 texts 為空"}
    if index.ntotal != len(texts):
        return {
            "status": "invalid",
            "reason": f"index 向量數 {index.ntotal} 不等於 texts 數 {len(texts)}",
        }
    return {"status": "ok", "vectors": index.ntotal}


# 使用 BGE Reranker 模型進行重排序
def rerank_with_bge(query, candidate_texts, top_k):
    pairs = [(query, passage) for passage in candidate_texts]
    print("[DEBUG] rerank top_k: ", top_k, flush=True)
    # Tokenize
    inputs = reranker_tokenizer(
        [q for q, p in pairs],
        [p for q, p in pairs],
        padding=True,
        truncation=True,
        return_tensors="pt",
        max_length=512,
    )
    # 因為 device 選擇用GPU，為避免使用CPU推理造成異常，故此處需使用GPU推理
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        scores = reranker_model(**inputs).logits.squeeze(-1)

    # 排序並選出 top_k
    top_k_indices = torch.topk(
        scores, k=min(top_k, len(candidate_texts))
    ).indices.tolist()
    reranked_texts = [candidate_texts[i] for i in top_k_indices]
    return reranked_texts


# 儲存對話記錄
def store_conversation(conv_id: str, q: str, a: str, user_id: str):
    try:
        conversation_dao.store_conversation(conv_id, q, a, user_id)
        print(f"[DEBUG] 對話記錄已儲存到資料庫: {conv_id}", flush=True)
    except Exception as e:
        print(f"[ERROR] 儲存對話記錄失敗: {e}", flush=True)


# 顯示對話記錄
@app.get("/conversations")
def get_user_conversations(current_user: Dict[str, Any] = Depends(get_current_user)):
    """獲取用戶的對話記錄"""
    try:
        conversations = conversation_dao.list_all_conversations(current_user["id"])
        res = []
        for conv in conversations:
            conv_id = conv["id"]
            messages = conversation_dao.get_conversations_by_conv_id(conv_id)
            formatted_messages = [
                {"q": msg["question"], "a": msg["answer"]} for msg in messages
            ]

            res.append(
                {
                    "id": conv_id,
                    "title": conv["title"],
                    "messages": formatted_messages,
                    "first_message_time": conv["first_message_time"],
                    "last_message_time": conv["last_message_time"],
                    "message_count": conv["message_count"],
                }
            )
        return res
    except Exception as e:
        print(f"[ERROR] 取得對話記錄失敗: {e}", flush=True)
        return []


# 刪除對話記錄
@app.delete("/conversations/{conv_id}")
def delete_conversation(
    conv_id: str, current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        if conversation_dao.delete_conversation(conv_id, current_user["id"]):
            return {"message": "deleted"}
        else:
            raise HTTPException(status_code=404, detail="對話不存在")
    except Exception as e:
        print(f"[ERROR] 刪除對話記錄失敗: {e}", flush=True)
        raise HTTPException(status_code=500, detail="刪除對話記錄失敗")


# 名詞分析
@app.post("/noun/analysis")
def noun_analysis(
    query: QueryTo, current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_limit = int(config["llm_req_limit_user"])
    total_limit = int(config["llm_req_limit_total"])
    if llm_request_dao.get_total_active_request_count() >= total_limit:
        return StreamingResponse(
            "# 系統忙碌，請稍後再試", media_type="application/json"
        )
    if llm_request_dao.get_user_active_request_count(current_user["id"]) >= user_limit:
        return StreamingResponse("# 仍在處理上次的請求", media_type="application/json")
    req_id = llm_request_dao.add_user_request(
        current_user["id"],
        getattr(query, "conv_id", None),
        getattr(query, "question", None),
    )
    start_time = time.time()
    try:
        prompt = config["noun_analysis_prompt"].replace("{question}", query.question)
        # Prepare messages for ollama_client.chat
        messages = [{"role": "user", "content": prompt}]
        stream = ollama_client.chat(
            model=config["llm_model"],
            messages=messages,
            think=False,
            stream=True,
            options={
                "num_ctx": int(config["num_ctx"]),
                "repeat_last_n": int(config["repeat_last_n"]),
                "repeat_penalty": float(config["repeat_penalty"]),
                "temperature": float(config["temperature"]),
                "seed": int(config["seed"]),
                "stop": [config["stop"]],
                "num_predict": int(config["num_predict"]),
                "top_k": int(config["top_k"]),
                "top_p": float(config["top_p"]),
                "min_p": float(config["min_p"]),
            },
        )

        def stream_generator():
            try:
                for chunk in stream:
                    if chunk and getattr(chunk, "message", None):
                        yield chunk.message.content
            except Exception as e:
                print(f"[ERROR] 儲存對話記錄失敗: {e}", flush=True)
                response_time = time.time() - start_time
                llm_request_dao.mark_request_completed(
                    req_id, response_time=response_time, error_message=str(e)
                )
            finally:
                print("finally", flush=True)
                response_time = time.time() - start_time
                llm_request_dao.mark_request_completed(
                    req_id, response_time=response_time
                )

        return StreamingResponse(stream_generator(), media_type="application/json")
    except Exception as ex:
        return {"error": "系統錯誤，請稍後再試"}


# 問答
@app.post("/query")
def query(query: QueryTo, current_user: Dict[str, Any] = Depends(get_current_user)):
    user_limit = int(config["llm_req_limit_user"])
    total_limit = int(config["llm_req_limit_total"])
    print("[DEBUG] user_limit: ", user_limit, flush=True)
    print("[DEBUG] total_limit: ", total_limit, flush=True)
    if llm_request_dao.get_total_active_request_count() >= total_limit:
        return StreamingResponse(
            "# 系統忙碌，請稍後再試", media_type="application/json"
        )
    if llm_request_dao.get_user_active_request_count(current_user["id"]) >= user_limit:
        return StreamingResponse("# 仍在處理上次的請求", media_type="application/json")
    req_id = llm_request_dao.add_user_request(
        current_user["id"],
        getattr(query, "conv_id", None),
        getattr(query, "question", None),
    )
    start_time = time.time()
    try:
        if index is None or len(texts) == 0:
            raise HTTPException(status_code=400, detail="尚未建立索引，請先分析文件")

        conversation_history = ""
        if query.conv_id:
            try:
                conv_data = conversation_dao.get_conversations_by_conv_id(query.conv_id)
                conversation_history = "\n".join(
                    f"User Question: {item['question']}\Answer: {item['answer']}"
                    for item in conv_data
                )
            except Exception as e:
                print(f"[ERROR] 取得對話記錄失敗: {e}", flush=True)

        q_str = (
            query.question + " " + query.keyword if query.question else query.keyword
        )
        print("[DEBUG] q_str: ", q_str, flush=True)
        q_vec = get_embedding_model().embed_query(q_str)
        # print("[DEBUG] q_vec: ", q_vec, flush=True)
        # print("[DEBUG] idx_result_count: ", int(config["idx_result_count"]), flush=True)

        # k值控制向量回傳結果數量,數量越多代表不相干的結果就會越多..通常是設定3~5就好
        D, I = index.search(
            np.array([q_vec]).astype("float32"), k=int(config["idx_result_count"])
        )

        print("[DEBUG] D: ", D, flush=True)
        print("[DEBUG] I: ", I, flush=True)

        #### reranker start ####
        # 用回傳的向量索引取出原始文字內容
        candidate_chunks = [texts[i] for i in I[0]]  # texts 是 dict 結構
        if not candidate_chunks:
            raise HTTPException(
                status_code=500, detail="找不到對應的文字內容，請重新建立索引"
            )
        # print("[DEBUG] candidate_chunks: ", candidate_chunks, flush=True)
        # for chunk in candidate_chunks:
        #    print("[DEBUG] chunk: ", chunk, flush=True)
        #    print("[DEBUG] ---------- candidate_chunks ----------", flush=True)

        # Rerank
        top_passages = rerank_with_bge(
            query.question,
            [c["content"] for c in candidate_chunks],
            int(config["rerank_top_k_final"]),
        )

        # print("[DEBUG] top_passages: ", top_passages, flush=True)
        passage_to_chunk = {c["content"]: c for c in candidate_chunks}
        md_files = set()
        src_files = set()
        chunk_context = ""
        for passage in top_passages:
            chunk = passage_to_chunk.get(passage)
            if chunk:
                md_files.add(chunk["markdown_file"])
                src_files.add(chunk["source_file"])
                chunk_context += chunk["content"]
                # print("[DEBUG] chunk_context: ", chunk_context, flush=True)

        context = chunk_context

        system_prompt = (
            config["system_prompt"]
            .replace("{context}", context)
            .replace("{question}", query.question)
            .replace("{keyword}", query.keyword)
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query.question},
        ]

        def stream_generator():
            try:
                full_answer = '<i class="fa-solid fa-robot"> 回覆如下 : </i><BR/>'
                yield json.dumps(
                    {"prompt": system_prompt, "answer": "", "thinking": ""}
                )  # [:-2]
                print("start call ollama", flush=True)
                stream = ollama_client.chat(
                    model=config["llm_model"],
                    messages=messages,
                    think=query.think,
                    stream=True,
                    options={
                        "num_ctx": int(config["num_ctx"]),
                        "repeat_last_n": int(config["repeat_last_n"]),
                        "repeat_penalty": float(config["repeat_penalty"]),
                        "temperature": float(config["temperature"]),
                        "seed": int(config["seed"]),
                        "stop": [config["stop"]],
                        "num_predict": int(config["num_predict"]),
                        "top_k": int(config["top_k"]),
                        "top_p": float(config["top_p"]),
                        "min_p": float(config["min_p"]),
                    },
                )
                print("end call ollama", flush=True)
                for chunk in stream:
                    if chunk and getattr(chunk, "message", None):
                        full_answer += chunk.message.content
                        yield json.dumps(
                            {
                                "content": chunk.message.content,
                                "thinking": chunk.message.thinking or "",
                            }
                        )
                # 回覆最後加上引用來源超連結
                if src_files:
                    links = []
                    for src in src_files:
                        if src.lower().endswith(".md"):
                            links.append(
                                f'<a href="/md_viewer?file={src}" target="_blank">{src}</a>'
                            )
                        else:
                            links.append(
                                f'<a href="/documents/{src}" target="_blank">{src}</a>'
                            )
                    full_answer += "\n\n引用來源：" + "、".join(links)

                store_conversation(
                    query.conv_id, query.question, full_answer, current_user["id"]
                )

            except Exception as e:
                print(f"[ERROR] 儲存對話記錄失敗: {e}", flush=True)
                response_time = time.time() - start_time
                llm_request_dao.mark_request_completed(
                    req_id, response_time=response_time, error_message=str(e)
                )
            finally:
                print("finally", flush=True)
                response_time = time.time() - start_time
                llm_request_dao.mark_request_completed(
                    req_id, response_time=response_time
                )

        return StreamingResponse(stream_generator(), media_type="application/json")
    except Exception as ex:
        return {"error": "系統錯誤，請稍後再試"}


@app.get("/documents/{filename}")
def get_document(
    filename: str, current_user: Dict[str, Any] = Depends(get_current_user)
):
    file_path = os.path.join(DOC_PATH, filename)

    # 檢查檔案是否存在
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # 使用 mimetypes 判斷檔案的 MIME 類型
    mime_type, _ = mimetypes.guess_type(file_path)

    # 若 MIME 類型無法判斷，則設為 application/octet-stream
    if mime_type is None:
        mime_type = "application/octet-stream"

    # URL 編碼檔名，確保支持中文或特殊字符
    encoded_filename = urllib.parse.quote(filename)

    # 為了確保瀏覽器顯示檔案而不是下載，設定 Content-Disposition: inline
    headers = {"Content-Disposition": f"inline; filename={encoded_filename}"}

    # 返回檔案並設置適當的 media_type 和 headers
    return FileResponse(
        file_path, filename=filename, media_type=mime_type, headers=headers
    )


@app.get("/documents/markdown/{md_filename}")
def get_markdown(
    md_filename: str, current_user: Dict[str, Any] = Depends(get_current_user)
):
    require_admin(current_user)
    md_path = os.path.join(MD_PATH, md_filename)

    # 檢查檔案是否存在
    if not os.path.exists(md_path):
        raise HTTPException(status_code=404, detail="Markdown file not found")

    # 使用 mimetypes 判斷檔案的 MIME 類型
    mime_type, _ = mimetypes.guess_type(md_path)

    # 若 MIME 類型無法判斷，則設為 text/plain (預設)
    if mime_type is None:
        mime_type = "text/plain"

    # URL 編碼檔名，確保支持中文或特殊字符
    encoded_filename = urllib.parse.quote(md_filename)

    # 為了確保瀏覽器顯示檔案而不是下載，設定 Content-Disposition: inline
    headers = {"Content-Disposition": f"inline; filename={encoded_filename}"}

    # 返回檔案並設置適當的 media_type 和 headers
    return FileResponse(
        md_path, filename=md_filename, media_type=mime_type, headers=headers
    )
