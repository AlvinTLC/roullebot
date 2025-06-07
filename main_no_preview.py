import cv2
import time
import numpy as np
import pyautogui
from datetime import datetime
import sys
import os
import json

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vision.screen_capture import capture_screen
from vision.window_region import obtener_region_chrome
from vision.detector import detect_number_from_image
from config.platform_config import config
from tools.calibrator import Calibrator

def es_numero_valido_ruleta(numero_str):
    """Check if it is a valid roulette number (0-36)"""
    try:
        numero = int(numero_str)
        return 0 <= numero <= 36
    except:
        return False

def apostar_al_numero(numero='24', calibration_data=None):
    """Click on specified number to bet with validation"""
    try:
        if calibration_data and 'bet_positions' in calibration_data:
            if str(numero) in calibration_data['bet_positions']:
                pos = calibration_data['bet_positions'][str(numero)]
                if pos and 'x' in pos and 'y' in pos:
                    x, y = pos['x'], pos['y']
                    print(f"🎯 Using calibration for #{numero}: ({x}, {y})")
                else:
                    print(f"⚠️  Invalid calibration for #{numero}, using defaults")
                    x, y = 1645, 1415
            else:
                print(f"⚠️  No calibration for #{numero}, using defaults")
                x, y = 1645, 1415
        else:
            print(f"⚠️  No calibration data, using defaults")
            x, y = 1645, 1415
        
        # Desactivar fail-safe temporalmente
        original_failsafe = pyautogui.FAILSAFE
        pyautogui.FAILSAFE = False
        
        try:
            if 0 <= x <= 5000 and 0 <= y <= 3000:  # Validar coordenadas
                pyautogui.click(x, y)
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                print(f"💰 [{timestamp}] ✅ BET PLACED #{numero} at ({x}, {y})")
                return True
            else:
                print(f"⚠️ Coordenadas fuera de rango válido [0-5000, 0-3000]: ({x}, {y})")
                return False
        finally:
            pyautogui.FAILSAFE = original_failsafe
    except Exception as e:
        print(f"❌ Error placing bet: {e}")
        return False

