# SpeakInsights - Requirement Analysis & Final Workflow
## AI-Powered Meeting Assistant

---

## Table of Contents
1. **Requirement Analysis**
   - Functional Requirements
   - Non-Functional Requirements
   - System Requirements
   - User Requirements

2. **Final Workflow**
   - System Architecture
   - Data Flow Diagram
   - Processing Pipeline
   - User Journey
   - Technology Stack

---

# PART 1: REQUIREMENT ANALYSIS

## 1.1 Functional Requirements

### Core Features
- **Audio Transcription**
  - Convert meeting audio files to text using OpenAI Whisper
  - Support multiple audio formats (MP3, WAV, M4A)
  - Handle audio files up to 100MB

- **Meeting Summarization**
  - Generate concise summaries using DistilBART model
  - Handle long transcripts through intelligent chunking
  - Provide contextual summaries for different meeting types

- **Sentiment Analysis**
  - Analyze emotional tone of meetings using RoBERTa model
  - Identify top 3 emotions with confidence scores
  - Filter professional-relevant sentiments

- **Action Item Extraction**
  - Use NLP pattern matching to identify tasks
  - Extract actionable items with keywords like "will", "need to", "should"
  - Return top 5 prioritized action items

- **Data Persistence**
  - Store all meeting data in SQLite database
  - Save transcripts, summaries, sentiment analysis, and action items
  - Maintain meeting metadata (title, date, audio filename)

### API Endpoints
- `POST /api/meetings/upload` - Process new meeting
- `GET /api/meetings` - Retrieve all meetings
- `GET /api/meetings/{id}` - Get specific meeting details

### Web Interface
- **Upload Interface**: Easy drag-and-drop audio file upload
- **Dashboard**: View all processed meetings
- **Meeting Details**: Display transcript, summary, sentiment, and action items
- **Export Features**: Download transcripts and meeting insights

## 1.2 Non-Functional Requirements

### Performance Requirements
- **Processing Time**: Complete analysis within 5-10 minutes for 1-hour audio
- **File Size**: Support audio files up to 100MB
- **Concurrent Users**: Handle multiple simultaneous uploads
- **Response Time**: API responses within 2-3 seconds for data retrieval

### Scalability Requirements
- **Storage**: Expandable database for growing meeting archives
- **Processing**: Asynchronous processing for multiple files
- **Model Loading**: Efficient model caching to reduce startup time

### Security Requirements
- **Data Privacy**: Local processing and storage of sensitive meeting data
- **File Validation**: Secure file upload with format verification
- **CORS**: Proper cross-origin resource sharing configuration

### Usability Requirements
- **User-Friendly Interface**: Intuitive Streamlit web application
- **Progress Indicators**: Real-time processing status updates
- **Error Handling**: Clear error messages and recovery options
- **Accessibility**: Responsive design for different screen sizes

## 1.3 System Requirements

### Hardware Requirements
- **Minimum RAM**: 8GB (16GB recommended for optimal performance)
- **Storage**: 10GB free space for models and data
- **Processor**: Multi-core CPU for efficient processing
- **GPU**: Optional CUDA support for faster AI model inference

### Software Requirements
- **Operating System**: Windows, Linux, or macOS
- **Python**: Version 3.8+ with pip package manager
- **FFMPEG**: Audio processing library (included in project)
- **Browser**: Modern web browser for frontend access

### Dependencies
```
- FastAPI 0.104.1 (Web framework)
- Streamlit 1.28.2 (Frontend interface)
- OpenAI Whisper 20231117 (Speech-to-text)
- Transformers 4.35.2 (NLP models)
- PyTorch 2.0.1 (Deep learning framework)
- Pandas 2.1.3 (Data manipulation)
- NLTK 3.8.1 (Natural language processing)
```

## 1.4 User Requirements

### Primary Users
1. **Business Professionals**: Need meeting summaries and action items
2. **Project Managers**: Require task tracking and follow-up items
3. **Team Leaders**: Want sentiment analysis for team dynamics
4. **Researchers**: Need accurate transcriptions for analysis

### User Stories
- **As a user**, I want to upload meeting recordings and get automatic transcripts
- **As a manager**, I need quick summaries to understand key discussion points
- **As a team member**, I want to see action items assigned during meetings
- **As an analyst**, I need sentiment data to gauge team morale and engagement

---

# PART 2: FINAL WORKFLOW

## 2.1 System Architecture

### High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│  (Streamlit)    │◄──►│   (FastAPI)     │◄──►│   (SQLite)      │
│                 │    │                 │    │                 │
│ - File Upload   │    │ - API Endpoints │    │ - Meeting Data  │
│ - Dashboard     │    │ - NLP Processing│    │ - Transcripts   │
│ - Meeting View  │    │ - Audio Process │    │ - Insights      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Details

#### Frontend Layer (Streamlit)
- **Purpose**: User interface for interaction
- **Location**: `frontend/app.py`
- **Features**:
  - File upload interface
  - Meeting dashboard
  - Real-time processing status
  - Data visualization

#### Backend Layer (FastAPI)
- **Purpose**: API server and processing engine
- **Location**: `app/main.py`
- **Components**:
  - RESTful API endpoints
  - File handling and validation
  - ML model orchestration
  - Database operations

