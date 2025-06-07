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
                # Guardar calibración
                self.calibration_data['winner_region'] = {
                    'x': clicks[0]['abs_x'] - 30,
                    'y': clicks[0]['abs_y'] - 20,
                    'width': 60,
                    'height': 40
                }
                self.calibration_data['countdown_region'] = {
                    'x': clicks[1]['abs_x'] - 30,
                    'y': clicks[1]['abs_y'] - 20,
                    'width': 60,
                    'height': 40
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
        print("  '1': Región original (60x40)")
        print("  '2': Región pequeña (40x30)")
        print("  '3': Región extra pequeña (30x25)")
        print("  'd': Activar/desactivar debug OCR")
        
        cv2.namedWindow('Test Calibración - Live Preview')
        cv2.namedWindow('OCR Debug')
        
        # Variables para ajuste dinámico
        region_sizes = [
            {'w': 60, 'h': 40, 'name': 'Original'},
            {'w': 40, 'h': 30, 'name': 'Pequeña'},
            {'w': 30, 'h': 25, 'name': 'Extra Pequeña'}
        ]
        current_size = 0
        debug_mode = False
        
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
            
            try:
                # Capturar pantalla de la región ganadora
                screenshot = capture_screen(adjusted_region)
                img = np.array(screenshot)
                
                if img.size > 0:
                    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                    
                    # Detectar número
                    if debug_mode:
                        numero, debug_images = detect_number_debug(img_bgr)
                        
                        # Mostrar imágenes de debug
                        if debug_images:
                            debug_combined = None
                            for i, (name, debug_img) in enumerate(debug_images[:4]):
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
                                cv2.imshow('OCR Debug', debug_combined)
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
                    
                    cv2.putText(combined, f"Debug: {'ON' if debug_mode else 'OFF'} | 1-3: Tamaño | D: Debug | Q: Salir", 
                               (10, y_text + 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                    
                    cv2.imshow('Test Calibración - Live Preview', combined)
                    
            except Exception as e:
                print(f"Error capturando región: {e}")
            
            key = cv2.waitKey(100) & 0xFF
            if key == ord('q'):
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
            elif key == ord('d'):
                debug_mode = not debug_mode
                print(f"✅ Debug mode: {'ON' if debug_mode else 'OFF'}")
        
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
        print("5. Salir")
        
        choice = input("\nSelecciona una opción (1-5): ").strip()
        
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
            print("👋 Hasta luego!")
            break
        else:
            print("❌ Opción inválida")


if __name__ == "__main__":
    run_calibration()