-- Insert dummy data into employees table
INSERT INTO employees (id, name, email, hashed_password, phone, department, position, user_type, profile_image, wellness_check_status, last_vibe, immediate_attention) VALUES
('EMP0000001', 'John Smith', 'john.smith@company.com', '$2a$10$xJwL3LFXlK8uMJ1XUXeR7.cHUMEHQ5RJTANt0hRWFqjgpKn4U7fUm', '5551234567', 'Engineering', 'Senior Developer', 'employee', '/images/profiles/john_smith.jpg', 'completed', 'happy', FALSE),
('EMP0000002', 'Sarah Johnson', 'sarah.johnson@company.com', '$2a$10$HxU5VgKxLKEx1rFHMnGX5uVL2rJJjZtA75hLjYYhWk8.duzgXpyB6', '5552345678', 'Marketing', 'Marketing Manager', 'employee', '/images/profiles/sarah_johnson.jpg', 'not_started', 'neutral', FALSE),
('EMP0000003', 'Michael Brown', 'michael.brown@company.com', '$2a$10$ftTWxz8GRmOQGhJIqhF3N.6U7aYqhPIZfkrS5nKn6xvTCj6PB4pXW', '5553456789', 'HR', 'HR Director', 'hr', '/images/profiles/michael_brown.jpg', 'completed', 'stressed', TRUE),
('EMP0000004', 'Emily Davis', 'emily.davis@company.com', '$2a$10$G5Ft3rEQnGkMfCFB/pz8Y.Xrx5MwUjKG9VyQ9tQkVCXxG.MCyZLnK', '5554567890', 'Finance', 'Financial Analyst', 'employee', '/images/profiles/emily_davis.jpg', 'not_received', 'happy', FALSE),
('EMP0000005', 'Robert Wilson', 'robert.wilson@company.com', '$2a$10$NXzDMDz6LDe3n8bKJQyV9eyFR51k.2zBB8J6R4Jp2HCvsMZMf/nXS', '5555678901', 'IT', 'Systems Administrator', 'admin', '/images/profiles/robert_wilson.jpg', 'completed', 'neutral', FALSE),
('EMP0000006', 'Jennifer Lee', 'jennifer.lee@company.com', '$2a$10$n6fkV3YHbYBWu.JRpnUB7.dVSbXzT.LYpPrsBxLz8iJoOXr.6MQzu', '5556789012', 'Sales', 'Sales Representative', 'employee', '/images/profiles/jennifer_lee.jpg', 'completed', 'happy', FALSE),
('EMP0000007', 'David Miller', 'david.miller@company.com', '$2a$10$Ug69Cy66kblGT.KXW72C3.K4LF3V8EKtaGZLhM4cJODxHe2nrCaHm', '5557890123', 'Engineering', 'Software Engineer', 'employee', '/images/profiles/david_miller.jpg', 'not_started', 'stressed', TRUE),
('EMP0000008', 'Lisa Anderson', 'lisa.anderson@company.com', '$2a$10$4QJ0S.7T4JtZND9bKzxhAOf0k8U0STPvzPWW0CJZpEp4D6c7KMHqS', '5558901234', 'Customer Support', 'Support Specialist', 'employee', '/images/profiles/lisa_anderson.jpg', 'completed', 'happy', FALSE),
('EMP0000009', 'James Taylor', 'james.taylor@company.com', '$2a$10$YxXt6qsV9Fv45EtLfj4g3OaobA/u6AEeZxptKSTTcq5.sWg7mD.iG', '5559012345', 'Product', 'Product Manager', 'employee', '/images/profiles/james_taylor.jpg', 'not_received', 'neutral', FALSE),
('EMP0000010', 'Patricia Moore', 'patricia.moore@company.com', '$2a$10$jG3V.hdqRITswFP/hKJnY.rr67nGMQK2ZhxRFMn77LmkNLFTzQzUu', '5550123456', 'HR', 'HR Specialist', 'hr', '/images/profiles/patricia_moore.jpg', 'completed', 'happy', FALSE);

