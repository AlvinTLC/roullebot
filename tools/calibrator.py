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

from vision.screen_capture import capturar_pantalla_region
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
            screenshot = capturar_pantalla_region(chrome_region)
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
            screenshot = capturar_pantalla_region(chrome_region)
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
        """Prueba la calibración actual"""
        if not self.calibration_data.get('winner_region'):
            print("❌ No hay calibración guardada. Ejecuta primero la calibración.")
            return
        
        print("\n🧪 PROBANDO CALIBRACIÓN")
        print("Presiona 'q' para salir")
        
        cv2.namedWindow('Test Calibración')
        
        while True:
            # Capturar regiones calibradas
            winner_region = self.calibration_data['winner_region']
            
            # Capturar pantalla de la región ganadora
            screenshot = capturar_pantalla_region({
                'left': winner_region['x'],
                'top': winner_region['y'],
                'width': winner_region['width'],
                'height': winner_region['height']
            })
            
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
            # Hacer imagen más grande para visualizar mejor
            img = cv2.resize(img, (img.shape[1]*4, img.shape[0]*4), 
                            interpolation=cv2.INTER_NEAREST)
            
            cv2.imshow('Test Calibración', img)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()


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