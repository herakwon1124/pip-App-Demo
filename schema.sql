-- Relational schema for class_dataset.csv
-- Entity -> table, 1:N -> foreign key, M:N -> bridge table.
-- Name is not the primary key; student_id is generated.

CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    netid TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    school_year TEXT NOT NULL,
    intro_programming TEXT NOT NULL,
    skill_programming SMALLINT NOT NULL CHECK (skill_programming BETWEEN 1 AND 5),
    skill_data_stats SMALLINT NOT NULL CHECK (skill_data_stats BETWEEN 1 AND 5),
    skill_frontend_design SMALLINT NOT NULL CHECK (skill_frontend_design BETWEEN 1 AND 5),
    skill_business_pitch SMALLINT NOT NULL CHECK (skill_business_pitch BETWEEN 1 AND 5),
    working_style TEXT,
    interests TEXT,
    semester_goal TEXT,
    submitted_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE tools (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE student_tools (
    student_id INTEGER NOT NULL REFERENCES students (student_id) ON DELETE CASCADE,
    tool_id INTEGER NOT NULL REFERENCES tools (id) ON DELETE CASCADE,
    PRIMARY KEY (student_id, tool_id)
);

CREATE TABLE availability (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE student_availability (
    student_id INTEGER NOT NULL REFERENCES students (student_id) ON DELETE CASCADE,
    availability_id INTEGER NOT NULL REFERENCES availability (id) ON DELETE CASCADE,
    PRIMARY KEY (student_id, availability_id)
);
