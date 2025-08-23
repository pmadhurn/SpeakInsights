#!/usr/bin/env python3
"""
WhisperX Integration Test for SpeakInsights
Comprehensive testing of WhisperX functionality
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔄 Testing imports...")
    
    try:
        from app.whisperx_transcription import (
            WhisperXTranscriber, 
            transcribe_with_whisperx, 
            WHISPERX_AVAILABLE
        )
        from app.transcription import (
            transcribe_audio, 
            get_transcript_text, 
            get_formatted_transcript,
            get_transcription_metadata,
            check_whisperx_status
        )
        from config import config
        
        print("✅ All imports successful")
        return True, {
            'whisperx_available': WHISPERX_AVAILABLE,
            'config_loaded': True
        }
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False, {'error': str(e)}

def test_configuration():
    """Test WhisperX configuration"""
    print("🔄 Testing configuration...")
    
    try:
        from config import config
        
        # Check WhisperX settings
        settings = {
            'enabled': getattr(config, 'WHISPERX_ENABLED', False),
            'model_size': getattr(config, 'WHISPERX_MODEL_SIZE', 'unknown'),
            'device': getattr(config, 'WHISPERX_DEVICE', 'unknown'),
            'vad_enabled': getattr(config, 'WHISPERX_ENABLE_VAD', False),
            'diarization_enabled': getattr(config, 'WHISPERX_ENABLE_DIARIZATION', False),
            'hf_token_configured': bool(getattr(config, 'WHISPERX_HF_TOKEN', None))
        }
        
        print("✅ Configuration loaded")
        for key, value in settings.items():
            print(f"  - {key}: {value}")
        
        return True, settings
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False, {'error': str(e)}

def test_whisperx_status():
    """Test WhisperX status check function"""
    print("🔄 Testing WhisperX status check...")
    
    try:
        from app.transcription import check_whisperx_status
        
        status = check_whisperx_status()
        
        print("✅ Status check successful")
        for key, value in status.items():
            print(f"  - {key}: {value}")
        
        return True, status
        
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return False, {'error': str(e)}

def test_transcriber_initialization():
    """Test WhisperX transcriber initialization"""
    print("🔄 Testing transcriber initialization...")
    
    try:
        from app.whisperx_transcription import WhisperXTranscriber, WHISPERX_AVAILABLE
        
        if not WHISPERX_AVAILABLE:
            print("⚠️ WhisperX not available - skipping initialization test")
            return True, {'skipped': True, 'reason': 'WhisperX not available'}
        
        transcriber = WhisperXTranscriber()
        
        print("✅ Transcriber initialized")
        print(f"  - Device: {transcriber.device}")
        print(f"  - Compute type: {transcriber.compute_type}")
        
        return True, {
            'device': transcriber.device,
            'compute_type': transcriber.compute_type
        }
        
    except Exception as e:
        print(f"❌ Transcriber initialization failed: {e}")
        return False, {'error': str(e)}

def test_model_loading():
    """Test WhisperX model loading"""
    print("🔄 Testing model loading...")
    
    try:
        from app.whisperx_transcription import WhisperXTranscriber, WHISPERX_AVAILABLE
        
        if not WHISPERX_AVAILABLE:
            print("⚠️ WhisperX not available - skipping model loading test")
            return True, {'skipped': True, 'reason': 'WhisperX not available'}
        
        transcriber = WhisperXTranscriber()
        
        # Try to load a small model for testing
        success = transcriber.load_model("tiny")
        
        if success:
            print("✅ Model loaded successfully")
            return True, {'model_loaded': True}
        else:
            print("❌ Model loading failed")
            return False, {'model_loaded': False}
        
    except Exception as e:
        print(f"❌ Model loading test failed: {e}")
        return False, {'error': str(e)}

def create_test_audio():
    """Create a simple test audio file using text-to-speech"""
    print("🔄 Creating test audio...")
    
    try:
        # Try to create a simple audio file for testing
        # This is a basic implementation - in practice you'd use a real audio file
        
        test_text = "Hello, this is a test of WhisperX integration. This is speaker one speaking."
        
        # For now, we'll just return a placeholder
        # In a real implementation, you'd generate actual audio
        print("⚠️ Test audio creation not implemented - use a real audio file for testing")
        
        return False, {'reason': 'Test audio creation not implemented'}
        
    except Exception as e:
        print(f"❌ Test audio creation failed: {e}")
        return False, {'error': str(e)}

def test_with_sample_audio(audio_path: str):
    """Test transcription with a sample audio file"""
    print(f"🔄 Testing transcription with: {audio_path}")
    
    if not os.path.exists(audio_path):
        print(f"❌ Audio file not found: {audio_path}")
        return False, {'error': 'File not found'}
    
    try:
        from app.transcription import transcribe_audio, get_transcript_text, get_transcription_metadata
        
        # Test enhanced transcription
        result = transcribe_audio(audio_path, use_whisperx=True)
        
        if isinstance(result, str) and result.startswith("Error"):
            print(f"❌ Transcription failed: {result}")
            return False, {'error': result}
        
        # Extract information
        transcript = get_transcript_text(result)
        metadata = get_transcription_metadata(result)
        
        print("✅ Transcription successful")
        print(f"  - Method: {metadata.get('method', 'unknown')}")
        print(f"  - Has speakers: {metadata.get('has_speakers', False)}")
        print(f"  - Speakers: {len(metadata.get('speakers', []))}")
        print(f"  - Transcript length: {len(transcript)} characters")
        
        if len(transcript) > 100:
            print(f"  - Preview: {transcript[:100]}...")
        else:
            print(f"  - Transcript: {transcript}")
        
        return True, {
            'transcript_length': len(transcript),
            'metadata': metadata,
            'has_speakers': metadata.get('has_speakers', False)
        }
        
    except Exception as e:
        print(f"❌ Transcription test failed: {e}")
        return False, {'error': str(e)}

def run_all_tests(audio_file: str = None):
    """Run all WhisperX integration tests"""
    
    print("🎙️ WhisperX Integration Test Suite")
    print("="*60)
    
    results = {}
    
    # Test 1: Imports
    success, data = test_imports()
    results['imports'] = {'success': success, 'data': data}
    
    if not success:
        print("❌ Critical failure - cannot continue tests")
        return results
    
    # Test 2: Configuration
    success, data = test_configuration()
    results['configuration'] = {'success': success, 'data': data}
    
    # Test 3: Status check
    success, data = test_whisperx_status()
    results['status_check'] = {'success': success, 'data': data}
    
    # Test 4: Transcriber initialization
    success, data = test_transcriber_initialization()
    results['transcriber_init'] = {'success': success, 'data': data}
    
    # Test 5: Model loading (if WhisperX available)
    if data.get('skipped') != True:
        success, data = test_model_loading()
        results['model_loading'] = {'success': success, 'data': data}
    
    # Test 6: Audio transcription (if audio file provided)
    if audio_file:
        success, data = test_with_sample_audio(audio_file)
        results['audio_transcription'] = {'success': success, 'data': data}
    
    return results

def print_test_summary(results: dict):
    """Print a summary of test results"""
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r['success'])
    
    print(f"✅ Passed: {passed_tests}/{total_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"  {status} - {test_name}")
        
        if not result['success'] and 'error' in result['data']:
            print(f"    Error: {result['data']['error']}")
        elif result['data'].get('skipped'):
            print(f"    Skipped: {result['data']['reason']}")
    
    # Overall assessment
    print(f"\n{'='*60}")
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED - WhisperX integration is working!")
    elif passed_tests >= total_tests * 0.8:
        print("⚠️ MOSTLY WORKING - Some issues detected but core functionality available")
    else:
        print("❌ SIGNIFICANT ISSUES - WhisperX integration needs attention")
    
    # Recommendations
    print(f"\n📋 RECOMMENDATIONS:")
    
    if not results.get('imports', {}).get('success'):
        print("  - Install WhisperX: pip install whisperx")
    
    if results.get('configuration', {}).get('success'):
        config_data = results['configuration']['data']
        if not config_data.get('enabled'):
            print("  - Enable WhisperX in config.json")
        if not config_data.get('hf_token_configured'):
            print("  - Add Hugging Face token for speaker diarization")
    
    if not results.get('model_loading', {}).get('success', True):
        print("  - Check GPU/CUDA installation for better performance")
        print("  - Try smaller model size if memory issues")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Test WhisperX integration")
    parser.add_argument('--audio', help='Path to audio file for transcription test')
    parser.add_argument('--save-results', help='Save test results to JSON file')
    
    args = parser.parse_args()
    
    # Run tests
    results = run_all_tests(args.audio)
    
    # Print summary
    print_test_summary(results)
    
    # Save results if requested
    if args.save_results:
        try:
            with open(args.save_results, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Results saved to: {args.save_results}")
        except Exception as e:
            print(f"\n❌ Failed to save results: {e}")

if __name__ == "__main__":
    main()