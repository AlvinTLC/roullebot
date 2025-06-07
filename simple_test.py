#!/usr/bin/env python3
"""
Simple test to demonstrate the calibration issue
"""
import sys
import os
import json

# Add the root directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vision.screen_capture import capture_screen
from vision.window_region import obtener_region_chrome
import cv2
import numpy as np

def simple_test():
    """Simple test to capture and save what the current calibration would see"""
    
    # Load calibration
    config_path = "/Users/alvinnunez/Library/Application Support/roullebot/calibration.json"
    with open(config_path, 'r') as f:
        calibration = json.load(f)
    
    # Get current Chrome position
    try:
        chrome_region = obtener_region_chrome(normalize=False)
        print(f"🔍 Chrome actual: ({chrome_region['left']}, {chrome_region['top']}) - {chrome_region['width']}x{chrome_region['height']}")
    except Exception as e:
        print(f"❌ Error detectando Chrome: {e}")
        return
    
    # Get calibrated winner region
    winner_region = calibration['winner_region']
    print(f"🎯 Región winner calibrada: ({winner_region['x']}, {winner_region['y']}) - {winner_region['width']}x{winner_region['height']}")
    
    # Check if region is inside Chrome
    if (winner_region['x'] >= chrome_region['left'] and 
        winner_region['y'] >= chrome_region['top'] and 
        winner_region['x'] + winner_region['width'] <= chrome_region['left'] + chrome_region['width'] and 
        winner_region['y'] + winner_region['height'] <= chrome_region['top'] + chrome_region['height']):
        print("✅ Región dentro de Chrome - debería funcionar")
    else:
        print("❌ Región FUERA de Chrome - por eso OCR no funciona")
        print("💡 Necesitas recalibrar o ajustar la región")
        
        # Calculate what the adjustment should be
        chrome_offset = calibration.get('chrome_offset', {})
        if chrome_offset.get('x') is not None:
            old_chrome_x = chrome_offset['x']
            old_chrome_y = chrome_offset['y']
            offset_x = chrome_region['left'] - old_chrome_x  
            offset_y = chrome_region['top'] - old_chrome_y
            
            adjusted_x = winner_region['x'] + offset_x
            adjusted_y = winner_region['y'] + offset_y
            
            print(f"🔧 Chrome cuando se calibró: ({old_chrome_x}, {old_chrome_y})")
            print(f"🔧 Chrome actual: ({chrome_region['left']}, {chrome_region['top']})")
            print(f"🔧 Offset necesario: ({offset_x:+d}, {offset_y:+d})")
            print(f"🔧 Región ajustada sería: ({adjusted_x}, {adjusted_y})")
            
            # Test the adjusted region
            adjusted_region = {
                'left': adjusted_x,
                'top': adjusted_y,
                'width': winner_region['width'],
                'height': winner_region['height']
            }
            
            if (adjusted_x >= chrome_region['left'] and 
                adjusted_y >= chrome_region['top'] and 
                adjusted_x + winner_region['width'] <= chrome_region['left'] + chrome_region['width'] and 
                adjusted_y + winner_region['height'] <= chrome_region['top'] + chrome_region['height']):
                print("✅ Región ajustada estaría dentro de Chrome")
                
                # Try to capture with adjusted region
                print("📸 Capturando con región ajustada...")
                try:
                    screenshot = capture_screen(adjusted_region)
                    img = np.array(screenshot)
                    if len(img.shape) == 3 and img.shape[2] == 3:
                        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                    else:
                        img_bgr = img
                    
                    debug_path = "test_adjusted_region.png"
                    cv2.imwrite(debug_path, img_bgr)
                    print(f"💾 Imagen capturada guardada en: {debug_path}")
                    print(f"📊 Forma de imagen: {img.shape}")
                    print(f"📊 Brillo promedio: {np.mean(img):.1f}")
                    
                    # Test OCR
                    from vision.detector import detect_number_from_image
                    numero = detect_number_from_image(img_bgr).strip()
                    print(f"🔍 OCR resultado: '{numero}'")
                    
                except Exception as e:
                    print(f"❌ Error capturando región ajustada: {e}")
            else:
                print("❌ Incluso la región ajustada estaría fuera de Chrome")
    
    # Try to capture with current (wrong) calibration for comparison
    print("\n📸 Capturando con calibración actual (probablemente fallará)...")
    try:
        screenshot = capture_screen(winner_region)
        img = np.array(screenshot)
        if img.size > 0:
            print(f"📊 Imagen capturada: {img.shape}")
            debug_path = "test_current_calibration.png"
            if len(img.shape) == 3 and img.shape[2] == 3:
                img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            else:
                img_bgr = img
            cv2.imwrite(debug_path, img_bgr)
            print(f"💾 Imagen guardada en: {debug_path}")
        else:
            print("❌ Imagen vacía - confirmando que la región está mal")
    except Exception as e:
        print(f"❌ Error capturando región actual: {e}")

if __name__ == "__main__":
    simple_test()