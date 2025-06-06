import cv2
import numpy as np
from vision.screen_capture import capture_screen
from vision.window_region import obtener_region_chrome
from vision.detector import detect_number_from_image

# Variables globales para el click
coordenadas_click = None
imagen_chrome = None
region_chrome = None

def mouse_callback(event, x, y, flags, param):
    """Callback para capturar clicks del mouse"""
    global coordenadas_click, imagen_chrome, region_chrome

    if event == cv2.EVENT_LBUTTONDOWN:  # Click izquierdo
        # Convertir coordenadas de la imagen escalada a coordenadas reales
        scale = param

        # Coordenadas reales en la captura de Chrome
        real_x = int(x / scale)
        real_y = int(y / scale)

        # Coordenadas absolutas en la pantalla
        abs_x = region_chrome["left"] + real_x
        abs_y = region_chrome["top"] + real_y

        coordenadas_click = {
            "absoluta": (abs_x, abs_y),
            "relativa": (real_x, real_y),
            "click_en_imagen": (x, y)
        }

        print(f"\n🎯 CLICK DETECTADO!")
        print(f"   Coordenadas absolutas: ({abs_x}, {abs_y})")
        print(f"   Coordenadas relativas: ({real_x}, {real_y})")

        # Mostrar preview de la región clickeada
        mostrar_preview_region(abs_x, abs_y)

