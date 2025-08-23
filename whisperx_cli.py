#!/usr/bin/env python3
"""
WhisperX CLI Tool for SpeakInsights
Command-line interface for batch processing audio files with WhisperX
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any
import tempfile

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.whisperx_transcription import transcribe_with_whisperx, transcribe_with_whisperx_cli, WHISPERX_AVAILABLE
    from config import config
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this from the SpeakInsights root directory")
    sys.exit(1)

def process_single_file(
    audio_path: str,
    output_dir: str = None,
    use_cli: bool = False,
    enable_diarization: bool = True,
    enable_vad: bool = True,
    model_size: str = None,
    hf_token: str = None
) -> Dict[str, Any]:
    """Process a single audio file with WhisperX"""
    
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    print(f"\n{'='*60}")
    print(f"Processing: {audio_path}")
    print(f"{'='*60}")
    
    try:
        if use_cli:
            # Use CLI approach
            result = transcribe_with_whisperx_cli(
                audio_path=audio_path,
                output_dir=output_dir,
                model_size=model_size or config.WHISPERX_MODEL_SIZE,
                enable_diarization=enable_diarization,
                hf_token=hf_token or config.WHISPERX_HF_TOKEN
            )
        else:
            # Use Python API approach
            result = transcribe_with_whisperx(
                audio_path=audio_path,
                enable_vad=enable_vad,
                enable_diarization=enable_diarization
            )
        
        # Save results if output directory specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
            audio_name = Path(audio_path).stem
            
            # Save JSON result
            json_file = os.path.join(output_dir, f"{audio_name}_whisperx.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"✅ JSON result saved: {json_file}")
            
            # Save plain transcript
            txt_file = os.path.join(output_dir, f"{audio_name}_transcript.txt")
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(result['transcript'])
            print(f"✅ Transcript saved: {txt_file}")
            
            # Save formatted transcript with speakers (if available)
            if result.get('has_speakers', False):
                formatted_file = os.path.join(output_dir, f"{audio_name}_transcript_with_speakers.txt")
                with open(formatted_file, 'w', encoding='utf-8') as f:
                    f.write(result['formatted_transcript'])
                print(f"✅ Formatted transcript saved: {formatted_file}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error processing {audio_path}: {e}")
        raise

def process_batch(
    input_dir: str,
    output_dir: str = None,
    file_extensions: List[str] = None,
    **kwargs
) -> List[Dict[str, Any]]:
    """Process multiple audio files in a directory"""
    
    if file_extensions is None:
        file_extensions = ['.mp3', '.wav', '.m4a', '.mp4', '.mpeg', '.mpga', '.webm', '.flac']
    
    input_path = Path(input_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    
    # Find audio files
    audio_files = []
    for ext in file_extensions:
        audio_files.extend(input_path.glob(f"*{ext}"))
        audio_files.extend(input_path.glob(f"*{ext.upper()}"))
    
    if not audio_files:
        print(f"No audio files found in {input_dir}")
        return []
    
    print(f"Found {len(audio_files)} audio files to process")
    
    results = []
    for i, audio_file in enumerate(audio_files, 1):
        print(f"\n[{i}/{len(audio_files)}] Processing: {audio_file.name}")
        
        try:
            result = process_single_file(
                audio_path=str(audio_file),
                output_dir=output_dir,
                **kwargs
            )
            results.append({
                'file': str(audio_file),
                'success': True,
                'result': result
            })
        except Exception as e:
            print(f"❌ Failed to process {audio_file.name}: {e}")
            results.append({
                'file': str(audio_file),
                'success': False,
                'error': str(e)
            })
    
    return results

def print_results_summary(results: List[Dict[str, Any]]):
    """Print a summary of processing results"""
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\n{'='*60}")
    print("PROCESSING SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"📊 Total: {len(results)}")
    
    if successful:
        print(f"\n📈 STATISTICS FROM SUCCESSFUL TRANSCRIPTIONS:")
        total_speakers = 0
        total_segments = 0
        total_duration = 0
        
        for result in successful:
            if 'result' in result:
                info = result['result'].get('processing_info', {})
                total_speakers += info.get('total_speakers', 0)
                total_segments += info.get('total_segments', 0)
                total_duration += info.get('duration', 0)
        
        print(f"🎭 Total speakers detected: {total_speakers}")
        print(f"📝 Total segments: {total_segments}")
        print(f"⏱️ Total duration: {total_duration/60:.1f} minutes")
    
    if failed:
        print(f"\n❌ FAILED FILES:")
        for result in failed:
            print(f"  - {Path(result['file']).name}: {result['error']}")

def main():
    parser = argparse.ArgumentParser(
        description="WhisperX CLI Tool for SpeakInsights",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single file
  python whisperx_cli.py audio.mp3
  
  # Process with output directory
  python whisperx_cli.py audio.mp3 -o ./output
  
  # Batch process directory
  python whisperx_cli.py -d ./audio_files -o ./transcripts
  
  # Use CLI method with custom model
  python whisperx_cli.py audio.mp3 --cli --model large-v3
  
  # Disable diarization
  python whisperx_cli.py audio.mp3 --no-diarization
        """
    )
    
    # Input options
    parser.add_argument('input', nargs='?', help='Input audio file or directory')
    parser.add_argument('-d', '--directory', help='Process all audio files in directory')
    
    # Output options
    parser.add_argument('-o', '--output', help='Output directory for results')
    
    # Processing options
    parser.add_argument('--model', default=None, help=f'WhisperX model size (default: {config.WHISPERX_MODEL_SIZE})')
    parser.add_argument('--cli', action='store_true', help='Use CLI method instead of Python API')
    parser.add_argument('--no-diarization', action='store_true', help='Disable speaker diarization')
    parser.add_argument('--no-vad', action='store_true', help='Disable VAD preprocessing')
    parser.add_argument('--hf-token', help='Hugging Face token for diarization')
    
    # Other options
    parser.add_argument('--extensions', nargs='+', default=['.mp3', '.wav', '.m4a', '.mp4'], 
                       help='File extensions to process (for directory mode)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Check WhisperX availability
    if not WHISPERX_AVAILABLE:
        print("❌ WhisperX not available. Install with: pip install whisperx")
        sys.exit(1)
    
    # Determine input
    input_path = args.input or args.directory
    if not input_path:
        parser.print_help()
        sys.exit(1)
    
    # Check if input exists
    if not os.path.exists(input_path):
        print(f"❌ Input not found: {input_path}")
        sys.exit(1)
    
    # Prepare processing options
    process_options = {
        'use_cli': args.cli,
        'enable_diarization': not args.no_diarization,
        'enable_vad': not args.no_vad,
        'model_size': args.model,
        'hf_token': args.hf_token
    }
    
    try:
        if os.path.isfile(input_path):
            # Single file processing
            print(f"🎙️ Processing single file: {input_path}")
            
            result = process_single_file(
                audio_path=input_path,
                output_dir=args.output,
                **process_options
            )
            
            # Print results
            print(f"\n{'='*60}")
            print("TRANSCRIPTION RESULTS")
            print(f"{'='*60}")
            
            print(f"Language: {result.get('language', 'unknown')}")
            print(f"Speakers: {len(result.get('speakers', []))}")
            print(f"Segments: {result.get('processing_info', {}).get('total_segments', 0)}")
            print(f"Duration: {result.get('processing_info', {}).get('duration', 0)/60:.1f} minutes")
            
            if result.get('has_speakers', False):
                print(f"\nSpeakers detected: {', '.join(result['speakers'])}")
                print("\nFormatted transcript with speakers:")
                print(result['formatted_transcript'][:500] + "..." if len(result['formatted_transcript']) > 500 else result['formatted_transcript'])
            else:
                print("\nTranscript:")
                print(result['transcript'][:500] + "..." if len(result['transcript']) > 500 else result['transcript'])
        
        elif os.path.isdir(input_path):
            # Batch processing
            print(f"🎙️ Processing directory: {input_path}")
            
            results = process_batch(
                input_dir=input_path,
                output_dir=args.output,
                file_extensions=args.extensions,
                **process_options
            )
            
            print_results_summary(results)
        
        else:
            print(f"❌ Invalid input: {input_path}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⚠️ Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()