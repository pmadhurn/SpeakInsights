"""
WhisperX Integration for SpeakInsights
Provides enhanced transcription with speaker diarization, VAD, and word-level timestamps
"""

import os
import sys
import json
import torch
import warnings
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
import tempfile
import subprocess

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

try:
    import whisperx
    WHISPERX_AVAILABLE = True
    WHISPERX_ERROR = None
except ImportError as e:
    WHISPERX_AVAILABLE = False
    WHISPERX_ERROR = str(e)
    print(f"[WARNING] WhisperX not available: {e}")
    print("[INFO] WhisperX requires NumPy >= 2.0, but Streamlit requires NumPy < 2.0")
    print("[INFO] Consider using a separate environment for WhisperX CLI processing")

from config import config

class WhisperXTranscriber:
    """Enhanced transcription with WhisperX"""
    
    def __init__(self):
        self.model = None
        self.align_model = None
        self.align_metadata = None
        self.diarize_model = None
        self.device = self._get_device()
        self.compute_type = self._get_compute_type()
        
    def _get_device(self) -> str:
        """Determine the best device for processing"""
        whisperx_device = getattr(config, 'WHISPERX_DEVICE', 'auto')
        
        if whisperx_device == 'auto':
            if torch.cuda.is_available():
                device = "cuda"
                print(f"[WhisperX] Using GPU: {torch.cuda.get_device_name(0)}")
            else:
                device = "cpu"
                print("[WhisperX] Using CPU")
        else:
            device = whisperx_device
            print(f"[WhisperX] Using configured device: {device}")
            
        return device
    
    def _get_compute_type(self) -> str:
        """Determine compute type based on device"""
        compute_type = getattr(config, 'WHISPERX_COMPUTE_TYPE', 'float16')
        
        if self.device == "cpu":
            compute_type = "int8"  # CPU works better with int8
        elif not torch.cuda.is_available():
            compute_type = "int8"
            
        return compute_type
    
    def load_model(self, model_size: str = None) -> bool:
        """Load WhisperX transcription model"""
        if not WHISPERX_AVAILABLE:
            raise ImportError("WhisperX not available. Please install with: pip install whisperx")
            
        try:
            model_size = model_size or getattr(config, 'WHISPERX_MODEL_SIZE', 'large-v2')
            batch_size = getattr(config, 'WHISPERX_BATCH_SIZE', 16)
            
            print(f"[WhisperX] Loading model '{model_size}' on {self.device} with {self.compute_type}...")
            
            self.model = whisperx.load_model(
                model_size, 
                device=self.device, 
                compute_type=self.compute_type,
                language=getattr(config, 'WHISPERX_LANGUAGE', 'en')
            )
            
            print(f"[WhisperX] Model loaded successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to load WhisperX model: {e}")
            return False
    
    def load_align_model(self, language: str = "en") -> bool:
        """Load alignment model for word-level timestamps"""
        try:
            print(f"[WhisperX] Loading alignment model for language: {language}")
            
            self.align_model, self.align_metadata = whisperx.load_align_model(
                language_code=language, 
                device=self.device
            )
            
            print(f"[WhisperX] Alignment model loaded successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to load alignment model: {e}")
            return False
    
    def load_diarization_model(self, hf_token: str = None) -> bool:
        """Load speaker diarization model"""
        try:
            hf_token = hf_token or getattr(config, 'WHISPERX_HF_TOKEN', None)
            
            if not hf_token:
                print("[WARNING] No Hugging Face token provided. Speaker diarization will be disabled.")
                print("To enable diarization, get a token from https://huggingface.co/settings/tokens")
                return False
            
            print("[WhisperX] Loading diarization model...")
            
            self.diarize_model = whisperx.DiarizationPipeline(
                use_auth_token=hf_token, 
                device=self.device
            )
            
            print("[WhisperX] Diarization model loaded successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to load diarization model: {e}")
            print("Note: Diarization requires a Hugging Face token and pyannote.audio")
            return False
    
    def transcribe_with_whisperx(
        self, 
        audio_path: str,
        enable_vad: bool = True,
        enable_diarization: bool = True,
        min_speakers: Optional[int] = None,
        max_speakers: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio with WhisperX including VAD, alignment, and diarization
        
        Returns:
            Dict containing transcript, segments with timestamps, and speaker labels
        """
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        if not self.model:
            if not self.load_model():
                raise RuntimeError("Failed to load WhisperX model")
        
        try:
            print(f"[WhisperX] Processing audio: {audio_path}")
            
            # Step 1: Load and preprocess audio
            print("[WhisperX] Loading audio...")
            audio = whisperx.load_audio(audio_path)
            
            # Step 2: Transcribe with VAD
            print("[WhisperX] Transcribing with VAD preprocessing...")
            batch_size = getattr(config, 'WHISPERX_BATCH_SIZE', 16)
            
            if enable_vad:
                vad_onset = getattr(config, 'WHISPERX_VAD_ONSET', 0.500)
                vad_offset = getattr(config, 'WHISPERX_VAD_OFFSET', 0.363)
                
                result = self.model.transcribe(
                    audio, 
                    batch_size=batch_size,
                    vad_filter=True,
                    vad_parameters={"onset": vad_onset, "offset": vad_offset}
                )
            else:
                result = self.model.transcribe(audio, batch_size=batch_size)
            
            print(f"[WhisperX] Initial transcription completed ({len(result['segments'])} segments)")
            
            # Step 3: Align for word-level timestamps
            language = result.get('language', 'en')
            
            if not self.align_model or self.align_metadata is None:
                if not self.load_align_model(language):
                    print("[WARNING] Alignment model not available, skipping word-level timestamps")
                    aligned_result = result
                else:
                    print("[WhisperX] Aligning for word-level timestamps...")
                    aligned_result = whisperx.align(
                        result["segments"], 
                        self.align_model, 
                        self.align_metadata, 
                        audio, 
                        self.device, 
                        return_char_alignments=False,
                        interpolate_method=getattr(config, 'WHISPERX_INTERPOLATE_METHOD', 'nearest')
                    )
            else:
                print("[WhisperX] Aligning for word-level timestamps...")
                aligned_result = whisperx.align(
                    result["segments"], 
                    self.align_model, 
                    self.align_metadata, 
                    audio, 
                    self.device, 
                    return_char_alignments=False,
                    interpolate_method=getattr(config, 'WHISPERX_INTERPOLATE_METHOD', 'nearest')
                )
            
            # Step 4: Speaker diarization (if enabled and available)
            final_result = aligned_result
            
            if enable_diarization and getattr(config, 'WHISPERX_ENABLE_DIARIZATION', True):
                if not self.diarize_model:
                    hf_token = getattr(config, 'WHISPERX_HF_TOKEN', None)
                    if not self.load_diarization_model(hf_token):
                        print("[WARNING] Diarization not available, proceeding without speaker labels")
                    else:
                        print("[WhisperX] Performing speaker diarization...")
                        
                        diarize_segments = self.diarize_model(
                            audio,
                            min_speakers=min_speakers,
                            max_speakers=max_speakers
                        )
                        
                        final_result = whisperx.assign_word_speakers(diarize_segments, aligned_result)
                        print(f"[WhisperX] Diarization completed")
                else:
                    print("[WhisperX] Performing speaker diarization...")
                    
                    diarize_segments = self.diarize_model(
                        audio,
                        min_speakers=min_speakers,
                        max_speakers=max_speakers
                    )
                    
                    final_result = whisperx.assign_word_speakers(diarize_segments, aligned_result)
                    print(f"[WhisperX] Diarization completed")
            
            # Process results
            processed_result = self._process_whisperx_result(final_result)
            
            print(f"[WhisperX] Processing completed successfully")
            return processed_result
            
        except Exception as e:
            print(f"[ERROR] WhisperX transcription failed: {e}")
            raise
    
    def _process_whisperx_result(self, result: Dict) -> Dict[str, Any]:
        """Process WhisperX result into SpeakInsights format"""
        
        segments = result.get("segments", [])
        
        # Extract full transcript
        full_transcript = ""
        speaker_segments = []
        word_level_data = []
        
        current_speaker = None
        current_text = ""
        current_start = None
        
        for segment in segments:
            segment_text = segment.get("text", "").strip()
            segment_start = segment.get("start", 0)
            segment_end = segment.get("end", 0)
            
            # Handle speaker information
            words = segment.get("words", [])
            
            if words:
                # Process word-level data
                for word_info in words:
                    word_data = {
                        "word": word_info.get("word", ""),
                        "start": word_info.get("start", 0),
                        "end": word_info.get("end", 0),
                        "score": word_info.get("score", 0),
                        "speaker": word_info.get("speaker", "SPEAKER_00")
                    }
                    word_level_data.append(word_data)
                    
                    # Track speaker changes for segment grouping
                    speaker = word_info.get("speaker", "SPEAKER_00")
                    
                    if current_speaker != speaker:
                        # Save previous speaker segment
                        if current_speaker is not None and current_text.strip():
                            speaker_segments.append({
                                "speaker": current_speaker,
                                "text": current_text.strip(),
                                "start": current_start,
                                "end": segment_end
                            })
                        
                        # Start new speaker segment
                        current_speaker = speaker
                        current_text = word_info.get("word", "")
                        current_start = word_info.get("start", segment_start)
                    else:
                        current_text += word_info.get("word", "")
            else:
                # Fallback for segments without word-level data
                speaker = "SPEAKER_00"  # Default speaker
                
                if current_speaker != speaker:
                    if current_speaker is not None and current_text.strip():
                        speaker_segments.append({
                            "speaker": current_speaker,
                            "text": current_text.strip(),
                            "start": current_start,
                            "end": segment_end
                        })
                    
                    current_speaker = speaker
                    current_text = segment_text
                    current_start = segment_start
                else:
                    current_text += " " + segment_text
            
            full_transcript += segment_text + " "
        
        # Add final speaker segment
        if current_speaker is not None and current_text.strip():
            speaker_segments.append({
                "speaker": current_speaker,
                "text": current_text.strip(),
                "start": current_start,
                "end": segments[-1].get("end", 0) if segments else 0
            })
        
        # Create formatted transcript with speakers
        formatted_transcript = ""
        for seg in speaker_segments:
            formatted_transcript += f"[{seg['speaker']}]: {seg['text']}\n\n"
        
        # Get unique speakers
        speakers = list(set(word.get("speaker", "SPEAKER_00") for word in word_level_data))
        
        return {
            "transcript": full_transcript.strip(),
            "formatted_transcript": formatted_transcript.strip(),
            "segments": segments,
            "speaker_segments": speaker_segments,
            "word_level_data": word_level_data,
            "speakers": sorted(speakers),
            "language": result.get("language", "en"),
            "has_speakers": len(speakers) > 1,
            "processing_info": {
                "total_segments": len(segments),
                "total_words": len(word_level_data),
                "total_speakers": len(speakers),
                "duration": segments[-1].get("end", 0) if segments else 0
            }
        }

# Global transcriber instance
_whisperx_transcriber = None

def get_whisperx_transcriber() -> WhisperXTranscriber:
    """Get global WhisperX transcriber instance"""
    global _whisperx_transcriber
    if _whisperx_transcriber is None:
        _whisperx_transcriber = WhisperXTranscriber()
    return _whisperx_transcriber

def transcribe_with_whisperx(
    audio_path: str,
    enable_vad: bool = None,
    enable_diarization: bool = None,
    min_speakers: Optional[int] = None,
    max_speakers: Optional[int] = None
) -> Dict[str, Any]:
    """
    Main function to transcribe audio with WhisperX
    
    Args:
        audio_path: Path to audio file
        enable_vad: Enable VAD preprocessing (default from config)
        enable_diarization: Enable speaker diarization (default from config)
        min_speakers: Minimum number of speakers
        max_speakers: Maximum number of speakers
    
    Returns:
        Dict with transcription results including speaker information
    """
    
    if not WHISPERX_AVAILABLE:
        raise ImportError("WhisperX not available. Please install with: pip install whisperx")
    
    # Use config defaults if not specified
    if enable_vad is None:
        enable_vad = getattr(config, 'WHISPERX_ENABLE_VAD', True)
    
    if enable_diarization is None:
        enable_diarization = getattr(config, 'WHISPERX_ENABLE_DIARIZATION', True)
    
    if min_speakers is None:
        min_speakers = getattr(config, 'WHISPERX_MIN_SPEAKERS', None)
    
    if max_speakers is None:
        max_speakers = getattr(config, 'WHISPERX_MAX_SPEAKERS', None)
    
    transcriber = get_whisperx_transcriber()
    
    return transcriber.transcribe_with_whisperx(
        audio_path=audio_path,
        enable_vad=enable_vad,
        enable_diarization=enable_diarization,
        min_speakers=min_speakers,
        max_speakers=max_speakers
    )

def transcribe_with_whisperx_cli(
    audio_path: str,
    output_dir: str = None,
    model_size: str = "large-v2",
    enable_diarization: bool = True,
    hf_token: str = None
) -> Dict[str, Any]:
    """
    Alternative CLI-based approach using WhisperX command line
    Useful for batch processing or when Python integration has issues
    """
    
    if not WHISPERX_AVAILABLE:
        raise ImportError("WhisperX not available. Please install with: pip install whisperx")
    
    try:
        # Create temporary output directory if not specified
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="whisperx_")
        else:
            os.makedirs(output_dir, exist_ok=True)
        
        # Build WhisperX CLI command
        cmd = [
            "whisperx",
            audio_path,
            "--model", model_size,
            "--output_dir", output_dir,
            "--output_format", "json",
            "--language", "en"
        ]
        
        # Add diarization if enabled and token provided
        if enable_diarization and hf_token:
            cmd.extend(["--diarize", "--hf_token", hf_token])
        
        print(f"[WhisperX CLI] Running: {' '.join(cmd)}")
        
        # Execute WhisperX CLI
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        
        if result.returncode != 0:
            raise RuntimeError(f"WhisperX CLI failed: {result.stderr}")
        
        # Load results from JSON output
        audio_name = Path(audio_path).stem
        json_file = os.path.join(output_dir, f"{audio_name}.json")
        
        if not os.path.exists(json_file):
            raise FileNotFoundError(f"WhisperX output not found: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            whisperx_result = json.load(f)
        
        # Process the CLI result
        processed_result = _process_cli_result(whisperx_result)
        
        print(f"[WhisperX CLI] Processing completed successfully")
        return processed_result
        
    except Exception as e:
        print(f"[ERROR] WhisperX CLI transcription failed: {e}")
        raise

def _process_cli_result(cli_result: Dict) -> Dict[str, Any]:
    """Process CLI result into SpeakInsights format"""
    
    segments = cli_result.get("segments", [])
    
    # Extract full transcript and speaker information
    full_transcript = ""
    formatted_transcript = ""
    speakers = set()
    
    for segment in segments:
        text = segment.get("text", "").strip()
        speaker = segment.get("speaker", "SPEAKER_00")
        
        full_transcript += text + " "
        formatted_transcript += f"[{speaker}]: {text}\n\n"
        speakers.add(speaker)
    
    return {
        "transcript": full_transcript.strip(),
        "formatted_transcript": formatted_transcript.strip(),
        "segments": segments,
        "speakers": sorted(list(speakers)),
        "language": cli_result.get("language", "en"),
        "has_speakers": len(speakers) > 1,
        "processing_info": {
            "total_segments": len(segments),
            "total_speakers": len(speakers),
            "method": "cli"
        }
    }

# Test function
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python whisperx_transcription.py <audio_file>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    
    if not os.path.exists(audio_file):
        print(f"Error: Audio file not found: {audio_file}")
        sys.exit(1)
    
    try:
        print("Testing WhisperX transcription...")
        result = transcribe_with_whisperx(audio_file)
        
        print("\n" + "="*50)
        print("TRANSCRIPTION RESULTS")
        print("="*50)
        
        print(f"\nLanguage: {result['language']}")
        print(f"Speakers detected: {len(result['speakers'])}")
        print(f"Total segments: {result['processing_info']['total_segments']}")
        
        if result['has_speakers']:
            print(f"\nSpeakers: {', '.join(result['speakers'])}")
            print("\nFormatted transcript with speakers:")
            print(result['formatted_transcript'])
        else:
            print("\nTranscript:")
            print(result['transcript'])
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)