def mostrar_preview_region(center_x, center_y, width=40, height=40):
    """Muestra preview de la región alrededor del click"""
    # Calcular región centrada en el click
    region_test = {
        "left": center_x - width // 2,
        "top": center_y - height // 2,
        "width": width,
        "height": height
    }

    # Capturar región
    img_region = capture_screen(region_test)

    if img_region is not None and img_region.size > 0:
        # Detectar número
        numero = detect_number_from_image(img_region)

        # Ampliar imagen
        scale = 15
        preview = cv2.resize(img_region, (width * scale, height * scale), interpolation=cv2.INTER_NEAREST)

        # Agregar información
        info_img = cv2.copyMakeBorder(preview, 100, 0, 0, 0, cv2.BORDER_CONSTANT, value=(50, 50, 50))

        cv2.putText(info_img, f"Region: {width}x{height}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(info_img, f"Centro: ({center_x}, {center_y})", (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(info_img, f"Numero: '{numero}'", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("Preview Region Clickeada", info_img)

        print(f"   Número detectado: '{numero}'")
        print(f"   Región: left={region_test['left']}, top={region_test['top']}, width={width}, height={height}")

def calibrar_con_click():
    """Calibración haciendo click donde aparece el número ganador"""
    global coordenadas_click, imagen_chrome, region_chrome

    region_chrome = obtener_region_chrome()
    print(f"🖥️ Chrome detectado: {region_chrome}")

    print("\n🎯 CALIBRACIÓN CON CLICK")
    print("=" * 50)
    print("1. Se abrirá una ventana con la captura de Chrome")
    print("2. HAZ CLICK exactamente donde aparece el NÚMERO GANADOR")
    print("3. Verás un preview de la región que seleccionaste")
    print("4. Presiona ENTER para confirmar o ESC para cancelar")
    print("5. R para refresh/actualizar la captura")
    print("=" * 50)
    print("💡 El número ganador aparece después de cada spin de ruleta")
    print("💡 Busca un número (0-36) que cambie después de cada ronda")

    while True:
        # Capturar Chrome completo
        imagen_chrome = capture_screen(region_chrome)

        if imagen_chrome is None or imagen_chrome.size == 0:
            print("❌ Error capturando Chrome")
            break

        # Escalar imagen para que quepa en pantalla
        height, width = imagen_chrome.shape[:2]
        max_width, max_height = 1400, 900
        scale = min(max_width / width, max_height / height, 1.0)

        new_width = int(width * scale)
        new_height = int(height * scale)

        img_scaled = cv2.resize(imagen_chrome, (new_width, new_height))

        # Agregar instrucciones en la imagen
        overlay = img_scaled.copy()
        cv2.rectangle(overlay, (10, 10), (500, 100), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, img_scaled, 0.3, 0, img_scaled)

        cv2.putText(img_scaled, "HAZ CLICK en el NUMERO GANADOR", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(img_scaled, "ENTER=confirmar, ESC=salir, R=refresh", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(img_scaled, "C=Cambiar tamaño de región", (20, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Configurar callback del mouse
        cv2.imshow("Chrome - Click en el Numero Ganador", img_scaled)
        cv2.setMouseCallback("Chrome - Click en el Numero Ganador", mouse_callback, scale)

        key = cv2.waitKey(0) & 0xFF

        if key == 13:  # ENTER - confirmar
            if coordenadas_click:
                print("\n✅ COORDENADAS CONFIRMADAS")
                guardar_coordenadas()
                break
            else:
                print("❌ Primero haz click en algún lugar")

        elif key == 27:  # ESC - salir
            print("❌ Calibración cancelada")
            break

        elif key == ord('r'):  # R - refresh
            print("🔄 Actualizando captura...")
            continue

        elif key == ord('c'):  # C - cambiar tamaño de región
            cambiar_tamaño_region()

    cv2.destroyAllWindows()

def cambiar_tamaño_region():
    """Permite cambiar el tamaño de la región de captura"""
    global width, height
    print("\n📏 CAMBIAR TAMAÑO DE REGIÓN")
    print("=" * 50)
    print("Selecciona el nuevo tamaño de la región:")
    print("1. Pequeño (60x30) - números de 1 dígito")
    print("2. Mediano (80x40) - números de 1-2 dígitos")
    print("3. Grande (100x50) - números grandes o con efectos")
    print("4. Personalizado")

    while True:
        opcion = input("Opción (1-4): ").strip()

        if opcion == "1":
            return 60, 30
        elif opcion == "2":
            return 80, 40
        elif opcion == "3":
            return 100, 50
        elif opcion == "4":
            try:
                width = int(input("Ancho: "))
                height = int(input("Alto: "))
                return width, height
            except ValueError:
                print("❌ Valores inválidos")
        else:
            print("❌ Opción inválida")

def guardar_coordenadas():
    """Guarda las coordenadas y genera código para main.py"""
    global coordenadas_click, region_chrome

    if not coordenadas_click:
        print("❌ No hay coordenadas para guardar")
        return

    abs_x, abs_y = coordenadas_click["absoluta"]

    # Ofrecer diferentes tamaños de región
    width, height = cambiar_tamaño_region()

    # Calcular región final (centrada en el click)
    final_left = abs_x - width // 2
    final_top = abs_y - height // 2

    # Mostrar preview final
    region_final = {
        "left": final_left,
        "top": final_top,
        "width": width,
        "height": height
    }

    img_final = capture_screen(region_final)
    if img_final is not None and img_final.size > 0:
        numero_final = detect_number_from_image(img_final)

        preview = cv2.resize(img_final, (width * 15, height * 15), interpolation=cv2.INTER_NEAREST)
        cv2.imshow("Región Final - Presiona cualquier tecla", preview)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        print(f"\n✅ CONFIGURACIÓN FINAL:")
        print(f"Coordenadas absolutas: ({final_left}, {final_top})")
        print(f"Coordenadas relativas: ({final_left - region_chrome['left']}, {final_top - region_chrome['top']})")
        print(f"Tamaño: {width}x{height}")
        print(f"Número detectado: '{numero_final}'")

        print(f"\n📋 CÓDIGO PARA main.py:")
        print("=" * 50)
        print(f"region_numero = {{")
        print(f"    'left': {final_left},")
        print(f"    'top': {final_top},")
        print(f"    'width': {width},")
        print(f"    'height': {height}")
        print(f"}}")
        print("=" * 50)

        # Ofrecer actualizar automáticamente
        actualizar = input("\n¿Actualizar main.py automáticamente? (s/n): ").strip().lower()
        if actualizar == 's':
            actualizar_main_py(final_left, final_top, width, height)

def actualizar_main_py(left, top, width, height):
    """Actualiza automáticamente main.py con las nuevas coordenadas"""
    try:
        # Leer main.py
        with open('main.py', 'r', encoding='utf-8') as f:
            contenido = f.read()

        # Buscar y reemplazar la región del número
        import re

        patron = r'region_numero = \{[^}]+\}'
        nuevo_codigo = f'''region_numero = {{
    "left": {left},
    "top": {top},
    "width": {width},
    "height": {height}
}}'''

        contenido_actualizado = re.sub(patron, nuevo_codigo, contenido)

        # Guardar backup
        with open('main.py.backup', 'w', encoding='utf-8') as f:
            f.write(contenido)

        # Guardar nuevo main.py
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(contenido_actualizado)

        print("✅ main.py actualizado exitosamente")
        print("💾 Backup guardado como main.py.backup")

    except Exception as e:
        print(f"❌ Error actualizando main.py: {e}")
        print("⚠️ Copia manualmente el código mostrado arriba")

if __name__ == "__main__":
    calibrar_con_click()