#### Data Layer (SQLite)
- **Purpose**: Persistent data storage
- **Location**: `speakinsights.db`
- **Storage**:
  - Meeting metadata
  - Full transcripts
  - Generated summaries
  - Sentiment analysis results
  - Extracted action items

## 2.2 Data Flow Diagram

```
[User] → [Upload Audio] → [FastAPI Backend]
                              ↓
                         [Save Audio File]
                              ↓
                      [Whisper Transcription]
                              ↓
                         [NLP Processing]
                              ↓
                    ┌─────────┼─────────┐
                    ↓         ↓         ↓
              [Summarization] [Sentiment] [Action Items]
                    ↓         ↓         ↓
                    └─────────┼─────────┘
                              ↓
                      [Save to Database]
                              ↓
                       [Return Results]
                              ↓
                      [Display in UI]
```

## 2.3 Processing Pipeline

### Step 1: Audio Upload & Validation
```python
# File validation and storage
- Check file format (MP3, WAV, M4A)
- Validate file size (< 100MB)
- Save to data/audio/ directory
- Generate unique filename
```

### Step 2: Speech-to-Text Transcription
```python
# Using OpenAI Whisper
- Load audio file with FFMPEG
- Process through Whisper base model
- Generate full transcript text
- Handle errors and timeouts
```

### Step 3: NLP Processing Pipeline
```python
# Parallel processing of transcript
├── Summarization (DistilBART)
│   ├── Text chunking for long content
│   ├── Generate concise summary
│   └── Handle context preservation
│
├── Sentiment Analysis (RoBERTa)
│   ├── Sample text for performance
│   ├── Analyze emotional content
│   └── Filter professional sentiments
│
└── Action Item Extraction (Pattern Matching)
    ├── Identify action keywords
    ├── Extract task phrases
    └── Prioritize and deduplicate
```

### Step 4: Data Storage & Response
```python
# Database operations
- Create meeting record
- Store all generated insights
- Return structured response
- Update UI with results
```

## 2.4 User Journey

### Typical User Flow
1. **Access Application**
   - Navigate to Streamlit interface (localhost:8501)
   - View dashboard with previous meetings

2. **Upload New Meeting**
   - Click "Upload New Meeting" in sidebar
   - Enter meeting title
   - Select audio file from device
   - Click "Process Meeting"

3. **Processing Phase**
   - View real-time processing status
   - Wait for transcription completion
   - See NLP analysis progress

4. **Review Results**
   - Access meeting from dashboard
   - Read generated summary
   - Review full transcript
   - Check identified action items
   - Analyze sentiment insights

5. **Export & Share**
   - Download transcript as text file
   - Copy summary for reports
   - Share action items with team

## 2.5 Technology Stack

### Frontend Technologies
- **Streamlit**: Web application framework
- **Python**: Core programming language
- **HTML/CSS**: UI styling and layout
- **JavaScript**: Interactive components

### Backend Technologies
- **FastAPI**: Modern Python web framework
- **Uvicorn**: ASGI server implementation
- **Pydantic**: Data validation and serialization
- **CORS Middleware**: Cross-origin request handling

### AI/ML Technologies
- **OpenAI Whisper**: State-of-the-art speech recognition
- **Transformers**: HuggingFace NLP library
- **DistilBART**: Text summarization model
- **RoBERTa**: Sentiment analysis model
- **PyTorch**: Deep learning framework
- **NLTK**: Natural language processing toolkit

### Data Technologies
- **SQLite**: Lightweight database system
- **Pandas**: Data manipulation and analysis
- **JSON**: Data exchange format

### Infrastructure
- **FFMPEG**: Audio processing library
- **Docker**: Containerization (planned)
- **Git**: Version control system

## 2.6 Deployment Architecture

### Development Environment
```
Local Machine
├── Python Virtual Environment
├── FastAPI Backend (Port 8000)
├── Streamlit Frontend (Port 8501)
├── SQLite Database
└── Audio File Storage
```

### Production Considerations
- **Containerization**: Docker containers for easy deployment
- **Load Balancing**: Handle multiple concurrent users
- **Cloud Storage**: Scalable file storage solutions
- **Database Migration**: PostgreSQL for production scale
- **Monitoring**: Health checks and performance metrics

---

## Key Benefits & Features Summary

### 🎯 **Core Value Proposition**
- **Time Savings**: Automatic meeting documentation
- **Accuracy**: AI-powered transcription and analysis
- **Insights**: Sentiment and action item extraction
- **Accessibility**: Easy-to-use web interface

### 🚀 **Technical Highlights**
- **Modern Architecture**: FastAPI + Streamlit stack
- **State-of-the-art AI**: OpenAI Whisper + Transformers
- **Scalable Design**: Modular component architecture
- **Local Processing**: Privacy-focused data handling

### 📈 **Future Enhancements**
- Real-time transcription during live meetings
- Integration with Zoom, Teams, and Google Meet
- Advanced analytics and reporting features
- Multi-language support and translation
- Cloud deployment and collaboration features

---

*This presentation content provides a comprehensive overview of the SpeakInsights project requirements and workflow. Each section can be expanded into detailed slides with visual diagrams and code examples as needed.*
