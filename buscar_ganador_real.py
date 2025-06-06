import cv2
import time
from vision.screen_capture import capture_screen
from vision.window_region import obtener_region_chrome
from vision.detector import detect_number_from_image


def buscar_todas_las_regiones_con_numeros():
    """Busca múltiples regiones que contengan números para encontrar el ganador real"""
    region_chrome = obtener_region_chrome()
    print(f"🖥️ Chrome: {region_chrome}")

    # Definir múltiples regiones para explorar
    # Expandir búsqueda alrededor del área actual y otras zonas comunes
    regiones_busqueda = []

    # Alrededor de la región actual (2861, 551)
    for x_offset in [-100, -50, 0, 50, 100]:
        for y_offset in [-50, -25, 0, 25, 50]:
            regiones_busqueda.append({
                "name": f"Offset({x_offset},{y_offset})",
                "left": 2861 + x_offset,
                "top": 551 + y_offset,
                "width": 80,
                "height": 50
            })

    # Zonas específicas basadas en la interfaz visible de Stake Roulette
    zonas_especiales = [
        # Números rojos arriba de la ruleta (donde veo "6" y "3")
        {"name": "Numero-Rojo-Izq", "left": region_chrome["left"] + 400, "top": region_chrome["top"] + 350, "width": 80,
         "height": 80},
        {"name": "Numero-Rojo-Der", "left": region_chrome["left"] + 500, "top": region_chrome["top"] + 350, "width": 80,
         "height": 80},
        {"name": "Numero-Rojo-Centro", "left": region_chrome["left"] + 450, "top": region_chrome["top"] + 320,
         "width": 100, "height": 100},

        # Centro de la mesa de ruleta
        {"name": "Centro-Mesa", "left": region_chrome["left"] + 640, "top": region_chrome["top"] + 400, "width": 120,
         "height": 80},
        {"name": "Centro-Ruleta", "left": region_chrome["left"] + 580, "top": region_chrome["top"] + 350, "width": 160,
         "height": 120},

        # Área de historial (números recientes abajo)
        {"name": "Historial-Centro", "left": region_chrome["left"] + 640, "top": region_chrome["top"] + 680,
         "width": 100, "height": 50},
        {"name": "Historial-Izq", "left": region_chrome["left"] + 500, "top": region_chrome["top"] + 680, "width": 80,
         "height": 50},
        {"name": "Historial-Der", "left": region_chrome["left"] + 780, "top": region_chrome["top"] + 680, "width": 80,
         "height": 50},

        # Panel derecho (ruleta digital)
        {"name": "Panel-Derecho-Centro", "left": region_chrome["left"] + 1100, "top": region_chrome["top"] + 400,
         "width": 120, "height": 80},
        {"name": "Panel-Derecho-Arriba", "left": region_chrome["left"] + 1100, "top": region_chrome["top"] + 300,
         "width": 120, "height": 80},

        # Área superior central (posible resultado destacado)
        {"name": "Superior-Centro", "left": region_chrome["left"] + 640, "top": region_chrome["top"] + 250,
         "width": 140, "height": 90},
        {"name": "Superior-Izq", "left": region_chrome["left"] + 500, "top": region_chrome["top"] + 250, "width": 120,
         "height": 90},
        {"name": "Superior-Der", "left": region_chrome["left"] + 780, "top": region_chrome["top"] + 250, "width": 120,
         "height": 90},
    ]

    regiones_busqueda.extend(zonas_especiales)

    print(f"🔍 Buscando en {len(regiones_busqueda)} regiones diferentes...")
    print("🎯 Objetivo: Encontrar región que muestre número ESTABLE después de cada ronda")
    print("⏱️ Cada región se monitoreará por 10 segundos")
    print("ESC para salir, ESPACIO para siguiente región")

    resultados = []

    for i, region in enumerate(regiones_busqueda):
        print(f"\n📍 [{i + 1}/{len(regiones_busqueda)}] Probando: {region['name']}")
        print(f"   Región: left={region['left']}, top={region['top']}")

        # Monitorear esta región por 10 segundos
        numeros_detectados = []
        inicio = time.time()

        while time.time() - inicio < 10:
            img = capture_screen(region)

            if img is not None and img.size > 0:
                numero = detect_number_from_image(img).strip()
                if numero and numero.isdigit():
                    numeros_detectados.append((time.time(), numero))

                # Mostrar preview
                preview = cv2.resize(img, (region["width"] * 8, region["height"] * 8), interpolation=cv2.INTER_NEAREST)
                info_img = cv2.copyMakeBorder(preview, 100, 0, 0, 300, cv2.BORDER_CONSTANT, value=(50, 50, 50))

                cv2.putText(info_img, f"{region['name']}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                cv2.putText(info_img, f"Numero: {numero}", (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(info_img, f"Tiempo: {10 - (time.time() - inicio):.1f}s", (10, 80), cv2.FONT_HERSHEY_SIMPLEX,
                            0.6, (255, 255, 0), 1)

                cv2.imshow("Buscando Ganador Real - ESC=salir, SPACE=siguiente", info_img)

            key = cv2.waitKey(50) & 0xFF
            if key == 27:  # ESC
                cv2.destroyAllWindows()
                return
            elif key == ord(' '):  # ESPACIO
                break

        # Analizar resultados de esta región
        if numeros_detectados:
            from collections import Counter
            conteo_numeros = Counter([n[1] for n in numeros_detectados])
            cambios = len(set([n[1] for n in numeros_detectados]))

            # Calcular estabilidad
            if cambios <= 2:
                estabilidad = "ALTA (Posible ganador real)"
                color = "🟢"
            elif cambios <= 5:
                estabilidad = "MEDIA (Podría ser ganador)"
                color = "🟡"
            else:
                estabilidad = "BAJA (Probablemente timer/contador)"
                color = "🔴"

            resultado = {
                "region": region,
                "numeros": numeros_detectados,
                "conteo": conteo_numeros,
                "cambios": cambios,
                "estabilidad": estabilidad
            }
            resultados.append(resultado)

            print(f"   {color} Números únicos: {cambios}")
            print(f"   {color} Más frecuente: {conteo_numeros.most_common(1)[0] if conteo_numeros else 'Ninguno'}")
            print(f"   {color} Estabilidad: {estabilidad}")
        else:
            print("   ❌ No se detectaron números")

    cv2.destroyAllWindows()

    # Mostrar resumen final
    print(f"\n" + "=" * 80)
    print(f"📊 RESUMEN: MEJORES CANDIDATOS PARA NÚMERO GANADOR")
    print(f"=" * 80)

    # Ordenar por estabilidad (menos cambios = mejor)
    resultados.sort(key=lambda x: x["cambios"])

    for i, resultado in enumerate(resultados[:5]):  # Top 5
        region = resultado["region"]
        print(f"\n🏆 #{i + 1}: {region['name']}")
        print(
            f"   📍 Región: left={region['left']}, top={region['top']}, width={region['width']}, height={region['height']}")
        print(f"   📊 Números únicos: {resultado['cambios']}")
        print(f"   🎯 Estabilidad: {resultado['estabilidad']}")
        print(f"   📋 Más frecuente: {resultado['conteo'].most_common(1)[0] if resultado['conteo'] else 'N/A'}")

    if resultados:
        mejor = resultados[0]
        print(f"\n✅ RECOMENDACIÓN: Usar región '{mejor['region']['name']}'")
        print(f"📋 CÓDIGO PARA main.py:")
        print(f"region_numero = {mejor['region']}")


