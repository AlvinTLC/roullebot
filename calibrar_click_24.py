import pyautogui
import time

def calibrar_click_numero_24():
    """Calibra el click exacto para el número 24"""

    # Coordenadas actuales
    x, y = 3050, 605

    print("🎯 CALIBRADOR DE CLICK - NÚMERO 24")
    print("=" * 50)
    print("Usa las teclas para ajustar la posición del click:")
    print("W/S: Arriba/Abajo")
    print("A/D: Izquierda/Derecha")
    print("SHIFT + tecla: Movimiento rápido (5px)")
    print("ENTER: Probar click en posición actual")
    print("ESPACIO: Mostrar posición actual")
    print("Q: Guardar y salir")
    print("ESC: Salir sin guardar")
    print("=" * 50)
    print(f"Posición inicial: ({x}, {y})")
    print("Ajusta hasta que haga click exactamente en el 24")

    # Configurar pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.01

    while True:
        try:
            # Mostrar posición actual
            print(f"\n📍 Posición actual: ({x}, {y})")
            print("Esperando comando... (W/A/S/D para mover, ENTER para probar, Q para guardar, ESC para salir)")

            # Leer comando
            comando = input(">>> ").strip().lower()

            # Movimiento normal (1 pixel)
            if comando == 'w':
                y -= 1
                print(f"⬆️ Movido arriba: ({x}, {y})")
            elif comando == 's':
                y += 1
                print(f"⬇️ Movido abajo: ({x}, {y})")
            elif comando == 'a':
                x -= 1
                print(f"⬅️ Movido izquierda: ({x}, {y})")
            elif comando == 'd':
                x += 1
                print(f"➡️ Movido derecha: ({x}, {y})")

            # Movimiento rápido (5 pixels)
            elif comando in ['shift+w', 'sw']:
                y -= 5
                print(f"⬆️⬆️ Movido arriba rápido: ({x}, {y})")
            elif comando in ['shift+s', 'ss']:
                y += 5
                print(f"⬇️⬇️ Movido abajo rápido: ({x}, {y})")
            elif comando in ['shift+a', 'sa']:
                x -= 5
                print(f"⬅️⬅️ Movido izquierda rápido: ({x}, {y})")
            elif comando in ['shift+d', 'sd']:
                x += 5
                print(f"➡️➡️ Movido derecha rápido: ({x}, {y})")

            # Movimiento personalizado
            elif ',' in comando:
                try:
                    dx, dy = map(int, comando.split(','))
                    x += dx
                    y += dy
                    print(f"🎯 Movido por ({dx}, {dy}): nueva posición ({x}, {y})")
                except ValueError:
                    print("❌ Formato inválido. Usa: dx,dy (ej: -5,3)")

            # Probar click
            elif comando in ['', 'enter', 'test']:
                print(f"🖱️ Probando click en ({x}, {y})...")
                print("⚠️ Tienes 3 segundos para ir a la mesa de ruleta...")

                # Countdown
                for i in range(3, 0, -1):
                    print(f"{i}...")
                    time.sleep(1)

                # Hacer click
                pyautogui.click(x, y)
                print(f"✅ Click realizado en ({x}, {y})")
                print("¿El click cayó exactamente en el número 24? (s/n)")

                respuesta = input(">>> ").strip().lower()
                if respuesta in ['s', 'si', 'yes', 'y']:
                    print("🎉 ¡Perfecto! Posición calibrada correctamente")
                else:
                    print("🔧 Continúa ajustando la posición...")

            # Mostrar posición
            elif comando in [' ', 'espacio', 'pos']:
                print(f"📍 Posición actual: ({x}, {y})")

            # Guardar y salir
            elif comando in ['q', 'quit', 'guardar']:
                print(f"\n✅ COORDENADAS FINALES CALIBRADAS:")
                print(f"x, y = {x}, {y}")
                print(f"\n📋 CÓDIGO PARA main.py:")
                print("=" * 50)
                print(f"def apostar_al_24():")
                print(f"    x, y = {x}, {y}")
                print(f"    pyautogui.click(x, y)")
                print("=" * 50)
                break

            # Salir sin guardar
            elif comando in ['esc', 'escape', 'salir']:
                print("❌ Calibración cancelada")
                break

            # Ayuda
            elif comando in ['help', 'h', '?']:
                print("\n🆘 COMANDOS DISPONIBLES:")
                print("W/A/S/D: Mover 1 pixel")
                print("SHIFT+W/S/A/D: Mover 5 pixels")
                print("dx,dy: Mover dx en X, dy en Y")
                print("ENTER: Probar click")
                print("Q: Guardar y salir")
                print("ESC: Salir sin guardar")
                print("HELP: Mostrar esta ayuda")

            else:
                print("❓ Comando no reconocido. Usa 'help' para ver comandos.")

            # Límites de pantalla
            x = max(0, min(x, pyautogui.size().width))
            y = max(0, min(y, pyautogui.size().height))

        except KeyboardInterrupt:
            print("\n❌ Calibración cancelada")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    calibrar_click_numero_24()
