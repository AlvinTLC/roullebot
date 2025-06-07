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
                    print(f"🎯 Usando calibración para #{numero}: ({x}, {y})")
                else:
                    print(f"⚠️  Calibración inválida para #{numero}, usando valores por defecto")
                    x, y = 1645, 1415  # Coordenadas por defecto para 24
            else:
                print(f"⚠️  No hay calibración para #{numero}, usando valores por defecto")
                x, y = 1645, 1415  # Coordenadas por defecto para 24
        else:
            print(f"⚠️  No hay datos de calibración, usando valores por defecto")
            x, y = 1645, 1415  # Coordenadas por defecto para 24
        
        # Mostrar dónde vamos a hacer click
        print(f"🖱️  Haciendo click en: ({x}, {y})")
        
        # Desactivar fail-safe temporalmente para apuestas
        original_failsafe = pyautogui.FAILSAFE
        pyautogui.FAILSAFE = False
        
        try:
            # Opcional: mover mouse primero para debug visual (con validación)
            if 0 <= x <= 5000 and 0 <= y <= 3000:  # Validar coordenadas razonables
                pyautogui.moveTo(x, y)
                time.sleep(0.1)  # Breve pausa para ver el movimiento
                pyautogui.click(x, y)
            else:
                print(f"⚠️ Coordenadas fuera de rango válido [0-5000, 0-3000]: ({x}, {y})")
                return False
        finally:
            # Restaurar fail-safe
            pyautogui.FAILSAFE = original_failsafe
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"💰 [{timestamp}] ✅ BET PLACED on number {numero} at ({x}, {y})")
        return True
    except Exception as e:
        print(f"❌ Error placing bet: {e}")
        import traceback
        traceback.print_exc()
        return False

