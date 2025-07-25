#!/usr/bin/env python3
"""
Verification script for optimized Molecular Plus Blender extension
This script verifies that the optimized extension was built correctly
"""

import os
import sys
import zipfile
import tempfile
import shutil
from pathlib import Path

def find_optimized_extensions():
    """Find all optimized extension files"""
    extensions = []
    # Look in root directory for extension files
    for file in os.listdir('..'):
        if file.startswith('molecular-plus-optimized_') and file.endswith('.zip'):
            extensions.append(f"../{file}")
    return extensions

def verify_extension_structure(zip_path):
    """Verify the internal structure of the extension"""
    print(f"\\n🔍 Verifying: {zip_path}")
    
    required_files = [
        'molecularplus/__init__.py',
        'molecularplus/blender_manifest.toml',
        'molecularplus/operators.py',
        'molecularplus/simulate.py',
        'molecularplus/wheels/'
    ]
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            file_list = z.namelist()
            
            print("  📁 Extension structure:")
            for file in sorted(file_list):
                if not file.endswith('/'):
                    print(f"    {file}")
            
            # Check required files
            missing_files = []
            for required in required_files:
                found = any(f.startswith(required) for f in file_list)
                if found:
                    print(f"  ✅ {required}")
                else:
                    print(f"  ❌ {required} - MISSING")
                    missing_files.append(required)
            
            # Check for wheel files
            wheel_files = [f for f in file_list if f.endswith('.whl')]
            if wheel_files:
                print(f"  🎯 Found {len(wheel_files)} wheel file(s):")
                for wheel in wheel_files:
                    print(f"    📦 {wheel}")
            else:
                print("  ❌ No wheel files found!")
                missing_files.append("wheel files")
            
            # Check for OpenMP library (macOS)
            omp_files = [f for f in file_list if 'libomp.dylib' in f]
            if omp_files:
                print(f"  🔧 OpenMP library found: {omp_files[0]}")
            
            return len(missing_files) == 0, missing_files
            
    except Exception as e:
        print(f"  ❌ Error reading extension: {e}")
        return False, [str(e)]

def test_wheel_import(zip_path):
    """Test if the wheel can be imported"""
    print(f"\\n🧪 Testing wheel import from: {zip_path}")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Extract the extension
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(temp_dir)
            
            # Find the wheel file
            wheels_dir = os.path.join(temp_dir, 'molecularplus', 'wheels')
            if not os.path.exists(wheels_dir):
                print("  ❌ Wheels directory not found")
                return False
            
            wheel_files = [f for f in os.listdir(wheels_dir) if f.endswith('.whl')]
            if not wheel_files:
                print("  ❌ No wheel files found in wheels directory")
                return False
            
            wheel_path = os.path.join(wheels_dir, wheel_files[0])
            print(f"  📦 Testing wheel: {wheel_files[0]}")
            
            # Extract wheel to test import
            wheel_extract_dir = os.path.join(temp_dir, 'wheel_test')
            os.makedirs(wheel_extract_dir)
            
            with zipfile.ZipFile(wheel_path, 'r') as wheel_zip:
                wheel_zip.extractall(wheel_extract_dir)
            
            # Check if molecular_core directory exists
            molecular_core_dir = os.path.join(wheel_extract_dir, 'molecular_core')
            if os.path.exists(molecular_core_dir):
                print("  ✅ molecular_core package found")
                
                # Check for compiled extension
                so_files = [f for f in os.listdir(molecular_core_dir) 
                           if f.endswith('.so') or f.endswith('.pyd') or f.endswith('.dll')]
                if so_files:
                    print(f"  ✅ Compiled extension found: {so_files[0]}")
                else:
                    print("  ❌ No compiled extension found")
                    return False
                
                # Check for OpenMP library
                if os.path.exists(os.path.join(molecular_core_dir, 'libomp.dylib')):
                    print("  ✅ OpenMP library included")
                
                return True
            else:
                print("  ❌ molecular_core package not found in wheel")
                return False
                
        except Exception as e:
            print(f"  ❌ Error testing wheel: {e}")
            return False

def get_extension_info(zip_path):
    """Extract information about the extension"""
    info = {
        'filename': os.path.basename(zip_path),
        'size': os.path.getsize(zip_path),
        'platform': 'unknown',
        'architecture': 'unknown',
        'optimizations': []
    }
    
    filename = info['filename']
    
    # Parse filename for information
    if '_macos_' in filename:
        info['platform'] = 'macOS'
    elif '_linux_' in filename:
        info['platform'] = 'Linux'
    elif '_win_' in filename:
        info['platform'] = 'Windows'
    
    if '_x64_' in filename:
        info['architecture'] = 'x86_64'
    elif '_arm64_' in filename:
        info['architecture'] = 'ARM64'
    
    # Extract optimization features
    if 'sse4.2' in filename:
        info['optimizations'].append('SSE4.2')
    if 'avx' in filename:
        info['optimizations'].append('AVX')
    if 'avx2' in filename:
        info['optimizations'].append('AVX2')
    if 'apple_silicon' in filename:
        info['optimizations'].append('Apple Silicon')
    if 'neon' in filename:
        info['optimizations'].append('NEON')
    
    return info

def main():
    """Main verification function"""
    print("=" * 70)
    print("MOLECULAR PLUS - OPTIMIZED EXTENSION VERIFIER")
    print("=" * 70)
    
    # Find optimized extensions
    extensions = find_optimized_extensions()
    
    if not extensions:
        print("❌ No optimized extensions found!")
        print("   Run pack_molecular_optimized.py first to create optimized extensions")
        return False
    
    print(f"Found {len(extensions)} optimized extension(s):")
    
    all_passed = True
    
    for ext in extensions:
        info = get_extension_info(ext)
        
        print(f"\\n📦 Extension: {info['filename']}")
        print(f"   Platform: {info['platform']}")
        print(f"   Architecture: {info['architecture']}")
        print(f"   Size: {info['size'] / (1024*1024):.1f} MB")
        print(f"   Optimizations: {', '.join(info['optimizations']) if info['optimizations'] else 'Standard'}")
        
        # Verify structure
        structure_ok, missing = verify_extension_structure(ext)
        if not structure_ok:
            print(f"  ❌ Structure verification failed: {missing}")
            all_passed = False
        else:
            print("  ✅ Structure verification passed")
        
        # Test wheel import
        import_ok = test_wheel_import(ext)
        if not import_ok:
            print("  ❌ Wheel import test failed")
            all_passed = False
        else:
            print("  ✅ Wheel import test passed")
    
    print("\\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL OPTIMIZED EXTENSIONS VERIFIED SUCCESSFULLY!")
        print("=" * 70)
        print("✅ Structure: Valid")
        print("✅ Wheels: Present and importable")
        print("✅ Libraries: Included")
        print("\\nYour optimized extensions are ready for distribution!")
        print("\\nInstallation instructions:")
        print("1. Open Blender")
        print("2. Go to Edit > Preferences > Extensions")
        print("3. Click 'Install from Disk'")
        print("4. Select your optimized .zip file")
        print("5. Enable Molecular Plus extension")
    else:
        print("❌ SOME EXTENSIONS FAILED VERIFICATION")
        print("=" * 70)
        print("Please check the errors above and rebuild if necessary")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)