import sys
import os

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.window_manager import window_manager

def obtener_region_chrome(normalize=False):
    """Obtiene la región de la ventana de Chrome de forma multiplataforma"""
    window_info = window_manager.find_chrome_window()
    
    if not window_info:
        raise Exception("❌ No se encontró ninguna ventana de Chrome.")
    
    # Si se solicita normalización
    if normalize:
        print("🔧 Normalizando ventana de Chrome para consistencia...")
        
        # Obtener tamaño recomendado según la resolución
        target_width, target_height, target_x, target_y = window_manager.get_recommended_chrome_size()
        
        # Normalizar la ventana
        normalized_info = window_manager.normalize_chrome_window(
            target_width, target_height, target_x, target_y
        )
        
        if normalized_info:
            window_info = normalized_info
            print(f"✅ Chrome normalizado: {target_width}x{target_height} en ({target_x}, {target_y})")
        else:
            print("⚠️ No se pudo normalizar Chrome, usando ventana actual")
    
    # Activar la ventana si es posible
    window_manager.activate_window(window_info)
    
    return {
        "left": window_info['x'],
        "top": window_info['y'],
        "width": window_info['width'],
        "height": window_info['height']
    }
