-- Create a simple meetings table if it doesn't exist
CREATE TABLE IF NOT EXISTS meetings (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    date TIMESTAMP NOT NULL,
    transcript TEXT,
    summary TEXT,
    sentiment TEXT,
    action_items JSONB,
    audio_filename TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

