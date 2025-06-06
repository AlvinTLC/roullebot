import cv2
import time
import numpy as np
import pyautogui
from datetime import datetime

# Funciones auxiliares simuladas
def capture_screen(region):
    # Simulación de captura de pantalla
    img = np.random.randint(0, 255, (region['height'], region['width'], 3), dtype=np.uint8)
    return img

def detect_number_from_image(img):
    # Simulación de detección de número
    return str(np.random.randint(0, 37))

def es_numero_valido_ruleta(numero_str):
    """Verifica si es un número válido de ruleta (0-36)"""
    try:
        numero = int(numero_str)
        return 0 <= numero <= 36
    except:
        return False

def apostar_al_24():
    """Hace click en el número 24 para apostar"""
    try:
        # Coordenadas calibradas perfectas
        x, y = 2559, 899

        # Hacer click en el número 24
        pyautogui.click(x, y)
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"💰 [{timestamp}] ✅ APUESTA REALIZADA al número 24")
        return True
    except Exception as e:
        print(f"❌ Error apostando: {e}")
        return False

class DetectorGanadoresSimple:
    def __init__(self):
        self.ultimo_ganador = None
        self.numero_candidato = None
        self.contador_confirmaciones = 0
        self.confirmaciones_requeridas = 3  # Para estar seguro
        self.historial_ganadores = []
        self.inicio_sesion = time.time()

        # Sistema de apostado simplificado
        self.total_apuestas = 0
        self.numero_objetivo = 24
        self.esperando_apuesta = False
        self.tiempo_espera_inicio = None

    def procesar_numero(self, numero):
        """Procesa número y confirma ganadores"""
        if not numero or not es_numero_valido_ruleta(numero):
            return False

        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        # Si es el mismo número candidato
        if numero == self.numero_candidato:
            self.contador_confirmaciones += 1

            # Si se confirma suficientes veces, es ganador confirmado
            if self.contador_confirmaciones >= self.confirmaciones_requeridas:
                if numero != self.ultimo_ganador:
                    self.historial_ganadores.append((timestamp, numero))

                    # Verificar si ganamos la apuesta anterior
                    if self.total_apuestas > 0:  # Solo si ya hemos apostado
                        if int(numero) == self.numero_objetivo:
                            print(f"🎉 [{timestamp}] ¡¡¡GANASTE!!! Número ganador: {numero} 🎉")
                        else:
                            print(f"💔 [{timestamp}] Perdiste. Ganador: {numero} (apostamos al {self.numero_objetivo})")
                    else:
                        print(f"🏆 [{timestamp}] PRIMER GANADOR DETECTADO: {numero}")

                    self.ultimo_ganador = numero

                    # Iniciar proceso de espera para próxima apuesta
                    self.iniciar_espera_para_apuesta()
                    return True
        else:
            # Nuevo candidato
            self.numero_candidato = numero
            self.contador_confirmaciones = 1

        return False

    def iniciar_espera_para_apuesta(self):
        """Inicia la espera de 3 segundos para la próxima apuesta"""
        self.esperando_apuesta = True
        self.tiempo_espera_inicio = time.time()
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"⏳ [{timestamp}] Esperando 3 segundos para habilitar apuestas...")

    def verificar_momento_apuesta(self):
        """Verifica si es momento de apostar (después de 3 segundos)"""
        if self.esperando_apuesta and self.tiempo_espera_inicio:
            tiempo_transcurrido = time.time() - self.tiempo_espera_inicio

            if tiempo_transcurrido >= 3.0:
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                print(f"🎯 [{timestamp}] ¡MOMENTO DE APOSTAR! (3 segundos completados)")

                if apostar_al_24():
                    self.total_apuestas += 1
                    timestamp_apuesta = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    print(f"✅ [{timestamp_apuesta}] Apuesta #{self.total_apuestas} confirmada al número {self.numero_objetivo}")

                    # Reset para próximo ciclo
                    self.esperando_apuesta = False
                    self.tiempo_espera_inicio = None
                    return True

        return False

    def mostrar_resumen(self, total_scans):
        """Muestra resumen de la sesión"""
        duracion = time.time() - self.inicio_sesion
        print(f"\n" + "="*70)
        print(f"📊 RESUMEN DE SESIÓN - APOSTADOR AUTOMÁTICO SIMPLIFICADO")
        print(f"="*70)
        print(f"⏱️  Duración: {duracion/60:.1f} minutos")
        print(f"🔍 Total scans: {total_scans}")
        print(f"⚡ FPS promedio: {total_scans/duracion:.1f}")
        print(f"🏆 Ganadores detectados: {len(self.historial_ganadores)}")
        print(f"💰 Total apuestas realizadas: {self.total_apuestas}")
        print(f"🎯 Número objetivo: {self.numero_objetivo}")

        # Análisis de resultados
        if self.historial_ganadores and self.total_apuestas > 0:
            print(f"\n🎯 RESULTADOS DE APUESTAS:")
            ganadas = 0
            perdidas = 0

            # Los resultados empiezan desde el segundo ganador (el primero no tiene apuesta)
            for i, (timestamp, numero) in enumerate(self.historial_ganadores):
                if i == 0:
                    print(f"   🎮 [{timestamp}] Primer ganador (sin apuesta): {numero}")
                else:
                    if int(numero) == self.numero_objetivo:
                        print(f"   ✅ [{timestamp}] GANASTE: {numero}")
                        ganadas += 1
                    else:
                        print(f"   ❌ [{timestamp}] Perdiste: {numero}")
                        perdidas += 1

            if ganadas + perdidas > 0:
                print(f"\n📈 ESTADÍSTICAS FINALES:")
                print(f"   🏆 Apuestas ganadas: {ganadas}")
                print(f"   💔 Apuestas perdidas: {perdidas}")
                tasa_exito = (ganadas / (ganadas + perdidas)) * 100
                print(f"   📊 Tasa de éxito: {tasa_exito:.1f}%")
                print(f"   💵 Balance teórico: {ganadas * 35 - perdidas} fichas (35:1 payout)")
        else:
            print(f"\n⚠️  No se completaron apuestas en esta sesión")

