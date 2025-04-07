-- Create the custom enum types first
CREATE TYPE user_type_enum AS ENUM ('admin', 'hr', 'employee');
CREATE TYPE wellness_check_status_enum AS ENUM ('not_received', 'not_started', 'completed');

-- Create the tables
CREATE TABLE IF NOT EXISTS employees (
    id CHAR(10) NOT NULL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    phone CHAR(10) NOT NULL,
    department VARCHAR(50),
    position VARCHAR(100),
    user_type user_type_enum NOT NULL,
    profile_image VARCHAR(255),
    wellness_check_status wellness_check_status_enum NOT NULL DEFAULT 'not_received',
    last_vibe VARCHAR(20) NOT NULL,
    immediate_attention BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS chat_sessions (
    employee_id CHAR(10) NOT NULL,
    session_id CHAR(10) NOT NULL PRIMARY KEY,
    start_time TIMESTAMPTZ DEFAULT now(),
    end_time TIMESTAMPTZ,
    summary TEXT,
    escalated BOOLEAN DEFAULT FALSE,
    suggestions TEXT,
    risk_factors TEXT,
    risk_score INT,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    session_id CHAR(10) NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS activity_data (
    id SERIAL PRIMARY KEY,
    employee_id CHAR(10) NOT NULL,
    date DATE NOT NULL,
    hours_worked INT NOT NULL,
    meetings_attended INT NOT NULL,
    emails_sent INT NOT NULL,
    teams_messages_sent INT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS leaves_data (
    id SERIAL PRIMARY KEY,
    employee_id CHAR(10) NOT NULL,
    leave_type VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    leave_days INT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS onboarding_data (
    id SERIAL PRIMARY KEY,
    employee_id CHAR(10) NOT NULL,
    onboarding_feedback VARCHAR(50),
    joining_date DATE NOT NULL,
    mentor_assigned BOOLEAN NOT NULL DEFAULT FALSE,
    training_completed BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rewards_data (
    id SERIAL PRIMARY KEY,
    employee_id CHAR(10) NOT NULL,
    reward_type VARCHAR(50) NOT NULL,
    reward_date DATE NOT NULL,
    points INT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS performance_data (
    id SERIAL PRIMARY KEY,
    employee_id CHAR(10) NOT NULL,
    review_period DATE NOT NULL,
    performance_rating VARCHAR(50) NOT NULL,
    manager_feedback TEXT,
    promotion_consideration BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS vibemeter_data (
    id SERIAL PRIMARY KEY,
    employee_id CHAR(10) NOT NULL,
    date DATE NOT NULL,
    vibe_score INT NOT NULL,
    emotion_zone VARCHAR(50) NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);