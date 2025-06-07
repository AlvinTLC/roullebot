import mss
import numpy as np
import cv2

def capture_screen(region=None):
    """Captura pantalla con mejor manejo de errores para macOS"""
    try:
        with mss.mss() as sct:
            if region is None:
                # Usar monitor principal
                monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
            else:
                # Normalizar formato de región (soportar tanto x,y como left,top)
                if 'x' in region and 'y' in region:
                    # Formato de calibración: x, y, width, height
                    monitor = {
                        'left': max(0, int(region['x'])),
                        'top': max(0, int(region['y'])),
                        'width': max(1, int(region['width'])),
                        'height': max(1, int(region['height']))
                    }
                elif 'left' in region and 'top' in region:
                    # Formato estándar MSS: left, top, width, height
                    monitor = {
                        'left': max(0, int(region['left'])),
                        'top': max(0, int(region['top'])),
                        'width': max(1, int(region['width'])),
                        'height': max(1, int(region['height']))
                    }
                else:
                    raise ValueError(f"Región inválida: se esperaba 'x,y' o 'left,top', se recibió: {list(region.keys())}")
            
            # Capturar screenshot
            screenshot = sct.grab(monitor)
            img = np.array(screenshot)
            
            # Verificar que la imagen no esté vacía
            if img.size == 0:
                raise ValueError("Screenshot capturado está vacío")
            
            # Convertir formato de color
            if img.shape[2] == 4:  # BGRA
                return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            elif img.shape[2] == 3:  # BGR
                return img
            else:
                raise ValueError(f"Formato de color no soportado: {img.shape}")
                
    except Exception as e:
        print(f"❌ Error capturando pantalla: {e}")
        # Retornar imagen negra pequeña como fallback
        return np.zeros((40, 60, 3), dtype=np.uint8)
