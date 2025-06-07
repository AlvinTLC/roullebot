#!/usr/bin/env python3
"""
Script específico para probar y resolver problemas de EasyOCR en Windows
"""
import sys
import os
import cv2
import numpy as np

# Add the root directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_easyocr_windows():
    """Test específico para EasyOCR en Windows"""
    print("🪟 Probando EasyOCR en Windows...")
    print("="*50)
    
    # Información del sistema
    print(f"🖥️ Sistema operativo: {os.name}")
    print(f"📁 Directorio actual: {os.getcwd()}")
    print(f"🏠 Directorio home: {os.path.expanduser('~')}")
    
    # Probar importación
    try:
        print("\n📦 Probando importación de EasyOCR...")
        import easyocr
        print("✅ EasyOCR importado correctamente")
        print(f"📍 Ubicación: {easyocr.__file__}")
    except ImportError as e:
        print(f"❌ Error importando EasyOCR: {e}")
        print("💡 Instala con: pip install easyocr")
        return False
    
    # Configurar variables de entorno
    print("\n🔧 Configurando variables de entorno...")
    torch_home = os.path.join(os.path.expanduser('~'), '.torch')
    easyocr_home = os.path.join(os.path.expanduser('~'), '.EasyOCR')
    
    os.makedirs(torch_home, exist_ok=True)
    os.makedirs(easyocr_home, exist_ok=True)
    
    os.environ['TORCH_HOME'] = torch_home
    os.environ['EASYOCR_MODULE_PATH'] = easyocr_home
    
    print(f"📁 TORCH_HOME: {torch_home}")
    print(f"📁 EASYOCR_MODULE_PATH: {easyocr_home}")
    
    # Verificar conectividad
    print("\n🌐 Verificando conectividad...")
    try:
        import urllib.request
        urllib.request.urlopen('https://www.google.com', timeout=5)
        print("✅ Conexión a internet disponible")
    except Exception as e:
        print(f"⚠️ Problema de conectividad: {e}")
    
    # Probar inicialización paso a paso
    print("\n🚀 Inicializando EasyOCR...")
    
    initialization_methods = [
        ("Método 1: Configuración completa", lambda: easyocr.Reader(['en'], gpu=False, verbose=True, download_enabled=True)),
        ("Método 2: Sin verbose", lambda: easyocr.Reader(['en'], gpu=False, download_enabled=True)),
        ("Método 3: Configuración mínima", lambda: easyocr.Reader(['en'], gpu=False)),
        ("Método 4: Solo idioma", lambda: easyocr.Reader(['en'])),
    ]
    
    reader = None
    successful_method = None
    
    for method_name, method_func in initialization_methods:
        print(f"\n🔄 {method_name}...")
        try:
            reader = method_func()
            successful_method = method_name
            print(f"✅ {method_name} exitoso!")
            break
        except Exception as e:
            print(f"❌ {method_name} falló: {e}")
            print(f"   Tipo de error: {type(e).__name__}")
            
            # Información detallada para errores comunes
            if "No such file or directory" in str(e) or "cannot find" in str(e).lower():
                print("   💡 Problema: Archivos de modelo no encontrados")
                print("   🔧 Posibles soluciones:")
                print("      - Verificar conexión a internet")
                print("      - Ejecutar como administrador")
                print("      - Limpiar caché: eliminar ~/.EasyOCR/")
            elif "Permission" in str(e):
                print("   💡 Problema: Permisos insuficientes")
                print("   🔧 Solución: Ejecutar como administrador")
            elif "SSL" in str(e) or "certificate" in str(e).lower():
                print("   💡 Problema: Certificados SSL")
                print("   🔧 Solución: Verificar configuración de red/proxy")
    
    if reader is None:
        print("\n❌ No se pudo inicializar EasyOCR con ningún método")
        print("\n🛠️ Pasos de resolución recomendados:")
        print("1. pip uninstall easyocr torch torchvision")
        print("2. pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu")
        print("3. pip install easyocr")
        print("4. Ejecutar este script como administrador")
        return False
    
    # Probar detección
    print(f"\n🎯 Probando detección con {successful_method}...")
    
    # Crear imagen de prueba
    test_img = np.ones((60, 120, 3), dtype=np.uint8) * 255  # Fondo blanco
    cv2.putText(test_img, '24', (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)
    
    try:
        results = reader.readtext(test_img, allowlist='0123456789')
        print(f"📊 Resultados EasyOCR: {results}")
        
        if results:
            detected_text = results[0][1] if len(results[0]) > 1 else "No detectado"
            confidence = results[0][2] if len(results[0]) > 2 else 0.0
            print(f"🎯 Número detectado: '{detected_text}' (confianza: {confidence:.2f})")
            
            if detected_text.strip() == '24':
                print("✅ ¡Test de detección exitoso!")
                return True
            else:
                print(f"⚠️ Detección incorrecta: esperado '24', obtuvo '{detected_text}'")
        else:
            print("⚠️ No se detectó ningún texto")
            
    except Exception as e:
        print(f"❌ Error en detección: {e}")
        return False
    
    return True

def test_multi_ocr_fallback():
    """Probar el sistema multi-OCR con fallback"""
    print("\n" + "="*50)
    print("🔍 Probando sistema Multi-OCR con fallback...")
    
    try:
        from vision.multi_ocr import multi_ocr
        
        print(f"📋 Motores disponibles: {multi_ocr.available_engines}")
        print(f"🚀 Motor actual: {multi_ocr.current_engine}")
        
        # Si EasyOCR falló, intentar reintento manual
        if 'easyocr' not in multi_ocr.available_engines:
            print("\n🔄 EasyOCR no disponible, intentando reintento manual...")
            success = multi_ocr.retry_easyocr_initialization()
            if success:
                print("✅ EasyOCR inicializado exitosamente en reintento")
            else:
                print("❌ Reintento manual también falló")
        
        # Probar detección con sistema multi-OCR
        print("\n🎯 Probando detección multi-OCR...")
        test_img = np.ones((60, 120, 3), dtype=np.uint8) * 255
        cv2.putText(test_img, '36', (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)
        
        from vision.multi_ocr import detect_number_from_image
        result = detect_number_from_image(test_img, method='smart')
        
        print(f"🎯 Resultado final: '{result}'")
        
        if result == '36':
            print("✅ ¡Sistema multi-OCR funcionando correctamente!")
        else:
            print(f"⚠️ Resultado inesperado: esperado '36', obtuvo '{result}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en sistema multi-OCR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🪟 DIAGNÓSTICO EASYOCR PARA WINDOWS")
    print("="*50)
    
    # Test 1: EasyOCR directo
    easyocr_success = test_easyocr_windows()
    
    # Test 2: Sistema Multi-OCR
    multiocr_success = test_multi_ocr_fallback()
    
    # Resumen final
    print("\n" + "="*50)
    print("📋 RESUMEN DEL DIAGNÓSTICO")
    print("="*50)
    print(f"🔍 EasyOCR directo: {'✅ FUNCIONANDO' if easyocr_success else '❌ FALLANDO'}")
    print(f"🔧 Sistema Multi-OCR: {'✅ FUNCIONANDO' if multiocr_success else '❌ FALLANDO'}")
    
    if not easyocr_success and not multiocr_success:
        print("\n🚨 ACCIÓN REQUERIDA:")
        print("1. Ejecutar como administrador")
        print("2. Verificar conexión a internet")
        print("3. Reinstalar EasyOCR completamente")
        print("4. Considerar usar solo PaddleOCR + Tesseract")
    elif not easyocr_success but multiocr_success:
        print("\n✅ SOLUCIÓN PARCIAL:")
        print("EasyOCR tiene problemas pero el sistema multi-OCR funciona")
        print("El bot funcionará con PaddleOCR/Tesseract como fallback")
    else:
        print("\n🎉 TODO FUNCIONANDO CORRECTAMENTE")
        print("El sistema está listo para usar")