-- Insert dummy data into chat_sessions table
INSERT INTO chat_sessions (employee_id, session_id, start_time, end_time, summary, escalated, suggestions, risk_factors, risk_score) VALUES
('EMP0000001', 'SES0000001', '2025-03-01 09:30:00+00', '2025-03-01 09:45:00+00', 'Discussed workload and project deadlines', FALSE, 'Consider redistributing tasks within the team', NULL, 2),
('EMP0000002', 'SES0000002', '2025-03-02 14:15:00+00', '2025-03-02 14:40:00+00', 'Discussed marketing campaign challenges', FALSE, 'Schedule follow-up with marketing director', NULL, 3),
('EMP0000003', 'SES0000003', '2025-03-03 11:00:00+00', '2025-03-03 11:30:00+00', 'Discussed HR policy updates and implementation timeline', FALSE, 'Provide additional resources for policy rollout', NULL, 1),
('EMP0000004', 'SES0000004', '2025-03-04 10:45:00+00', '2025-03-04 11:15:00+00', 'Discussed financial reporting deadlines', FALSE, 'Offer additional support during month-end close', NULL, 2),
('EMP0000005', 'SES0000005', '2025-03-05 16:00:00+00', '2025-03-05 16:20:00+00', 'Discussed system upgrade plans', FALSE, 'Review timeline for potential adjustments', NULL, 1),
('EMP0000006', 'SES0000006', '2025-03-06 13:30:00+00', '2025-03-06 14:00:00+00', 'Discussed sales targets and client acquisition strategies', FALSE, 'Schedule additional training session on new CRM features', NULL, 2),
('EMP0000007', 'SES0000007', '2025-03-07 09:00:00+00', '2025-03-07 09:45:00+00', 'Discussed ongoing project challenges and personal stress', TRUE, 'Immediate manager follow-up recommended', 'Mentions of burnout, sleep issues, deadline pressure', 7),
('EMP0000008', 'SES0000008', '2025-03-08 11:30:00+00', '2025-03-08 12:00:00+00', 'Discussed customer support queue management', FALSE, 'Review team allocation during peak hours', NULL, 2),
('EMP0000009', 'SES0000009', '2025-03-09 15:15:00+00', '2025-03-09 15:45:00+00', 'Discussed product roadmap and feature prioritization', FALSE, 'Schedule cross-team alignment meeting', NULL, 1),
('EMP0000010', 'SES0000010', '2025-03-10 10:00:00+00', '2025-03-10 10:30:00+00', 'Discussed HR recruitment plans for Q2', FALSE, 'Review budget allocation for external recruiters', NULL, 1);

-- Insert dummy data into chat_messages table
INSERT INTO chat_messages (session_id, question, answer) VALUES
('SES0000001', 'How are you feeling about your current workload?', 'I''m managing it, but feeling a bit concerned about the upcoming project deadline.'),
('SES0000001', 'What specifically concerns you about the deadline?', 'I think we might need more resources to complete everything on time.'),
('SES0000001', 'Have you discussed this with your team lead?', 'Not yet, I was planning to bring it up in our next team meeting.'),
('SES0000002', 'How is the new marketing campaign progressing?', 'We''re facing some challenges with the creative direction.'),
('SES0000002', 'What kind of challenges are you experiencing?', 'There seems to be a disconnect between what the client wants and what our creative team is producing.'),
('SES0000002', 'Have you considered bringing both teams together for a workshop?', 'That''s a good idea, I''ll see if I can arrange that for next week.'),
('SES0000003', 'How are the HR policy updates coming along?', 'We''re on track but there''s a lot to implement in a short timeframe.'),
('SES0000003', 'Are there specific areas that are particularly challenging?', 'The new leave policy has generated a lot of questions from employees.'),
('SES0000003', 'Would it help to create a detailed FAQ for employees?', 'Yes, that would definitely help address the common questions.'),
('SES0000007', 'How have you been feeling at work lately?', 'Honestly, I''ve been feeling overwhelmed and exhausted.'),
('SES0000007', 'Can you tell me more about what''s contributing to these feelings?', 'I''ve been working late every night for weeks, and I''m starting to have trouble sleeping.'),
('SES0000007', 'Have you discussed this with your manager?', 'No, I don''t want to seem like I can''t handle my responsibilities.'),
('SES0000007', 'What do you think would help improve the situation?', 'I think I need some of the deadlines extended or some help with the workload.');

