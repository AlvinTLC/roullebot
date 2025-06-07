import platform
import os
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

class PlatformConfig:
    """Configuración específica para cada plataforma (Windows, macOS, Linux)"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.is_windows = self.system == 'windows'
        self.is_mac = self.system == 'darwin'
        self.is_linux = self.system == 'linux'
        
        # Detección automática de resolución y DPI
        self.resolution_info = self._detect_resolution()
        self.dpi_scale = self._get_dpi_scale()
        
        # Configuración de Tesseract
        self.tesseract_cmd = self._get_tesseract_path()
        
        # Configuración de ventanas
        self.window_backend = self._get_window_backend()
        
        # Configuración de rutas
        self.config_dir = self._get_config_dir()
        
    def _get_tesseract_path(self) -> Optional[str]:
        """Obtiene la ruta de Tesseract según el SO"""
        if self.is_windows:
            # Rutas comunes en Windows
            possible_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                r'C:\Users\%s\AppData\Local\Tesseract-OCR\tesseract.exe' % os.environ.get('USERNAME', '')
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    return path
        elif self.is_mac:
            # En macOS, normalmente instalado con Homebrew
            possible_paths = [
                '/opt/homebrew/bin/tesseract',  # Apple Silicon
                '/usr/local/bin/tesseract',      # Intel
                '/usr/bin/tesseract'
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    return path
        elif self.is_linux:
            # En Linux, normalmente en el PATH
            return 'tesseract'
        
        # Si no se encuentra, intentar usar el comando directamente
        return 'tesseract'
    
    def _get_window_backend(self) -> str:
        """Determina qué backend usar para manejo de ventanas"""
        if self.is_windows:
            return 'pygetwindow'
        elif self.is_mac:
            return 'applescript'
        elif self.is_linux:
            return 'xdotool'
        return 'none'
    
    def _detect_resolution(self) -> Dict[str, any]:
        """Detecta automáticamente la resolución de la pantalla"""
        resolution_info = {
            'width': 1920,
            'height': 1080,
            'is_2k': False,
            'is_4k': False,
            'scale_factor': 1.0
        }
        
        try:
            if self.is_windows:
                import tkinter as tk
                root = tk.Tk()
                width = root.winfo_screenwidth()
                height = root.winfo_screenheight()
                root.destroy()
                
                resolution_info['width'] = width
                resolution_info['height'] = height
                
                # Detectar tipo de resolución
                if width >= 2560 and height >= 1440:
                    resolution_info['is_2k'] = True
                    resolution_info['scale_factor'] = width / 1920
                elif width >= 3840 and height >= 2160:
                    resolution_info['is_4k'] = True
                    resolution_info['scale_factor'] = width / 1920
                    
            elif self.is_mac:
                import subprocess
                result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                                      capture_output=True, text=True)
                # Parsear resolución de macOS
                # Por ahora usar valores por defecto
                pass
                
        except Exception as e:
            print(f"⚠️ No se pudo detectar resolución automáticamente: {e}")
            
        return resolution_info
    
    def _get_dpi_scale(self) -> float:
        """Obtiene el factor de escalado DPI en Windows"""
        if not self.is_windows:
            return 1.0
            
        try:
            import ctypes
            from ctypes import wintypes
            
            # Obtener DPI awareness
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()
            
            # Obtener DPI del monitor principal
            dc = user32.GetDC(0)
            dpi = ctypes.windll.gdi32.GetDeviceCaps(dc, 88)  # LOGPIXELSX
            user32.ReleaseDC(0, dc)
            
            # DPI estándar es 96
            scale = dpi / 96.0
            return scale
            
        except Exception as e:
            print(f"⚠️ No se pudo obtener escala DPI: {e}")
            return 1.0
    
    def _get_config_dir(self) -> Path:
        """Obtiene el directorio de configuración según el SO"""
        if self.is_windows:
            base = Path(os.environ.get('APPDATA', ''))
        elif self.is_mac:
            base = Path.home() / 'Library' / 'Application Support'
        else:  # Linux
            base = Path.home() / '.config'
        
        config_dir = base / 'roullebot'
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    def get_chrome_window_title(self) -> str:
        """Retorna el patrón de título de ventana de Chrome según el SO"""
        if self.is_windows:
            return "Google Chrome"
        elif self.is_mac:
            return "Google Chrome"
        elif self.is_linux:
            return "Google Chrome"
        return "Chrome"
    
    def get_click_delay(self) -> float:
        """Retorna el delay recomendado entre clicks según el SO"""
        if self.is_mac:
            return 0.1  # macOS puede necesitar un poco más de delay
        return 0.05
    
    def get_performance_settings(self) -> Dict[str, any]:
        """Retorna configuraciones optimizadas de rendimiento por SO"""
        if self.is_windows:
            return {
                'capture_method': 'mss',  # Más rápido en Windows
                'opencv_threads': 4,      # Usar múltiples threads
                'capture_interval': 0.02, # 50 FPS máximo
                'preview_interval': 0.033,  # Preview a 30 FPS (1/30 = 0.033s)
                'ocr_threads': 2,         # OCR en paralelo
                'resize_before_ocr': True,# Redimensionar antes de OCR
                'skip_frames': 2,         # Procesar 1 de cada 2 frames
                'memory_cleanup': True,   # Limpiar memoria regularmente
                'priority_boost': True    # Aumentar prioridad del proceso
            }
        elif self.is_mac:
            return {
                'capture_method': 'mss',
                'opencv_threads': 2,
                'capture_interval': 0.03,
                'preview_interval': 0.2,
                'ocr_threads': 1,
                'resize_before_ocr': False,
                'skip_frames': 1,
                'memory_cleanup': False,
                'priority_boost': False
            }
        else:  # Linux
            return {
                'capture_method': 'mss',
                'opencv_threads': 2,
                'capture_interval': 0.025,
                'preview_interval': 0.15,
                'ocr_threads': 2,
                'resize_before_ocr': True,
                'skip_frames': 1,
                'memory_cleanup': True,
                'priority_boost': False
            }
    
    def optimize_for_windows(self):
        """Optimizaciones específicas para Windows"""
        if not self.is_windows:
            return
            
        import os
        import sys
        
        try:
            # Aumentar prioridad del proceso
            import psutil
            p = psutil.Process(os.getpid())
            p.nice(psutil.HIGH_PRIORITY_CLASS)
            print("🚀 Prioridad del proceso aumentada (Windows)")
        except ImportError:
            print("⚠️ psutil no disponible - instala con: pip install psutil")
        except Exception as e:
            print(f"⚠️ No se pudo aumentar prioridad: {e}")
        
        try:
            # Configurar OpenCV para mejor rendimiento en Windows
            import cv2
            cv2.setNumThreads(4)  # Usar 4 threads
            cv2.setUseOptimized(True)  # Optimizaciones habilitadas
            print("🔧 OpenCV optimizado para Windows")
        except Exception as e:
            print(f"⚠️ Error configurando OpenCV: {e}")
            
        # Variables de entorno para mejor rendimiento
        os.environ['OMP_NUM_THREADS'] = '4'
        os.environ['OPENCV_DNN_OPENCL'] = '1'
    
    def verify_dependencies(self) -> Dict[str, bool]:
        """Verifica que las dependencias del sistema estén instaladas"""
        deps = {}
        
        # Verificar Tesseract
        deps['tesseract'] = os.path.exists(self.tesseract_cmd) if self.tesseract_cmd else False
        
        # Verificar herramientas de ventana
        if self.is_mac:
            deps['applescript'] = True  # Siempre disponible en macOS
        elif self.is_linux:
            deps['xdotool'] = os.system('which xdotool > /dev/null 2>&1') == 0
        
        return deps
    
    def get_install_instructions(self) -> Dict[str, str]:
        """Retorna instrucciones de instalación para dependencias faltantes"""
        instructions = {}
        
        if self.is_windows:
            instructions['tesseract'] = (
                "Descarga Tesseract desde: https://github.com/UB-Mannheim/tesseract/wiki\n"
                "O usa: choco install tesseract"
            )
        elif self.is_mac:
            instructions['tesseract'] = "Instala con Homebrew: brew install tesseract"
            instructions['tesseract-lang'] = "Para español: brew install tesseract-lang"
        elif self.is_linux:
            instructions['tesseract'] = "Instala con: sudo apt-get install tesseract-ocr"
            instructions['xdotool'] = "Instala con: sudo apt-get install xdotool"
            
        return instructions
    
    def get_resolution_info(self) -> str:
        """Retorna información detallada de la resolución detectada"""
        info = self.resolution_info
        return (f"🖥️ Resolución: {info['width']}x{info['height']} "
                f"({'2K' if info['is_2k'] else '4K' if info['is_4k'] else 'FullHD'}) "
                f"| DPI Scale: {self.dpi_scale:.2f}x")
    
    def auto_scale_regions(self, regions: Dict) -> Dict:
        """Escala automáticamente las regiones según la resolución detectada"""
        if not self.is_windows or self.resolution_info['scale_factor'] == 1.0:
            return regions
            
        scale = self.resolution_info['scale_factor']
        dpi_scale = self.dpi_scale
        total_scale = scale * dpi_scale
        
        scaled_regions = {}
        for key, region in regions.items():
            if isinstance(region, dict):
                if 'x' in region and 'y' in region:
                    # Región con coordenadas
                    scaled_regions[key] = {
                        'x': int(region['x'] * total_scale),
                        'y': int(region['y'] * total_scale),
                        'width': int(region.get('width', 100) * total_scale),
                        'height': int(region.get('height', 70) * total_scale)
                    }
                elif key == 'bet_positions':
                    # Posiciones de apuesta
                    scaled_positions = {}
                    for num, pos in region.items():
                        scaled_positions[num] = {
                            'x': int(pos['x'] * total_scale),
                            'y': int(pos['y'] * total_scale)
                        }
                    scaled_regions[key] = scaled_positions
                else:
                    scaled_regions[key] = region
            else:
                scaled_regions[key] = region
                
        return scaled_regions
    
    def get_optimal_capture_size(self) -> Tuple[int, int]:
        """Retorna el tamaño óptimo de captura según la resolución"""
        if self.resolution_info['is_2k']:
            return (133, 93)  # 33% más grande para 2K
        elif self.resolution_info['is_4k']:
            return (200, 140)  # 100% más grande para 4K
        else:
            return (100, 70)   # Tamaño estándar para FullHD
    
    def get_optimal_countdown_size(self) -> Tuple[int, int]:
        """Retorna el tamaño óptimo para countdown (más grande)"""
        if self.resolution_info['is_2k']:
            return (160, 120)  # Más grande para countdown en 2K
        elif self.resolution_info['is_4k']:
            return (240, 180)  # Más grande para countdown en 4K
        else:
            return (120, 90)   # 20% más grande que winner para FullHD

# Instancia global de configuración
config = PlatformConfig()