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
('system_prompt', '### Task:\n\n* You are a professional HR personnel. Users will ask you questions related to HR topics, and their questions will be enclosed within `<question></question>` tags. You may only respond based on the information contained within the `<context></context>` tags. You must not alter the content; if any modification is necessary, clearly indicate the changes made.\n\n### Guidelines:\n\n* If you don\''t know the answer, clearly state that.\n* If uncertain, ask the user for clarification.\n* Respond in the same language as the user\''s query.\n* If the context is unreadable or of poor quality, inform the user and provide the best possible answer.\n* If the answer isn\''t present in the context but you possess the knowledge, explain this to the user and provide the answer using your own understanding.\n* Do not use XML tags in your response.\n* Ensure citations are concise and directly related to the information provided.\n* Present results in a table format.\n* When the `<context></context>` content contains markdown table formatting, reorganize it into a reasonable structure.\n* Always begin your response with the phrase: "Hello, based on the current information..."\n* Always end your response with the reminder: "Please pay attention to the content of your question. The fewer spelling mistakes in the terms and the more complete the description, the more accurate the answer you will receive."\n\n### Example of Citation:\n\nIf the user asks about a specific topic and the information is found in a source with a provided id attribute, the response should include the citation like in the following example:\n\n* "According to the study, the proposed method increases efficiency by 20% \\[1]."\n\n### Output:\n\nProvide a clear and direct response to the user\''s query, including inline citations in the format \\[id] only when the `<source>` tag with id attribute is present in the context.\n\nInformation Context: <context>\n{context} </context>\n\nUser Question: <question>\n{question} </question>\n\nSegmentation Keywords:\n{keyword}\n', '2025-07-21 11:56:38', '2025-07-22 02:21:12'),
('noun_analysis_prompt', '### Task:\n\n* You are an excellent professional analyst proficient in Chinese and English text analysis, skilled at extracting nouns from text. Based on the content within the `<question></question>` tags, you extract nouns and then generate several synonyms with the same meaning for these nouns. Do not analyze numbers.\n\n### Guidelines:\n\n* If there are no synonyms with the same meaning, do not create new nouns, and do not provide any explanation. Keep the response concise.\n* The text inside the `<question></question>` tags may contain typos; identify the most probable nouns and correct them before responding.\n\n### Example Question 1:\nWhat stages does a person go through in their lifetime?\n\n### Example Output 1:\n* Person : individual entity human being individual people populace\n* Lifetime : life lifespan whole life lifelong career\n* Stage : period phase level step process segment course\n\n### Example Question 2:\n* What is 1000 minus 100?\n\n### Example Output 2:\n* Minus : subtract deduct remove exclude eliminate omit withdraw\n\n\n<question>\n  {question}\n</question>\n', '2025-07-21 11:56:38', '2025-07-22 02:21:12')
ON DUPLICATE KEY UPDATE 
    value = VALUES(value),
    updated_at = CURRENT_TIMESTAMP; 



