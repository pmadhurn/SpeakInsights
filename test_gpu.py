#!/usr/bin/env python3
"""
GPU Detection Test for SpeakInsights
"""

import torch
import sys

def test_gpu():
    print("=" * 60)
    print("🔍 GPU Detection Test")
    print("=" * 60)
    
    # Check PyTorch CUDA availability
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"Number of GPUs: {torch.cuda.device_count()}")
        
        for i in range(torch.cuda.device_count()):
            gpu_name = torch.cuda.get_device_name(i)
            gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
            print(f"GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")
        
        # Test GPU tensor operations
        try:
            x = torch.randn(1000, 1000).cuda()
            y = torch.randn(1000, 1000).cuda()
            z = torch.matmul(x, y)
            print("✅ GPU tensor operations working!")
        except Exception as e:
            print(f"❌ GPU tensor test failed: {e}")
    else:
        print("❌ No GPU detected - will use CPU only")
        print("This will make AI processing much slower.")
        
        # Check if CUDA drivers are installed
        try:
            import subprocess
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            if result.returncode == 0:
                print("💡 NVIDIA drivers detected but PyTorch can't access GPU")
                print("   Try reinstalling PyTorch with CUDA support:")
                print("   pip uninstall torch torchvision torchaudio")
                print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
            else:
                print("💡 No NVIDIA drivers detected")
        except:
            print("💡 nvidia-smi not found - no NVIDIA drivers installed")
    
    print("=" * 60)

if __name__ == "__main__":
    test_gpu()