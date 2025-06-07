#!/usr/bin/env python3
"""
Test script para verificar detección de ventanas en Windows
Especialmente para Stake.com
"""
import sys
import os

# Add the root directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_window_detection():
    """Test window detection for Stake.com"""
    print("🧪 Testing window detection for Stake.com...")
    
    try:
        from utils.window_manager import window_manager
        
        print(f"Sistema detectado: {window_manager.system}")
        
        if window_manager.is_windows:
            print("\n🪟 WINDOWS DETECTADO - Probando detección mejorada...")
            
            # Test the improved find_chrome_window function
            window_info = window_manager.find_chrome_window()
            
            if window_info:
                print(f"✅ ¡Ventana encontrada!")
                print(f"   Título: '{window_info['title']}'")
                print(f"   Posición: ({window_info['x']}, {window_info['y']})")
                print(f"   Tamaño: {window_info['width']}x{window_info['height']}")
                
                # Test region detection
                from vision.window_region import obtener_region_chrome
                
                try:
                    region = obtener_region_chrome(normalize=False)
                    print(f"\n📊 Región detectada:")
                    print(f"   left={region['left']}, top={region['top']}")
                    print(f"   width={region['width']}, height={region['height']}")
                    
                    print(f"\n✅ ¡Detección de Stake.com funciona correctamente!")
                    print(f"💡 Ahora puedes ejecutar la calibración (opción 1)")
                    
                except Exception as e:
                    print(f"❌ Error en detección de región: {e}")
            else:
                print(f"❌ No se encontró ventana compatible")
                print(f"💡 Soluciones:")
                print(f"   1. Abre Stake.com en cualquier navegador")
                print(f"   2. Asegúrate que la pestaña esté activa")
                print(f"   3. Verifica que 'Stake' aparezca en el título de la ventana")
        else:
            print("ℹ️  Este test es específico para Windows")
            print("En macOS y Linux, la detección funciona de manera diferente")
            
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Asegúrate de instalar: pip install pygetwindow")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_window_detection()