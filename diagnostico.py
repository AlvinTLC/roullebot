import cv2
import time
from vision.screen_capture import capture_screen
from vision.window_region import obtener_region_chrome
from vision.detector import detect_number_from_image


def mostrar_multiples_regiones():
    """Muestra múltiples regiones para encontrar el número ganador"""
    region_chrome = obtener_region_chrome()
    print(f"🖥️ Chrome: {region_chrome}")

    # Diferentes regiones a probar (relativas a Chrome)
    regiones = [
        {"name": "Actual (600,240)", "x": 600, "y": 240, "w": 60, "h": 60},
        {"name": "Arriba (600,200)", "x": 600, "y": 200, "w": 80, "h": 40},
        {"name": "Más arriba (600,160)", "x": 600, "y": 160, "w": 80, "h": 40},
        {"name": "Centro (640,250)", "x": 640, "y": 250, "w": 80, "h": 40},
        {"name": "Izquierda (550,220)", "x": 550, "y": 220, "w": 80, "h": 40},
        {"name": "Derecha (650,220)", "x": 650, "y": 220, "w": 80, "h": 40},
    ]

    print("\n🔍 DIAGNÓSTICO - Mostrando múltiples regiones")
    print("Presiona ESPACIO para siguiente región, Q para salir")

    region_idx = 0

    while True:
        if region_idx >= len(regiones):
            region_idx = 0

        region_info = regiones[region_idx]

        # Calcular coordenadas absolutas
        abs_x = region_chrome["left"] + region_info["x"]
        abs_y = region_chrome["top"] + region_info["y"]

        region_captura = {
            "left": abs_x,
            "top": abs_y,
            "width": region_info["w"],
            "height": region_info["h"]
        }

        # Capturar imagen
        img = capture_screen(region_captura)

        if img is not None and img.size > 0:
            # Detectar número
            numero = detect_number_from_image(img)

            # Ampliar imagen
            scale = 12
            preview = cv2.resize(img, (region_info["w"] * scale, region_info["h"] * scale),
                                 interpolation=cv2.INTER_NEAREST)

            # Agregar información
            info_img = cv2.copyMakeBorder(preview, 120, 0, 0, 200, cv2.BORDER_CONSTANT, value=(50, 50, 50))

            # Texto de información
            cv2.putText(info_img, f"Region: {region_info['name']}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (255, 255, 255), 2)
            cv2.putText(info_img, f"Rel: ({region_info['x']}, {region_info['y']})", (10, 60), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (255, 255, 255), 1)
            cv2.putText(info_img, f"Abs: ({abs_x}, {abs_y})", (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255),
                        1)
            cv2.putText(info_img, f"Numero: '{numero}'", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            cv2.imshow("Diagnostico - ESPACIO=siguiente, Q=salir", info_img)

            print(f"📍 {region_info['name']} -> Número detectado: '{numero}'")

        key = cv2.waitKey(0) & 0xFF

        if key == ord(' '):  # ESPACIO - siguiente región
            region_idx += 1
        elif key == ord('q'):  # Q - salir
            break
        elif key == ord('r'):  # R - repetir actual
            pass

    cv2.destroyAllWindows()


def captura_continua_actual():
    """Captura continua de la región actual para ver cambios"""
    region_chrome = obtener_region_chrome()

    # Región actual que está funcionando
    region_numero = {
        "left": region_chrome["left"] + 600,
        "top": region_chrome["top"] + 240,
        "width": 60,
        "height": 60
    }

    print(f"🎯 Captura continua de región: {region_numero}")
    print("Observa los cambios en tiempo real (Q para salir)")

    ultimo_numero = None
    contador = 0

    while True:
        img = capture_screen(region_numero)

        if img is not None and img.size > 0:
            numero = detect_number_from_image(img)
            contador += 1

            if numero != ultimo_numero:
                print(f"🔄 Cambio #{contador}: '{ultimo_numero}' -> '{numero}'")
                ultimo_numero = numero

            # Mostrar imagen ampliada
            preview = cv2.resize(img, (img.shape[1] * 15, img.shape[0] * 15), interpolation=cv2.INTER_NEAREST)

            # Agregar número detectado al preview
            cv2.putText(preview, f"Numero: {numero}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(preview, f"Frame: {contador}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)

            cv2.imshow("Captura Continua - Q para salir", preview)

        if cv2.waitKey(100) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


def menu_diagnostico():
    """Menú de opciones de diagnóstico"""
    while True:
        print("\n" + "=" * 50)
        print("🔍 DIAGNÓSTICO DEL DETECTOR DE NÚMEROS")
        print("=" * 50)
        print("1. Ver múltiples regiones (encontrar número ganador)")
        print("2. Captura continua (región actual)")
        print("3. Salir")
        print("=" * 50)

        opcion = input("Selecciona opción (1-3): ").strip()

        try:
            if opcion == "1":
                mostrar_multiples_regiones()
            elif opcion == "2":
                captura_continua_actual()
            elif opcion == "3":
                print("👋 Diagnóstico terminado")
                break
            else:
                print("❌ Opción no válida")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    menu_diagnostico()