# WhisperX Integration for SpeakInsights

This document describes the WhisperX integration that enhances SpeakInsights with advanced transcription capabilities including speaker diarization, VAD preprocessing, and word-level timestamps.

## 🚀 Features

### Enhanced Transcription
- **70× faster** than standard Whisper on GPU
- **Word-level timestamps** with precise alignment
- **VAD (Voice Activity Detection)** preprocessing for better accuracy
- **Speaker diarization** - identifies who said what
- **Multiple speaker detection** and labeling
- **Enhanced accuracy** for long-form audio

### Integration Benefits
- **Seamless fallback** to standard Whisper if WhisperX unavailable
- **Rich metadata** including speaker information and timing
- **Formatted transcripts** with speaker labels
- **Speaker analytics** and timeline visualization
- **Both Python API and CLI** approaches supported

## 📦 Installation

### Automatic Setup
```bash
python setup_whisperx.py
```

### Manual Installation
```bash
# Install WhisperX
pip install whisperx

# Install additional dependencies
pip install pyannote.audio>=3.1.0 faster-whisper>=0.9.0 ctranslate2>=3.20.0 onnxruntime>=1.16.0
```

### Hugging Face Token (for Speaker Diarization)
1. Visit https://huggingface.co/settings/tokens
2. Create a new token with 'Read' access
3. Add to `config.json`:
```json
{
  "whisperx_settings": {
    "hf_token": "your_token_here"
  }
}
```

## ⚙️ Configuration

WhisperX settings in `config.json`:

```json
{
  "whisperx_settings": {
    "enabled": true,
    "model_size": "large-v2",
    "compute_type": "float16",
    "batch_size": 16,
    "enable_vad": true,
    "vad_onset": 0.500,
    "vad_offset": 0.363,
    "enable_diarization": true,
    "min_speakers": null,
    "max_speakers": null,
    "hf_token": null,
    "device": "auto",
    "language": "en",
    "align_model": null,
    "interpolate_method": "nearest"
  }
}
```

### Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| `enabled` | Enable WhisperX transcription | `true` |
| `model_size` | Whisper model size | `"large-v2"` |
| `compute_type` | Computation precision | `"float16"` |
| `batch_size` | Processing batch size | `16` |
| `enable_vad` | Voice Activity Detection | `true` |
| `vad_onset` | VAD onset threshold | `0.500` |
| `vad_offset` | VAD offset threshold | `0.363` |
| `enable_diarization` | Speaker diarization | `true` |
| `min_speakers` | Minimum speakers (auto if null) | `null` |
| `max_speakers` | Maximum speakers (auto if null) | `null` |
| `hf_token` | Hugging Face token | `null` |
| `device` | Processing device | `"auto"` |
| `language` | Audio language | `"en"` |

### Model Recommendations

| Model | Speed | Accuracy | Memory | Use Case |
|-------|-------|----------|--------|----------|
| `large-v2` | Slower | Best | High | Production, best quality |
| `medium` | Medium | Good | Medium | Balanced performance |
| `small` | Fast | Fair | Low | Quick processing |
| `base` | Fastest | Basic | Lowest | Testing, demos |

## 🎯 Usage

### Python API

```python
from app.transcription import transcribe_audio, get_transcript_text, get_transcription_metadata

# Enhanced transcription with WhisperX
result = transcribe_audio("audio.mp3", use_whisperx=True)

# Extract plain text
transcript = get_transcript_text(result)

# Get metadata
metadata = get_transcription_metadata(result)
print(f"Speakers detected: {len(metadata['speakers'])}")
print(f"Has speakers: {metadata['has_speakers']}")
```

### Direct WhisperX API

```python
from app.whisperx_transcription import transcribe_with_whisperx

result = transcribe_with_whisperx(
    audio_path="audio.mp3",
    enable_vad=True,
    enable_diarization=True,
    min_speakers=2,
    max_speakers=5
)

print(f"Transcript: {result['transcript']}")
print(f"Formatted: {result['formatted_transcript']}")
print(f"Speakers: {result['speakers']}")
```

### Command Line Interface

```bash
# Process single file
python whisperx_cli.py audio.mp3

# Process with output directory
python whisperx_cli.py audio.mp3 -o ./output

# Batch process directory
python whisperx_cli.py -d ./audio_files -o ./transcripts

# Use specific model
python whisperx_cli.py audio.mp3 --model large-v3

# Disable diarization
python whisperx_cli.py audio.mp3 --no-diarization

# Use CLI method
python whisperx_cli.py audio.mp3 --cli
```

## 📊 Output Format

### Enhanced Result Structure

```json
{
  "transcript": "Full plain text transcript",
  "formatted_transcript": "[SPEAKER_00]: Hello there...\n[SPEAKER_01]: Hi, how are you?",
  "segments": [
    {
      "start": 0.0,
      "end": 2.5,
      "text": "Hello there",
      "words": [
        {
          "word": "Hello",
          "start": 0.0,
          "end": 0.5,
          "score": 0.95,
          "speaker": "SPEAKER_00"
        }
      ]
    }
  ],
  "speaker_segments": [
    {
      "speaker": "SPEAKER_00",
      "text": "Hello there",
      "start": 0.0,
      "end": 2.5
    }
  ],
  "word_level_data": [
    {
      "word": "Hello",
      "start": 0.0,
      "end": 0.5,
      "score": 0.95,
      "speaker": "SPEAKER_00"
    }
  ],
  "speakers": ["SPEAKER_00", "SPEAKER_01"],
  "language": "en",
  "has_speakers": true,
  "processing_info": {
    "total_segments": 10,
    "total_words": 150,
    "total_speakers": 2,
    "duration": 60.0
  }
}
```

