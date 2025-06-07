#!/usr/bin/env python3
"""
Test simple para verificar que el sistema OCR funciona sin recursión
"""
import sys
import os
import cv2
import numpy as np

# Add the root directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_simple_ocr():
    """Test básico sin recursión"""
    print("🧪 Probando sistema OCR sin recursión...")
    
    try:
        # Crear imagen de prueba simple
        img = np.ones((50, 100, 3), dtype=np.uint8) * 255  # Fondo blanco
        cv2.putText(img, '24', (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        print("📸 Imagen de prueba creada: número '24'")
        
        # Probar detector original (con multi-ocr)
        from vision.detector import detect_number_from_image
        resultado = detect_number_from_image(img)
        
        print(f"✅ Resultado OCR: '{resultado}'")
        
        if resultado == '24':
            print("🎯 ¡Test exitoso! OCR funcionando correctamente")
        else:
            print(f"⚠️ Resultado inesperado: esperado '24', obtuvo '{resultado}'")
            
    except RecursionError as e:
        print(f"❌ Error de recursión: {e}")
        print("💡 El problema de recursión aún existe")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_ocr()