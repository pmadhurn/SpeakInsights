-- Initialize SpeakInsights PostgreSQL Database
-- This script runs when the PostgreSQL container starts for the first time

-- Create the meetings table with all required fields
CREATE TABLE IF NOT EXISTS meetings (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    date TIMESTAMP NOT NULL,
    transcript TEXT,
    summary TEXT,
    sentiment TEXT,
    sentiment_score REAL,
    action_items JSONB,
    audio_filename TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_meetings_created_at ON meetings(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_meetings_title ON meetings(title);
CREATE INDEX IF NOT EXISTS idx_meetings_date ON meetings(date DESC);

-- Create a simple view for meeting summaries
CREATE OR REPLACE VIEW meeting_summaries AS
SELECT 
    id,
    title,
    date,
    created_at,
    CASE 
        WHEN LENGTH(transcript) > 100 THEN LEFT(transcript, 100) || '...'
        ELSE transcript
    END as transcript_preview,
    summary,
    sentiment,
    sentiment_score,
    jsonb_array_length(COALESCE(action_items, '[]'::jsonb)) as action_item_count,
    audio_filename
FROM meetings
ORDER BY created_at DESC;

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON TABLE meetings TO speakinsights_user;
GRANT ALL PRIVILEGES ON SEQUENCE meetings_id_seq TO speakinsights_user;
GRANT SELECT ON meeting_summaries TO speakinsights_user;

-- Insert a sample meeting for testing (optional)
INSERT INTO meetings (title, date, transcript, summary, sentiment, sentiment_score, action_items, audio_filename)
VALUES (
    'Sample Meeting - Docker Setup',
    NOW(),
    'This is a sample transcript to verify that the database is working correctly in Docker.',
    'Sample meeting to test database functionality.',
    'positive (75%)',
    0.75,
    '["Test database connection", "Verify Docker setup"]'::jsonb,
    'sample_audio.mp3'
) ON CONFLICT DO NOTHING;

