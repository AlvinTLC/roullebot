"""
Herramienta unificada de calibración multiplataforma
Combina las funcionalidades de calibrar.py, calibrar_click_24.py y calibracion_manual.py
"""

import cv2
import numpy as np
import pyautogui
import json
import os
import sys
import time
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision.screen_capture import capture_screen
from vision.window_region import obtener_region_chrome
from config.platform_config import config


class Calibrator:
    def __init__(self):
        self.config_file = config.config_dir / 'calibration.json'
        self.calibration_data = self.load_calibration()
        
    def load_calibration(self):
        """Carga calibración existente o crea una nueva"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    
                    # Auto-escalar regiones si es Windows con resolución alta
                    if config.is_windows and (config.resolution_info['is_2k'] or config.resolution_info['is_4k']):
                        print(f"🔧 Auto-escalando calibración para {config.get_resolution_info()}")
                        data = config.auto_scale_regions(data)
                        
                    return data
            except:
                pass
        
        # Usar tamaños óptimos según resolución
        optimal_width, optimal_height = config.get_optimal_capture_size()
        countdown_width, countdown_height = config.get_optimal_countdown_size()
        
        return {
            'winner_region': None,
            'countdown_region': None,
            'balance_region': None,
            'total_bet_region': None,
            'repeat_bet_region': None,
            'chip_regions': {},  # Para diferentes valores de fichas
            'bet_positions': {},
            'chrome_offset': {'x': 0, 'y': 0},
            'optimal_capture_size': {'width': optimal_width, 'height': optimal_height},
            'optimal_countdown_size': {'width': countdown_width, 'height': countdown_height}
        }
    
    def save_calibration(self):
        """Guarda la calibración actual"""
        with open(self.config_file, 'w') as f:
            json.dump(self.calibration_data, f, indent=2)
        print(f"✅ Calibración guardada en: {self.config_file}")
    
    def validate_calibration(self):
        """Valida que las coordenadas estén en rangos razonables"""
        issues = []
        
        # Validar regiones
        for region_name in ['winner_region', 'countdown_region', 'balance_region', 'total_bet_region']:
            region = self.calibration_data.get(region_name)
            if region and isinstance(region, dict):
                x, y = region.get('x', 0), region.get('y', 0)
                if not (0 <= x <= 5000 and 0 <= y <= 3000):
                    issues.append(f"❌ {region_name}: coordenadas fuera de rango ({x}, {y})")
        
        # Validar posiciones de apuesta
        bet_positions = self.calibration_data.get('bet_positions', {})
        for numero, pos in bet_positions.items():
            if pos and isinstance(pos, dict):
                x, y = pos.get('x', 0), pos.get('y', 0)
                if not (0 <= x <= 5000 and 0 <= y <= 3000):
                    issues.append(f"❌ Bet position #{numero}: coordenadas fuera de rango ({x}, {y})")
        
        if issues:
            print("⚠️ PROBLEMAS EN CALIBRACIÓN:")
            for issue in issues:
                print(f"   {issue}")
            return False
        else:
            print("✅ Calibración validada correctamente")
            return True
    
    def calibrate_visual_click(self):
        """Calibración visual por click (más intuitiva)"""
        print("\n🎯 CALIBRACIÓN VISUAL POR CLICK")
        print("=" * 50)
        print("1. Se abrirá una ventana mostrando Chrome")
        print("2. Haz click en las áreas que se te indiquen")
        print("3. Presiona 't' para probar coordenadas, 's' para guardar, 'q' para salir")
        
        try:
            chrome_region = obtener_region_chrome()
            print(f"\n🔍 DEBUG CHROME REGION:")
            print(f"   left={chrome_region['left']}, top={chrome_region['top']}")
            print(f"   width={chrome_region['width']}, height={chrome_region['height']}")
        except Exception as e:
            print(f"❌ Error: {e}")
            return
        
        clicks = []
        current_task = 0
        tasks = [
            "Click en el área donde aparece el NÚMERO GANADOR",
            "Click en el área donde aparece el COUNTDOWN",
            "Click en el área donde aparece el BALANCE/SALDO",
            "Click en el área donde aparece TOTAL BET",
            "Click en el área del botón REPEAT BET",
            "Click en el NÚMERO 24 para apostar",
            "Click en el NÚMERO 0 para apostar", 
            "Click en el NÚMERO 12 para apostar",
            "Click en FICHA $1 (valor más bajo)",
            "Click en FICHA $5",
            "Click en FICHA $25 (valor alto)"
        ]
        
        def mouse_callback(event, x, y, flags, param):
            nonlocal current_task
            if event == cv2.EVENT_LBUTTONDOWN:
                # IMPORTANTE: Las coordenadas x,y ya son absolutas de la pantalla
                # porque estamos capturando la región completa de Chrome
                
                # Las coordenadas del click son relativas a la ventana CV
                # Necesitamos convertirlas a coordenadas absolutas de pantalla
                abs_x = chrome_region['left'] + x
                abs_y = chrome_region['top'] + y
                
                # Mostrar información detallada para debug
                print(f"\n🖱️  CLICK DETECTADO:")
                print(f"   Coordenadas en ventana CV: ({x}, {y})")
                print(f"   Chrome región: left={chrome_region['left']}, top={chrome_region['top']}")
                print(f"   Coordenadas absolutas calculadas: ({abs_x}, {abs_y})")
                
                clicks.append({
                    'task': tasks[current_task],
                    'rel_x': x,  # Relativas a la ventana
                    'rel_y': y,
                    'abs_x': abs_x,  # Absolutas de pantalla
                    'abs_y': abs_y
                })
                
                print(f"✅ {tasks[current_task]}: ABSOLUTO=({abs_x}, {abs_y})")
                current_task += 1
                
                if current_task >= len(tasks):
                    print("\n✅ Calibración completada!")
                    print("Presiona 's' para guardar o 'q' para cancelar")
        
        cv2.namedWindow('Calibración Visual')
        cv2.setMouseCallback('Calibración Visual', mouse_callback)
        
        print(f"\n📋 {tasks[0]}")
        
        while True:
            # Capturar pantalla
            screenshot = capture_screen(chrome_region)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
            # Mostrar instrucción actual
            if current_task < len(tasks):
                cv2.putText(img, tasks[current_task], (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Dibujar grilla de ayuda
            grid_size = 50
            height, width = img.shape[:2]
            
            # Líneas verticales
            for x in range(0, width, grid_size):
                cv2.line(img, (x, 0), (x, height), (128, 128, 128), 1)
            
            # Líneas horizontales
            for y in range(0, height, grid_size):
                cv2.line(img, (0, y), (width, y), (128, 128, 128), 1)
            
            # Mostrar clicks anteriores con cuadrados de selección
            for i, click in enumerate(clicks):
                # Colores según tipo de calibración
                if i < 2:  # Winner y Countdown
                    color = (0, 255, 0)
                elif i < 5:  # Balance, Total Bet, Repeat
                    color = (255, 255, 0)  # Amarillo para regiones de info
                elif i < 8:  # Números de apuesta
                    color = (255, 0, 0)    # Rojo para posiciones de apuesta
                else:  # Fichas
                    color = (255, 0, 255)  # Magenta para fichas
                
                # Determinar tamaño del cuadrado según el tipo
                if i == 0:  # Winner region
                    optimal_width, optimal_height = config.get_optimal_capture_size()
                    rect_w, rect_h = optimal_width//2, optimal_height//2
                elif i == 1:  # Countdown region
                    countdown_width, countdown_height = config.get_optimal_countdown_size()
                    rect_w, rect_h = countdown_width//2, countdown_height//2
                elif i in [2, 3]:  # Balance, Total Bet
                    rect_w, rect_h = 80, 25
                elif i == 4:  # Repeat button
                    rect_w, rect_h = 40, 20
                else:  # Bet positions y fichas
                    rect_w, rect_h = 15, 15
                
                # Usar coordenadas relativas para dibujar en la ventana
                click_x = click['rel_x']
                click_y = click['rel_y']
                
                # Dibujar cuadrado de selección
                cv2.rectangle(img, 
                            (click_x - rect_w, click_y - rect_h),
                            (click_x + rect_w, click_y + rect_h),
                            color, 2)
                
                # Círculo central
                cv2.circle(img, (click_x, click_y), 3, color, -1)
                
                # Etiquetas mejoradas
                labels = ["WINNER", "COUNTDOWN", "BALANCE", "TOTAL BET", "REPEAT", 
                         "BET 24", "BET 0", "BET 12", "CHIP $1", "CHIP $5", "CHIP $25"]
                label = labels[i] if i < len(labels) else f"ITEM {i+1}"
                cv2.putText(img, label, (click_x+rect_w+5, click_y-5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
                
                # Mostrar coordenadas absolutas
                cv2.putText(img, f"({click['abs_x']},{click['abs_y']})", 
                           (click_x+rect_w+5, click_y+10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
            
            cv2.imshow('Calibración Visual', img)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("❌ Calibración cancelada")
                break
            elif key == ord('t'):
                # Test: mostrar dónde haríamos click con las coordenadas actuales
                print("\n🧪 TEST DE COORDENADAS:")
                for i, click in enumerate(clicks):
                    mouse_x, mouse_y = click['abs_x'], click['abs_y']
                    print(f"   {i+1}. {click['task']}: ({mouse_x}, {mouse_y})")
                    # Mover mouse a esa posición para verificar (con fail-safe off)
                    original_failsafe = pyautogui.FAILSAFE
                    pyautogui.FAILSAFE = False
                    try:
                        if 0 <= mouse_x <= 3000 and 0 <= mouse_y <= 2000:
                            pyautogui.moveTo(mouse_x, mouse_y)
                            import time
                            time.sleep(0.5)
                        else:
                            print(f"   ⚠️ Coordenadas fuera de rango: ({mouse_x}, {mouse_y})")
                    finally:
                        pyautogui.FAILSAFE = original_failsafe
                print("✅ Revisa si el mouse se posicionó correctamente en cada punto")
                
            elif key == ord('s') and len(clicks) >= 3:
                # Usar tamaños óptimos según resolución
                optimal_width, optimal_height = config.get_optimal_capture_size()
                countdown_width, countdown_height = config.get_optimal_countdown_size()
                
                # Guardar calibración con áreas auto-escaladas
                self.calibration_data['winner_region'] = {
                    'x': clicks[0]['abs_x'] - optimal_width//2,
                    'y': clicks[0]['abs_y'] - optimal_height//2,
                    'width': optimal_width,
                    'height': optimal_height
                }
                self.calibration_data['countdown_region'] = {
                    'x': clicks[1]['abs_x'] - countdown_width//2,
                    'y': clicks[1]['abs_y'] - countdown_height//2,
                    'width': countdown_width,
                    'height': countdown_height
                }
                # Regiones de información
                self.calibration_data['balance_region'] = {
                    'x': clicks[2]['abs_x'] - 80,
                    'y': clicks[2]['abs_y'] - 25,
                    'width': 160,
                    'height': 50
                }
                self.calibration_data['total_bet_region'] = {
                    'x': clicks[3]['abs_x'] - 80,
                    'y': clicks[3]['abs_y'] - 25,
                    'width': 160,
                    'height': 50
                }
                self.calibration_data['repeat_bet_region'] = {
                    'x': clicks[4]['abs_x'] - 40,
                    'y': clicks[4]['abs_y'] - 20,
                    'width': 80,
                    'height': 40
                }
                
                # Posiciones de apuesta
                bet_start_idx = 5
                self.calibration_data['bet_positions'] = {
                    '24': {'x': clicks[bet_start_idx]['abs_x'], 'y': clicks[bet_start_idx]['abs_y']} if len(clicks) > bet_start_idx else None,
                    '0': {'x': clicks[bet_start_idx + 1]['abs_x'], 'y': clicks[bet_start_idx + 1]['abs_y']} if len(clicks) > bet_start_idx + 1 else None,
                    '12': {'x': clicks[bet_start_idx + 2]['abs_x'], 'y': clicks[bet_start_idx + 2]['abs_y']} if len(clicks) > bet_start_idx + 2 else None
                }
                
                # Posiciones de fichas
                chip_start_idx = 8
                self.calibration_data['chip_regions'] = {
                    '1': {'x': clicks[chip_start_idx]['abs_x'], 'y': clicks[chip_start_idx]['abs_y']} if len(clicks) > chip_start_idx else None,
                    '5': {'x': clicks[chip_start_idx + 1]['abs_x'], 'y': clicks[chip_start_idx + 1]['abs_y']} if len(clicks) > chip_start_idx + 1 else None,
                    '25': {'x': clicks[chip_start_idx + 2]['abs_x'], 'y': clicks[chip_start_idx + 2]['abs_y']} if len(clicks) > chip_start_idx + 2 else None
                }
                self.calibration_data['chrome_offset'] = {
                    'x': chrome_region['left'],
                    'y': chrome_region['top']
                }
                
                self.save_calibration()
                break
        
        cv2.destroyAllWindows()
    
    def calibrate_bet_position(self, number='24'):
        """Calibración específica para posición de apuesta"""
        print(f"\n🎯 CALIBRACIÓN DE CLICK PARA NÚMERO {number}")
        print("=" * 50)
        print(f"1. Mueve el mouse al número {number} en la ruleta")
        print("2. Presiona ESPACIO cuando esté en posición")
        print("3. Presiona 'q' para cancelar")
        
        try:
            chrome_region = obtener_region_chrome()
        except Exception as e:
            print(f"❌ Error: {e}")
            return
        
        print("\n⏳ Esperando posicionamiento del mouse...")
        
        cv2.namedWindow('Vista Chrome')
        
        while True:
            # Obtener posición del mouse
            mouse_x, mouse_y = pyautogui.position()
            
            # Capturar pantalla
            screenshot = capture_screen(chrome_region)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
            # Mostrar posición del mouse
            rel_x = mouse_x - chrome_region['left']
            rel_y = mouse_y - chrome_region['top']
            
            # Dibujar cruz en posición del mouse
            if 0 <= rel_x < img.shape[1] and 0 <= rel_y < img.shape[0]:
                cv2.line(img, (rel_x-10, rel_y), (rel_x+10, rel_y), (0, 255, 0), 2)
                cv2.line(img, (rel_x, rel_y-10), (rel_x, rel_y+10), (0, 255, 0), 2)
            
            # Mostrar información
            cv2.putText(img, f"Mouse: ({mouse_x}, {mouse_y})", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(img, "Presiona ESPACIO cuando esté sobre el número", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            cv2.imshow('Vista Chrome', img)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):
                # Guardar posición
                if 'bet_positions' not in self.calibration_data:
                    self.calibration_data['bet_positions'] = {}
                
                self.calibration_data['bet_positions'][str(number)] = {
                    'x': mouse_x,
                    'y': mouse_y
                }
                
                print(f"✅ Posición del número {number} guardada: x={mouse_x}, y={mouse_y}")
                self.save_calibration()
                break
            elif key == ord('q'):
                print("❌ Calibración cancelada")
                break
        
        cv2.destroyAllWindows()
    
    def test_calibration(self):
        """Prueba la calibración actual con live preview y detección OCR"""
        if not self.calibration_data.get('winner_region'):
            print("❌ No hay calibración guardada. Ejecuta primero la calibración.")
            return
        
        print("\n🧪 PROBANDO CALIBRACIÓN")
        print("=" * 50)
        print("Controles:")
        print("  'q': Salir")
        print("  '1-4': Cambiar tamaño región")
        print("  'TAB': Cambiar región activa (Winner/Countdown/Balance/etc.)")
        print("  'd': Activar/desactivar debug OCR")
        print("  'FLECHAS': Mover región activa (←↑→↓)")
        print("  'WAFS': Mover región activa (alternativo)")
        print("  'g': Guardar todas las posiciones")
        print("  'r': Reset región activa a original")
        
        # Configurar ventanas específicas para macOS
        main_window = 'Test Calibración - Live Preview'
        debug_window = 'OCR Debug'
        
        cv2.namedWindow(main_window, cv2.WINDOW_NORMAL)
        cv2.namedWindow(debug_window, cv2.WINDOW_NORMAL)
        
        # En macOS, posicionar ventanas para mejor visibilidad
        if config.system == 'darwin':
            cv2.moveWindow(main_window, 100, 100)
            cv2.moveWindow(debug_window, 700, 100)
            cv2.resizeWindow(main_window, 600, 500)
        
        # Variables para ajuste dinámico
        region_sizes = [
            {'w': 100, 'h': 70, 'name': 'Grande (Grilla)'},
            {'w': 80, 'h': 60, 'name': 'Mediana'},
            {'w': 60, 'h': 40, 'name': 'Pequeña (Original)'},
            {'w': 40, 'h': 30, 'name': 'Extra Pequeña'}
        ]
        current_size = 0
        debug_mode = False
        frame_count = 0
        
        # Variables para mover región
        move_step = 5  # Pixeles por movimiento
        region_modified = False
        
        # Sistema multi-región
        regions_info = [
            {'key': 'winner_region', 'name': 'WINNER', 'color': (0, 255, 0)},
            {'key': 'countdown_region', 'name': 'COUNTDOWN', 'color': (255, 255, 0)},
            {'key': 'balance_region', 'name': 'BALANCE', 'color': (255, 0, 255)},
            {'key': 'total_bet_region', 'name': 'TOTAL BET', 'color': (0, 255, 255)},
            {'key': 'repeat_bet_region', 'name': 'REPEAT', 'color': (255, 128, 0)}
        ]
        current_region_idx = 0  # Empezar con winner_region
        
        # Hacer copias para poder modificar
        regions_backup = {}
        for info in regions_info:
            key = info['key']
            if self.calibration_data.get(key):
                regions_backup[key] = self.calibration_data[key].copy()
        
        from vision.detector import detect_number_from_image, detect_number_debug
        
        while True:
            # Obtener región activa
            current_region_info = regions_info[current_region_idx]
            current_region_key = current_region_info['key']
            current_region_name = current_region_info['name']
            current_region_color = current_region_info['color']
            
            # Verificar que la región existe
            if not self.calibration_data.get(current_region_key):
                print(f"⚠️ Región {current_region_name} no calibrada, saltando a la siguiente...")
                current_region_idx = (current_region_idx + 1) % len(regions_info)
                continue
                
            current_region = self.calibration_data[current_region_key].copy()
            size = region_sizes[current_size]
            
            # Ajustar región para centrarla mejor
            center_x = current_region['x'] + current_region['width'] // 2
            center_y = current_region['y'] + current_region['height'] // 2
            
            adjusted_region = {
                'left': center_x - size['w'] // 2,
                'top': center_y - size['h'] // 2,
                'width': size['w'],
                'height': size['h']
            }
            
            frame_count += 1
            
            try:
                # Capturar pantalla de la región ganadora
                screenshot = capture_screen(adjusted_region)
                img = np.array(screenshot)
                
                if img.size > 0:
                    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                    
                    # Detectar número
                    numero = ""
                    if debug_mode:
                        numero, debug_images = detect_number_debug(img_bgr)
                        
                        # Mostrar imágenes de debug solo cada pocos frames para no sobrecargar
                        if debug_images and frame_count % 3 == 0:
                            debug_combined = None
                            for name, debug_img in debug_images[:4]:
                                if len(debug_img.shape) == 2:
                                    debug_img = cv2.cvtColor(debug_img, cv2.COLOR_GRAY2BGR)
                                debug_resized = cv2.resize(debug_img, (150, 100))
                                cv2.putText(debug_resized, name, (5, 15), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
                                
                                if debug_combined is None:
                                    debug_combined = debug_resized
                                else:
                                    debug_combined = np.hstack((debug_combined, debug_resized))
                            
                            if debug_combined is not None:
                                cv2.imshow(debug_window, debug_combined)
                    else:
                        numero = detect_number_from_image(img_bgr)
                    
                    # Hacer imagen más grande para visualizar mejor
                    display_img = cv2.resize(img_bgr, (img_bgr.shape[1]*8, img_bgr.shape[0]*8), 
                                           interpolation=cv2.INTER_NEAREST)
                    
                    # Añadir información overlay
                    info_height = 120
                    info_img = np.zeros((info_height, display_img.shape[1], 3), dtype=np.uint8)
                    
                    # Combinar imagen principal con info
                    combined = np.vstack((display_img, info_img))
                    
                    # Añadir texto informativo
                    y_text = display_img.shape[0] + 25
                    # Detectar contenido según el tipo de región
                    detection_text = "N/A"
                    if numero:
                        detection_text = numero
                    
                    # Información de región activa (destacada)
                    cv2.putText(combined, f"REGION ACTIVA: {current_region_name}", 
                               (10, y_text), cv2.FONT_HERSHEY_SIMPLEX, 0.8, current_region_color, 2)
                    
                    cv2.putText(combined, f"Detectado: {detection_text}", 
                               (10, y_text + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                               (0, 255, 0) if numero else (0, 0, 255), 2)
                    
                    cv2.putText(combined, f"Tamaño: {size['name']} ({size['w']}x{size['h']})", 
                               (10, y_text + 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    
                    cv2.putText(combined, f"Pos: x={adjusted_region['left']}, y={adjusted_region['top']}", 
                               (10, y_text + 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    
                    # Controles y estado
                    cv2.putText(combined, f"TAB: Cambiar región | FLECHAS: Mover | G: Guardar | R: Reset", 
                               (10, y_text + 105), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 100), 1)
                    
                    # Indicador de modificación
                    if region_modified:
                        cv2.putText(combined, "REGION MODIFICADA - Presiona G para guardar", 
                                   (10, y_text + 125), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                    
                    # Lista de regiones disponibles
                    regions_text = " | ".join([f"{i+1}.{info['name']}" for i, info in enumerate(regions_info)])
                    cv2.putText(combined, f"Regiones: {regions_text}", 
                               (10, y_text + 145), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
                    
                    cv2.imshow(main_window, combined)
                    
                    # Forzar actualización de ventana en macOS
                    if config.system == 'darwin':
                        cv2.setWindowProperty(main_window, cv2.WND_PROP_TOPMOST, 1)
                        cv2.setWindowProperty(main_window, cv2.WND_PROP_TOPMOST, 0)
                    
            except Exception as e:
                print(f"Error capturando región: {e}")
                import traceback
                traceback.print_exc()
            
            # Manejo de eventos optimizado para macOS
            wait_time = 1 if config.system == 'darwin' else 30
            key = cv2.waitKey(wait_time) & 0xFF
            
            # También verificar si alguna ventana fue cerrada
            try:
                if cv2.getWindowProperty(main_window, cv2.WND_PROP_VISIBLE) < 1:
                    print("❌ Ventana cerrada")
                    break
            except:
                print("❌ Error verificando ventana")
                break
            
            if key == ord('q') or key == 27:  # ESC también funciona
                print("👋 Saliendo...")
                break
            elif key == ord('1'):
                current_size = 0
                print(f"✅ Cambiado a región {region_sizes[current_size]['name']}")
            elif key == ord('2'):
                current_size = 1
                print(f"✅ Cambiado a región {region_sizes[current_size]['name']}")
            elif key == ord('3'):
                current_size = 2
                print(f"✅ Cambiado a región {region_sizes[current_size]['name']}")
            elif key == ord('4'):
                current_size = 3
                print(f"✅ Cambiado a región {region_sizes[current_size]['name']}")
            elif key == ord('d'):
                debug_mode = not debug_mode
                print(f"✅ Debug mode: {'ON' if debug_mode else 'OFF'}")
            elif key == ord('g'):
                # Guardar todas las posiciones
                self.save_calibration()
                region_modified = False
                print(f"💾 Todas las regiones guardadas!")
            elif key == 9:  # TAB
                # Cambiar región activa
                current_region_idx = (current_region_idx + 1) % len(regions_info)
                next_region = regions_info[current_region_idx]
                print(f"🔄 Cambiado a región: {next_region['name']}")
                region_modified = False
            elif key == ord('r'):
                # Reset región activa a original
                if current_region_key in regions_backup:
                    self.calibration_data[current_region_key] = regions_backup[current_region_key].copy()
                    print(f"🔄 Región {current_region_name} restaurada a original")
                    region_modified = False
            # Teclas de flecha (códigos especiales para OpenCV en macOS)
            elif key == 63234 or key == ord('a'):  # Flecha izquierda o 'a' (macOS)
                self.calibration_data[current_region_key]['x'] -= move_step
                region_modified = True
                print(f"⬅️ {current_region_name} movido izquierda: x={self.calibration_data[current_region_key]['x']}")
            elif key == 63235 or key == ord('f'):  # Flecha derecha o 'f' (macOS)
                self.calibration_data[current_region_key]['x'] += move_step
                region_modified = True
                print(f"➡️ {current_region_name} movido derecha: x={self.calibration_data[current_region_key]['x']}")
            elif key == 63232 or key == ord('w'):  # Flecha arriba o 'w' (macOS)
                self.calibration_data[current_region_key]['y'] -= move_step
                region_modified = True
                print(f"⬆️ {current_region_name} movido arriba: y={self.calibration_data[current_region_key]['y']}")
            elif key == 63233 or key == ord('s'):  # Flecha abajo o 's' (macOS)
                self.calibration_data[current_region_key]['y'] += move_step
                region_modified = True
                print(f"⬇️ {current_region_name} movido abajo: y={self.calibration_data[current_region_key]['y']}")
            elif key != 255:  # Cualquier otra tecla (para debug)
                print(f"🔍 Tecla presionada: {key} (char: {chr(key) if 32 <= key <= 126 else 'special'})")
        
        cv2.destroyAllWindows()
        
        # Ofrecer guardar la región optimizada
        if current_size != 0:
            print(f"\n💡 Estás usando la región {region_sizes[current_size]['name']}")
            save_new = input("¿Quieres guardar esta región como nueva calibración? (s/n): ").strip().lower()
            if save_new == 's':
                # Actualizar calibración con nueva región
                center_x = self.calibration_data['winner_region']['x'] + self.calibration_data['winner_region']['width'] // 2
                center_y = self.calibration_data['winner_region']['y'] + self.calibration_data['winner_region']['height'] // 2
                size = region_sizes[current_size]
                
                self.calibration_data['winner_region'] = {
                    'x': center_x - size['w'] // 2,
                    'y': center_y - size['h'] // 2,
                    'width': size['w'],
                    'height': size['h']
                }
                self.save_calibration()
                print("✅ Nueva región guardada!")
    
    def _test_screen_capture(self):
        """Prueba de captura usando las regiones calibradas"""
        print("\n🧪 PRUEBA DE CALIBRACIÓN REAL")
        print("=" * 50)
        print("Controles:")
        print("  ESPACIO: Capturar regiones calibradas")
        print("  A: Captura automática continua")
        print("  S: Parar captura automática")
        print("  1: Mostrar solo región ganadora")
        print("  2: Mostrar solo región countdown")
        print("  3: Mostrar ambas regiones")
        print("  Q/ESC: Salir")
        
        # Verificar calibración
        if not self.calibration_data.get('winner_region'):
            print("❌ No hay región ganadora calibrada")
            return
            
        winner_region = self.calibration_data['winner_region']
        countdown_region = self.calibration_data.get('countdown_region')
        
        print(f"🎯 Región ganadora: x={winner_region['x']}, y={winner_region['y']}, size={winner_region['width']}x{winner_region['height']}")
        if countdown_region:
            print(f"⏰ Región countdown: x={countdown_region['x']}, y={countdown_region['y']}, size={countdown_region['width']}x{countdown_region['height']}")
        else:
            print("⚠️ No hay región countdown calibrada")
        
        try:
            chrome_region = obtener_region_chrome()
            print(f"✅ Chrome detectado: {chrome_region}")
        except Exception as e:
            print(f"❌ Error detectando Chrome: {e}")
            return
        
        cv2.namedWindow('Test Calibración Real', cv2.WINDOW_NORMAL)
        if config.system == 'darwin':
            cv2.moveWindow('Test Calibración Real', 100, 100)
            cv2.resizeWindow('Test Calibración Real', 800, 600)
        
        # Variables para captura automática
        auto_capture = False
        capture_count = 0
        last_capture_time = 0
        display_mode = 3  # 1=winner, 2=countdown, 3=both
        
        # Importar detector para OCR
        from vision.detector import detect_number_from_image
        
        def create_display_image(images, detections, mode):
            """Crear imagen para mostrar según el modo"""
            if mode == 1 and images['winner'] is not None:
                # Solo región ganadora
                img = images['winner']
                big_img = cv2.resize(img, (img.shape[1]*8, img.shape[0]*8), 
                                   interpolation=cv2.INTER_NEAREST)
                cv2.putText(big_img, f"WINNER: {detections['winner']}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                return big_img
                
            elif mode == 2 and images['countdown'] is not None:
                # Solo región countdown
                img = images['countdown']
                big_img = cv2.resize(img, (img.shape[1]*8, img.shape[0]*8), 
                                   interpolation=cv2.INTER_NEAREST)
                cv2.putText(big_img, f"COUNTDOWN: {detections['countdown']}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                return big_img
                
            elif mode == 3:
                # Ambas regiones
                display_img = np.zeros((600, 800, 3), dtype=np.uint8)
                
                # Región ganadora arriba
                if images['winner'] is not None:
                    # Convertir a BGR si es necesario
                    winner_array = np.array(images['winner'])
                    if len(winner_array.shape) == 3 and winner_array.shape[2] == 3:
                        winner_bgr = cv2.cvtColor(winner_array, cv2.COLOR_RGB2BGR)
                    else:
                        winner_bgr = winner_array
                    
                    winner_img = cv2.resize(winner_bgr, (400, 280), 
                                          interpolation=cv2.INTER_NEAREST)
                    # Asegurar que las dimensiones coincidan
                    if winner_img.shape[:2] == (280, 400):
                        display_img[10:290, 10:410] = winner_img
                
                cv2.putText(display_img, f"WINNER: {detections['winner']}", (10, 310), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                
                # Región countdown abajo
                if images['countdown'] is not None:
                    # Convertir a BGR si es necesario
                    countdown_array = np.array(images['countdown'])
                    if len(countdown_array.shape) == 3 and countdown_array.shape[2] == 3:
                        countdown_bgr = cv2.cvtColor(countdown_array, cv2.COLOR_RGB2BGR)
                    else:
                        countdown_bgr = countdown_array
                    
                    countdown_img = cv2.resize(countdown_bgr, (400, 280), 
                                             interpolation=cv2.INTER_NEAREST)
                    # Asegurar que las dimensiones coincidan
                    if countdown_img.shape[:2] == (280, 400):
                        display_img[330:610, 10:410] = countdown_img
                elif countdown_region:
                    cv2.putText(display_img, "Error capturando countdown", (10, 450), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                cv2.putText(display_img, f"COUNTDOWN: {detections['countdown']}", (10, 350), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                
                # Info adicional en el lado derecho
                cv2.putText(display_img, f"Mode: {mode} (1=W, 2=C, 3=Both)", (420, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(display_img, f"Auto: {'ON' if auto_capture else 'OFF'}", (420, 80), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(display_img, f"Count: {capture_count}", (420, 110), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Coordenadas de regiones
                cv2.putText(display_img, f"Winner pos: ({winner_region['x']},{winner_region['y']})", 
                           (420, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
                if countdown_region:
                    cv2.putText(display_img, f"Countdown pos: ({countdown_region['x']},{countdown_region['y']})", 
                               (420, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
                
                return display_img
            
            # Fallback - imagen negra con mensaje
            fallback_img = np.zeros((400, 600, 3), dtype=np.uint8)
            cv2.putText(fallback_img, "No hay imagen disponible", (50, 200), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            return fallback_img
        
        # Función para capturar y procesar regiones
        def capture_and_process():
            images = {}
            detections = {}
            
            # Capturar región ganadora
            try:
                img_winner = capture_screen(winner_region)
                if img_winner is not None and hasattr(img_winner, 'size') and img_winner.size > 0:
                    # Convertir PIL a numpy array si es necesario
                    if hasattr(img_winner, 'mode'):
                        images['winner'] = np.array(img_winner)
                    else:
                        images['winner'] = img_winner
                    
                    number = detect_number_from_image(images['winner']).strip()
                    detections['winner'] = number if number else "N/A"
                else:
                    images['winner'] = None
                    detections['winner'] = "ERROR"
            except Exception as e:
                images['winner'] = None
                detections['winner'] = f"ERROR: {str(e)[:50]}"
            
            # Capturar región countdown si existe
            if countdown_region:
                try:
                    img_countdown = capture_screen(countdown_region)
                    if img_countdown is not None and hasattr(img_countdown, 'size') and img_countdown.size > 0:
                        # Convertir PIL a numpy array si es necesario
                        if hasattr(img_countdown, 'mode'):
                            images['countdown'] = np.array(img_countdown)
                        else:
                            images['countdown'] = img_countdown
                        
                        countdown = detect_number_from_image(images['countdown']).strip()
                        detections['countdown'] = countdown if countdown else "N/A"
                    else:
                        images['countdown'] = None
                        detections['countdown'] = "ERROR"
                except Exception as e:
                    images['countdown'] = None
                    detections['countdown'] = f"ERROR: {str(e)[:50]}"
            else:
                images['countdown'] = None
                detections['countdown'] = "NO CALIBRADO"
            
            return images, detections
        
        # Captura inicial
        print("📸 Captura inicial de regiones calibradas...")
        images, detections = capture_and_process()
        
        print(f"🎯 Número detectado: {detections['winner']}")
        print(f"⏰ Countdown detectado: {detections['countdown']}")
        
        # Mostrar captura inicial
        display_img = create_display_image(images, detections, display_mode)
        cv2.imshow('Test Calibración Real', display_img)
        
        print("\n🎮 Ventana lista. Usa los controles para probar...")

        while True:
            current_time = time.time()
            
            # Captura automática cada 500ms
            if auto_capture and (current_time - last_capture_time) > 0.5:
                capture_count += 1
                images, detections = capture_and_process()
                
                # Mostrar detecciones en consola cada 10 capturas
                if capture_count % 10 == 0:
                    print(f"📸 Auto #{capture_count} - Winner: {detections['winner']}, Countdown: {detections['countdown']}")
                
                # Actualizar display
                display_img = create_display_image(images, detections, display_mode)
                cv2.imshow('Test Calibración Real', display_img)
                last_capture_time = current_time
            
            # Manejo de teclas con timeout más corto para mejor responsividad
            key = cv2.waitKey(30) & 0xFF
            
            # Verificar si la ventana sigue abierta
            try:
                if cv2.getWindowProperty('Test Calibración Real', cv2.WND_PROP_VISIBLE) < 1:
                    print("❌ Ventana cerrada")
                    break
            except:
                break
            
            if key == ord(' '):
                print("📸 Captura manual...")
                images, detections = capture_and_process()
                print(f"🎯 Winner: {detections['winner']}")
                print(f"⏰ Countdown: {detections['countdown']}")
                
                display_img = create_display_image(images, detections, display_mode)
                cv2.imshow('Test Calibración Real', display_img)
                    
            elif key == ord('a'):
                auto_capture = True
                capture_count = 0
                print("🔄 Captura automática ACTIVADA (cada 500ms)")
                
            elif key == ord('s'):
                auto_capture = False
                print("⏹️  Captura automática DETENIDA")
                
            elif key == ord('1'):
                display_mode = 1
                print("👁️  Modo: Solo región ganadora")
                
            elif key == ord('2'):
                display_mode = 2
                if countdown_region:
                    print("👁️  Modo: Solo región countdown")
                else:
                    print("❌ No hay región countdown calibrada")
                    display_mode = 3
                
            elif key == ord('3'):
                display_mode = 3
                print("👁️  Modo: Ambas regiones")
                
            elif key == ord('q') or key == 27:
                print("👋 Saliendo...")
                break
            elif key != 255:  # Cualquier otra tecla
                print(f"🔍 Tecla presionada: {key} (char: {chr(key) if 32 <= key <= 126 else 'special'})")
        
        cv2.destroyAllWindows()
        print("✅ Prueba de captura completada")


    def test_bet_positions(self):
        """Prueba las posiciones de apuesta moviendo el mouse"""
        if not self.calibration_data.get('bet_positions'):
            print("❌ No hay posiciones de apuesta calibradas")
            return
            
        print("\n🧪 PROBANDO POSICIONES DE APUESTA")
        print("=" * 50)
        print("El mouse se moverá a cada posición calibrada...")
        
        # Desactivar fail-safe para el test
        original_failsafe = pyautogui.FAILSAFE
        pyautogui.FAILSAFE = False
        
        try:
            bet_positions = self.calibration_data['bet_positions']
            for numero, pos in bet_positions.items():
                if pos and 'x' in pos and 'y' in pos:
                    x, y = pos['x'], pos['y']
                    if 0 <= x <= 5000 and 0 <= y <= 3000:
                        print(f"📍 Moviendo a número {numero}: ({x}, {y})")
                        pyautogui.moveTo(x, y)
                        time.sleep(1.5)
                    else:
                        print(f"⚠️ Número {numero} tiene coordenadas fuera de rango: ({x}, {y})")
        finally:
            pyautogui.FAILSAFE = original_failsafe
                
        print("✅ Test completado. ¿Las posiciones eran correctas?")
    
    def auto_detect_roulette_numbers(self):
        """Auto-detecta las posiciones de los 36 números de la ruleta"""
        print("\n🔍 AUTO-DETECTOR DE NÚMEROS DE RULETA")
        print("=" * 60)
        print("Este proceso intentará encontrar automáticamente los 36 números.")
        print("Necesitarás marcar el área aproximada de la grilla de números.")
        print("\n📋 INSTRUCCIONES:")
        print("1. Se abrirá una ventana con la imagen de Chrome")
        print("2. Dibuja un rectángulo alrededor de TODA la grilla de números")
        print("3. Click en esquina superior izquierda de la grilla")
        print("4. Click en esquina inferior derecha de la grilla")
        print("5. El sistema detectará automáticamente los 36 números")
        
        try:
            chrome_region = obtener_region_chrome()
            print(f"\n✅ Chrome detectado: {chrome_region}")
        except Exception as e:
            print(f"❌ Error detectando Chrome: {e}")
            return
        
        # Variables para la selección del área
        clicks = []
        selecting = True
        
        def mouse_callback(event, x, y, flags, param):
            nonlocal selecting
            if event == cv2.EVENT_LBUTTONDOWN and selecting:
                abs_x = chrome_region['left'] + x
                abs_y = chrome_region['top'] + y
                clicks.append({'x': x, 'y': y, 'abs_x': abs_x, 'abs_y': abs_y})
                
                if len(clicks) == 1:
                    print(f"✅ Esquina superior izquierda: ({abs_x}, {abs_y})")
                    print("👆 Ahora click en esquina inferior derecha de la grilla")
                elif len(clicks) == 2:
                    print(f"✅ Esquina inferior derecha: ({abs_x}, {abs_y})")
                    print("🔍 Analizando grilla... Presiona ESPACIO para procesar")
                    selecting = False
        
        cv2.namedWindow('Auto-Detector Ruleta')
        cv2.setMouseCallback('Auto-Detector Ruleta', mouse_callback)
        
        print(f"\n👆 Click en la esquina SUPERIOR IZQUIERDA de la grilla de números")
        
        while True:
            # Capturar pantalla
            screenshot = capture_screen(chrome_region)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
            # Dibujar grilla de ayuda
            height, width = img.shape[:2]
            grid_size = 30
            for x in range(0, width, grid_size):
                cv2.line(img, (x, 0), (x, height), (100, 100, 100), 1)
            for y in range(0, height, grid_size):
                cv2.line(img, (0, y), (width, y), (100, 100, 100), 1)
            
            # Mostrar clicks
            for i, click in enumerate(clicks):
                color = (0, 255, 0) if i == 0 else (0, 0, 255)
                label = "TOP-LEFT" if i == 0 else "BOTTOM-RIGHT"
                cv2.circle(img, (click['x'], click['y']), 8, color, -1)
                cv2.putText(img, label, (click['x']+15, click['y']-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Dibujar rectángulo si tenemos 2 clicks
            if len(clicks) == 2:
                pt1 = (clicks[0]['x'], clicks[0]['y'])
                pt2 = (clicks[1]['x'], clicks[1]['y'])
                cv2.rectangle(img, pt1, pt2, (255, 255, 0), 2)
                
                # Mostrar información
                width_area = abs(clicks[1]['x'] - clicks[0]['x'])
                height_area = abs(clicks[1]['y'] - clicks[0]['y'])
                cv2.putText(img, f"Grilla: {width_area}x{height_area} px", 
                           (clicks[0]['x'], clicks[0]['y']-20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            # Instrucciones en pantalla
            if len(clicks) == 0:
                cv2.putText(img, "Click: Esquina superior izquierda", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            elif len(clicks) == 1:
                cv2.putText(img, "Click: Esquina inferior derecha", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                cv2.putText(img, "Presiona ESPACIO para detectar numeros", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            cv2.imshow('Auto-Detector Ruleta', img)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("❌ Auto-detección cancelada")
                cv2.destroyAllWindows()
                return
            elif key == ord(' ') and len(clicks) == 2:
                # Procesar la detección
                self._process_roulette_grid(chrome_region, clicks)
                break
        
        cv2.destroyAllWindows()
    
    def _process_roulette_grid(self, chrome_region, clicks):
        """Procesa la grilla y detecta las posiciones de los números"""
        print("\n🔍 PROCESANDO GRILLA DE NÚMEROS...")
        
        # Calcular área de la grilla
        x1, y1 = clicks[0]['abs_x'], clicks[0]['abs_y']
        x2, y2 = clicks[1]['abs_x'], clicks[1]['abs_y']
        
        # Asegurar que x1,y1 sea top-left y x2,y2 sea bottom-right
        grid_left = min(x1, x2)
        grid_top = min(y1, y2)
        grid_right = max(x1, x2)
        grid_bottom = max(y1, y2)
        
        grid_width = grid_right - grid_left
        grid_height = grid_bottom - grid_top
        
        print(f"📐 Área de grilla: {grid_width}x{grid_height} px")
        print(f"📍 Posición: ({grid_left}, {grid_top}) a ({grid_right}, {grid_bottom})")
        
        # Validar que el área de la grilla sea razonable
        if grid_width < 200 or grid_height < 60:
            print(f"⚠️ ADVERTENCIA: Área de grilla muy pequeña. Asegúrate de cubrir toda la grilla de números.")
            print(f"   Tamaño mínimo recomendado: 200x60 px")
        
        # Layout típico de ruleta europea (3 filas x 12 columnas)
        rows = 3
        cols = 12
        
        # Calcular tamaño de cada celda
        cell_width = grid_width / cols
        cell_height = grid_height / rows
        
        print(f"🔲 Tamaño de celda: {cell_width:.1f}x{cell_height:.1f} px")
        
        # Calcular posición del 0 y mostrar debug
        zero_x_calculated = grid_left + (grid_width / 2)
        zero_y_calculated = grid_top - (cell_height / 2)
        zero_y_final = max(10, zero_y_calculated)
        
        print(f"🔍 DEBUG posición del 0:")
        print(f"   X calculada: {zero_x_calculated:.1f}")
        print(f"   Y calculada: {zero_y_calculated:.1f}")
        print(f"   Y final (min 10): {zero_y_final:.1f}")
        
        # Mapeo de números de ruleta europea estándar
        # Fila superior (1-34 números impares), medio (2-35 pares), inferior (3-36 múltiplos de 3)
        roulette_layout = [
            # Fila 1 (superior)
            [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36],
            # Fila 2 (medio)  
            [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35],
            # Fila 3 (inferior)
            [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34]
        ]
        
        detected_positions = {}
        
        # Detectar posición de cada número
        for row in range(rows):
            for col in range(cols):
                numero = roulette_layout[row][col]
                
                # Calcular centro de la celda
                center_x = grid_left + (col * cell_width) + (cell_width / 2)
                center_y = grid_top + (row * cell_height) + (cell_height / 2)
                
                detected_positions[str(numero)] = {
                    'x': int(center_x),
                    'y': int(center_y),
                    'row': row,
                    'col': col
                }
        
        # Agregar posición del 0 (normalmente arriba de la grilla)
        detected_positions['0'] = {
            'x': int(zero_x_calculated),
            'y': int(zero_y_final),
            'row': -1,
            'col': 6  # Centro
        }
        
        print(f"\n✅ Detectados {len(detected_positions)} números!")
        
        # Mostrar algunos ejemplos y verificar rangos
        ejemplos = ['0', '1', '18', '24', '36']
        fuera_de_rango = []
        
        for num in ejemplos:
            if num in detected_positions:
                pos = detected_positions[num]
                x, y = pos['x'], pos['y']
                print(f"   #{num}: ({x}, {y})")
                
                # Verificar si está fuera de rango
                if not (0 <= x <= 5000 and 0 <= y <= 3000):
                    fuera_de_rango.append(f"#{num}: ({x}, {y})")
        
        # Verificar todos los números para problemas de rango
        total_fuera_rango = 0
        for num, pos in detected_positions.items():
            x, y = pos['x'], pos['y']
            if not (0 <= x <= 5000 and 0 <= y <= 3000):
                total_fuera_rango += 1
                
        if total_fuera_rango > 0:
            print(f"⚠️ ADVERTENCIA: {total_fuera_rango} números tienen coordenadas fuera del rango válido")
            print(f"   Rango válido: X=[0-5000], Y=[0-3000]")
            print(f"   💡 Sugerencia: Asegúrate de que la grilla esté completamente dentro de la pantalla")
            print(f"   💡 Si el número 0 está fuera de rango, quizás está demasiado arriba de la grilla")
        else:
            print(f"✅ Todas las coordenadas están dentro del rango válido")
        
        # Preguntar si guardar
        print(f"\n💾 ¿Guardar las {len(detected_positions)} posiciones detectadas?")
        respuesta = input("Escribe 'si' para guardar, 'test' para probar, o Enter para cancelar: ").strip().lower()
        
        if respuesta == 'si':
            # Guardar en calibración
            if 'bet_positions' not in self.calibration_data:
                self.calibration_data['bet_positions'] = {}
            
            self.calibration_data['bet_positions'].update(detected_positions)
            self.save_calibration()
            print(f"✅ ¡{len(detected_positions)} posiciones guardadas!")
            
        elif respuesta == 'test':
            # Probar las posiciones detectadas
            self._test_detected_positions(detected_positions)
            
            # Preguntar de nuevo si guardar después del test
            if input("\n¿Las posiciones se ven correctas? (si/no): ").strip().lower() == 'si':
                if 'bet_positions' not in self.calibration_data:
                    self.calibration_data['bet_positions'] = {}
                self.calibration_data['bet_positions'].update(detected_positions)
                self.save_calibration()
                print(f"✅ ¡{len(detected_positions)} posiciones guardadas!")
        else:
            print("❌ Detección cancelada")
    
    def _test_detected_positions(self, positions):
        """Prueba las posiciones detectadas moviendo el mouse"""
        print("\n🧪 PROBANDO POSICIONES DETECTADAS")
        print("El mouse se moverá a cada número...")
        
        # Desactivar fail-safe
        original_failsafe = pyautogui.FAILSAFE
        pyautogui.FAILSAFE = False
        
        try:
            # Ordenar números para un recorrido lógico
            numeros_ordenados = ['0'] + [str(i) for i in range(1, 37)]
            
            for numero in numeros_ordenados:
                if numero in positions:
                    pos = positions[numero]
                    x, y = pos['x'], pos['y']
                    
                    if 0 <= x <= 5000 and 0 <= y <= 3000:
                        print(f"📍 #{numero}: ({x}, {y})")
                        pyautogui.moveTo(x, y)
                        time.sleep(0.3)  # Pausa más rápida
                    else:
                        print(f"⚠️ #{numero}: coordenadas fuera de rango ({x}, {y})")
        finally:
            pyautogui.FAILSAFE = original_failsafe
        
        print("✅ Test completado")

def run_calibration():
    """Función principal de calibración"""
    calibrator = Calibrator()
    
    while True:
        print("\n🎯 HERRAMIENTA DE CALIBRACIÓN")
        print("=" * 50)
        print("1. Calibración visual completa (recomendado)")
        print("2. Calibrar posición de apuesta específica")
        print("3. Probar calibración actual")
        print("4. Ver calibración guardada")
        print("5. Test de posiciones de apuesta (mouse)")
        print("6. 🚀 AUTO-DETECTOR de 37 números (0-36)")
        print("7. Prueba rápida de captura (debug)")
        print("8. Salir")
        
        choice = input("\nSelecciona una opción (1-8): ").strip()
        
        if choice == '1':
            calibrator.calibrate_visual_click()
        elif choice == '2':
            number = input("Número a calibrar (default: 24): ").strip() or '24'
            calibrator.calibrate_bet_position(number)
        elif choice == '3':
            calibrator.test_calibration()
        elif choice == '4':
            print("\n📋 Calibración actual:")
            print(json.dumps(calibrator.calibration_data, indent=2))
        elif choice == '5':
            calibrator.test_bet_positions()
        elif choice == '6':
            calibrator.auto_detect_roulette_numbers()
        elif choice == '7':
            calibrator._test_screen_capture()
        elif choice == '8':
            print("👋 Hasta luego!")
            break
        else:
            print("❌ Opción inválida")


if __name__ == "__main__":
    run_calibration()