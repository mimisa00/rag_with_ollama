-- 建立資料庫
CREATE DATABASE IF NOT EXISTS rag_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE rag_db;

-- 建立使用者表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100),
    password_hash VARCHAR(255),
    role ENUM('admin', 'user') DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_role (role)
);

-- 建立配置表
CREATE TABLE IF NOT EXISTS configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_key (`key`)
);

-- 建立對話記錄表
CREATE TABLE IF NOT EXISTS conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conv_id VARCHAR(100) NOT NULL,
    user_id VARCHAR(36),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_conv_id (conv_id),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- 建立 LLM 請求狀態追蹤表
CREATE TABLE IF NOT EXISTS llm_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    conv_id VARCHAR(100),
    question TEXT,
    status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
    error_message TEXT,
    response_time FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- 插入預設配置
INSERT INTO configs (`key`, value) VALUES
('docling_image_export_mode', 'placeholder'),
('embedding_model', 'intfloat/multilingual-e5-large'),
('chunk_size', '512'),
('chunk_overlap', '64'),
('idx_result_count', '20'),
('rerank_top_k_final', '16'),
('llm_model', 'gemma3:4b'),
('is_enable_think', 'false'),
('llm_req_limit_total', '3'),
('llm_req_limit_user', '1'),
('num_ctx', '4096'),
('repeat_last_n', '64'),
('repeat_penalty', '1.1'),
('temperature', '0.5'),
('seed', '0'),
('stop', '[<|endoftext|>]'),
('num_predict', '1024'),
('top_k', '10'),
('top_p', '0.9'),
('min_p', '0.0'),
('system_prompt', '### Task:\n- 你是一名專業的HR 人員，使用者將對你提問有關HR相關的問題，提問的內容放在 `<question></question>`  tags 裡面，你只能根據 `<context></context>` 標籤內的內容回應資訊，不可以自行修改內容，如有任何修改，務必清楚標示出所做的變更。\n\n### Guidelines:\n- If you don''t know the answer, clearly state that.\n- If uncertain, ask the user for clarification.\n- Respond in the same language as the user''s query.\n- If the context is unreadable or of poor quality, inform the user and provide the best possible answer.\n- If the answer isn''t present in the context but you possess the knowledge, explain this to the user and provide the answer using your own understanding.\n- Do not use XML tags in your response.\n- Ensure citations are concise and directly related to the information provided.\n- 用表格呈現結果\n- `<context></context>` 內容含有 markdown 格式的表格標記時，需要重組成合理的結構\n- 回答問題的開頭一律為這個格式「您好，根據目前的資訊...」\n- 回答的最後一定要提醒使用者「請注意輸入的問題內容，名詞錯別字越少、描述的越完整才能得到越正確的答案。」\n\n### Example of Citation:\nIf the user asks about a specific topic and the information is found in a source with a provided id attribute, the response should include the citation like in the following example:\n* \"According to the study, the proposed method increases efficiency by 20% [1].\"\n\n### Output:\nProvide a clear and direct response to the user''s query, including inline citations in the format [id] only when the <source> tag with id attribute is present in the context.\n\n\nInformation Context:\n<context>\n{context}\n</context>\n\nUser Question:\n<question>\n{question}\n</question>\n\n分詞的關鍵字 :\n{keyword}'),
('noun_analysis_prompt', '### 任務:\n- 你是一名最優秀的專業中文、英文文字分析人員擅長將文字裡面的名詞取出來，你根據 `<question></question>` 這段標籤的內容將名詞提取出來，然後透過這些名詞再產生幾個相同語義的名詞，你不分析數字。\n\n### Guidelines:\n- 如果沒有相同語義的名詞，不要自己創造新的名詞，不要任何說明，保持簡潔的回覆\n- <question></question>` 標籤內容的文字有可能打錯字，找出最有可能的名詞進行修正後回覆\n\n### 範例問題 1:\n- 人的一生會經過哪幾個階段?\n\n### 範例輸出 1:\n-  人 : 人物 個體 人類 人士 人們 民眾\n- 一生 : 生命 人生 一輩子 終身 生涯\n- 階段 : 時期 階層 階次 階程 段落 歷程\n\n### 範例問題 2:\n- 1000減掉100等於多少?\n\n### 範例輸出 2:\n- 減掉 : 扣除 減去 刪除 去除 省掉 排除 移除\n\n<question>\n  {question}\n</question>')
ON DUPLICATE KEY UPDATE 
    value = VALUES(value),
    updated_at = CURRENT_TIMESTAMP; 