## 🎭 Speaker Diarization

### Requirements
- Hugging Face token (free account)
- `pyannote.audio` library
- Internet connection for model download

### Speaker Labels
- Automatic: `SPEAKER_00`, `SPEAKER_01`, etc.
- Configurable min/max speaker limits
- Timeline visualization in frontend

### Accuracy Factors
- Audio quality (clear speech, minimal background noise)
- Speaker distinctiveness (different voices)
- Sufficient speech per speaker
- Proper microphone setup

## 🔧 Troubleshooting

### Common Issues

#### WhisperX Not Available
```bash
# Install WhisperX
pip install whisperx

# Check installation
python -c "import whisperx; print('WhisperX available')"
```

#### GPU Not Detected
```bash
# Check CUDA installation
python -c "import torch; print(torch.cuda.is_available())"

# Install CUDA-compatible PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### Diarization Fails
- Verify Hugging Face token is valid
- Check internet connection
- Ensure `pyannote.audio` is installed
- Try without diarization first

#### Memory Issues
- Use smaller model (`medium`, `small`, `base`)
- Reduce batch size in config
- Use CPU instead of GPU
- Process shorter audio segments

#### Slow Processing
- Ensure GPU is being used
- Check model size (smaller = faster)
- Increase batch size if memory allows
- Use `compute_type: "int8"` for CPU

### Performance Optimization

#### GPU Setup
```bash
# Check GPU memory
nvidia-smi

# Optimize for your GPU
# RTX 3080/4080: batch_size: 16, compute_type: "float16"
# RTX 3060: batch_size: 8, compute_type: "float16"  
# GTX 1660: batch_size: 4, compute_type: "int8"
```

#### CPU Optimization
```json
{
  "whisperx_settings": {
    "device": "cpu",
    "compute_type": "int8",
    "batch_size": 4
  }
}
```

## 🧪 Testing

### Integration Test
```bash
python test_whisperx_integration.py
```

### With Audio File
```bash
python test_whisperx_integration.py --audio sample.mp3
```

### Demo Script
```bash
python test_whisperx_demo.py
```

## 📈 Performance Comparison

| Method | Speed | Accuracy | Features |
|--------|-------|----------|----------|
| Standard Whisper | 1× | Good | Basic transcription |
| WhisperX | 70× | Better | + VAD, alignment, diarization |
| WhisperX + GPU | 70× | Better | + Fast processing |
| WhisperX + Diarization | 50× | Best | + Speaker identification |

## 🔄 Migration from Standard Whisper

### Automatic Fallback
The integration automatically falls back to standard Whisper if:
- WhisperX is not installed
- WhisperX is disabled in config
- WhisperX processing fails

### Database Schema
Enhanced database schema supports:
- `formatted_transcript` - transcript with speaker labels
- `transcription_metadata` - processing information
- `speaker_segments` - detailed speaker timeline

### Backward Compatibility
- Existing meetings continue to work
- New features available for new transcriptions
- No data migration required

## 🎯 Best Practices

### Audio Quality
- Use high-quality audio (16kHz+ sample rate)
- Minimize background noise
- Ensure clear speech separation
- Use proper microphone placement

### Configuration
- Start with default settings
- Adjust model size based on hardware
- Enable diarization for multi-speaker content
- Use VAD for noisy environments

### Processing
- Process shorter segments for faster results
- Use batch processing for multiple files
- Monitor GPU memory usage
- Save intermediate results

## 📚 API Reference

### Core Functions

#### `transcribe_audio(audio_path, use_whisperx=None)`
Main transcription function with automatic WhisperX/Whisper selection.

#### `transcribe_with_whisperx(audio_path, **kwargs)`
Direct WhisperX transcription with full control.

#### `get_transcript_text(result)`
Extract plain text from transcription result.

#### `get_formatted_transcript(result)`
Get formatted transcript with speaker labels.

#### `get_transcription_metadata(result)`
Extract metadata including speaker information.

#### `check_whisperx_status()`
Check WhisperX availability and configuration.

### CLI Commands

#### Basic Usage
```bash
whisperx_cli.py <audio_file> [options]
```

#### Options
- `-o, --output` - Output directory
- `--model` - Model size
- `--cli` - Use CLI method
- `--no-diarization` - Disable diarization
- `--no-vad` - Disable VAD
- `--hf-token` - Hugging Face token

## 🤝 Contributing

### Development Setup
1. Install development dependencies
2. Run integration tests
3. Test with sample audio files
4. Verify speaker diarization

### Adding Features
- Extend `WhisperXTranscriber` class
- Update configuration schema
- Add frontend components
- Include tests

## 📄 License

WhisperX integration follows the same license as SpeakInsights. WhisperX itself is licensed under BSD-4-Clause.

## 🔗 Resources

- [WhisperX GitHub](https://github.com/m-bain/whisperX)
- [Hugging Face Tokens](https://huggingface.co/settings/tokens)
- [PyAnnote Audio](https://github.com/pyannote/pyannote-audio)
- [Faster Whisper](https://github.com/guillaumekln/faster-whisper)

---

For support and questions, please refer to the main SpeakInsights documentation or create an issue in the repository.