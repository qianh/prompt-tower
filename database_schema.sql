-- PostgreSQL DDL Script for Prompt Management System

-- Ensure to connect to your target database before running this script.
-- Example: psql -U your_username -d your_database_name

-- ---
-- Table: users
-- ---
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- ---
-- Table: tags
-- ---
CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);

-- ---
-- Table: prompts
-- ---
CREATE TABLE IF NOT EXISTS prompts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    description TEXT,
    creator_username VARCHAR(255), -- Will be linked via FOREIGN KEY
    status VARCHAR(50) DEFAULT 'active',
    version VARCHAR(50),
    usage_count INTEGER DEFAULT 0,
    priority INTEGER DEFAULT 0,
    settings JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_creator_username
        FOREIGN KEY(creator_username) 
        REFERENCES users(username)
        ON DELETE SET NULL  -- Or RESTRICT if prompts must always have a valid creator
        ON UPDATE CASCADE   -- If usernames can change and you want to reflect it
);

CREATE INDEX IF NOT EXISTS idx_prompts_title ON prompts(title);
CREATE INDEX IF NOT EXISTS idx_prompts_creator_username ON prompts(creator_username);
CREATE INDEX IF NOT EXISTS idx_prompts_status ON prompts(status);

-- ---
-- Table: prompt_tags (Association Table)
-- ---
CREATE TABLE IF NOT EXISTS prompt_tags (
    id SERIAL PRIMARY KEY,
    prompt_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    CONSTRAINT fk_prompt
        FOREIGN KEY(prompt_id) 
        REFERENCES prompts(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_tag
        FOREIGN KEY(tag_id) 
        REFERENCES tags(id)
        ON DELETE CASCADE,
    UNIQUE (prompt_id, tag_id)
);

CREATE INDEX IF NOT EXISTS idx_prompt_tags_prompt_id ON prompt_tags(prompt_id);
CREATE INDEX IF NOT EXISTS idx_prompt_tags_tag_id ON prompt_tags(tag_id);

-- ---
-- Update timestamps trigger function (Optional, but good practice)
-- This automatically updates the 'updated_at' field on row modification.
-- ---
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply the trigger to tables that have 'updated_at'
-- Note: 'users' table already has DEFAULT CURRENT_TIMESTAMP for updated_at, 
-- which works for inserts. This trigger handles updates.
-- If you want created_at to be strictly insert-only and updated_at to reflect any change:

DROP TRIGGER IF EXISTS set_timestamp_users ON users; 
CREATE TRIGGER set_timestamp_users
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

DROP TRIGGER IF EXISTS set_timestamp_prompts ON prompts;
CREATE TRIGGER set_timestamp_prompts
BEFORE UPDATE ON prompts
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Note: 'tags' table doesn't have an 'updated_at' in the current schema design,
-- but if it did, you would add a trigger for it too.

COMMENT ON TABLE users IS 'Stores user information including username and hashed passwords.';
COMMENT ON TABLE tags IS 'Stores a global list of unique tags for prompts.';
COMMENT ON TABLE prompts IS 'Stores prompt details, content, metadata, and associations.';
COMMENT ON TABLE prompt_tags IS 'Associates prompts with tags in a many-to-many relationship.';

-- End of DDL script