class DetectorGanadoresSimple:
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
        
        # Variables de debug y rendimiento
        self.debug_detecciones = True
        self.ultimo_numero_detectado = ""
        self.ultimo_countdown_detectado = ""
        self.contador_detecciones_validas = 0
        self.tiempo_ultima_apuesta = 0
        
        print(f"🎰 Iniciando con número objetivo ALEATORIO: {self.numero_objetivo}")
        print(f"🔄 Modo aleatorio activado - cambiar de número cada ronda")
        print(f"💡 Comandos en tiempo real:")
        print(f"   - Presiona F1-F9 para fijar números 1-9")
        print(f"   - Presiona F10 para volver a modo aleatorio")
        print(f"   - Presiona F11 para cambiar número aleatorio manualmente")

    def procesar_numero(self, numero):
        """Process number and confirm winners with debug info"""
        if not numero or not es_numero_valido_ruleta(numero):
            return False

        # Debug: mostrar detección solo si cambió
        if numero != self.ultimo_numero_detectado:
            if self.debug_detecciones:
                print(f"🔍 Winner detectado (región WINNER): {numero}")
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
                            print(f"🎉 [{timestamp}] YOU WIN!!! Winning number: {numero} 🎉")
                        else:
                            print(f"💔 [{timestamp}] You lost. Winner: {numero} (we bet on {self.numero_objetivo})")
                    else:
                        print(f"🏆 [{timestamp}] FIRST WINNER DETECTED: {numero}")

                    self.ultimo_ganador = numero
                    
                    # Sistema de números aleatorios: elegir nuevo número
                    if self.modo_aleatorio:
                        import random
                        nuevo_numero = random.choice(self.numeros_disponibles)
                        self.numero_objetivo = nuevo_numero
                        print(f"🎲 Nuevo número objetivo aleatorio: {self.numero_objetivo}")
                    
                    self.puede_apostar = True  # Permitir apuestas después de un ganador
                    # Para modo fallback (sin countdown)
                    self.esperando_apuesta = True
                    self.tiempo_espera_inicio = time.time()
                    return True
        else:
            self.numero_candidato = numero
            self.contador_confirmaciones = 1

        return False

    def procesar_countdown(self, countdown_str):
        """Process countdown and determine when to bet with debug"""
        if not countdown_str or not countdown_str.isdigit():
            return False
        
        countdown = int(countdown_str)
        
        # VALIDAR: countdown debe estar en rango típico de 0-30
        if countdown < 0 or countdown > 30:
            if self.debug_detecciones:
                print(f"⚠️ Countdown fuera de rango válido: {countdown} (ignorando)")
            return False
        
        # Debug: mostrar countdown solo si cambió
        if countdown_str != self.ultimo_countdown_detectado:
            if self.debug_detecciones and countdown <= 20:
                print(f"⏰ Countdown detectado (región COUNTDOWN): {countdown}")
            self.ultimo_countdown_detectado = str(countdown_str) if countdown_str is not None else ""
        
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # Solo mostrar cambios significativos del countdown
        if self.ultimo_countdown != countdown:
            if countdown <= 15:  # Solo mostrar cuando se acerque el momento de apostar
                print(f"⏰ [{timestamp}] Countdown (validated): {countdown}")
            self.ultimo_countdown = countdown
        
        return countdown

    def verificar_momento_apuesta(self, countdown=None):
        """Check if it's time to bet - IMPROVED CONSISTENCY"""
        if not self.puede_apostar:
            return False
        
        tiempo_actual = time.time()
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # Verificar que no hayamos apostado muy recientemente
        if tiempo_actual - self.tiempo_ultima_apuesta < 0.8:  # Reducido a 0.8s
            return False
            
        apuesta_realizada = False
        
        # MODO MEJORADO: Apostar en countdown 8 o 9
        if countdown is not None and countdown > 0:
            # Apostar específicamente en countdown 8 o 9
            if countdown in [9, 8]:  # Solo en 8 o 9
                print(f"🎯 [{timestamp}] BETTING NOW! (Countdown = {countdown})")
                apuesta_realizada = True
                # Marcar inmediatamente para evitar apuestas múltiples
                self.puede_apostar = False
                
        elif self.esperando_apuesta and self.tiempo_espera_inicio:
            # Modo fallback más agresivo
            tiempo_transcurrido = tiempo_actual - self.tiempo_espera_inicio
            if tiempo_transcurrido >= 2.5:  # Reducido a 2.5 segundos
                print(f"🎯 [{timestamp}] BETTING NOW! (2.5s fallback)")
                apuesta_realizada = True
                self.puede_apostar = False

        if apuesta_realizada:
            # Intentar apuesta con retry
            success = False
            for intento in range(2):  # Hasta 2 intentos
                if apostar_al_numero(self.numero_objetivo, self.calibration_data):
                    success = True
                    break
                else:
                    time.sleep(0.1)  # Pequeña pausa entre intentos
                    
            if success:
                self.total_apuestas += 1
                self.tiempo_ultima_apuesta = tiempo_actual
                timestamp_apuesta = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                print(f"✅ [{timestamp_apuesta}] BET #{self.total_apuestas} CONFIRMED → {self.numero_objetivo}")
                print(f"🎲 Next target will be: RANDOM (after next winner)")

                # En modo agresivo, seguir apostando hasta que termine la ronda
                # self.puede_apostar = False  # Comentado para apuestas continuas
                return True

        return False
    
    def cambiar_numero_objetivo(self, nuevo_numero, manual=False):
        """Cambiar número objetivo en tiempo real"""
        if es_numero_valido_ruleta(str(nuevo_numero)):
            self.numero_objetivo = int(nuevo_numero)
            if manual:
                self.modo_aleatorio = False
                print(f"🎯 Número objetivo cambiado MANUALMENTE a: {self.numero_objetivo}")
            else:
                print(f"🎯 Número objetivo cambiado a: {self.numero_objetivo}")
            return True
        return False
    
    def activar_modo_aleatorio(self):
        """Activar modo aleatorio"""
        import random
        self.modo_aleatorio = True
        self.numero_objetivo = random.choice(self.numeros_disponibles)
        print(f"🔄 Modo aleatorio ACTIVADO - Nuevo número: {self.numero_objetivo}")
        
    def nuevo_numero_aleatorio(self):
        """Generar nuevo número aleatorio manualmente"""
        import random
        self.numero_objetivo = random.choice(self.numeros_disponibles)
        print(f"🎲 Nuevo número aleatorio: {self.numero_objetivo}")

    def mostrar_resumen(self, total_scans):
        """Show session summary"""
        duracion = time.time() - self.inicio_sesion
        print(f"\n" + "="*70)
        print(f"📊 SESSION SUMMARY - SIMPLIFIED AUTOMATIC BETTOR")
        print(f"="*70)
        print(f"⏱️ Duration: {duracion/60:.1f} minutes")
        print(f"🔍 Total scans: {total_scans}")
        print(f"⚡ Average FPS: {total_scans/duracion:.1f}")
        print(f"🏆 Winners detected: {len(self.historial_ganadores)}")
        print(f"💰 Total bets placed: {self.total_apuestas}")
        print(f"🎯 Target number: {self.numero_objetivo}")

        if self.historial_ganadores and self.total_apuestas > 0:
            print(f"\n🎯 BET RESULTS:")
            ganadas = 0
            perdidas = 0

            for i, (timestamp, numero) in enumerate(self.historial_ganadores):
                if i == 0:
                    print(f"   🎮 [{timestamp}] First winner (no bet): {numero}")
                else:
                    if int(numero) == self.numero_objetivo:
                        print(f"   ✅ [{timestamp}] YOU WIN: {numero}")
                        ganadas += 1
                    else:
                        print(f"   ❌ [{timestamp}] You lost: {numero}")
                        perdidas += 1

            if ganadas + perdidas > 0:
                print(f"\n📈 FINAL STATISTICS:")
                print(f"   🏆 Bets won: {ganadas}")
                print(f"   💔 Bets lost: {perdidas}")
                tasa_exito = (ganadas / (ganadas + perdidas)) * 100
                print(f"   📊 Success rate: {tasa_exito:.1f}%")
                print(f"   💵 Theoretical balance: {ganadas * 35 - perdidas} chips (35:1 payout)")
        else:
            print(f"\n⚠️ No bets were completed in this session")

