import cv2
import time
from vision.screen_capture import capture_screen
from vision.window_region import obtener_region_chrome
from vision.detector import detect_number_from_image, detect_number_debug


def mostrar_grilla_chrome():
    """Muestra una grilla sobre la ventana de Chrome para calibración"""
    region_chrome = obtener_region_chrome()
    print(f"🖥️ Chrome: {region_chrome}")

    while True:
        img = capture_screen(region_chrome)

        # Dibujar grilla
        height, width = img.shape[:2]
        step = 50

        # Líneas verticales
        for x in range(0, width, step):
            cv2.line(img, (x, 0), (x, height), (0, 255, 0), 1)
            if x % 100 == 0:
                cv2.putText(img, str(x), (x + 5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Líneas horizontales
        for y in range(0, height, step):
            cv2.line(img, (0, y), (width, y), (0, 255, 0), 1)
            if y % 100 == 0:
                cv2.putText(img, str(y), (5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        cv2.imshow("Grilla Chrome (Q para salir)", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(0.1)

    cv2.destroyAllWindows()


def calibrar_region_interactivo():
    """Calibración interactiva de la región del número"""
    region_chrome = obtener_region_chrome()

    # Coordenadas iniciales (área del número ganador)
    x, y = 730, 450  # Absolutas (arriba del countdown)
    width, height = 80, 40

    print("\n🎯 CALIBRACIÓN INTERACTIVA")
    print("Usa las teclas para mover la región:")
    print("WASD: mover región")
    print("IJKL: ajustar tamaño")
    print("ENTER: probar detección")
    print("Q: guardar y salir")
    print("ESC: salir sin guardar")

    while True:
        # Usar coordenadas absolutas directamente
        region_numero = {
            "left": x,
            "top": y,
            "width": width,
            "height": height
        }

        # Capturar imagen de la región
        img_region = capture_screen(region_numero)

        if img_region is not None and img_region.size > 0:
            # Ampliar para visualización
            scale = 8
            preview = cv2.resize(img_region, (width * scale, height * scale), interpolation=cv2.INTER_NEAREST)

            # Agregar información
            info_img = cv2.copyMakeBorder(preview, 100, 0, 0, 200, cv2.BORDER_CONSTANT, value=(50, 50, 50))

            # Texto de información
            cv2.putText(info_img, f"Pos abs: ({x}, {y})", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(info_img, f"Tamaño: {width}x{height}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255),
                        1)
            cv2.putText(info_img, "Area: Numero ganador", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)

            cv2.imshow("Calibración - Región del Número", info_img)

        key = cv2.waitKey(30) & 0xFF

        # Movimiento
        if key == ord('w'):
            y -= 5
        elif key == ord('s'):
            y += 5
        elif key == ord('a'):
            x -= 5
        elif key == ord('d'):
            x += 5

        # Tamaño
        elif key == ord('i'):
            height -= 5
        elif key == ord('k'):
            height += 5
        elif key == ord('j'):
            width -= 5
        elif key == ord('l'):
            width += 5

        # Probar detección
        elif key == 13:  # ENTER
            numero = detect_number_from_image(img_region)
            print(f"🔍 Número detectado: '{numero}'")

        # Salir
        elif key == ord('q'):
            print(f"\n✅ COORDENADAS CALIBRADAS:")
            print(f"Absolutas: left={x}, top={y}")
            print(f"Tamaño: width={width}, height={height}")
            break
        elif key == 27:  # ESC
            print("\n❌ Calibración cancelada")
            break

    cv2.destroyAllWindows()


def probar_coordenadas_multiples():
    """Prueba múltiples coordenadas para encontrar la mejor"""
    region_chrome = obtener_region_chrome()

    # Lista de coordenadas a probar
    coordenadas = [
        (730, 450),  # Número ganador (arriba del countdown)
        (740, 455),  # Variación 1
        (720, 445),  # Variación 2
        (750, 460),  # Variación 3
        (750, 415),  # Coordenadas anteriores
        (953, 441),  # Coordenadas originales de scan.py
    ]

    print("🧪 PROBANDO MÚLTIPLES COORDENADAS...")

    for i, (test_x, test_y) in enumerate(coordenadas):
        # Todas las coordenadas son absolutas ahora
        region_test = {"left": test_x, "top": test_y, "width": 80, "height": 40}
        print(f"\n{i + 1}. Probando coordenadas absolutas: ({test_x}, {test_y})")

        img = capture_screen(region_test)
        if img is not None and img.size > 0:
            numero, debug_imgs = detect_number_debug(img)
            print(f"   Resultado: '{numero}'")

            # Mostrar imagen
            preview = cv2.resize(img, (img.shape[1] * 8, img.shape[0] * 8), interpolation=cv2.INTER_NEAREST)
            cv2.imshow(f"Test {i + 1} - Coord: ({test_x}, {test_y})", preview)
            cv2.waitKey(1000)  # Mostrar por 1 segundo
        else:
            print("   ❌ Error capturando imagen")

    cv2.destroyAllWindows()


def menu_principal():
    """Menú principal de calibración"""
    while True:
        print("\n" + "=" * 50)
        print("🎯 HERRAMIENTA DE CALIBRACIÓN DE RULETA")
        print("=" * 50)
        print("1. Mostrar grilla sobre Chrome")
        print("2. Calibración interactiva")
        print("3. Probar múltiples coordenadas")
        print("4. Salir")
        print("=" * 50)

        opcion = input("Selecciona una opción (1-4): ").strip()

        try:
            if opcion == "1":
                mostrar_grilla_chrome()
            elif opcion == "2":
                calibrar_region_interactivo()
            elif opcion == "3":
                probar_coordenadas_multiples()
            elif opcion == "4":
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción no válida")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    menu_principal()