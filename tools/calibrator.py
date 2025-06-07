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
                    return json.load(f)
            except:
                pass
        
        return {
            'winner_region': None,
            'countdown_region': None,
            'bet_positions': {},
            'chrome_offset': {'x': 0, 'y': 0}
        }
    
    def save_calibration(self):
        """Guarda la calibración actual"""
        with open(self.config_file, 'w') as f:
            json.dump(self.calibration_data, f, indent=2)
        print(f"✅ Calibración guardada en: {self.config_file}")
    
    def calibrate_visual_click(self):
        """Calibración visual por click (más intuitiva)"""
        print("\n🎯 CALIBRACIÓN VISUAL POR CLICK")
        print("=" * 50)
        print("1. Se abrirá una ventana mostrando Chrome")
        print("2. Haz click en las áreas que se te indiquen")
        print("3. Presiona 'q' para salir, 's' para guardar")
        
        try:
            chrome_region = obtener_region_chrome()
        except Exception as e:
            print(f"❌ Error: {e}")
            return
        
        clicks = []
        current_task = 0
        tasks = [
            "Click en el área donde aparece el NÚMERO GANADOR",
            "Click en el área donde aparece el COUNTDOWN",
            "Click en el NÚMERO 24 para apostar",
            "Click en el NÚMERO 0 para apostar",
            "Click en el NÚMERO 12 para apostar"
        ]
        
        def mouse_callback(event, x, y, flags, param):
            nonlocal current_task
            if event == cv2.EVENT_LBUTTONDOWN:
                # Convertir coordenadas relativas a absolutas
                abs_x = chrome_region['left'] + x
                abs_y = chrome_region['top'] + y
                
                clicks.append({
                    'task': tasks[current_task],
                    'x': x,
                    'y': y,
                    'abs_x': abs_x,
                    'abs_y': abs_y
                })
                
                print(f"✅ {tasks[current_task]}: x={abs_x}, y={abs_y}")
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
            
            # Mostrar clicks anteriores
            for i, click in enumerate(clicks):
                cv2.circle(img, (click['x'], click['y']), 5, (0, 0, 255), -1)
                cv2.putText(img, f"{i+1}", (click['x']+10, click['y']-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            cv2.imshow('Calibración Visual', img)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("❌ Calibración cancelada")
                break
            elif key == ord('s') and len(clicks) >= 3:
                # Guardar calibración con áreas más grandes
                self.calibration_data['winner_region'] = {
                    'x': clicks[0]['abs_x'] - 50,
                    'y': clicks[0]['abs_y'] - 35,
                    'width': 100,
                    'height': 70
                }
                self.calibration_data['countdown_region'] = {
                    'x': clicks[1]['abs_x'] - 50,
                    'y': clicks[1]['abs_y'] - 35,
                    'width': 100,
                    'height': 70
                }
                self.calibration_data['bet_positions'] = {
                    '24': {'x': clicks[2]['abs_x'], 'y': clicks[2]['abs_y']},
                    '0': {'x': clicks[3]['abs_x'], 'y': clicks[3]['abs_y']} if len(clicks) > 3 else None,
                    '12': {'x': clicks[4]['abs_x'], 'y': clicks[4]['abs_y']} if len(clicks) > 4 else None
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
        print("  '1': Región grande (100x70) - Para grilla de números")
        print("  '2': Región mediana (80x60)")
        print("  '3': Región pequeña (60x40) - Original")
        print("  '4': Región extra pequeña (40x30)")
        print("  'd': Activar/desactivar debug OCR")
        
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
        
        from vision.detector import detect_number_from_image, detect_number_debug
        
        while True:
            # Capturar regiones calibradas
            winner_region = self.calibration_data['winner_region']
            size = region_sizes[current_size]
            
            # Ajustar región para centrarla mejor
            center_x = winner_region['x'] + winner_region['width'] // 2
            center_y = winner_region['y'] + winner_region['height'] // 2
            
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
                    cv2.putText(combined, f"Numero detectado: {numero if numero else 'N/A'}", 
                               (10, y_text), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                               (0, 255, 0) if numero else (0, 0, 255), 2)
                    
                    cv2.putText(combined, f"Region: {size['name']} ({size['w']}x{size['h']})", 
                               (10, y_text + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    
                    cv2.putText(combined, f"Pos: x={adjusted_region['left']}, y={adjusted_region['top']}", 
                               (10, y_text + 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    
                    cv2.putText(combined, f"Debug: {'ON' if debug_mode else 'OFF'} | 1-4: Tamaño | D: Debug | Q: Salir", 
                               (10, y_text + 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                    
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
        """Prueba rápida de captura de pantalla para debugging"""
        print("\n🧪 PRUEBA RÁPIDA DE CAPTURA")
        print("=" * 50)
        print("Presiona ESPACIO para capturar, Q para salir")
        
        try:
            chrome_region = obtener_region_chrome()
            print(f"✅ Chrome detectado: {chrome_region}")
        except Exception as e:
            print(f"❌ Error detectando Chrome: {e}")
            return
        
        # Región más grande en el centro para prueba
        test_region = {
            'left': chrome_region['left'] + chrome_region['width'] // 2 - 50,
            'top': chrome_region['top'] + chrome_region['height'] // 2 - 35,
            'width': 100,
            'height': 70
        }
        
        print(f"📍 Región de prueba: {test_region}")
        
        cv2.namedWindow('Test Captura', cv2.WINDOW_NORMAL)
        if config.system == 'darwin':
            cv2.moveWindow('Test Captura', 100, 100)
        
        while True:
            key = cv2.waitKey(1 if config.system == 'darwin' else 30) & 0xFF
            
            if key == ord(' '):
                print("📸 Capturando...")
                try:
                    img = capture_screen(test_region)
                    if img is not None and img.size > 0:
                        # Mostrar imagen ampliada
                        big_img = cv2.resize(img, (img.shape[1]*8, img.shape[0]*8), 
                                           interpolation=cv2.INTER_NEAREST)
                        cv2.imshow('Test Captura', big_img)
                        print(f"✅ Captura exitosa: {img.shape}")
                    else:
                        print("❌ Captura falló - imagen vacía")
                except Exception as e:
                    print(f"❌ Error en captura: {e}")
                    
            elif key == ord('q') or key == 27:
                break
        
        cv2.destroyAllWindows()
        print("✅ Prueba de captura completada")


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
        print("5. Prueba rápida de captura (debug)")
        print("6. Salir")
        
        choice = input("\nSelecciona una opción (1-6): ").strip()
        
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
            calibrator._test_screen_capture()
        elif choice == '6':
            print("👋 Hasta luego!")
            break
        else:
            print("❌ Opción inválida")


if __name__ == "__main__":
    run_calibration()