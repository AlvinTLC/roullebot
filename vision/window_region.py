import sys
import os

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.window_manager import window_manager

def obtener_region_chrome():
    """Obtiene la región de la ventana de Chrome de forma multiplataforma"""
    window_info = window_manager.find_chrome_window()
    
    if not window_info:
        raise Exception("❌ No se encontró ninguna ventana de Chrome.")
    
    # Activar la ventana si es posible
    window_manager.activate_window(window_info)
    
    return {
        "left": window_info['x'],
        "top": window_info['y'],
        "width": window_info['width'],
        "height": window_info['height']
    }
