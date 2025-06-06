from vision.screen_capture import capture_screen
from vision.detector import detect_number_from_image
import time

# Coordenadas exactas del número ganador (calibradas con click - versión refinada)
region = {"left": 2861, "top": 551, "width": 60, "height": 60}

print("🎯 SCAN RÁPIDO EN TIEMPO REAL (solo texto)")
print(f"Región: {region}")
print("Ctrl+C para salir")
print("-" * 50)

ultimo_numero = None
contador = 0
cambios_detectados = 0

try:
    while True:
        # Capturar y procesar
        img = capture_screen(region)

        if img is not None and img.size > 0:
            numero = detect_number_from_image(img)
            contador += 1

            # Mostrar solo cambios importantes
            if numero and numero != ultimo_numero:
                timestamp = time.strftime("%H:%M:%S")
                cambios_detectados += 1
                print(f"🎲 [{timestamp}] NUEVO GANADOR: {numero} (cambio #{cambios_detectados})")
                ultimo_numero = numero

            # Heartbeat cada 100 scans (~20 segundos)
            elif contador % 100 == 0:
                timestamp = time.strftime("%H:%M:%S")
                print(
                    f"⏱️ [{timestamp}] Activo - Scans: {contador} | Último: {ultimo_numero} | Cambios: {cambios_detectados}")

        # Scan ultra-rápido: cada 100ms (10 veces por segundo)
        time.sleep(0.1)

except KeyboardInterrupt:
    print(f"\n🛑 SCAN FINALIZADO")
    print(f"📊 Estadísticas:")
    print(f"   Total scans: {contador}")
    print(f"   Cambios detectados: {cambios_detectados}")
    print(f"   Último número: {ultimo_numero}")
    print(f"   Tiempo promedio: {contador * 0.1:.1f} segundos")
except Exception as e:
    print(f"❌ Error: {e}")