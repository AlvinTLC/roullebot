#!/usr/bin/env python3
"""
Test script to debug calibration issues on macOS
"""
import sys
import os

# Add the root directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.calibrator import Calibrator

def test_calibration():
    """Test the calibration directly"""
    print("🧪 Testing calibration directly...")
    
    calibrator = Calibrator()
    
    # Check if calibration exists
    if not calibrator.calibration_data.get('winner_region'):
        print("❌ No calibration found")
        return
    
    print("✅ Calibration found")
    print(f"Winner region: {calibrator.calibration_data['winner_region']}")
    
    # Run the simple test
    print("\n🚀 Running simple test...")
    calibrator.test_calibration_simple()

if __name__ == "__main__":
    test_calibration()