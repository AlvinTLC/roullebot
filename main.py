import cv2
import time
import numpy as np
import pyautogui
from datetime import datetime

def capture_screen(region):
    # Use pyautogui to capture the actual screen region
    screenshot = pyautogui.screenshot(region=(region['left'], region['top'], region['width'], region['height']))
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return img

def obtener_region_chrome():
    # Simulate obtaining the Chrome region
    return {"left": 0, "top": 0, "width": 1920, "height": 1080}

def detect_number_from_image(img):
    # Simulate detecting a number from the image
    return str(np.random.randint(0, 37))

def es_numero_valido_ruleta(numero_str):
    """Check if it is a valid roulette number (0-36)"""
    try:
        numero = int(numero_str)
        return 0 <= numero <= 36
    except:
        return False

def apostar_al_24():
    """Click on number 24 to bet"""
    try:
        x, y = 3050, 605
        pyautogui.click(x, y)
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"💰 [{timestamp}] ✅ BET PLACED on number 24")
        return True
    except Exception as e:
        print(f"❌ Error placing bet: {e}")
        return False

class DetectorGanadoresSimple:
    def __init__(self):
        self.ultimo_ganador = None
        self.numero_candidato = None
        self.contador_confirmaciones = 0
        self.confirmaciones_requeridas = 3
        self.historial_ganadores = []
        self.inicio_sesion = time.time()
        self.total_apuestas = 0
        self.numero_objetivo = 24
        self.esperando_apuesta = False
        self.tiempo_espera_inicio = None

    def procesar_numero(self, numero):
        """Process number and confirm winners"""
        if not numero or not es_numero_valido_ruleta(numero):
            return False

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
                    self.iniciar_espera_para_apuesta()
                    return True
        else:
            self.numero_candidato = numero
            self.contador_confirmaciones = 1

        return False

    def iniciar_espera_para_apuesta(self):
        """Start waiting for 3 seconds for the next bet"""
        self.esperando_apuesta = True
        self.tiempo_espera_inicio = time.time()
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"⏳ [{timestamp}] Waiting 3 seconds to enable bets...")

    def verificar_momento_apuesta(self):
        """Check if it's time to bet (after 3 seconds)"""
        if self.esperando_apuesta and self.tiempo_espera_inicio:
            tiempo_transcurrido = time.time() - self.tiempo_espera_inicio

            if tiempo_transcurrido >= 3.0:
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                print(f"🎯 [{timestamp}] TIME TO BET! (3 seconds completed)")

                if apostar_al_24():
                    self.total_apuestas += 1
                    timestamp_apuesta = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    print(f"✅ [{timestamp_apuesta}] Bet #{self.total_apuestas} confirmed on number {self.numero_objetivo}")

                    self.esperando_apuesta = False
                    self.tiempo_espera_inicio = None
                    return True

        return False

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
    region_chrome = obtener_region_chrome()
    print(f"🖥️ Chrome detected at: {region_chrome}")

    region_numero = {
        "left": 2850,
        "top": 560,
        "width": 80,
        "height": 40
    }

    print(f"🎯 Monitoring ONLY winning number: {region_numero}")
    print(f"💰 SIMPLIFIED SYSTEM:")
    print(f"   1️⃣ Detect winning number")
    print(f"   2️⃣ Wait 3 seconds")
    print(f"   3️⃣ Automatically bet on 24")
    print(f"🚀 MAXIMUM SPEED: ~50 FPS detection")
    print(f"⏱️ Session started: {datetime.now().strftime('%H:%M:%S')}")
    print(f"💡 Ctrl+C to finish and see summary")
    print("-" * 70)

    detector = DetectorGanadoresSimple()
    contador_scans = 0

    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.01

    try:
        while True:
            img_ganador = capture_screen(region_numero)
            contador_scans += 1

            if img_ganador is not None and img_ganador.size > 0:
                numero_ganador = detect_number_from_image(img_ganador).strip()
                if numero_ganador:
                    detector.procesar_numero(numero_ganador)

                detector.verificar_momento_apuesta()

            if contador_scans % 250 == 0:
                if img_ganador is not None:
                    preview = cv2.resize(img_ganador, (300, 300), interpolation=cv2.INTER_NEAREST)
                    info_img = cv2.copyMakeBorder(preview, 0, 120, 0, 0, cv2.BORDER_CONSTANT, value=(50, 50, 50))

                    cv2.putText(info_img, f"Winner: {numero_ganador}", (10, 320), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    cv2.putText(info_img, f"Bets: {detector.total_apuestas}", (10, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    cv2.putText(info_img, f"Target: {detector.numero_objetivo}", (150, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    cv2.putText(info_img, f"Winners: {len(detector.historial_ganadores)}", (10, 375), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

                    if detector.esperando_apuesta:
                        tiempo_restante = 3.0 - (time.time() - detector.tiempo_espera_inicio)
                        if tiempo_restante > 0:
                            cv2.putText(info_img, f"Waiting: {tiempo_restante:.1f}s", (10, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                        else:
                            cv2.putText(info_img, "BETTING...", (10, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    else:
                        cv2.putText(info_img, "Waiting for winner...", (10, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

                    if contador_scans > 100:
                        duracion_actual = time.time() - detector.inicio_sesion
                        fps_actual = contador_scans / duracion_actual
                        cv2.putText(info_img, f"FPS: {fps_actual:.1f}", (200, 375), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                    cv2.imshow("Simplified Bettor on 24", info_img)

            if contador_scans % 2500 == 0:
                duracion = time.time() - detector.inicio_sesion
                fps = contador_scans / duracion
                print(f"📊 [{datetime.now().strftime('%H:%M:%S')}] Scans: {contador_scans} | FPS: {fps:.1f} | Bets: {detector.total_apuestas} | Winners: {len(detector.historial_ganadores)}")

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print(f"\n🛑 Session ended by the user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cv2.destroyAllWindows()
        detector.mostrar_resumen(contador_scans)

if __name__ == "__main__":
    main()
