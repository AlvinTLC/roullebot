import platform
import subprocess
import re
from typing import Optional, Tuple, List
import time

class WindowManager:
    """Manejo multiplataforma de ventanas"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.is_windows = self.system == 'windows'
        self.is_mac = self.system == 'darwin'
        self.is_linux = self.system == 'linux'
        
    def find_chrome_window(self) -> Optional[dict]:
        """Encuentra la ventana de Chrome activa"""
        if self.is_windows:
            return self._find_chrome_windows_win()
        elif self.is_mac:
            return self._find_chrome_window_mac()
        elif self.is_linux:
            return self._find_chrome_window_linux()
        return None
    
    def _find_chrome_windows_win(self) -> Optional[dict]:
        """Encuentra ventana de Chrome en Windows"""
        try:
            import pygetwindow as gw
            windows = gw.getWindowsWithTitle('Chrome')
            if windows:
                win = windows[0]
                return {
                    'title': win.title,
                    'x': win.left,
                    'y': win.top,
                    'width': win.width,
                    'height': win.height
                }
        except ImportError:
            print("pygetwindow no está instalado. Instala con: pip install pygetwindow")
        except Exception as e:
            print(f"Error encontrando ventana Chrome en Windows: {e}")
        return None
    
    def _find_chrome_window_mac(self) -> Optional[dict]:
        """Encuentra ventana de Chrome en macOS usando AppleScript"""
        try:
            # AppleScript para obtener información de la ventana de Chrome
            script = '''
            tell application "System Events"
                tell process "Google Chrome"
                    if exists then
                        try
                            set frontWindow to front window
                            set windowTitle to name of frontWindow
                            set windowPosition to position of frontWindow
                            set windowSize to size of frontWindow
                            return {windowTitle, item 1 of windowPosition, item 2 of windowPosition, item 1 of windowSize, item 2 of windowSize}
                        on error
                            return ""
                        end try
                    end if
                end tell
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                # Parsear resultado
                parts = result.stdout.strip().split(', ')
                if len(parts) >= 5:
                    return {
                        'title': parts[0],
                        'x': int(parts[1]),
                        'y': int(parts[2]),
                        'width': int(parts[3]),
                        'height': int(parts[4])
                    }
        except Exception as e:
            print(f"Error encontrando ventana Chrome en macOS: {e}")
        return None
    
    def _find_chrome_window_linux(self) -> Optional[dict]:
        """Encuentra ventana de Chrome en Linux usando xdotool"""
        try:
            # Buscar ventanas de Chrome
            result = subprocess.run(['xdotool', 'search', '--name', 'Chrome'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                window_ids = result.stdout.strip().split('\n')
                if window_ids:
                    window_id = window_ids[0]  # Usar la primera ventana encontrada
                    
                    # Obtener geometría
                    geo_result = subprocess.run(['xdotool', 'getwindowgeometry', window_id],
                                              capture_output=True, text=True)
                    
                    if geo_result.returncode == 0:
                        # Parsear geometría
                        lines = geo_result.stdout.strip().split('\n')
                        position_match = re.search(r'Position: (\d+),(\d+)', lines[1])
                        size_match = re.search(r'Geometry: (\d+)x(\d+)', lines[2])
                        
                        if position_match and size_match:
                            return {
                                'title': 'Google Chrome',
                                'x': int(position_match.group(1)),
                                'y': int(position_match.group(2)),
                                'width': int(size_match.group(1)),
                                'height': int(size_match.group(2))
                            }
        except FileNotFoundError:
            print("xdotool no está instalado. Instala con: sudo apt-get install xdotool")
        except Exception as e:
            print(f"Error encontrando ventana Chrome en Linux: {e}")
        return None
    
    def get_monitor_info(self) -> List[dict]:
        """Obtiene información de los monitores disponibles"""
        monitors = []
        
        if self.is_windows:
            try:
                from screeninfo import get_monitors
                for m in get_monitors():
                    monitors.append({
                        'name': m.name,
                        'x': m.x,
                        'y': m.y,
                        'width': m.width,
                        'height': m.height,
                        'is_primary': m.is_primary
                    })
            except ImportError:
                print("screeninfo no está instalado. Instala con: pip install screeninfo")
        
        elif self.is_mac:
            try:
                # Usar system_profiler para obtener info de displays
                result = subprocess.run(['system_profiler', 'SPDisplaysDataType', '-json'],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    import json
                    data = json.loads(result.stdout)
                    # Parsear la información (estructura compleja, simplificado aquí)
                    monitors.append({
                        'name': 'Main Display',
                        'x': 0,
                        'y': 0,
                        'width': 1920,  # Valores por defecto
                        'height': 1080,
                        'is_primary': True
                    })
            except Exception as e:
                print(f"Error obteniendo info de monitores en macOS: {e}")
        
        elif self.is_linux:
            try:
                # Usar xrandr para obtener información
                result = subprocess.run(['xrandr'], capture_output=True, text=True)
                if result.returncode == 0:
                    # Parsear salida de xrandr
                    for line in result.stdout.split('\n'):
                        if ' connected' in line:
                            parts = line.split()
                            name = parts[0]
                            # Buscar resolución
                            for part in parts:
                                if 'x' in part and '+' in part:
                                    res_pos = part.split('+')
                                    res = res_pos[0].split('x')
                                    monitors.append({
                                        'name': name,
                                        'x': int(res_pos[1]),
                                        'y': int(res_pos[2]) if len(res_pos) > 2 else 0,
                                        'width': int(res[0]),
                                        'height': int(res[1]),
                                        'is_primary': 'primary' in line
                                    })
                                    break
            except Exception as e:
                print(f"Error obteniendo info de monitores en Linux: {e}")
        
        return monitors if monitors else [{'name': 'Default', 'x': 0, 'y': 0, 
                                          'width': 1920, 'height': 1080, 'is_primary': True}]
    
    def activate_window(self, window_info: dict) -> bool:
        """Activa/enfoca una ventana"""
        try:
            if self.is_windows:
                import pygetwindow as gw
                windows = gw.getWindowsWithTitle(window_info.get('title', ''))
                if windows:
                    windows[0].activate()
                    return True
                    
            elif self.is_mac:
                script = '''
                tell application "Google Chrome"
                    activate
                end tell
                '''
                subprocess.run(['osascript', '-e', script])
                return True
                
            elif self.is_linux:
                # Usar xdotool para activar ventana
                subprocess.run(['xdotool', 'search', '--name', 'Chrome', 
                              'windowactivate', '--sync'])
                return True
                
        except Exception as e:
            print(f"Error activando ventana: {e}")
        
        return False
    
    def normalize_chrome_window(self, target_width=1200, target_height=800, target_x=100, target_y=100) -> dict:
        """Normaliza la ventana de Chrome a un tamaño y posición específicos"""
        print(f"🔧 Normalizando ventana de Chrome...")
        print(f"   Tamaño objetivo: {target_width}x{target_height}")
        print(f"   Posición objetivo: ({target_x}, {target_y})")
        
        try:
            if self.is_windows:
                return self._normalize_chrome_windows(target_width, target_height, target_x, target_y)
            elif self.is_mac:
                return self._normalize_chrome_mac(target_width, target_height, target_x, target_y)
            elif self.is_linux:
                return self._normalize_chrome_linux(target_width, target_height, target_x, target_y)
        except Exception as e:
            print(f"❌ Error normalizando ventana: {e}")
            
        return None
    
    def _normalize_chrome_windows(self, width, height, x, y) -> dict:
        """Normaliza Chrome en Windows"""
        try:
            import pygetwindow as gw
            windows = gw.getWindowsWithTitle('Chrome')
            if windows:
                win = windows[0]
                
                # Activar y redimensionar
                win.activate()
                time.sleep(0.5)
                
                # Restaurar si está maximizada
                if win.isMaximized:
                    win.restore()
                    time.sleep(0.3)
                
                # Redimensionar y mover
                win.resizeTo(width, height)
                time.sleep(0.2)
                win.moveTo(x, y)
                time.sleep(0.3)
                
                print(f"✅ Chrome normalizado en Windows")
                return {
                    'title': win.title,
                    'x': win.left,
                    'y': win.top,
                    'width': win.width,
                    'height': win.height
                }
        except Exception as e:
            print(f"❌ Error normalizando Chrome en Windows: {e}")
        return None
    
    def _normalize_chrome_mac(self, width, height, x, y) -> dict:
        """Normaliza Chrome en macOS"""
        try:
            # Script AppleScript para redimensionar y mover Chrome
            script = f'''
            tell application "Google Chrome"
                activate
            end tell
            
            delay 0.5
            
            tell application "System Events"
                tell process "Google Chrome"
                    set frontWindow to front window
                    set position of frontWindow to {{{x}, {y}}}
                    set size of frontWindow to {{{width}, {height}}}
                end tell
            end tell
            
            delay 0.5
            
            tell application "System Events"
                tell process "Google Chrome"
                    set frontWindow to front window
                    set windowPosition to position of frontWindow
                    set windowSize to size of frontWindow
                    return {{item 1 of windowPosition, item 2 of windowPosition, item 1 of windowSize, item 2 of windowSize}}
                end tell
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split(', ')
                if len(parts) >= 4:
                    print(f"✅ Chrome normalizado en macOS")
                    return {
                        'title': 'Google Chrome',
                        'x': int(parts[0]),
                        'y': int(parts[1]),
                        'width': int(parts[2]),
                        'height': int(parts[3])
                    }
        except Exception as e:
            print(f"❌ Error normalizando Chrome en macOS: {e}")
        return None
    
    def _normalize_chrome_linux(self, width, height, x, y) -> dict:
        """Normaliza Chrome en Linux"""
        try:
            # Buscar ventana de Chrome
            result = subprocess.run(['xdotool', 'search', '--name', 'Chrome'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                window_ids = result.stdout.strip().split('\n')
                if window_ids:
                    window_id = window_ids[0]
                    
                    # Activar ventana
                    subprocess.run(['xdotool', 'windowactivate', window_id])
                    time.sleep(0.5)
                    
                    # Quitar maximización si existe
                    subprocess.run(['xdotool', 'windowstate', '--remove', 'MAXIMIZED_HORZ', window_id])
                    subprocess.run(['xdotool', 'windowstate', '--remove', 'MAXIMIZED_VERT', window_id])
                    time.sleep(0.3)
                    
                    # Redimensionar y mover
                    subprocess.run(['xdotool', 'windowsize', window_id, str(width), str(height)])
                    time.sleep(0.2)
                    subprocess.run(['xdotool', 'windowmove', window_id, str(x), str(y)])
                    time.sleep(0.3)
                    
                    # Verificar nueva geometría
                    geo_result = subprocess.run(['xdotool', 'getwindowgeometry', window_id],
                                              capture_output=True, text=True)
                    
                    if geo_result.returncode == 0:
                        lines = geo_result.stdout.strip().split('\n')
                        position_match = re.search(r'Position: (\d+),(\d+)', lines[1])
                        size_match = re.search(r'Geometry: (\d+)x(\d+)', lines[2])
                        
                        if position_match and size_match:
                            print(f"✅ Chrome normalizado en Linux")
                            return {
                                'title': 'Google Chrome',
                                'x': int(position_match.group(1)),
                                'y': int(position_match.group(2)),
                                'width': int(size_match.group(1)),
                                'height': int(size_match.group(2))
                            }
        except Exception as e:
            print(f"❌ Error normalizando Chrome en Linux: {e}")
        return None
    
    def get_recommended_chrome_size(self) -> Tuple[int, int, int, int]:
        """Obtiene tamaño y posición recomendados para Chrome según la resolución"""
        monitors = self.get_monitor_info()
        if monitors:
            primary = next((m for m in monitors if m.get('is_primary', False)), monitors[0])
            monitor_width = primary['width']
            monitor_height = primary['height']
            
            # Calcular tamaño óptimo (75% del monitor)
            target_width = int(monitor_width * 0.75)
            target_height = int(monitor_height * 0.75)
            
            # Posición centrada
            target_x = (monitor_width - target_width) // 4
            target_y = (monitor_height - target_height) // 4
            
            # Ajustes mínimos y máximos
            target_width = max(1000, min(target_width, 1600))
            target_height = max(700, min(target_height, 1200))
            target_x = max(50, target_x)
            target_y = max(50, target_y)
            
            return target_width, target_height, target_x, target_y
        
        # Valores por defecto
        return 1200, 800, 100, 100

# Instancia global
window_manager = WindowManager()