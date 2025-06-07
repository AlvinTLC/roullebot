"""
Sistema Multi-OCR con fallback automático
Soporta EasyOCR, PaddleOCR y Tesseract con fallback inteligente
"""
import cv2
import numpy as np
import sys
import os
import time
from typing import Optional, List, Tuple

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.platform_config import config

class MultiOCREngine:
    """Motor de OCR múltiple con fallback automático"""
    
    def __init__(self):
        self.engines = {}
        self.engine_order = ['easyocr', 'paddleocr', 'tesseract']  # Orden de preferencia
        self.available_engines = []
        self.current_engine = None
        
        print("🔍 Inicializando motores OCR...")
        self._initialize_engines()
        
    def _initialize_engines(self):
        """Inicializa todos los motores OCR disponibles"""
        
        # 1. EasyOCR (Mejor para números pequeños y gaming)
        try:
            import easyocr
            self.engines['easyocr'] = easyocr.Reader(['en'], gpu=False, verbose=False)
            self.available_engines.append('easyocr')
            print("✅ EasyOCR inicializado (Recomendado para gaming)")
        except ImportError:
            print("⚠️ EasyOCR no disponible - instala con: pip install easyocr")
        except Exception as e:
            print(f"⚠️ Error inicializando EasyOCR: {e}")
            
        # 2. PaddleOCR (Muy rápido y preciso)
        try:
            from paddleocr import PaddleOCR
            self.engines['paddleocr'] = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
            self.available_engines.append('paddleocr')
            print("✅ PaddleOCR inicializado (Rápido y preciso)")
        except ImportError:
            print("⚠️ PaddleOCR no disponible - instala con: pip install paddlepaddle paddleocr")
        except Exception as e:
            print(f"⚠️ Error inicializando PaddleOCR: {e}")
            
        # 3. Tesseract (Fallback tradicional)
        try:
            import pytesseract
            # Configurar Tesseract según la plataforma
            if config.tesseract_cmd and config.tesseract_cmd != 'tesseract':
                pytesseract.pytesseract.tesseract_cmd = config.tesseract_cmd
            
            # Test básico
            test_img = np.ones((50, 100), dtype=np.uint8) * 255
            cv2.putText(test_img, '123', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, 0, 2)
            result = pytesseract.image_to_string(test_img, config='--psm 8 -c tessedit_char_whitelist=0123456789')
            
            self.engines['tesseract'] = pytesseract
            self.available_engines.append('tesseract')
            print("✅ Tesseract inicializado (Fallback clásico)")
        except ImportError:
            print("⚠️ Tesseract no disponible - instala con: pip install pytesseract")
        except Exception as e:
            print(f"⚠️ Error inicializando Tesseract: {e}")
        
        if self.available_engines:
            self.current_engine = self.available_engines[0]
            print(f"🚀 Motor principal: {self.current_engine.upper()}")
            print(f"📋 Motores disponibles: {', '.join([e.upper() for e in self.available_engines])}")
        else:
            print("❌ ¡No hay motores OCR disponibles!")
            
    def detect_number_easyocr(self, img: np.ndarray) -> str:
        """Detección con EasyOCR"""
        try:
            # EasyOCR funciona mejor con imágenes más grandes
            height, width = img.shape[:2]
            if height < 40 or width < 40:
                scale_factor = max(3, 60 // min(height, width))
                img = cv2.resize(img, (width * scale_factor, height * scale_factor), 
                               interpolation=cv2.INTER_CUBIC)
            
            # EasyOCR puede trabajar directamente con BGR
            results = self.engines['easyocr'].readtext(img, 
                                                      allowlist='0123456789',
                                                      width_ths=0.7,
                                                      height_ths=0.7)
            
            # Filtrar y obtener el mejor resultado
            valid_numbers = []
            for (bbox, text, confidence) in results:
                # Limpiar texto
                clean_text = ''.join(c for c in text if c.isdigit())
                if clean_text and confidence > 0.3:  # Umbral de confianza más bajo para números
                    try:
                        number = int(clean_text)
                        if 0 <= number <= 36:  # Números válidos de ruleta
                            valid_numbers.append((number, confidence))
                    except:
                        continue
            
            if valid_numbers:
                # Ordenar por confianza y retornar el mejor
                valid_numbers.sort(key=lambda x: x[1], reverse=True)
                return str(valid_numbers[0][0])
                
        except Exception as e:
            print(f"Error en EasyOCR: {e}")
        
        return ""
    
    def detect_number_paddleocr(self, img: np.ndarray) -> str:
        """Detección con PaddleOCR"""
        try:
            # PaddleOCR funciona bien con imágenes medianas
            height, width = img.shape[:2]
            if height < 30 or width < 30:
                scale_factor = max(2, 40 // min(height, width))
                img = cv2.resize(img, (width * scale_factor, height * scale_factor), 
                               interpolation=cv2.INTER_CUBIC)
            
            results = self.engines['paddleocr'].ocr(img, cls=True)
            
            # PaddleOCR retorna estructura anidada
            valid_numbers = []
            if results and results[0]:
                for line in results[0]:
                    if len(line) == 2:
                        bbox, (text, confidence) = line
                        # Limpiar texto
                        clean_text = ''.join(c for c in text if c.isdigit())
                        if clean_text and confidence > 0.3:
                            try:
                                number = int(clean_text)
                                if 0 <= number <= 36:
                                    valid_numbers.append((number, confidence))
                            except:
                                continue
            
            if valid_numbers:
                valid_numbers.sort(key=lambda x: x[1], reverse=True)
                return str(valid_numbers[0][0])
                
        except Exception as e:
            print(f"Error en PaddleOCR: {e}")
        
        return ""
    
    def detect_number_tesseract(self, img: np.ndarray) -> str:
        """Detección con Tesseract (método original mejorado)"""
        try:
            from .detector import detect_number_from_image
            return detect_number_from_image(img)
        except Exception as e:
            print(f"Error en Tesseract: {e}")
        
        return ""
    
    def detect_number_smart(self, img: np.ndarray, timeout: float = 1.0) -> str:
        """
        Detección inteligente con fallback automático
        Prueba motores en orden de preferencia con timeout
        """
        if not self.available_engines:
            return ""
        
        start_time = time.time()
        
        for engine in self.available_engines:
            if time.time() - start_time > timeout:
                break
                
            try:
                if engine == 'easyocr':
                    result = self.detect_number_easyocr(img)
                elif engine == 'paddleocr':
                    result = self.detect_number_paddleocr(img)
                elif engine == 'tesseract':
                    result = self.detect_number_tesseract(img)
                else:
                    continue
                
                if result and result.strip():
                    # Validar que es un número de ruleta válido
                    try:
                        number = int(result.strip())
                        if 0 <= number <= 36:
                            return str(number)
                    except:
                        continue
                        
            except Exception as e:
                continue  # Probar siguiente motor
        
        return ""
    
    def detect_number_consensus(self, img: np.ndarray) -> str:
        """
        Detección por consenso - usa múltiples motores y toma la mayoría
        Más lento pero más confiable para casos críticos
        """
        if len(self.available_engines) < 2:
            return self.detect_number_smart(img)
        
        results = []
        
        for engine in self.available_engines:
            try:
                if engine == 'easyocr':
                    result = self.detect_number_easyocr(img)
                elif engine == 'paddleocr':
                    result = self.detect_number_paddleocr(img)
                elif engine == 'tesseract':
                    result = self.detect_number_tesseract(img)
                
                if result and result.strip():
                    try:
                        number = int(result.strip())
                        if 0 <= number <= 36:
                            results.append(number)
                    except:
                        continue
                        
            except Exception:
                continue
        
        if results:
            # Retornar el número más común
            from collections import Counter
            counter = Counter(results)
            most_common = counter.most_common(1)
            return str(most_common[0][0])
        
        return ""
    
    def get_engine_stats(self) -> dict:
        """Retorna estadísticas de los motores disponibles"""
        return {
            'available': self.available_engines,
            'current': self.current_engine,
            'total_engines': len(self.available_engines)
        }


# Instancia global
multi_ocr = MultiOCREngine()


def detect_number_from_image(img: np.ndarray, method: str = 'smart') -> str:
    """
    Función principal de detección de números
    
    Args:
        img: Imagen en formato numpy array
        method: 'smart' (fallback), 'consensus' (múltiples motores), 
                'easyocr', 'paddleocr', 'tesseract' (motor específico)
    """
    if method == 'smart':
        return multi_ocr.detect_number_smart(img)
    elif method == 'consensus':
        return multi_ocr.detect_number_consensus(img)
    elif method in multi_ocr.available_engines:
        if method == 'easyocr':
            return multi_ocr.detect_number_easyocr(img)
        elif method == 'paddleocr':
            return multi_ocr.detect_number_paddleocr(img)
        elif method == 'tesseract':
            return multi_ocr.detect_number_tesseract(img)
    
    # Fallback a smart si el método no está disponible
    return multi_ocr.detect_number_smart(img)


def detect_number_debug(img: np.ndarray) -> Tuple[str, List[Tuple[str, np.ndarray]]]:
    """Versión debug que muestra resultados de todos los motores"""
    debug_images = []
    debug_info = []
    
    # Probar todos los motores disponibles
    for engine in multi_ocr.available_engines:
        try:
            if engine == 'easyocr':
                result = multi_ocr.detect_number_easyocr(img)
            elif engine == 'paddleocr':
                result = multi_ocr.detect_number_paddleocr(img)
            elif engine == 'tesseract':
                result = multi_ocr.detect_number_tesseract(img)
            
            debug_info.append(f"{engine.upper()}: '{result}'")
            
            # Crear imagen de debug con resultado
            debug_img = img.copy()
            cv2.putText(debug_img, f"{engine}: {result}", (5, 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            debug_images.append((f"{engine}_{result}", debug_img))
            
        except Exception as e:
            debug_info.append(f"{engine.upper()}: ERROR")
    
    # Resultado final con smart method
    final_result = multi_ocr.detect_number_smart(img)
    print(f"🔍 OCR Debug: {' | '.join(debug_info)} | FINAL: '{final_result}'")
    
    return final_result, debug_images