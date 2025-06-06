import cv2
import time
from vision.screen_capture import capture_screen
from utils.ventana_chrome import abrir_y_posicionar_chrome

# Posicionar ventana de Chrome
abrir_y_posicionar_chrome(x=0, y=0, width=1280, height=720)

# Región a capturar (ajústalo si cambia)
region_chrome = {
    "left": 0,
    "top": 0,
    "width": 1280,
    "height": 720
}

print("🎥 Mostrando vista en vivo de la ventana de Chrome... (presiona Q para salir)")
while True:
    frame = capture_screen(region_chrome)
    cv2.imshow("Vista Chrome", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(0.03)  # 30 fps aprox

cv2.destroyAllWindows()