class DetectorGanadoresRapido:
    def __init__(self, calibration_data=None):
        self.ultimo_ganador = None
        self.numero_candidato = None
        self.contador_confirmaciones = 0
        self.confirmaciones_requeridas = 3
        self.historial_ganadores = []
        self.inicio_sesion = time.time()
        self.total_apuestas = 0
        
        # Sistema de números aleatorios
        import random
        self.numeros_disponibles = list(range(0, 37))  # 0-36
        self.numero_objetivo = random.choice(self.numeros_disponibles)
        self.modo_aleatorio = True
        
        self.esperando_apuesta = False
        self.tiempo_espera_inicio = None
        self.calibration_data = calibration_data
        self.ultimo_countdown = None
        self.puede_apostar = True
        
        # Variables de rendimiento máximo
        self.ultimo_numero_detectado = ""
        self.ultimo_countdown_detectado = ""
        self.contador_detecciones_validas = 0
        self.tiempo_ultima_apuesta = 0
        self.contador_stats = 0
        
        print(f"🎰 MODO RÁPIDO SIN PREVIEW - Número objetivo ALEATORIO: {self.numero_objetivo}")
        print(f"🔄 Modo aleatorio activado")
        print(f"⚡ Máximo rendimiento - solo consola")

    def procesar_numero(self, numero):
        """Process number and confirm winners - FAST MODE"""
        if not numero or not es_numero_valido_ruleta(numero):
            return False

        # Solo mostrar si cambió (evitar spam)
        if numero != self.ultimo_numero_detectado:
            self.ultimo_numero_detectado = str(numero) if numero is not None else ""
            self.contador_detecciones_validas += 1

        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        if numero == self.numero_candidato:
            self.contador_confirmaciones += 1

            if self.contador_confirmaciones >= self.confirmaciones_requeridas:
                if numero != self.ultimo_ganador:
                    self.historial_ganadores.append((timestamp, numero))

                    if self.total_apuestas > 0:
                        if int(numero) == self.numero_objetivo:
                            print(f"🎉 [{timestamp}] YOU WIN!!! Winner: {numero} (Target: {self.numero_objetivo}) 🎉")
                        else:
                            print(f"💔 [{timestamp}] You lost. Winner: {numero} (Target: {self.numero_objetivo})")
                    else:
                        print(f"🏆 [{timestamp}] FIRST WINNER: {numero}")

                    self.ultimo_ganador = numero
                    
                    # Sistema de números aleatorios: elegir nuevo número
                    if self.modo_aleatorio:
                        import random
                        nuevo_numero = random.choice(self.numeros_disponibles)
                        self.numero_objetivo = nuevo_numero
                        print(f"🎲 NEW TARGET: {self.numero_objetivo}")
                    
                    self.puede_apostar = True
                    self.esperando_apuesta = True
                    self.tiempo_espera_inicio = time.time()
                    return True
        else:
            self.numero_candidato = numero
            self.contador_confirmaciones = 1

        return False

    def procesar_countdown(self, countdown_str):
        """Process countdown - FAST MODE"""
        if not countdown_str or not countdown_str.isdigit():
            return False
        
        countdown = int(countdown_str)
        
        # Solo mostrar si cambió
        if countdown_str != self.ultimo_countdown_detectado:
            self.ultimo_countdown_detectado = str(countdown_str) if countdown_str is not None else ""
        
        # Solo mostrar countdown crítico
        if self.ultimo_countdown != countdown and countdown <= 12:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"⏰ [{timestamp}] Countdown: {countdown}")
            self.ultimo_countdown = countdown
        
        return countdown

    def verificar_momento_apuesta(self, countdown=None):
        """Check betting moment - AGGRESSIVE FAST MODE"""
        if not self.puede_apostar:
            return False
        
        tiempo_actual = time.time()
        if tiempo_actual - self.tiempo_ultima_apuesta < 0.8:  # Reducido a 0.8s
            return False
            
        apuesta_realizada = False
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # MODO OPTIMIZADO: Apostar en countdown 8 o 9
        if countdown is not None:
            if countdown in [9, 8]:  # Solo en 8 o 9 para mejor timing
                print(f"🎯 [{timestamp}] BETTING NOW! (Countdown = {countdown})")
                apuesta_realizada = True
                # Marcar inmediatamente para evitar apuestas múltiples
                self.puede_apostar = False
        else:
            # Modo fallback más rápido
            if self.esperando_apuesta and self.tiempo_espera_inicio:
                tiempo_transcurrido = tiempo_actual - self.tiempo_espera_inicio
                if tiempo_transcurrido >= 2.0:  # Reducido a 2 segundos
                    print(f"🎯 [{timestamp}] BETTING NOW! (2s completed)")
                    apuesta_realizada = True

        if apuesta_realizada:
            if apostar_al_numero(self.numero_objetivo, self.calibration_data):
                self.total_apuestas += 1
                self.tiempo_ultima_apuesta = tiempo_actual
                print(f"✅ BET #{self.total_apuestas} → Target: {self.numero_objetivo} | Next: RANDOM")
                return True

        return False
    
    def mostrar_stats_rapidas(self, total_scans):
        """Stats rápidas cada cierto tiempo"""
        self.contador_stats += 1
        
        # Stats más frecuentes al inicio, luego menos frecuentes
        if total_scans < 1000 and self.contador_stats % 500 == 0:  # Cada 500 scans los primeros 1000
            duracion = time.time() - self.inicio_sesion
            fps = total_scans / duracion if duracion > 0 else 0
            
            print(f"\n📊 STARTING STATS [{datetime.now().strftime('%H:%M:%S')}]")
            print(f"   Scans: {total_scans} | FPS: {fps:.1f} | Bets: {self.total_apuestas}")
            print(f"   Target: {self.numero_objetivo} | Detections: {self.contador_detecciones_validas}")
            
        elif self.contador_stats % 5000 == 0:  # Cada 5000 scans después
            duracion = time.time() - self.inicio_sesion
            fps = total_scans / duracion if duracion > 0 else 0
            
            print(f"\n📊 QUICK STATS [{datetime.now().strftime('%H:%M:%S')}]")
            print(f"   Scans: {total_scans} | FPS: {fps:.1f} | Bets: {self.total_apuestas}")
            print(f"   Winners: {len(self.historial_ganadores)} | Target: {self.numero_objetivo}")
            print(f"   Valid detections: {self.contador_detecciones_validas}")
            
            if len(self.historial_ganadores) > 0:
                ultimo_ganador = self.historial_ganadores[-1][1]
                print(f"   Last winner: {ultimo_ganador}")

    def cambiar_numero_objetivo(self, nuevo_numero):
        """Cambiar número objetivo"""
        if es_numero_valido_ruleta(str(nuevo_numero)):
            self.numero_objetivo = int(nuevo_numero)
            self.modo_aleatorio = False
            print(f"🎯 TARGET CHANGED to: {self.numero_objetivo} (MANUAL)")
            return True
        return False
    
    def activar_modo_aleatorio(self):
        """Activar modo aleatorio"""
        import random
        self.modo_aleatorio = True
        self.numero_objetivo = random.choice(self.numeros_disponibles)
        print(f"🔄 RANDOM MODE ON - New target: {self.numero_objetivo}")

