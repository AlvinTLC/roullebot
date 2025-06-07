import pytesseract
import cv2
import numpy as np
import sys
import os

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.platform_config import config

# Configurar Tesseract según la plataforma
if config.tesseract_cmd and config.tesseract_cmd != 'tesseract':
    pytesseract.pytesseract.tesseract_cmd = config.tesseract_cmd


def preprocess_image(img, method='adaptive'):
    """Preprocesa la imagen para mejorar la detección"""
    if img is None or img.size == 0:
        return None

    # Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Aplicar padding para evitar problemas con bordes
    padded = cv2.copyMakeBorder(gray, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=255)

    if method == 'adaptive':
        # Aumentar el contraste
        enhanced = cv2.convertScaleAbs(padded, alpha=1.8, beta=10)
        
        # Aplicar desenfoque gaussiano para reducir ruido
        blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
        
        # Umbral adaptativo para mejor detección
        block_size = max(5, min(blurred.shape) // 3)
        if block_size % 2 == 0:
            block_size += 1
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, 2)
        
    elif method == 'otsu':
        # Método Otsu para binarización automática
        blurred = cv2.GaussianBlur(padded, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
    elif method == 'simple':
        # Umbral simple con valor dinámico
        mean_val = np.mean(padded)
        thresh_val = max(100, min(200, mean_val - 20))
        _, thresh = cv2.threshold(padded, thresh_val, 255, cv2.THRESH_BINARY)
    
    else:
        return padded

    # Operaciones morfológicas para limpiar la imagen
    kernel = np.ones((2, 2), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)

    return cleaned


def detect_number_from_image(img):
    """Detecta número usando el sistema multi-OCR con fallback automático"""
    try:
        # Intentar usar el nuevo sistema multi-OCR
        from .multi_ocr import detect_number_from_image as multi_detect
        result = multi_detect(img, method='smart')
        if result:
            return result
    except ImportError:
        # Fallback al método original si multi_ocr no está disponible
        pass
    except Exception as e:
        print(f"⚠️ Error en multi-OCR, usando Tesseract: {e}")
    
    # Método original con Tesseract (fallback)
    return _detect_number_tesseract_original(img)


def _detect_number_tesseract_original(img):
    """Método original de Tesseract (mantenido como fallback)"""
    if img is None or img.size == 0:
        return ""

    # Redimensionar imagen si es muy pequeña para mejorar OCR
    height, width = img.shape[:2]
    if height < 40 or width < 40:
        scale_factor = max(2, 40 // min(height, width))
        img = cv2.resize(img, (width * scale_factor, height * scale_factor), 
                        interpolation=cv2.INTER_CUBIC)

    # Métodos de preprocesamiento
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Método 1: Umbral simple optimizado
    mean_val = np.mean(gray)
    thresh_val = max(80, min(180, mean_val - 30))
    _, thresh1 = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)

    # Método 2: Preprocesamiento adaptativo
    thresh2 = preprocess_image(img, 'adaptive')

    # Método 3: Método Otsu
    thresh3 = preprocess_image(img, 'otsu')

    # Método 4: Umbral invertido para números oscuros en fondo claro
    _, thresh4 = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY_INV)

    # Método 5: Simple dinámico
    thresh5 = preprocess_image(img, 'simple')

    # Configuraciones de Tesseract optimizadas para números pequeños
    configs = [
        '--psm 8 -c tessedit_char_whitelist=0123456789',  # Palabra única
        '--psm 7 -c tessedit_char_whitelist=0123456789',  # Línea de texto única
        '--psm 10 -c tessedit_char_whitelist=0123456789', # Carácter único
        '--psm 13 -c tessedit_char_whitelist=0123456789', # Línea cruda
        '--psm 6 -c tessedit_char_whitelist=0123456789'   # Bloque uniforme
    ]

    resultados = []

    # Probar diferentes combinaciones
    for i, thresh in enumerate([thresh1, thresh2, thresh3, thresh4, thresh5]):
        if thresh is None:
            continue

        for config in configs:
            try:
                text = pytesseract.image_to_string(thresh, config=config).strip()
                # Limpiar texto detectado
                text = ''.join(c for c in text if c.isdigit())
                
                if text and len(text) <= 2:
                    numero = int(text)
                    if 0 <= numero <= 36:  # Números válidos de ruleta
                        resultados.append(numero)
                        # Si encontramos un número válido, darle más peso
                        if i == 1 or i == 2:  # Métodos adaptativos tienen más peso
                            resultados.extend([numero] * 2)
            except:
                continue

    # Retornar el número más frecuente
    if resultados:
        from collections import Counter
        counter = Counter(resultados)
        return str(counter.most_common(1)[0][0])

    return ""


def detect_number_debug(img):
    """Versión de debug que muestra los pasos de procesamiento"""
    try:
        # Intentar usar el nuevo sistema multi-OCR debug
        from .multi_ocr import detect_number_debug as multi_debug
        return multi_debug(img)
    except ImportError:
        # Fallback al método original si multi_ocr no está disponible
        pass
    except Exception as e:
        print(f"⚠️ Error en multi-OCR debug, usando método original: {e}")
    
    # Método debug original
    if img is None or img.size == 0:
        return "", []

    debug_images = []

    # Redimensionar si es necesario (como en la función principal)
    height, width = img.shape[:2]
    processed_img = img
    if height < 40 or width < 40:
        scale_factor = max(2, 40 // min(height, width))
        processed_img = cv2.resize(img, (width * scale_factor, height * scale_factor), 
                                 interpolation=cv2.INTER_CUBIC)

    # Imagen original (procesada)
    debug_images.append(("Original", processed_img))

    # Escala de grises
    gray = cv2.cvtColor(processed_img, cv2.COLOR_BGR2GRAY)
    debug_images.append(("Gris", gray))

    # Método 1: Umbral dinámico
    mean_val = np.mean(gray)
    thresh_val = max(80, min(180, mean_val - 30))
    _, thresh1 = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)
    debug_images.append(("Umbral Dinámico", thresh1))

    # Método 2: Adaptativo
    thresh2 = preprocess_image(processed_img, 'adaptive')
    if thresh2 is not None:
        debug_images.append(("Adaptativo", thresh2))

    # Método 3: Otsu
    thresh3 = preprocess_image(processed_img, 'otsu')
    if thresh3 is not None:
        debug_images.append(("Otsu", thresh3))

    # Método 4: Invertido
    _, thresh4 = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY_INV)
    debug_images.append(("Invertido", thresh4))

    # Detectar número
    numero = detect_number_from_image(img)

    return numero, debug_images