#!/usr/bin/env python3
"""
Test script para comparar los diferentes motores OCR
"""
import sys
import os
import time
import cv2
import numpy as np

# Add the root directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_test_images():
    """Crear imágenes de prueba con números de ruleta"""
    test_images = []
    
    # Crear diferentes tipos de imágenes de prueba
    sizes = [(50, 80), (30, 50), (20, 30)]  # Diferentes tamaños
    numbers = ['0', '7', '13', '24', '36']    # Números de prueba
    
    for i, (h, w) in enumerate(sizes):
        for number in numbers:
            # Crear imagen base
            img = np.ones((h, w, 3), dtype=np.uint8) * 255  # Fondo blanco
            
            # Agregar número
            font_scale = h / 50.0  # Escalar fuente según tamaño
            font_thickness = max(1, int(h / 25))
            
            # Calcular posición centrada del texto
            text_size = cv2.getTextSize(number, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)[0]
            text_x = (w - text_size[0]) // 2
            text_y = (h + text_size[1]) // 2
            
            # Texto negro sobre fondo blanco
            cv2.putText(img, number, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), font_thickness)
            
            test_images.append({
                'image': img,
                'expected': number,
                'size': f"{w}x{h}",
                'name': f"test_{number}_{w}x{h}"
            })
    
    return test_images

def test_ocr_engines():
    """Probar todos los motores OCR disponibles"""
    print("🧪 PRUEBA COMPARATIVA DE MOTORES OCR")
    print("=" * 60)
    
    try:
        from vision.multi_ocr import multi_ocr
        
        # Mostrar motores disponibles
        stats = multi_ocr.get_engine_stats()
        print(f"🔍 Motores OCR disponibles: {len(stats['available'])}")
        for engine in stats['available']:
            print(f"   ✅ {engine.upper()}")
        
        if not stats['available']:
            print("❌ No hay motores OCR disponibles")
            print("💡 Instala al menos uno:")
            print("   pip install easyocr")
            print("   pip install paddlepaddle paddleocr")
            print("   O asegúrate que Tesseract esté instalado")
            return
        
        print(f"\n🚀 Motor principal: {stats['current'].upper()}")
        
        # Crear imágenes de prueba
        print("\n📸 Creando imágenes de prueba...")
        test_images = create_test_images()
        print(f"   Generadas {len(test_images)} imágenes de prueba")
        
        # Probar cada motor
        results = {}
        
        for engine in stats['available']:
            print(f"\n🔍 Probando {engine.upper()}...")
            engine_results = []
            total_time = 0
            
            for test_img in test_images:
                img = test_img['image']
                expected = test_img['expected']
                
                # Medir tiempo
                start_time = time.time()
                
                # Probar motor específico
                try:
                    if engine == 'easyocr':
                        result = multi_ocr.detect_number_easyocr(img)
                    elif engine == 'paddleocr':
                        result = multi_ocr.detect_number_paddleocr(img)
                    elif engine == 'tesseract':
                        result = multi_ocr.detect_number_tesseract(img)
                    
                    elapsed = time.time() - start_time
                    total_time += elapsed
                    
                    # Verificar resultado
                    correct = (result == expected)
                    engine_results.append({
                        'test': test_img['name'],
                        'expected': expected,
                        'result': result,
                        'correct': correct,
                        'time': elapsed * 1000  # ms
                    })
                    
                    if correct:
                        print(f"   ✅ {test_img['name']}: '{result}' ({elapsed*1000:.1f}ms)")
                    else:
                        print(f"   ❌ {test_img['name']}: esperado '{expected}', obtuvo '{result}' ({elapsed*1000:.1f}ms)")
                        
                except Exception as e:
                    print(f"   💥 {test_img['name']}: ERROR - {e}")
                    engine_results.append({
                        'test': test_img['name'],
                        'expected': expected,
                        'result': 'ERROR',
                        'correct': False,
                        'time': 0
                    })
            
            # Calcular estadísticas
            correct_count = sum(1 for r in engine_results if r['correct'])
            accuracy = (correct_count / len(engine_results)) * 100
            avg_time = total_time / len(engine_results) * 1000  # ms
            
            results[engine] = {
                'accuracy': accuracy,
                'avg_time': avg_time,
                'correct': correct_count,
                'total': len(engine_results),
                'results': engine_results
            }
            
            print(f"   📊 Precisión: {accuracy:.1f}% ({correct_count}/{len(engine_results)})")
            print(f"   ⚡ Tiempo promedio: {avg_time:.1f}ms")
        
        # Resumen comparativo
        print(f"\n🏆 RESUMEN COMPARATIVO")
        print("=" * 50)
        print(f"{'Motor':<12} {'Precisión':<12} {'Tiempo':<12} {'Recomendación'}")
        print("-" * 50)
        
        best_accuracy = max(results.values(), key=lambda x: x['accuracy'])['accuracy']
        fastest_time = min(results.values(), key=lambda x: x['avg_time'])['avg_time']
        
        for engine, stats in results.items():
            accuracy = stats['accuracy']
            avg_time = stats['avg_time']
            
            # Determinar recomendación
            if accuracy == best_accuracy and avg_time <= fastest_time * 1.5:
                recommendation = "🥇 MEJOR"
            elif accuracy >= 80:
                recommendation = "👍 BUENO"
            elif accuracy >= 60:
                recommendation = "⚠️ REGULAR"
            else:
                recommendation = "❌ MALO"
            
            print(f"{engine.upper():<12} {accuracy:>7.1f}% {avg_time:>8.1f}ms     {recommendation}")
        
        # Probar método smart (fallback automático)
        print(f"\n🤖 PROBANDO MÉTODO SMART (fallback automático)...")
        smart_correct = 0
        smart_total_time = 0
        
        for test_img in test_images:
            img = test_img['image']
            expected = test_img['expected']
            
            start_time = time.time()
            result = multi_ocr.detect_number_smart(img)
            elapsed = time.time() - start_time
            smart_total_time += elapsed
            
            correct = (result == expected)
            if correct:
                smart_correct += 1
            
        smart_accuracy = (smart_correct / len(test_images)) * 100
        smart_avg_time = smart_total_time / len(test_images) * 1000
        
        print(f"   📊 Smart method - Precisión: {smart_accuracy:.1f}% ({smart_correct}/{len(test_images)})")
        print(f"   ⚡ Smart method - Tiempo promedio: {smart_avg_time:.1f}ms")
        
        # Recomendaciones finales
        print(f"\n💡 RECOMENDACIONES:")
        if 'easyocr' in results and results['easyocr']['accuracy'] >= 80:
            print("   🎯 Para gaming: EasyOCR es el mejor para números pequeños")
        if 'paddleocr' in results and results['paddleocr']['accuracy'] >= 80:
            print("   ⚡ Para velocidad: PaddleOCR es rápido y preciso")
        if smart_accuracy >= max(r['accuracy'] for r in results.values()) * 0.9:
            print("   🤖 El método SMART (fallback automático) funciona muy bien")
        
        print(f"\n✅ Prueba completada. El bot usará automáticamente el mejor motor disponible.")
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Instala los motores OCR:")
        print("   pip install easyocr paddlepaddle paddleocr")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ocr_engines()