-- Insert dummy data into activity_data table
INSERT INTO activity_data (employee_id, date, hours_worked, meetings_attended, emails_sent, teams_messages_sent) VALUES
('EMP0000001', '2025-03-01', 8, 3, 15, 42),
('EMP0000001', '2025-03-02', 9, 2, 20, 37),
('EMP0000001', '2025-03-03', 8, 4, 18, 45),
('EMP0000002', '2025-03-01', 8, 5, 25, 30),
('EMP0000002', '2025-03-02', 7, 3, 22, 28),
('EMP0000002', '2025-03-03', 9, 4, 30, 35),
('EMP0000003', '2025-03-01', 8, 6, 40, 25),
('EMP0000003', '2025-03-02', 8, 5, 35, 20),
('EMP0000003', '2025-03-03', 7, 4, 30, 22),
('EMP0000004', '2025-03-01', 8, 2, 15, 18),
('EMP0000004', '2025-03-02', 8, 1, 20, 15),
('EMP0000004', '2025-03-03', 9, 3, 25, 20),
('EMP0000005', '2025-03-01', 8, 4, 30, 45),
('EMP0000005', '2025-03-02', 10, 5, 35, 50),
('EMP0000005', '2025-03-03', 9, 3, 25, 40),
('EMP0000006', '2025-03-01', 8, 2, 40, 15),
('EMP0000006', '2025-03-02', 8, 3, 45, 20),
('EMP0000006', '2025-03-03', 8, 4, 35, 25),
('EMP0000007', '2025-03-01', 10, 2, 15, 30),
('EMP0000007', '2025-03-02', 11, 3, 20, 35),
('EMP0000007', '2025-03-03', 12, 1, 10, 25),
('EMP0000008', '2025-03-01', 8, 1, 50, 60),
('EMP0000008', '2025-03-02', 8, 0, 55, 65),
('EMP0000008', '2025-03-03', 8, 1, 45, 55),
('EMP0000009', '2025-03-01', 9, 5, 25, 30),
('EMP0000009', '2025-03-02', 8, 6, 30, 35),
('EMP0000009', '2025-03-03', 9, 4, 20, 25),
('EMP0000010', '2025-03-01', 8, 3, 35, 20),
('EMP0000010', '2025-03-02', 8, 4, 40, 25),
('EMP0000010', '2025-03-03', 8, 5, 30, 15);

-- Insert dummy data into leaves_data table
INSERT INTO leaves_data (employee_id, leave_type, start_date, end_date, leave_days) VALUES
('EMP0000001', 'Annual Leave', '2025-03-15', '2025-03-19', 5),
('EMP0000002', 'Sick Leave', '2025-03-05', '2025-03-06', 2),
('EMP0000003', 'Personal Leave', '2025-03-20', '2025-03-20', 1),
('EMP0000004', 'Annual Leave', '2025-04-10', '2025-04-17', 8),
('EMP0000005', 'Training Leave', '2025-03-25', '2025-03-26', 2),
('EMP0000006', 'Sick Leave', '2025-03-08', '2025-03-09', 2),
('EMP0000007', 'Personal Leave', '2025-03-22', '2025-03-22', 1),
('EMP0000008', 'Annual Leave', '2025-05-01', '2025-05-10', 10),
('EMP0000009', 'Conference Leave', '2025-04-15', '2025-04-18', 4),
('EMP0000010', 'Sick Leave', '2025-03-12', '2025-03-13', 2);

-- Insert dummy data into onboarding_data table
INSERT INTO onboarding_data (employee_id, onboarding_feedback, joining_date, mentor_assigned, training_completed) VALUES
('EMP0000001', 'Excellent', '2023-06-15', TRUE, TRUE),
('EMP0000002', 'Good', '2023-08-01', TRUE, TRUE),
('EMP0000003', 'Excellent', '2022-11-10', TRUE, TRUE),
('EMP0000004', 'Good', '2023-02-20', TRUE, TRUE),
('EMP0000005', 'Satisfactory', '2022-09-05', TRUE, TRUE),
('EMP0000006', 'Good', '2023-05-12', TRUE, TRUE),
('EMP0000007', 'Excellent', '2024-01-10', TRUE, FALSE),
('EMP0000008', 'Good', '2023-10-15', TRUE, TRUE),
('EMP0000009', 'Excellent', '2022-12-01', TRUE, TRUE),
('EMP0000010', 'Good', '2023-07-20', TRUE, TRUE);

