import os
import pymysql
from dbutils.pooled_db import PooledDB
from typing import Dict, List, Optional, Any
import logging
import traceback

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        self.connection_pool = None
        

    def _init_pool(self):
        """初始化資料庫連線池"""
        try:
            self.host = os.getenv("DB_HOST")
            self.port = int(os.getenv("DB_PORT"))
            self.database = os.getenv("DB_NAME")
            self.user = os.getenv("DB_USER")
            self.password = os.getenv("DB_PASSWORD")

            self.connection_pool = PooledDB(
                creator=pymysql,  # 使用 pymysql 作為資料庫連接的驅動
                maxconnections=10,  # 最大連線數
                mincached=2,  # 最小連線數
                maxcached=5,  # 最大空閒連線數
                blocking=True,  # 是否阻塞直到有空閒連線
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True,
            )
            logger.info("資料庫連線池初始化成功")
        except Exception as e:
            logger.error(f"資料庫連線池初始化失敗: {e}")
            raise

    def get_connection(self):
        """從連線池中獲取資料庫連線"""
        try:
            if self.connection_pool is None:
                self._init_pool()
            connection = self.connection_pool.connection()
            return connection
        except Exception as e:
            logger.error(f"取得資料庫連線失敗: {e}")
            raise

    def _is_connection_alive(self):
        """檢查資料庫連線是否有效"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except:
            return False

    def close(self):
        """關閉資料庫連線池"""
        if self.connection_pool:
            self.connection_pool.close()
            logger.info("資料庫連線池已關閉")

    def close_connection(self, connection):
        """手動關閉資料庫連線"""
        if connection:
            connection.close()
            logger.info("資料庫連線已關閉")


class ConfigDAO:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_all_configs(self) -> Dict[str, Any]:
        """取得所有配置"""
        try:
            connection = self.db_manager.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT `key`, value FROM configs"
                cursor.execute(query)
                results = cursor.fetchall()

            configs = {}
            for row in results:
                configs[row["key"]] = row["value"]

            return configs
        except Exception as e:
            logger.error(f"取得配置失敗: {e}")
            return {}

    def get_config_by_key(self, key: str) -> Optional[str]:
        """根據鍵名取得配置值"""
        try:
            connection = self.db_manager.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT value FROM configs WHERE `key` = %s"
                cursor.execute(query, (key,))
                result = cursor.fetchone()
                print(f"[DEBUG] 查詢結果: {result}", flush=True)
            return result['value'] if result else None
        except Exception as e:
            logger.error(f"取得配置 {key} 失敗: {e}")
            return None

    def update_config(self, key: str, value: str) -> bool:
        """更新配置"""
        try:
            connection = self.db_manager.get_connection()
            with connection.cursor() as cursor:
                query = """
                    INSERT INTO configs (`key`, value) 
                    VALUES (%s, %s) 
                    ON DUPLICATE KEY UPDATE value = VALUES(value), updated_at = CURRENT_TIMESTAMP
                """
                cursor.execute(query, (key, value))
            connection.commit()
            return True
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"更新配置 {key} 失敗: {e}")
            return False

    def update_configs(self, configs: Dict[str, Any]) -> bool:
        """批次更新配置"""
        try:
            connection = self.db_manager.get_connection()
            with connection.cursor() as cursor:
                for key, value in configs.items():
                    query = """
                        INSERT INTO configs (`key`, value) 
                        VALUES (%s, %s) 
                        ON DUPLICATE KEY UPDATE value = VALUES(value), updated_at = CURRENT_TIMESTAMP
                    """
                    cursor.execute(query, (key, str(value)))
            connection.commit()
            return True
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"批次更新配置失敗: {e}")
            return False


class ConversationDAO:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def store_conversation(
        self, conv_id: str, question: str, answer: str, user_id: int
    ) -> bool:
        """儲存對話記錄"""
        try:
            connection = self.db_manager.get_connection()
            with connection.cursor() as cursor:
                query = """
                INSERT INTO conversations (conv_id, user_id, question, answer) 
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (conv_id, user_id, question, answer))

            return True
        except Exception as e:
            logger.error(f"儲存對話記錄失敗: {e}")
            return False

    def get_conversations_by_conv_id(self, conv_id: str) -> List[Dict[str, Any]]:
        """根據對話ID取得對話記錄"""
        try:
            connection = self.db_manager.get_connection()
            with connection.cursor() as cursor:
                query = """
                SELECT id, conv_id, user_id, question, answer, created_at 
                FROM conversations 
                WHERE conv_id = %s 
                ORDER BY created_at ASC
             """
                cursor.execute(query, (conv_id,))
                results = cursor.fetchall()

            return results
        except Exception as e:
            logger.error(f"取得對話記錄失敗: {e}")
            return []

    def list_all_conversations(self, user_id: int) -> List[Dict[str, Any]]:
        """列出所有對話（可選按使用者篩選）"""
        try:
            connection = self.db_manager.get_connection()
            with connection.cursor() as cursor:
                if user_id is not None:
                    query = """
                        SELECT DISTINCT conv_id, 
                               MIN(created_at) as first_message_time,
                               MAX(created_at) as last_message_time,
                               COUNT(*) as message_count
                        FROM conversations 
                        WHERE user_id = %s 
                        GROUP BY conv_id 
                        ORDER BY last_message_time DESC
                    """
                    cursor.execute(query, (user_id,))
                else:
                    query = """
                        SELECT DISTINCT conv_id, 
                               MIN(created_at) as first_message_time,
                               MAX(created_at) as last_message_time,
                               COUNT(*) as message_count
                        FROM conversations 
                        GROUP BY conv_id 
                        ORDER BY last_message_time DESC
                    """
                    cursor.execute(query)

                results = cursor.fetchall()

            # 為每個對話取得第一條訊息作為標題
            conversations = []
            for row in results:
                conv_id = row["conv_id"]
                first_message = self.get_conversations_by_conv_id(conv_id)
                title = (
                    first_message[0]["question"][:10]
                    if first_message
                    else "New Conversation"
                )

                conversations.append(
                    {
                        "id": conv_id,
                        "title": title,
                        "first_message_time": row["first_message_time"],
                        "last_message_time": row["last_message_time"],
                        "message_count": row["message_count"],
                    }
                )

            return conversations
        except Exception as e:
            logger.error(f"列出對話失敗: {e}")
            return []

    def delete_conversation(self, conv_id: str, user_id: int) -> bool:
        """刪除對話記錄"""
        try:
            connection = self.db_manager.get_connection()
            with connection.cursor() as cursor:
                if user_id is not None:
                    query = (
                        "DELETE FROM conversations WHERE conv_id = %s AND user_id = %s"
                    )
                    cursor.execute(query, (conv_id, user_id))
                else:
                    query = "DELETE FROM conversations WHERE conv_id = %s"
                    cursor.execute(query, (conv_id,))

            return True
        except Exception as e:
            logger.error(f"刪除對話記錄失敗: {e}")
            return False