def main_fast():
    print(f"⚡ RouletteBot - MODO ULTRA RÁPIDO (SIN PREVIEW)")
    print(f"🖥️  Sistema: {config.system.upper()}")
    print(f"📺 {config.get_resolution_info()}")
    print("=" * 60)
    
    # Optimizaciones máximas
    if config.is_windows:
        print("🔧 Aplicando optimizaciones MÁXIMAS para Windows...")
        config.optimize_for_windows()
    
    perf_settings = config.get_performance_settings()
    # Overrides para máximo rendimiento
    perf_settings['capture_interval'] = 0.015  # 66 FPS
    perf_settings['skip_frames'] = 1           # No saltear frames
    
    print(f"🚀 Configuración ULTRA RÁPIDA:")
    print(f"   - Captura: {1/perf_settings['capture_interval']:.0f} FPS")
    print(f"   - Preview: DESHABILITADO")
    print(f"   - OCR threads: {perf_settings['ocr_threads']}")
    print("=" * 60)
    
    # Cargar calibración
    print("\n📋 CARGANDO CALIBRACIÓN...")
    print("-" * 50)
    calibrator = Calibrator()
    
    # Verificar que se cargó correctamente
    if not calibrator.calibration_data:
        print("❌ No se pudo cargar ninguna calibración")
        return
        
    if not calibrator.calibration_data.get('winner_region'):
        print("❌ No hay región ganadora calibrada")
        print("📋 Ejecuta primero: python roullebot.py --mode calibrate")
        print(f"   Datos disponibles: {list(calibrator.calibration_data.keys())}")
        return
    
    # Usar regiones calibradas
    region_numero = calibrator.calibration_data['winner_region']
    region_countdown = calibrator.calibration_data.get('countdown_region')
    
    try:
        # Normalizar Chrome para consistencia con la calibración  
        region_chrome = obtener_region_chrome(normalize=True)
        print(f"✅ Chrome detectado y normalizado: {region_chrome}")
        
        # Test inicial de captura
        print("🧪 Testing initial capture...")
        test_capture = capture_screen(region_numero)
        if test_capture is not None:
            print(f"✅ Initial capture successful: {np.array(test_capture).shape}")
        else:
            print("❌ Initial capture failed - no image returned")
            
    except Exception as e:
        print(f"❌ Error detectando Chrome: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Mostrar información completa de calibración
    print(f"📋 FAST MODE CALIBRATION:")
    print(f"🎯 Winner: x={region_numero['x']}, y={region_numero['y']}, size={region_numero['width']}x{region_numero['height']}")
    
    if region_countdown:
        print(f"⏰ Countdown: x={region_countdown['x']}, y={region_countdown['y']}, size={region_countdown['width']}x{region_countdown['height']}")
    
    # Mostrar posiciones de apuesta
    bet_positions = calibrator.calibration_data.get('bet_positions', {})
    if bet_positions:
        print(f"💰 Bet positions:")
        for numero, pos in bet_positions.items():
            if pos:
                print(f"   #{numero}: ({pos['x']}, {pos['y']})")
    else:
        print(f"⚠️  No bet positions - using defaults")
    
    if region_countdown:
        print(f"💰 ULTRA FAST SYSTEM: Bet at countdown 8 or 9")
    else:
        print("⚠️ No countdown - using 2.5s delay mode")
        print(f"💰 ULTRA FAST SYSTEM: Bet 2.5s after winner")
    
    print(f"🚀 MAX SPEED: ~66 FPS detection")
    print(f"⏱️  Session started: {datetime.now().strftime('%H:%M:%S')}")
    print(f"💡 Ctrl+C to stop | R=Random | 0-9=Set target")
    print("=" * 60)

    detector = DetectorGanadoresRapido(calibrator.calibration_data)
    contador_scans = 0

    # Configuración segura de PyAutoGUI para modo fast
    pyautogui.FAILSAFE = False  # Desactivado para máximo rendimiento
    pyautogui.PAUSE = 0.01      # Mínimo delay

    # Variables de optimización máxima
    skip_frames = perf_settings['skip_frames']
    capture_interval = perf_settings['capture_interval']
    
    last_capture_time = 0
    last_input_check = 0

    try:
        print("🟢 STARTING ULTRA FAST MODE...")
        
        # Debug inicial para verificar que el bucle funciona
        debug_mode = True
        debug_count = 0
        
        while True:
            current_time = time.time()
            
            # Captura ultra rápida
            if (current_time - last_capture_time) >= capture_interval:
                
                if contador_scans % skip_frames == 0:
                    
                    try:
                        # Capturar región del número ganador
                        screenshot = capture_screen(region_numero)
                        img_ganador = np.array(screenshot)
                        
                        numero_ganador = ""
                        countdown_actual = None

                        if img_ganador is not None and img_ganador.size > 0:
                            numero_ganador = detect_number_from_image(img_ganador).strip()
                            if numero_ganador:
                                detector.procesar_numero(numero_ganador)
                            
                            # Debug inicial
                            if debug_mode and debug_count < 10:
                                debug_count += 1
                                print(f"🔍 Debug #{debug_count}: Winner region captured, size={img_ganador.shape}, detected='{numero_ganador}'")

                        # Capturar countdown menos frecuente
                        if region_countdown and contador_scans % 3 == 0:
                            try:
                                screenshot_countdown = capture_screen(region_countdown)
                                img_countdown = np.array(screenshot_countdown)
                                if img_countdown is not None and img_countdown.size > 0:
                                    countdown_str = detect_number_from_image(img_countdown).strip()
                                    if countdown_str:
                                        countdown_actual = detector.procesar_countdown(countdown_str)
                            except Exception as e:
                                if debug_mode and debug_count < 5:
                                    print(f"⚠️ Countdown error: {e}")
                    
                    except Exception as e:
                        if debug_mode and debug_count < 5:
                            print(f"❌ Capture error: {e}")
                            import traceback
                            traceback.print_exc()
                        
                        # Desactivar debug después de unos intentos
                        if debug_count >= 10:
                            debug_mode = False
                            print("🔇 Debug mode OFF - switching to silent mode")
                
                last_capture_time = current_time

            # Verificar apuesta
            if 'countdown_actual' in locals() and countdown_actual is not None:
                detector.verificar_momento_apuesta(countdown_actual)
            else:
                detector.verificar_momento_apuesta()
            
            # Stats rápidas
            detector.mostrar_stats_rapidas(contador_scans)
            
            contador_scans += 1

            # Verificar input menos frecuentemente para no impactar rendimiento
            if (current_time - last_input_check) >= 0.1:  # Cada 100ms
                
                # Verificar teclas sin bloquear (Windows)
                if config.is_windows:
                    try:
                        import msvcrt
                        if msvcrt.kbhit():
                            key = msvcrt.getch().decode('utf-8').lower()
                            if key == 'r':
                                detector.activar_modo_aleatorio()
                            elif key.isdigit():
                                detector.cambiar_numero_objetivo(int(key))
                    except ImportError:
                        pass  # msvcrt no disponible en este sistema
                
                last_input_check = current_time

            # Delay mínimo
            time.sleep(0.0005)  # 0.5ms

    except KeyboardInterrupt:
        print(f"\n🛑 ULTRA FAST MODE STOPPED")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Mostrar resumen final
        duracion = time.time() - detector.inicio_sesion
        print(f"\n" + "="*60)
        print(f"📊 ULTRA FAST SESSION SUMMARY")
        print(f"="*60)
        print(f"⏱️ Duration: {duracion/60:.1f} minutes")
        print(f"🔍 Total scans: {contador_scans}")
        print(f"⚡ Average FPS: {contador_scans/duracion:.1f}")
        print(f"🏆 Winners detected: {len(detector.historial_ganadores)}")
        print(f"💰 Total bets: {detector.total_apuestas}")
        print(f"🎯 Final target: {detector.numero_objetivo}")
        print(f"✅ Valid detections: {detector.contador_detecciones_validas}")

if __name__ == "__main__":
    main_fast()