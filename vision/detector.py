import pytesseract
import cv2
import numpy as np

# ✅ Ruta para Windows — AJUSTA si está en otro lugar
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def preprocess_image(img):
    """Preprocesa la imagen para mejorar la detección"""
    if img is None or img.size == 0:
        return None

    # Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Aumentar el contraste
    gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)

    # Aplicar desenfoque gaussiano para reducir ruido
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # Umbral adaptativo para mejor detección
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Operaciones morfológicas para limpiar la imagen
    kernel = np.ones((2, 2), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    return thresh


def detect_number_from_image(img):
    """Detecta número de la imagen con múltiples métodos"""
    if img is None or img.size == 0:
        return ""

    # Método 1: Preprocesamiento básico
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh1 = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)

    # Método 2: Preprocesamiento avanzado
    thresh2 = preprocess_image(img)

    # Método 3: Umbral invertido
    _, thresh3 = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # Configuraciones de Tesseract
    configs = [
        '--psm 8 -c tessedit_char_whitelist=0123456789',
        '--psm 7 -c tessedit_char_whitelist=0123456789',
        '--psm 10 -c tessedit_char_whitelist=0123456789',
        '--psm 13 -c tessedit_char_whitelist=0123456789'
    ]

    resultados = []

    # Probar diferentes combinaciones
    for thresh in [thresh1, thresh2, thresh3]:
        if thresh is None:
            continue

        for config in configs:
            try:
                text = pytesseract.image_to_string(thresh, config=config).strip()
                if text and text.isdigit() and len(text) <= 2:
                    numero = int(text)
                    if 0 <= numero <= 36:  # Números válidos de ruleta
                        resultados.append(numero)
            except:
                continue

    # Retornar el número más frecuente
    if resultados:
        return str(max(set(resultados), key=resultados.count))

    return ""


def detect_number_debug(img):
    """Versión de debug que muestra los pasos de procesamiento"""
    if img is None or img.size == 0:
        return "", []

    debug_images = []

    # Imagen original
    debug_images.append(("Original", img))

    # Escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    debug_images.append(("Gris", gray))

    # Umbral simple
    _, thresh1 = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
    debug_images.append(("Umbral Simple", thresh1))

    # Preprocesamiento avanzado
    thresh2 = preprocess_image(img)
    if thresh2 is not None:
        debug_images.append(("Preprocesado", thresh2))

    # Detectar número
    numero = detect_number_from_image(img)

    return numero, debug_images