def main():
    # Regiones de interés
    region_numero_ganador = {
        "left": 2850,
        "top": 560,
        "width": 80,
        "height": 40
    }

    region_apuesta_total = {
        "left": 2519,
        "top": 879,
        "width": 80,
        "height": 40
    }

    region_balance = {
        "left": 2439,
        "top": 882,
        "width": 80,
        "height": 40
    }

    region_waiting_for_next_game = {
        "left": 2852,
        "top": 705,
        "width": 80,
        "height": 40
    }

    region_play_time = {
        "left": 2849,
        "top": 645,
        "width": 80,
        "height": 40
    }

    region_ficha_5 = {
        "left": 2722,
        "top": 841,
        "width": 80,
        "height": 40
    }

    region_ficha_50 = {
        "left": 2756,
        "top": 844,
        "width": 80,
        "height": 40
    }

    print(f"🎯 Monitoreando regiones específicas")
    print(f"💰 SISTEMA SIMPLIFICADO:")
    print(f"   1️⃣ Detecta número ganador")
    print(f"   2️⃣ Espera 3 segundos")
    print(f"   3️⃣ Apuesta automáticamente al 24")
    print(f"🚀 MÁXIMA VELOCIDAD: ~50 FPS de detección")
    print(f"⏱️  Sesión iniciada: {datetime.now().strftime('%H:%M:%S')}")
    print(f"💡 Ctrl+C para finalizar y ver resumen")
    print("-" * 70)

    detector = DetectorGanadoresSimple()
    contador_scans = 0

    # Configurar pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.01

    try:
        while True:
            # Capturar regiones de interés
            img_numero_ganador = capture_screen(region_numero_ganador)
            img_apuesta_total = capture_screen(region_apuesta_total)
            img_balance = capture_screen(region_balance)
            img_waiting_for_next_game = capture_screen(region_waiting_for_next_game)
            img_play_time = capture_screen(region_play_time)
            img_ficha_5 = capture_screen(region_ficha_5)
            img_ficha_50 = capture_screen(region_ficha_50)

            contador_scans += 1

            # Procesar número ganador
            if img_numero_ganador is not None and img_numero_ganador.size > 0:
                numero_ganador = detect_number_from_image(img_numero_ganador).strip()
                if numero_ganador:
                    detector.procesar_numero(numero_ganador)

                # Verificar si es momento de apostar
                detector.verificar_momento_apuesta()

            # Preview cada 250 scans (~5 segundos a 50 FPS)
            if contador_scans % 250 == 0:
                if img_numero_ganador is not None:
                    # Preview simple solo del ganador
                    preview = cv2.resize(img_numero_ganador, (300, 300), interpolation=cv2.INTER_NEAREST)

                    # Agregar información
                    info_img = cv2.copyMakeBorder(preview, 0, 120, 0, 0, cv2.BORDER_CONSTANT, value=(50, 50, 50))

                    # Información actual
                    cv2.putText(info_img, f"Ganador: {numero_ganador}", (10, 320), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    cv2.putText(info_img, f"Apuestas: {detector.total_apuestas}", (10, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    cv2.putText(info_img, f"Objetivo: {detector.numero_objetivo}", (150, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    cv2.putText(info_img, f"Ganadores: {len(detector.historial_ganadores)}", (10, 375), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

                    # Estado actual
                    if detector.esperando_apuesta:
                        tiempo_restante = 3.0 - (time.time() - detector.tiempo_espera_inicio)
                        if tiempo_restante > 0:
                            cv2.putText(info_img, f"Esperando: {tiempo_restante:.1f}s", (10, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                        else:
                            cv2.putText(info_img, "APOSTANDO...", (10, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    else:
                        cv2.putText(info_img, "Esperando ganador...", (10, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

                    # FPS info
                    if contador_scans > 100:
                        duracion_actual = time.time() - detector.inicio_sesion
                        fps_actual = contador_scans / duracion_actual
                        cv2.putText(info_img, f"FPS: {fps_actual:.1f}", (200, 375), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                    cv2.imshow("Apostador Simplificado al 24", info_img)

            # Estadísticas cada 2500 scans
            if contador_scans % 2500 == 0:
                duracion = time.time() - detector.inicio_sesion
                fps = contador_scans / duracion
                print(f"📊 [{datetime.now().strftime('%H:%M:%S')}] Scans: {contador_scans} | FPS: {fps:.1f} | Apuestas: {detector.total_apuestas} | Ganadores: {len(detector.historial_ganadores)}")

            # Check para salir
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print(f"\n🛑 Sesión finalizada por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cv2.destroyAllWindows()
        detector.mostrar_resumen(contador_scans)

if __name__ == "__main__":
    main()
