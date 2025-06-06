from vision.screen_capture import capture_screen
from vision.window_region import obtener_region_chrome
import cv2
import time

region = obtener_region_chrome()
print(f"🖥️ Capturando Chrome en: {region}")

while True:
    img = capture_screen(region)
    cv2.imshow("Streaming Chrome", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(0.1)  # Captura cada 100ms (ajusta si quieres más velocidad)

cv2.destroyAllWindows()
