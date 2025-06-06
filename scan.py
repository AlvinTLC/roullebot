from vision.screen_capture import capture_screen
from vision.detector import detect_number_from_image
import cv2
import time

# Coordenadas exactas del número ganador (calibradas con click)
region = {"left": 2850, "top": 560, "width": 40, "height": 40}

print(f"🎯 SCAN EN TIEMPO REAL - Región: {region}")
print("Monitoreando número ganador de la ruleta...")
print("Presiona Q para salir")

ultimo_numero = None
contador = 0

try:
    while True:
        # Capturar región
        img = capture_screen(region)

        if img is not None and img.size > 0:
            # Detectar número
            numero = detect_number_from_image(img)
            contador += 1

            # Solo mostrar cuando cambia
            if numero and numero != ultimo_numero:
                timestamp = time.strftime("%H:%M:%S")
                print(f"🎲 [{timestamp}] Número ganador: {numero} (scan #{contador})")
                ultimo_numero = numero
            elif contador % 50 == 0:  # Heartbeat cada 50 scans
                timestamp = time.strftime("%H:%M:%S")
                print(f"⏱️ [{timestamp}] Monitoreando... (scan #{contador}) - Último: {ultimo_numero}")

            # Mostrar imagen ampliada cada 10 scans para evitar lag
            if contador % 10 == 0:
                preview = cv2.resize(img, (img.shape[1] * 15, img.shape[0] * 15), interpolation=cv2.INTER_NEAREST)

                # Agregar información al preview
                info_img = cv2.copyMakeBorder(preview, 100, 0, 0, 200, cv2.BORDER_CONSTANT, value=(50, 50, 50))
                cv2.putText(info_img, f"Numero: {numero}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
                cv2.putText(info_img, f"Scan: {contador}", (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)
                cv2.putText(info_img, f"Ultimo: {ultimo_numero}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                            (255, 255, 0), 1)

                cv2.imshow("Scan Tiempo Real - Q para salir", info_img)

            # Check para salir
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print(f"❌ Error capturando imagen (scan #{contador})")

        # Scan cada 200ms (5 veces por segundo)
        time.sleep(0.2)

except KeyboardInterrupt:
    print("\n🛑 Scan detenido por el usuario")
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    cv2.destroyAllWindows()
    print(f"\n📊 Estadísticas finales:")
    print(f"   Total de scans: {contador}")
    print(f"   Último número detectado: {ultimo_numero}")
    print("👋 Scan finalizado")