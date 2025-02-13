

USE axiora;

CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE LLM (
    llm_id INT AUTO_INCREMENT PRIMARY KEY,
    llm_name VARCHAR(255) NOT NULL,
    requirements TEXT
);

CREATE TABLE Session (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    data_info TEXT,
    llm_id INT NOT NULL,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (llm_id) REFERENCES LLM(llm_id) ON DELETE CASCADE
);

CREATE TABLE Data_Set (
    data_set_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    raw_data TEXT,
    transformed_data_set TEXT,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES Session(session_id) ON DELETE CASCADE
);

CREATE TABLE Dashboards (
    dashboard_id INT AUTO_INCREMENT PRIMARY KEY,
    data_set_id INT NOT NULL,
    FOREIGN KEY (data_set_id) REFERENCES Data_Set(data_set_id) ON DELETE CASCADE
);

CREATE TABLE Final_Report (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    recommendation TEXT NOT NULL,
    dashboard_id INT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES Session(session_id) ON DELETE CASCADE,
    FOREIGN KEY (dashboard_id) REFERENCES Dashboards(dashboard_id) ON DELETE CASCADE
);

CREATE TABLE Chat (
    chat_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    llm_id INT NOT NULL,
    number_dataset INT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES Session(session_id) ON DELETE CASCADE,
    FOREIGN KEY (llm_id) REFERENCES LLM(llm_id) ON DELETE CASCADE
);

CREATE TABLE Chat_History (
    chat_history_id INT AUTO_INCREMENT PRIMARY KEY,
    chat_id INT NOT NULL,
    message_number INT NOT NULL,
    prompt TEXT,
    response TEXT,
    additional_kwargs TEXT,
    response_metadata TEXT,
    FOREIGN KEY (chat_id) REFERENCES Chat(chat_id) ON DELETE CASCADE
);

CREATE TABLE Chat_DataSet (
    chat_dataset_id INT AUTO_INCREMENT PRIMARY KEY,
    chat_history_id INT NOT NULL,
    FOREIGN KEY (chat_history_id) REFERENCES Chat_History(chat_history_id) ON DELETE CASCADE
);

CREATE TABLE Questions (
    chat_history_id INT NOT NULL,
    question_num INT NOT NULL,
    question TEXT NOT NULL,
    PRIMARY KEY (chat_history_id, question_num),
    FOREIGN KEY (chat_history_id) REFERENCES Chat_History(chat_history_id) ON DELETE CASCADE
);

CREATE TABLE Summary (
    summary_id INT AUTO_INCREMENT PRIMARY KEY,
    summary_content TEXT,
    session_id INT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES Session(session_id) ON DELETE CASCADE
);

CREATE TABLE Charts (
    chart_id INT AUTO_INCREMENT PRIMARY KEY,
    chart_type VARCHAR(255) NOT NULL,
    dashboard_id INT NOT NULL,
    FOREIGN KEY (dashboard_id) REFERENCES Dashboards(dashboard_id) ON DELETE CASCADE
);

CREATE TABLE Session_Memory (
    session_id INT NOT NULL,
    llm_id INT NOT NULL,
    chat_history_id INT NOT NULL,
    prompt TEXT,
    response TEXT,
    additional_kwargs TEXT,
    response_metadata TEXT,
    message_number INT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES Session(session_id) ON DELETE CASCADE,
    FOREIGN KEY (llm_id) REFERENCES LLM(llm_id) ON DELETE CASCADE,
    FOREIGN KEY (chat_history_id) REFERENCES Chat_History(chat_history_id) ON DELETE CASCADE
);

-- Indexes for Performance Optimization
CREATE INDEX idx_session_id ON Chat(session_id);
CREATE INDEX idx_dashboard_id ON Charts(dashboard_id);
CREATE INDEX idx_chat_history_id ON Questions(chat_history_id);
CREATE INDEX idx_session_memory_id ON Session_Memory(session_id);
