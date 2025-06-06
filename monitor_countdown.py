from vision.screen_capture import capture_screen
from vision.detector import detect_number_from_image
import time
import cv2

# Coordenadas exactas del COUNTDOWN/TIMER (corregidas)
region_countdown = {"left": 2966, "top": 509, "width": 60, "height": 60}

print("⏰ MONITOR COUNTDOWN - Solo timer de la ruleta")
print(f"Región: {region_countdown}")
print("Ctrl+C para salir")
print("-" * 50)

ultimo_countdown = None
contador = 0

try:
    while True:
        img = capture_screen(region_countdown)

        if img is not None and img.size > 0:
            countdown = detect_number_from_image(img).strip()
            contador += 1

            if countdown and countdown != ultimo_countdown:
                timestamp = time.strftime("%H:%M:%S")

                # Interpretar el countdown
                if countdown.isdigit():
                    num_countdown = int(countdown)
                    if num_countdown == 0:
                        print(f"🚀 [{timestamp}] ¡JUEGO INICIANDO! Countdown: {countdown}")
                    elif num_countdown == 1:
                        print(f"⚡ [{timestamp}] ¡1 SEGUNDO! Countdown: {countdown}")
                    elif num_countdown <= 3:
                        print(f"🔥 [{timestamp}] ¡ÚLTIMOS SEGUNDOS! Countdown: {countdown}")
                    elif num_countdown <= 5:
                        print(f"⚠️  [{timestamp}] ¡APÚRATE! Countdown: {countdown}")
                    elif num_countdown <= 10:
                        print(f"⏰ [{timestamp}] Countdown: {countdown}")
                    elif num_countdown <= 20:
                        print(f"⏳ [{timestamp}] Preparándose... Countdown: {countdown}")
                    else:
                        print(f"💤 [{timestamp}] Esperando nueva ronda - Countdown: {countdown}")
                else:
                    print(f"❓ [{timestamp}] Countdown: {countdown}")

                ultimo_countdown = countdown

            # Mostrar preview cada 20 scans para evitar lag
            if contador % 20 == 0:
                preview = cv2.resize(img, (img.shape[1] * 20, img.shape[0] * 20), interpolation=cv2.INTER_NEAREST)

                # Agregar información
                info_img = cv2.copyMakeBorder(preview, 100, 0, 0, 300, cv2.BORDER_CONSTANT, value=(50, 50, 50))
                cv2.putText(info_img, f"Countdown: {countdown}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0),
                            2)
                cv2.putText(info_img, f"Scan: {contador} (~25 FPS)", (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                            (255, 255, 255), 1)

                # Indicador de estado
                if countdown and countdown.isdigit():
                    num = int(countdown)
                    if num == 0:
                        cv2.putText(info_img, "INICIANDO!", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    elif num <= 5:
                        cv2.putText(info_img, "ULTIMO MOMENTO!", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255),
                                    2)
                    elif num <= 10:
                        cv2.putText(info_img, "Preparate...", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
                    else:
                        cv2.putText(info_img, "Esperando...", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200),
                                    1)

                cv2.imshow("Monitor Countdown ALTA VELOCIDAD - Q para salir", info_img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        time.sleep(0.04)  # 25 veces por segundo - MUCHO MÁS RÁPIDO

except KeyboardInterrupt:
    print(f"\n🛑 Monitor finalizado")
    print(f"📊 Total scans: {contador}")
    print(f"⏰ Último countdown: {ultimo_countdown}")
finally:
    cv2.destroyAllWindows()