def main():
    print(f"🎰 RouletteBot - Sistema Automático de Apuestas")
    print(f"🖥️  Sistema: {config.system.upper()}")
    print(f"📺 {config.get_resolution_info()}")
    print("-" * 70)
    
    # Optimizaciones específicas para Windows
    if config.is_windows:
        print("🔧 Aplicando optimizaciones para Windows...")
        config.optimize_for_windows()
    
    # Obtener configuraciones de rendimiento
    perf_settings = config.get_performance_settings()
    print(f"⚡ Configuración de rendimiento cargada:")
    print(f"   - Captura: cada {perf_settings['capture_interval']*1000:.0f}ms ({int(1/perf_settings['capture_interval'])} FPS)")
    print(f"   - Preview: cada {perf_settings['preview_interval']*1000:.0f}ms ({int(1/perf_settings['preview_interval'])} FPS)")
    print(f"   - OpenCV threads: {perf_settings['opencv_threads']}")
    print(f"   - Saltear frames: 1 de cada {perf_settings['skip_frames']}")
    print(f"   - Prioridad alta: {'SÍ' if perf_settings['priority_boost'] else 'NO'}")
    print("-" * 70)
    
    # Cargar calibración
    print("\n📋 CARGANDO CALIBRACIÓN...")
    print("-" * 50)
    
    # DEBUG: Mostrar factor de escala
    print(f"🔍 DEBUG Escalado:")
    print(f"   Sistema: {config.system}")
    print(f"   Es Windows: {config.is_windows}")
    print(f"   Es 2K: {config.resolution_info['is_2k']}")
    print(f"   Factor de escala: {config.resolution_info.get('scale_factor', 1.0)}")
    print(f"   DPI Scale: {config.dpi_scale}")
    
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
    
    # Validar calibración
    print("🔍 Validando calibración...")
    if not calibrator.validate_calibration():
        print("⚠️ Hay problemas con la calibración. Considera recalibrar.")
        respuesta = input("¿Continuar de todas formas? (s/n): ").strip().lower()
        if respuesta != 's':
            return
    
    try:
        # Normalizar Chrome para consistencia con la calibración
        region_chrome = obtener_region_chrome(normalize=True)
        print(f"✅ Chrome detectado y normalizado: {region_chrome}")
    except Exception as e:
        print(f"❌ Error detectando Chrome: {e}")
        return
    
    # Usar regiones calibradas
    region_numero = calibrator.calibration_data['winner_region']
    region_countdown = calibrator.calibration_data.get('countdown_region')
    
    # Mostrar información completa de calibración
    print(f"📋 CALIBRACIÓN CARGADA:")
    print(f"🎯 Winner region: x={region_numero['x']}, y={region_numero['y']}, size={region_numero['width']}x{region_numero['height']}")
    
    if region_countdown:
        print(f"⏰ Countdown region: x={region_countdown['x']}, y={region_countdown['y']}, size={region_countdown['width']}x{region_countdown['height']}")
    
    # Mostrar posiciones de apuesta disponibles
    bet_positions = calibrator.calibration_data.get('bet_positions', {})
    if bet_positions:
        print(f"💰 Posiciones de apuesta calibradas:")
        for numero, pos in bet_positions.items():
            if pos:
                print(f"   #{numero}: ({pos['x']}, {pos['y']})")
    else:
        print(f"⚠️  No hay posiciones de apuesta calibradas - usando valores por defecto")
    
    # Mostrar regiones adicionales si existen
    if calibrator.calibration_data.get('balance_region'):
        balance_region = calibrator.calibration_data['balance_region']
        print(f"💵 Balance region: x={balance_region['x']}, y={balance_region['y']}")
        
    if calibrator.calibration_data.get('total_bet_region'):
        total_bet_region = calibrator.calibration_data['total_bet_region']
        print(f"💸 Total bet region: x={total_bet_region['x']}, y={total_bet_region['y']}")
    
    print("-" * 70)
    
    if region_countdown:
        print(f"💰 SISTEMA AUTOMÁTICO:")
        print(f"   1️⃣ Detectar número ganador")
        print(f"   2️⃣ Monitorear countdown")
        print(f"   3️⃣ Apostar cuando countdown = 8 o 9")
    else:
        print("⚠️ No hay región de countdown calibrada. Usando modo de espera de 2.5 segundos.")
        print(f"💰 SISTEMA SIMPLIFICADO:")
        print(f"   1️⃣ Detectar número ganador")
        print(f"   2️⃣ Esperar 2.5 segundos") 
        print(f"   3️⃣ Apostar automáticamente")
    print(f"🚀 VELOCIDAD MÁXIMA: ~50 FPS de detección")
    print(f"⏱️  Sesión iniciada: {datetime.now().strftime('%H:%M:%S')}")
    print(f"💡 Ctrl+C para terminar y ver resumen")
    print("-" * 70)

    detector = DetectorGanadoresSimple(calibrator.calibration_data)
    contador_scans = 0

    # Configuración segura de PyAutoGUI
    pyautogui.FAILSAFE = False  # Desactivamos para evitar errores con esquinas
    pyautogui.PAUSE = 0.1       # Pausa entre comandos
    pyautogui.PAUSE = config.get_click_delay()

    # Variables de optimización
    skip_frames = perf_settings['skip_frames']
    capture_interval = perf_settings['capture_interval']
    preview_interval = perf_settings['preview_interval']
    memory_cleanup = perf_settings['memory_cleanup']
    
    last_capture_time = 0
    last_preview_time = 0
    memory_cleanup_counter = 0
    
    # Variables para contador de FPS del preview
    preview_fps_counter = 0
    preview_fps_start_time = time.time()
    preview_fps_actual = 0
    
    # Variables para regiones ajustadas (disponibles para preview)
    adjusted_winner_region = None
    adjusted_countdown_region = None

    try:
        while True:
            current_time = time.time()
            
            # Control de frecuencia de captura basado en tiempo real
            if (current_time - last_capture_time) >= capture_interval:
                
                    # Optimización: Saltear frames según configuración
                    if contador_scans % skip_frames == 0:
                        
                        # Capturar región del número ganador (WINNER REGION) - USANDO MISMO APPROACH DEL CALIBRADOR
                        # Ajustar región para centrarla mejor (igual que en calibrator.py)
                        center_x = region_numero['x'] + region_numero['width'] // 2
                        center_y = region_numero['y'] + region_numero['height'] // 2
                        
                        # Usar tamaño optimizado según resolución (igual que calibrador)
                        # NOTA: En Windows 2K, usar el tamaño ya escalado de la calibración
                        if config.is_windows and config.resolution_info['is_2k']:
                            # Usar el tamaño ya escalado
                            optimal_width = region_numero['width']
                            optimal_height = region_numero['height']
                            print(f"🔧 Usando tamaño escalado para 2K: {optimal_width}x{optimal_height}")
                        else:
                            optimal_width, optimal_height = config.get_optimal_capture_size()
                        
                        # Actualizar variable global para preview
                        adjusted_winner_region = {
                            'left': center_x - optimal_width // 2,
                            'top': center_y - optimal_height // 2,
                            'width': optimal_width,
                            'height': optimal_height
                        }
                        
                        # DEBUG: Mostrar ajuste cada 100 frames para verificar
                        if contador_scans % 100 == 0:
                            print(f"🔍 DEBUG Region Adjustment:")
                            print(f"   Original: ({region_numero['x']}, {region_numero['y']}) {region_numero['width']}x{region_numero['height']}")
                            print(f"   Center: ({center_x}, {center_y})")
                            print(f"   Adjusted: ({adjusted_winner_region['left']}, {adjusted_winner_region['top']}) {adjusted_winner_region['width']}x{adjusted_winner_region['height']}")
                            
                            # EXPERIMENTO: Probar captura sin ajuste cada 1000 frames
                            if contador_scans % 1000 == 0:
                                print(f"🧪 EXPERIMENTO: Probando captura directa sin ajuste...")
                                test_region = {
                                    'left': region_numero['x'],
                                    'top': region_numero['y'],
                                    'width': region_numero['width'],
                                    'height': region_numero['height']
                                }
                                test_screenshot = capture_screen(test_region)
                                test_img = np.array(test_screenshot)
                                test_numero = detect_number_from_image(test_img).strip()
                                print(f"   Resultado sin ajuste: '{test_numero}' (size: {test_img.shape})")
                        
                        screenshot = capture_screen(adjusted_winner_region)
                        img_ganador = np.array(screenshot)
                        
                        numero_ganador = ""
                        countdown_actual = None

                        if img_ganador is not None and img_ganador.size > 0:
                            numero_ganador = detect_number_from_image(img_ganador).strip()
                            
                            # DEBUG: Mostrar resultado OCR y guardar imagen de debug
                            if contador_scans % 200 == 0:
                                print(f"🔍 DEBUG OCR: '{numero_ganador}' (size: {img_ganador.shape})")
                                # Estadísticas de imagen
                                mean_val = np.mean(img_ganador)
                                std_val = np.std(img_ganador)
                                print(f"   Brillo promedio: {mean_val:.1f}, Desv. estándar: {std_val:.1f}")
                                
                                # Guardar imagen de debug para análisis
                                if contador_scans == 200:  # Solo la primera vez
                                    import os
                                    debug_path = os.path.join(os.path.dirname(__file__), f"debug_winner_{contador_scans}.png")
                                    cv2.imwrite(debug_path, img_ganador)
                                    print(f"💾 Imagen debug guardada en: {debug_path}")
                                    print(f"   Revisa esta imagen para ver qué está capturando")
                                
                            if numero_ganador:
                                detector.procesar_numero(numero_ganador)
                            elif contador_scans % 500 == 0:
                                print(f"⚠️ OCR sin resultado en frame {contador_scans}")

                        # Capturar countdown a la MISMA frecuencia para sincronizar preview
                        if region_countdown:  # Sin reducir frecuencia para mejor sync
                            try:
                                # Ajustar región countdown igual que en calibrador
                                countdown_center_x = region_countdown['x'] + region_countdown['width'] // 2
                                countdown_center_y = region_countdown['y'] + region_countdown['height'] // 2
                                
                                # Usar tamaño optimizado para countdown
                                countdown_width, countdown_height = config.get_optimal_countdown_size()
                                
                                # Actualizar variable global para preview
                                adjusted_countdown_region = {
                                    'left': countdown_center_x - countdown_width // 2,
                                    'top': countdown_center_y - countdown_height // 2,
                                    'width': countdown_width,
                                    'height': countdown_height
                                }
                                
                                screenshot_countdown = capture_screen(adjusted_countdown_region)
                                img_countdown = np.array(screenshot_countdown)
                                if img_countdown is not None and img_countdown.size > 0:
                                    countdown_str = detect_number_from_image(img_countdown).strip()
                                    if countdown_str:
                                        countdown_actual = detector.procesar_countdown(countdown_str)
                            except Exception as e:
                                if contador_scans % 5000 == 0:  # Reducir spam de errores
                                    print(f"⚠️ Error capturando countdown: {e}")
                    
                    last_capture_time = current_time

            # Verificar momento de apuesta (siempre, para no perder oportunidades)
            if 'countdown_actual' in locals() and countdown_actual is not None:
                detector.verificar_momento_apuesta(countdown_actual)
            else:
                detector.verificar_momento_apuesta()  # Sin countdown
            
            # Limpieza de memoria en Windows
            if memory_cleanup and contador_scans % 10000 == 0:
                memory_cleanup_counter += 1
                if memory_cleanup_counter % 5 == 0:  # Cada 50k scans
                    import gc
                    gc.collect()
                    if config.is_windows:
                        print(f"🧹 Memoria limpiada (scan #{contador_scans})")
            
            contador_scans += 1

            # Preview mejorado - MUESTRA LA REGIÓN WINNER AJUSTADA (igual que calibrador)
            if (current_time - last_preview_time) >= preview_interval and 'img_ganador' in locals():
                if img_ganador is not None:
                    # Convertir a BGR para cv2 - img_ganador viene de adjusted_winner_region (AJUSTADA)
                    img_bgr = cv2.cvtColor(img_ganador, cv2.COLOR_RGB2BGR)
                    
                    # Preview más grande y centrado
                    preview = cv2.resize(img_bgr, (400, 280), interpolation=cv2.INTER_NEAREST)
                    
                    # Panel de información organizado
                    info_panel = np.zeros((180, 400, 3), dtype=np.uint8)
                    info_panel[:] = (40, 40, 40)  # Fondo gris oscuro
                    
                    # Combinar preview + info panel
                    display_img = np.vstack([preview, info_panel])
                    
                    # Dibujar línea separadora
                    cv2.line(display_img, (0, 280), (400, 280), (100, 100, 100), 2)
                    
                    # Información principal (lado izquierdo)
                    current_winner = numero_ganador if 'numero_ganador' in locals() and numero_ganador else detector.ultimo_numero_detectado
                    current_countdown = countdown_actual if 'countdown_actual' in locals() and countdown_actual else detector.ultimo_countdown
                    
                    # Convertir countdown a string para verificación
                    current_countdown_str = str(current_countdown) if current_countdown is not None else None
                    
                    # Título indicativo de región ajustada
                    cv2.putText(display_img, "CALIBRATOR-STYLE ADJUSTED REGION", (15, 290), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                    
                    # Winner detectado (grande y prominente)
                    current_winner_str = str(current_winner) if current_winner is not None else ""
                    winner_color = (0, 255, 0) if current_winner_str and current_winner_str.isdigit() else (0, 0, 255)
                    cv2.putText(display_img, f"WINNER: {current_winner or 'N/A'}", (15, 315), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.9, winner_color, 2)
                    
                    # Countdown (prominente con estado de apuesta)
                    if current_countdown_str and current_countdown_str.isdigit():
                        countdown_num = int(current_countdown_str)
                        if countdown_num in [9, 8]:
                            countdown_color = (0, 255, 0)  # Verde - momento de apostar
                            countdown_text = f"COUNTDOWN: {current_countdown_str} ⚡ BETTING TIME!"
                        elif countdown_num <= 15:
                            countdown_color = (0, 255, 255)  # Cian - preparándose
                            countdown_text = f"COUNTDOWN: {current_countdown_str} 🔄 Waiting..."
                        else:
                            countdown_color = (255, 255, 0)  # Amarillo - normal
                            countdown_text = f"COUNTDOWN: {current_countdown_str}"
                    else:
                        countdown_color = (255, 255, 0)
                        countdown_text = f"COUNTDOWN: {current_countdown_str or 'N/A'}"
                    
                    cv2.putText(display_img, countdown_text, (15, 345), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, countdown_color, 2)
                    
                    # Target actual
                    target_color = (255, 0, 255) if detector.modo_aleatorio else (255, 255, 255)
                    mode_text = "RANDOM" if detector.modo_aleatorio else "FIXED"
                    cv2.putText(display_img, f"TARGET: {detector.numero_objetivo} ({mode_text})", (15, 375), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, target_color, 1)
                    
                    # Estadísticas (lado derecho)
                    cv2.putText(display_img, f"Bets: {detector.total_apuestas}", (220, 315), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(display_img, f"Winners: {len(detector.historial_ganadores)}", (220, 335), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(display_img, f"Detections: {detector.contador_detecciones_validas}", (220, 355), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

                    # Estado de apuestas (centro inferior)
                    if region_countdown:
                        if detector.puede_apostar:
                            if current_countdown_str and current_countdown_str.isdigit():
                                countdown_num = int(current_countdown_str)
                                if countdown_num in [9, 8]:
                                    color = (0, 255, 0)
                                    status_text = f"⚡ BETTING NOW! (countdown: {current_countdown_str})"
                                elif countdown_num <= 15:
                                    color = (0, 255, 255)
                                    status_text = f"🔄 Ready to bet at 8-9 (countdown: {current_countdown_str})"
                                else:
                                    color = (200, 200, 200)
                                    status_text = f"⏳ Waiting for countdown 8-9 (current: {current_countdown_str})"
                            else:
                                color = (200, 200, 200)
                                status_text = "Waiting for countdown detection..."
                        else:
                            color = (100, 100, 255)
                            status_text = "Bet placed, waiting for next winner"
                    else:
                        # Modo fallback (3 segundos)
                        if detector.esperando_apuesta and detector.tiempo_espera_inicio:
                            tiempo_restante = 3.0 - (time.time() - detector.tiempo_espera_inicio)
                            if tiempo_restante > 0:
                                color = (255, 255, 0)
                                status_text = f"Waiting: {tiempo_restante:.1f}s"
                            else:
                                color = (0, 255, 0)
                                status_text = "BETTING NOW!"
                        else:
                            color = (200, 200, 200)
                            status_text = "Waiting for winner..."
                    
                    cv2.putText(display_img, status_text, (15, 405), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

                    # FPS y región info en esquina inferior derecha
                    if contador_scans > 100:
                        duracion_actual = time.time() - detector.inicio_sesion
                        fps_actual = contador_scans / duracion_actual
                        cv2.putText(display_img, f"FPS: {fps_actual:.1f}", (320, 375), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    # Último ganador si existe
                    if len(detector.historial_ganadores) > 0:
                        ultimo_ganador = detector.historial_ganadores[-1][1]
                        cv2.putText(display_img, f"Last: {ultimo_ganador}", (220, 390), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                    
                    # Mostrar qué región está viendo el preview (AJUSTADA igual que calibrador)
                    if adjusted_winner_region:
                        cv2.putText(display_img, f"ADJUSTED Winner: {adjusted_winner_region['width']}x{adjusted_winner_region['height']}", (220, 420), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
                        cv2.putText(display_img, f"Pos: ({adjusted_winner_region['left']}, {adjusted_winner_region['top']})", (220, 435), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)
                        # Mostrar comparación con región original
                        cv2.putText(display_img, f"Original: {region_numero['width']}x{region_numero['height']} at ({region_numero['x']},{region_numero['y']})", (10, 450), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.3, (128, 128, 128), 1)
                    else:
                        cv2.putText(display_img, f"Region: Winner ({region_numero['width']}x{region_numero['height']})", (220, 420), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 200, 100), 1)
                    
                    # Calcular FPS real del preview
                    preview_fps_counter += 1
                    if current_time - preview_fps_start_time >= 1.0:
                        preview_fps_actual = preview_fps_counter
                        preview_fps_counter = 0
                        preview_fps_start_time = current_time
                    
                    # Mostrar FPS del preview
                    cv2.putText(display_img, f"Preview: {preview_fps_actual} FPS", (320, 395), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 255, 100), 1)

                    cv2.imshow("RouletteBot - Live Preview", display_img)
                    last_preview_time = current_time

            if contador_scans % 2500 == 0:
                duracion = time.time() - detector.inicio_sesion
                fps = contador_scans / duracion
                countdown_status = f"Countdown: {countdown_actual}" if countdown_actual else "No countdown"
                bet_status = "Can bet" if detector.puede_apostar else "Bet placed"
                print(f"📊 [{datetime.now().strftime('%H:%M:%S')}] Scans: {contador_scans} | FPS: {fps:.1f} | Bets: {detector.total_apuestas} | Winners: {len(detector.historial_ganadores)} | {countdown_status} | {bet_status}")

            # Detección de teclas para control en tiempo real
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            # Teclas F1-F9 para números fijos (aproximación con números 1-9)
            elif key >= ord('1') and key <= ord('9'):
                numero = int(chr(key))
                detector.cambiar_numero_objetivo(numero, manual=True)
            elif key == ord('0'):
                detector.cambiar_numero_objetivo(0, manual=True)
            elif key == ord('r'):  # R para random
                detector.activar_modo_aleatorio()
            elif key == ord('n'):  # N para nuevo número aleatorio
                detector.nuevo_numero_aleatorio()
            elif key == ord('d'):  # D para toggle debug
                detector.debug_detecciones = not detector.debug_detecciones
                print(f"🐛 Debug mode: {'ON' if detector.debug_detecciones else 'OFF'}")
            
            # Delay adaptativo según SO
            if config.is_windows:
                time.sleep(0.001)  # 1ms para Windows (más rápido)
            else:
                time.sleep(0.005)  # 5ms para otros SO

    except KeyboardInterrupt:
        print(f"\n🛑 Session ended by the user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cv2.destroyAllWindows()
        detector.mostrar_resumen(contador_scans)

if __name__ == "__main__":
    main()