def monitor_multiple_regions():
    """Monitorea 4 regiones simultáneamente para comparar"""

    # Regiones específicas para comparar
    regiones = [
        {"name": "Actual", "left": 2861, "top": 551, "width": 60, "height": 60, "color": (0, 255, 0)},
        {"name": "Arriba", "left": 2861, "top": 500, "width": 80, "height": 50, "color": (255, 0, 0)},
        {"name": "Centro", "left": 2800, "top": 550, "width": 80, "height": 50, "color": (0, 0, 255)},
        {"name": "Derecha", "left": 2900, "top": 551, "width": 80, "height": 50, "color": (255, 255, 0)},
    ]

    print("🎯 MONITOR MÚLTIPLE - Comparando 4 regiones")
    print("🔍 Busca la región que muestre números ESTABLES")
    print("Q para salir")

    while True:
        # Crear imagen combinada
        combined_height = 300
        combined_width = len(regiones) * 200
        combined = np.zeros((combined_height, combined_width, 3), dtype=np.uint8)

        for i, region in enumerate(regiones):
            img = capture_screen(region)

            if img is not None and img.size > 0:
                numero = detect_number_from_image(img).strip()

                # Redimensionar para el combo
                preview = cv2.resize(img, (180, 180), interpolation=cv2.INTER_NEAREST)

                # Posición en imagen combinada
                x_start = i * 200
                combined[10:190, x_start + 10:x_start + 190] = preview

                # Agregar información
                cv2.putText(combined, region['name'], (x_start + 10, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            region['color'], 2)
                cv2.putText(combined, f"Num: {numero}", (x_start + 10, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                            (255, 255, 255), 1)
                cv2.putText(combined, f"{region['left']},{region['top']}", (x_start + 10, 270),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.imshow("Monitor Múltiple - Q para salir", combined)

        if cv2.waitKey(100) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


def menu_busqueda():
    """Menú para buscar el número ganador real"""
    while True:
        print("\n" + "=" * 60)
        print("🔍 BUSCAR NÚMERO GANADOR REAL")
        print("=" * 60)
        print("El sistema actual captura un timer/contador, no el ganador")
        print("Necesitamos encontrar dónde aparece el número ganador real")
        print()
        print("1. Búsqueda exhaustiva (probar muchas regiones)")
        print("2. Monitor múltiple (comparar 4 regiones)")
        print("3. Salir")
        print("=" * 60)

        opcion = input("Selecciona opción (1-3): ").strip()

        if opcion == "1":
            buscar_todas_las_regiones_con_numeros()
        elif opcion == "2":
            import numpy as np
            monitor_multiple_regions()
        elif opcion == "3":
            break
        else:
            print("❌ Opción inválida")


if __name__ == "__main__":
    menu_busqueda()