-- Insert dummy data into rewards_data table
INSERT INTO rewards_data (employee_id, reward_type, reward_date, points) VALUES
('EMP0000001', 'Project Completion', '2024-12-15', 100),
('EMP0000001', 'Innovation Award', '2025-02-10', 150),
('EMP0000002', 'Sales Target Achievement', '2025-01-05', 120),
('EMP0000003', 'Employee of the Month', '2024-11-30', 200),
('EMP0000004', 'Process Improvement', '2025-01-20', 100),
('EMP0000005', 'System Upgrade Success', '2025-02-28', 150),
('EMP0000006', 'Client Satisfaction', '2025-01-10', 120),
('EMP0000007', 'Code Quality Award', '2025-03-01', 100),
('EMP0000008', 'Customer Service Excellence', '2025-02-15', 130),
('EMP0000009', 'Product Launch Success', '2024-12-20', 180),
('EMP0000010', 'Training Excellence', '2025-01-30', 100);

-- Insert dummy data into performance_data table
INSERT INTO performance_data (employee_id, review_period, performance_rating, manager_feedback, promotion_consideration) VALUES
('EMP0000001', '2024-12-31', 'Exceeds Expectations', 'Consistently delivers high-quality work and demonstrates strong technical skills.', TRUE),
('EMP0000002', '2024-12-31', 'Meets Expectations', 'Effectively manages marketing campaigns and works well with cross-functional teams.', FALSE),
('EMP0000003', '2024-12-31', 'Exceeds Expectations', 'Excellent leadership in HR initiatives and policy development.', TRUE),
('EMP0000004', '2024-12-31', 'Meets Expectations', 'Accurate financial analysis and timely reporting.', FALSE),
('EMP0000005', '2024-12-31', 'Exceeds Expectations', 'Outstanding system management and proactive issue resolution.', TRUE),
('EMP0000006', '2024-12-31', 'Meets Expectations', 'Consistently meets sales targets and maintains good client relationships.', FALSE),
('EMP0000007', '2024-12-31', 'Needs Improvement', 'Technical skills are strong but needs to improve team collaboration and time management.', FALSE),
('EMP0000008', '2024-12-31', 'Exceeds Expectations', 'Exceptional customer support and problem-solving skills.', TRUE),
('EMP0000009', '2024-12-31', 'Meets Expectations', 'Effective product management and feature prioritization.', FALSE),
('EMP0000010', '2024-12-31', 'Exceeds Expectations', 'Excellent HR program development and implementation.', TRUE);

-- Insert dummy data into vibemeter_data table
INSERT INTO vibemeter_data (employee_id, date, vibe_score, emotion_zone) VALUES
('EMP0000001', '2025-03-01', 85, 'happy'),
('EMP0000001', '2025-03-02', 80, 'happy'),
('EMP0000001', '2025-03-03', 82, 'happy'),
('EMP0000002', '2025-03-01', 75, 'neutral'),
('EMP0000002', '2025-03-02', 70, 'neutral'),
('EMP0000002', '2025-03-03', 72, 'neutral'),
('EMP0000003', '2025-03-01', 55, 'stressed'),
('EMP0000003', '2025-03-02', 50, 'stressed'),
('EMP0000003', '2025-03-03', 53, 'stressed'),
('EMP0000004', '2025-03-01', 90, 'happy'),
('EMP0000004', '2025-03-02', 88, 'happy'),
('EMP0000004', '2025-03-03', 92, 'happy'),
('EMP0000005', '2025-03-01', 75, 'neutral'),
('EMP0000005', '2025-03-02', 77, 'neutral'),
('EMP0000005', '2025-03-03', 73, 'neutral'),
('EMP0000006', '2025-03-01', 85, 'happy'),
('EMP0000006', '2025-03-02', 87, 'happy'),
('EMP0000006', '2025-03-03', 89, 'happy'),
('EMP0000007', '2025-03-01', 60, 'stressed'),
('EMP0000007', '2025-03-02', 55, 'stressed'),
('EMP0000007', '2025-03-03', 50, 'stressed'),
('EMP0000008', '2025-03-01', 88, 'happy'),
('EMP0000008', '2025-03-02', 90, 'happy'),
('EMP0000008', '2025-03-03', 87, 'happy'),
('EMP0000009', '2025-03-01', 73, 'neutral'),
('EMP0000009', '2025-03-02', 75, 'neutral'),
('EMP0000009', '2025-03-03', 74, 'neutral'),
('EMP0000010', '2025-03-01', 80, 'happy'),
('EMP0000010', '2025-03-02', 82, 'happy'),
('EMP0000010', '2025-03-03', 85, 'happy');