class UserDAO:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """根據使用者名稱取得使用者資訊"""
        try:
            connection = self.db_manager.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT * FROM users WHERE username = %s"
                cursor.execute(query, (username,))
                result = cursor.fetchone()

            return result
        except Exception as e:
            logger.error(f"取得使用者資訊失敗: {e}")
            return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根據使用者ID取得使用者資訊"""
        try:
            connection = self.db_manager.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT * FROM users WHERE id = %s AND is_active = 1"
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()

            return result
        except Exception as e:
            logger.error(f"取得使用者資訊失敗: {e}")
            return None

    def get_all_users(self) -> List[Dict[str, Any]]:
        """獲取所有用戶（管理員功能）"""
        try:
            connection = self.db_manager.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT id, username, role, is_active, created_at FROM users ORDER BY created_at DESC"
                cursor.execute(query)
                results = cursor.fetchall()
            return results
        except Exception as e:
            logger.error(f"取得所有用戶失敗: {e}")
            return []

    def create_user(self, username: str, password_hash: str, role: str) -> int:
        """創建新用戶"""
        try:
            connection = self.db_manager.get_connection()
            with connection.cursor() as cursor:
                query = "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)"
                cursor.execute(query, (username, password_hash, role))
                user_id = cursor.lastrowid
            connection.commit()
            return user_id
        except Exception as e:
            logger.error(f"創建用戶失敗: {e}")
            return -1

    def update_user_role(self, user_id: int, role: str) -> bool:
        """更新用戶管理員狀態"""
        try:
            connection = self.db_manager.get_connection()
            with connection.cursor() as cursor:
                query = "UPDATE users SET role = %s WHERE id = %s"
                cursor.execute(query, (role, user_id))
            connection.commit()
            return True
        except Exception as e:
            logger.error(f"更新用戶管理員狀態失敗: {e}")
            return False

    def deactivate_user(self, user_id: int) -> bool:
        """停用用戶"""
        try:
            connection = self.db_manager.get_connection()
            with connection.cursor() as cursor:
                query = "UPDATE users SET is_active = FALSE WHERE id = %s"
                cursor.execute(query, (user_id,))
            connection.commit()
            return True
        except Exception as e:
            logger.error(f"停用用戶失敗: {e}")
            return False

    def activate_user(self, user_id: int) -> bool:
        """啟用用戶"""
        try:
            connection = self.db_manager.get_connection()
            with connection.cursor() as cursor:
                query = "UPDATE users SET is_active = TRUE WHERE id = %s"
                cursor.execute(query, (user_id,))
            connection.commit()
            return True
        except Exception as e:
            logger.error(f"啟用用戶失敗: {e}")
            return False
            
    def update_user_password(self, user_id: int, password_hash: str) -> bool:
        """更新用戶密碼"""
        try:
            connection = self.db_manager.get_connection()
            with connection.cursor() as cursor:
                query = "UPDATE users SET password_hash = %s WHERE id = %s"
                cursor.execute(query, (password_hash, user_id))
            connection.commit()
            return True
        except Exception as e:
            logger.error(f"更新用戶密碼失敗: {e}")
            return False


class LLMRequestDAO:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_user_active_request_count(self, user_id: int) -> int:
        """取得用戶目前進行中的請求數 (status = 'pending')"""
        try:
            connection = self.db_manager.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT COUNT(*) FROM llm_requests WHERE user_id = %s AND status = 'pending'"
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
            # 日誌輸出返回結果的類型和內容
            logger.info(f"查詢結果: {result}, 類型: {type(result)}")
            return result.get("COUNT(*)", 0) if result else 0
        except Exception as e:
            logger.error(f"取得用戶 {user_id} 進行中請求數失敗: {e}")
            logger.error(f"異常類型: {type(e)}")
            logger.error(f"異常訊息: {str(e)}")
            logger.error(f"異常追蹤: {traceback.print_exc()}")
            return 0

    def add_user_request(self, user_id: int, conv_id: str, question: str) -> int:
        """新增一筆用戶請求，預設 status = 'pending'，回傳 request_id"""
        try:
            connection = self.db_manager.get_connection()
            with connection.cursor() as cursor:
                query = """
                    INSERT INTO llm_requests (user_id, conv_id, question, status)
                    VALUES (%s, %s, %s, 'pending')
                """
                cursor.execute(query, (user_id, conv_id, question))
                request_id = cursor.lastrowid
            connection.commit()
            return request_id
        except Exception as e:
            logger.error(f"新增用戶 {user_id} 請求失敗: {e}")
            return -1

    def mark_request_completed(
        self, request_id: int, response_time: float = None, error_message: str = None
    ):
        """將請求標記為 completed，並可選擇記錄 response_time 與 error_message"""
        try:
            connection = self.db_manager.get_connection()
            with connection.cursor() as cursor:
                query = "UPDATE llm_requests SET status = 'completed', updated_at = NOW(), response_time = %s, error_message = %s WHERE id = %s"
                # 若 response_time 或 error_message 為 None，需設為 NULL
                cursor.execute(
                    query,
                    (
                        response_time if response_time is not None else None,
                        error_message if error_message is not None else None,
                        request_id,
                    ),
                )
            connection.commit()
        except Exception as e:
            logger.error(f"標記請求 {request_id} 完成失敗: {e}")

    def has_user_active_request(self, user_id: int) -> bool:
        """檢查用戶是否有進行中的請求 (status = 'pending')"""
        try:
            connection = self.db_manager.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT 1 FROM llm_requests WHERE user_id = %s AND status = 'pending' LIMIT 1"
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
            return result is not None
        except Exception as e:
            logger.error(f"檢查用戶 {user_id} 是否有進行中請求失敗: {e}")
            return False

    def get_total_active_request_count(self) -> int:
        """取得全系統目前進行中的請求數 (status = 'pending')"""
        try:
            connection = self.db_manager.get_connection()
            with connection.cursor() as cursor:
                query = "SELECT COUNT(*) FROM llm_requests WHERE status = 'pending'"
                cursor.execute(query)
                result = cursor.fetchone()
            # 日誌輸出返回結果的類型和內容
            logger.info(f"查詢結果: {result}, 類型: {type(result)}")
            return result.get("COUNT(*)", 0) if result else 0
        except Exception as e:
            logger.error(f"取得全系統進行中請求數失敗: {str(e)}")
            logger.error(f"異常類型: {type(e)}")
            logger.error(f"異常訊息: {str(e)}")
            logger.error(f"異常追蹤: {traceback.print_exc()}")
            return 0


# 全域資料庫管理器
db_manager = DatabaseManager()
config_dao = ConfigDAO(db_manager)
conversation_dao = ConversationDAO(db_manager)
user_dao = UserDAO(db_manager)
llm_request_dao = LLMRequestDAO(db_manager)
