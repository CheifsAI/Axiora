
USE axiora;


CREATE TABLE Users (
    user_id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(255) NOT NULL,
    password NVARCHAR(255) NOT NULL,
    email NVARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE Data_Set (
    data_set_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    transformed_data_set NVARCHAR(MAX),
    uploaded_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

CREATE TABLE Chats (
    chat_id INT IDENTITY(1,1) PRIMARY KEY,
    message_number INT NOT NULL,
    prompt NVARCHAR(MAX),
    data_set_id INT NOT NULL,
    FOREIGN KEY (data_set_id) REFERENCES Data_Set(data_set_id) ON DELETE CASCADE
);

CREATE TABLE LLM (
    llm_id INT IDENTITY(1,1) PRIMARY KEY,
    llm_name NVARCHAR(255) NOT NULL,
    requirements NVARCHAR(MAX),
    responses NVARCHAR(MAX)
);

CREATE TABLE Reports (
    report_id INT IDENTITY(1,1) PRIMARY KEY,
    summary NVARCHAR(MAX),
    recommendations NVARCHAR(MAX),
    questions NVARCHAR(MAX)
);

CREATE TABLE Dashboards (
    dashboard_id INT IDENTITY(1,1) PRIMARY KEY,
    data_set_id INT NOT NULL,
    FOREIGN KEY (data_set_id) REFERENCES Data_Set(data_set_id) ON DELETE CASCADE
);

CREATE TABLE Charts (
    chart_id INT IDENTITY(1,1) PRIMARY KEY,
    chart_type NVARCHAR(255) NOT NULL,
    dashboard_id INT NOT NULL,
    FOREIGN KEY (dashboard_id) REFERENCES Dashboards(dashboard_id) ON DELETE CASCADE
);

ALTER TABLE Chats ADD llm_id INT;
ALTER TABLE Chats ADD FOREIGN KEY (llm_id) REFERENCES LLM(llm_id);

ALTER TABLE Data_Set ADD llm_id INT;
ALTER TABLE Data_Set ADD FOREIGN KEY (llm_id) REFERENCES LLM(llm_id);

ALTER TABLE Reports ADD data_set_id INT;
ALTER TABLE Reports ADD FOREIGN KEY (data_set_id) REFERENCES Data_Set(data_set_id) ON DELETE CASCADE;

