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
    """Click on specified number to bet"""
    try:
        if calibration_data and 'bet_positions' in calibration_data:
            if str(numero) in calibration_data['bet_positions']:
                pos = calibration_data['bet_positions'][str(numero)]
                x, y = pos['x'], pos['y']
            else:
                print(f"⚠️  No hay calibración para el número {numero}, usando valores por defecto")
                x, y = 3050, 605
        else:
            # Valores por defecto (ajustar según necesidad)
            x, y = 3050, 605
        
        pyautogui.click(x, y)
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"💰 [{timestamp}] ✅ BET PLACED on number {numero}")
        return True
    except Exception as e:
        print(f"❌ Error placing bet: {e}")
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
                print(f"🔍 Número detectado: {numero}")
            self.ultimo_numero_detectado = numero
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
        
        # Debug: mostrar countdown solo si cambió
        if countdown_str != self.ultimo_countdown_detectado:
            if self.debug_detecciones and countdown <= 20:
                print(f"⏰ Countdown detectado: {countdown}")
            self.ultimo_countdown_detectado = countdown_str
        
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # Solo mostrar cambios significativos del countdown
        if self.ultimo_countdown != countdown:
            if countdown <= 15:  # Solo mostrar cuando se acerque el momento de apostar
                print(f"⏰ [{timestamp}] Countdown: {countdown}")
            self.ultimo_countdown = countdown
        
        return countdown

    def verificar_momento_apuesta(self, countdown=None):
        """Check if it's time to bet - AGGRESSIVE BETTING MODE"""
        if not self.puede_apostar:
            return False
        
        # Verificar que no hayamos apostado muy recientemente (evitar spam)
        tiempo_actual = time.time()
        if tiempo_actual - self.tiempo_ultima_apuesta < 1.0:  # 1 segundo mínimo entre apuestas
            return False
            
        apuesta_realizada = False
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # MODO AGRESIVO: Apostar en múltiples momentos
        if countdown is not None:
            # Apostar cuando countdown = 10, 8, 6, 4 (múltiples oportunidades)
            if countdown in [10, 8, 6, 4]:
                print(f"🎯 [{timestamp}] TIME TO BET! (Countdown = {countdown})")
                apuesta_realizada = True
        else:
            # Modo fallback: apostar después de 3 segundos
            if self.esperando_apuesta and self.tiempo_espera_inicio:
                tiempo_transcurrido = tiempo_actual - self.tiempo_espera_inicio
                if tiempo_transcurrido >= 3.0:
                    print(f"🎯 [{timestamp}] TIME TO BET! (3 seconds completed)")
                    apuesta_realizada = True

        if apuesta_realizada:
            if apostar_al_numero(self.numero_objetivo, self.calibration_data):
                self.total_apuestas += 1
                self.tiempo_ultima_apuesta = tiempo_actual
                timestamp_apuesta = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                print(f"✅ [{timestamp_apuesta}] Bet #{self.total_apuestas} confirmed on number {self.numero_objetivo}")
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
    print("-" * 70)
    
    # Cargar calibración
    calibrator = Calibrator()
    if not calibrator.calibration_data.get('winner_region'):
        print("❌ No hay calibración guardada.")
        print("📋 Ejecuta primero: python roullebot.py --mode calibrate")
        return
    
    try:
        region_chrome = obtener_region_chrome()
        print(f"✅ Chrome detectado en: {region_chrome}")
    except Exception as e:
        print(f"❌ Error detectando Chrome: {e}")
        return
    
    # Usar regiones calibradas
    region_numero = calibrator.calibration_data['winner_region']
    region_countdown = calibrator.calibration_data.get('countdown_region')
    
    print(f"🎯 Monitoreando número ganador en: x={region_numero['x']}, y={region_numero['y']}")
    
    if region_countdown:
        print(f"⏰ Monitoreando countdown en: x={region_countdown['x']}, y={region_countdown['y']}")
        print(f"💰 SISTEMA AUTOMÁTICO:")
        print(f"   1️⃣ Detectar número ganador")
        print(f"   2️⃣ Monitorear countdown")
        print(f"   3️⃣ Apostar al 24 cuando countdown = 10")
    else:
        print("⚠️ No hay región de countdown calibrada. Usando modo de espera de 3 segundos.")
        print(f"💰 SISTEMA SIMPLIFICADO:")
        print(f"   1️⃣ Detectar número ganador")
        print(f"   2️⃣ Esperar 3 segundos") 
        print(f"   3️⃣ Apostar automáticamente al 24")
    print(f"🚀 VELOCIDAD MÁXIMA: ~50 FPS de detección")
    print(f"⏱️  Sesión iniciada: {datetime.now().strftime('%H:%M:%S')}")
    print(f"💡 Ctrl+C para terminar y ver resumen")
    print("-" * 70)

    detector = DetectorGanadoresSimple(calibrator.calibration_data)
    contador_scans = 0

    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = config.get_click_delay()

    try:
        while True:
            # Optimización: Reducir frecuencia de captura para mejorar rendimiento
            if contador_scans % 2 == 0:  # Capturar cada 2 frames en lugar de todos
                
                # Capturar región del número ganador
                screenshot = capture_screen(region_numero)
                img_ganador = np.array(screenshot)
                
                numero_ganador = ""
                countdown_actual = None

                if img_ganador is not None and img_ganador.size > 0:
                    numero_ganador = detect_number_from_image(img_ganador).strip()
                    if numero_ganador:
                        detector.procesar_numero(numero_ganador)

                # Capturar countdown si está disponible (menos frecuente para optimizar)
                if region_countdown and contador_scans % 3 == 0:  # Countdown cada 3 frames
                    try:
                        screenshot_countdown = capture_screen(region_countdown)
                        img_countdown = np.array(screenshot_countdown)
                        if img_countdown is not None and img_countdown.size > 0:
                            countdown_str = detect_number_from_image(img_countdown).strip()
                            if countdown_str:
                                countdown_actual = detector.procesar_countdown(countdown_str)
                    except Exception as e:
                        if contador_scans % 2000 == 0:  # Reducir mensajes de error
                            print(f"⚠️ Error capturando countdown: {e}")

            # Verificar momento de apuesta (siempre, para no perder oportunidades)
            if region_countdown and countdown_actual is not None:
                detector.verificar_momento_apuesta(countdown_actual)
            else:
                detector.verificar_momento_apuesta()  # Sin countdown
            
            contador_scans += 1

            # Preview optimizado: mostrar menos frecuentemente
            if contador_scans % 500 == 0 and 'img_ganador' in locals():  # Reducir frecuencia
                if img_ganador is not None:
                    # Convertir a BGR para cv2
                    img_bgr = cv2.cvtColor(img_ganador, cv2.COLOR_RGB2BGR)
                    preview = cv2.resize(img_bgr, (300, 300), interpolation=cv2.INTER_NEAREST)
                    info_img = cv2.copyMakeBorder(preview, 0, 140, 0, 0, cv2.BORDER_CONSTANT, value=(50, 50, 50))

                    cv2.putText(info_img, f"Winner: {numero_ganador if 'numero_ganador' in locals() else detector.ultimo_numero_detectado}", (10, 320), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    cv2.putText(info_img, f"Countdown: {countdown_actual if 'countdown_actual' in locals() and countdown_actual else detector.ultimo_countdown}", (10, 345), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
                    cv2.putText(info_img, f"Bets: {detector.total_apuestas}", (10, 370), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    cv2.putText(info_img, f"Target: {detector.numero_objetivo} {'(RANDOM)' if detector.modo_aleatorio else '(FIXED)'}", (10, 395), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    cv2.putText(info_img, f"Winners: {len(detector.historial_ganadores)}", (10, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    cv2.putText(info_img, f"Valid detections: {detector.contador_detecciones_validas}", (10, 445), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

                    # Mostrar estado actual
                    if region_countdown:
                        if detector.puede_apostar:
                            if countdown_actual and countdown_actual <= 15:
                                color = (0, 255, 255) if countdown_actual > 10 else (0, 255, 0)
                                cv2.putText(info_img, f"Ready to bet at countdown 10", (10, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                            else:
                                cv2.putText(info_img, "Waiting for countdown...", (10, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                        else:
                            cv2.putText(info_img, "Bet placed, waiting for next winner", (10, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 255), 1)
                    else:
                        # Modo fallback (3 segundos)
                        if detector.esperando_apuesta and detector.tiempo_espera_inicio:
                            tiempo_restante = 3.0 - (time.time() - detector.tiempo_espera_inicio)
                            if tiempo_restante > 0:
                                cv2.putText(info_img, f"Waiting: {tiempo_restante:.1f}s", (10, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                            else:
                                cv2.putText(info_img, "BETTING...", (10, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        else:
                            cv2.putText(info_img, "Waiting for winner...", (10, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

                    if contador_scans > 100:
                        duracion_actual = time.time() - detector.inicio_sesion
                        fps_actual = contador_scans / duracion_actual
                        cv2.putText(info_img, f"FPS: {fps_actual:.1f}", (200, 375), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                    cv2.imshow("Simplified Bettor on 24", info_img)

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
            
            # Pequeño delay para evitar saturar CPU
            time.sleep(0.001)  # 1ms delay

    except KeyboardInterrupt:
        print(f"\n🛑 Session ended by the user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cv2.destroyAllWindows()
        detector.mostrar_resumen(contador_scans)

if __name__ == "__main__":
    main()
