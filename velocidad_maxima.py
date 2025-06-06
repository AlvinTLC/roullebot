from vision.screen_capture import capture_screen
from vision.detector import detect_number_from_image
import time
from datetime import datetime

# Coordenadas exactas
region_ganador = {"left": 2967, "top": 410, "width": 60, "height": 60}
region_countdown = {"left": 2966, "top": 509, "width": 60, "height": 60}

print("⚡ VELOCIDAD MÁXIMA - SIN PREVIEW VISUAL")
print("🚀 ~50 FPS de detección pura")
print("Ctrl+C para salir")
print("-" * 60)

ultimo_ganador = None
ultimo_countdown = None
contador = 0
cambios_ganador = 0
cambios_countdown = 0

inicio = time.time()

try:
    while True:
        # Capturar ambas regiones simultáneamente
        img_ganador = capture_screen(region_ganador)
        img_countdown = capture_screen(region_countdown)

        contador += 1

        # Procesar número ganador
        if img_ganador is not None and img_ganador.size > 0:
            ganador = detect_number_from_image(img_ganador).strip()
            if ganador and ganador != ultimo_ganador:
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Microsegundos
                print(f"🏆 [{timestamp}] GANADOR: {ganador}")
                ultimo_ganador = ganador
                cambios_ganador += 1

        # Procesar countdown
        if img_countdown is not None and img_countdown.size > 0:
            countdown = detect_number_from_image(img_countdown).strip()
            if countdown and countdown != ultimo_countdown:
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Microsegundos

                # Emoji según countdown
                if countdown.isdigit():
                    num = int(countdown)
                    if num == 0:
                        emoji = "🚀"
                    elif num <= 3:
                        emoji = "⚡"
                    elif num <= 10:
                        emoji = "⏰"
                    else:
                        emoji = "⏳"
                else:
                    emoji = "❓"

                print(f"{emoji} [{timestamp}] COUNTDOWN: {countdown}")
                ultimo_countdown = countdown
                cambios_countdown += 1

        # Estadísticas cada 1000 scans
        if contador % 1000 == 0:
            duracion = time.time() - inicio
            fps = contador / duracion
            print(
                f"📊 Scans: {contador} | FPS: {fps:.1f} | Ganadores: {cambios_ganador} | Countdowns: {cambios_countdown}")

        # SIN SLEEP - MÁXIMA VELOCIDAD POSIBLE
        # time.sleep(0.02)  # Descomenta si necesitas reducir un poco la carga de CPU

except KeyboardInterrupt:
    duracion = time.time() - inicio
    fps = contador / duracion
    print(f"\n🛑 ESTADÍSTICAS FINALES:")
    print(f"⏱️  Duración: {duracion:.1f} segundos")
    print(f"🔢 Total scans: {contador}")
    print(f"⚡ FPS promedio: {fps:.1f}")
    print(f"🏆 Cambios ganador: {cambios_ganador}")
    print(f"⏰ Cambios countdown: {cambios_countdown}")
    print(f"🎯 Último ganador: {ultimo_ganador}")
    print(f"⏳ Último countdown: {ultimo_countdown}")