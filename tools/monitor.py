"""
Monitor unificado multiplataforma
Combina monitor_countdown.py, velocidad_maxima.py y buscar_ganador_real.py
"""

import cv2
import numpy as np
import time
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision.screen_capture import capturar_pantalla_region
from vision.detector import detect_number_from_image
from vision.window_region import obtener_region_chrome
from config.platform_config import config


class Monitor:
    def __init__(self):
        self.running = False
        self.stats = {
            'winner_detections': 0,
            'countdown_detections': 0,
            'total_scans': 0,
            'start_time': None
        }
        
    def monitor_countdown(self, region):
        """Monitorea el countdown en tiempo real"""
        print("\n⏱️  MONITOREANDO COUNTDOWN")
        print("=" * 50)
        print("Presiona 'q' para salir")
        
        cv2.namedWindow('Monitor Countdown')
        self.stats['start_time'] = time.time()
        
        while True:
            screenshot = capturar_pantalla_region(region)
            img = np.array(screenshot)
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
            # Detectar número (countdown)
            countdown = detect_number_from_image(img)
            self.stats['total_scans'] += 1
            
            if countdown:
                self.stats['countdown_detections'] += 1
                print(f"⏱️  Countdown: {countdown}")
            
            # Hacer imagen más grande para mejor visualización
            img_display = cv2.resize(img_bgr, (img_bgr.shape[1]*4, img_bgr.shape[0]*4), 
                                    interpolation=cv2.INTER_NEAREST)
            
            # Añadir información
            cv2.putText(img_display, f"Countdown: {countdown if countdown else 'N/A'}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(img_display, f"Detecciones: {self.stats['countdown_detections']}/{self.stats['total_scans']}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow('Monitor Countdown', img_display)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()
        self._show_stats()
    
    def monitor_speed(self, winner_region, countdown_region=None):
        """Monitor de máxima velocidad sin preview visual"""
        print("\n🚀 MONITOR DE VELOCIDAD MÁXIMA")
        print("=" * 50)
        print("Sin preview visual para máximo rendimiento")
        print("Presiona Ctrl+C para detener")
        
        self.stats['start_time'] = time.time()
        last_winner = None
        last_countdown = None
        
        try:
            while True:
                # Capturar región ganadora
                screenshot = capturar_pantalla_region(winner_region)
                img = np.array(screenshot)
                winner = detect_number_from_image(img)
                
                self.stats['total_scans'] += 1
                
                # Capturar countdown si está configurado
                countdown = None
                if countdown_region:
                    screenshot_cd = capturar_pantalla_region(countdown_region)
                    img_cd = np.array(screenshot_cd)
                    countdown = detect_number_from_image(img_cd)
                
                # Mostrar solo cambios
                if winner and winner != last_winner:
                    self.stats['winner_detections'] += 1
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] 🎰 Ganador: {winner}")
                    last_winner = winner
                
                if countdown and countdown != last_countdown:
                    self.stats['countdown_detections'] += 1
                    print(f"⏱️  Countdown: {countdown}")
                    last_countdown = countdown
                
                # Sin delay para máxima velocidad
                
        except KeyboardInterrupt:
            print("\n⏹️  Monitor detenido")
        
        self._show_stats()
    
    def find_winner_region(self):
        """Herramienta interactiva para encontrar la región del ganador"""
        print("\n🔎 BUSCADOR DE REGIÓN GANADORA")
        print("=" * 50)
        print("Usa las teclas para mover y ajustar la región:")
        print("  Flechas: Mover región")
        print("  W/S: Ajustar altura")
        print("  A/D: Ajustar ancho")
        print("  ESPACIO: Probar detección")
        print("  ENTER: Guardar región")
        print("  Q: Salir")
        
        try:
            chrome_region = obtener_region_chrome()
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
        
        # Región inicial (centro de Chrome)
        x = chrome_region['width'] // 2 - 30
        y = chrome_region['height'] // 2 - 20
        width = 60
        height = 40
        
        cv2.namedWindow('Buscador de Región')
        
        while True:
            # Capturar pantalla completa de Chrome
            screenshot = capturar_pantalla_region(chrome_region)
            img = np.array(screenshot)
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
            # Dibujar región actual
            cv2.rectangle(img_bgr, (x, y), (x + width, y + height), (0, 255, 0), 2)
            
            # Extraer región
            roi = img[y:y+height, x:x+width]
            
            # Mostrar región ampliada
            if roi.size > 0:
                roi_large = cv2.resize(roi, (width*4, height*4), 
                                      interpolation=cv2.INTER_NEAREST)
                # Insertar en la esquina
                img_bgr[10:10+height*4, 10:10+width*4] = cv2.cvtColor(roi_large, cv2.COLOR_RGB2BGR)
                cv2.rectangle(img_bgr, (10, 10), (10+width*4, 10+height*4), (255, 255, 255), 2)
            
            # Mostrar información
            cv2.putText(img_bgr, f"Posición: ({x}, {y})", (10, img_bgr.shape[0]-60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(img_bgr, f"Tamaño: {width}x{height}", (10, img_bgr.shape[0]-40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(img_bgr, "ESPACIO: Probar | ENTER: Guardar", (10, img_bgr.shape[0]-20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            cv2.imshow('Buscador de Región', img_bgr)
            
            key = cv2.waitKey(1) & 0xFF
            
            # Controles
            step = 5
            if key == ord('q'):
                break
            elif key == 81:  # Flecha izquierda
                x = max(0, x - step)
            elif key == 83:  # Flecha derecha
                x = min(chrome_region['width'] - width, x + step)
            elif key == 82:  # Flecha arriba
                y = max(0, y - step)
            elif key == 84:  # Flecha abajo
                y = min(chrome_region['height'] - height, y + step)
            elif key == ord('a'):
                width = max(20, width - 5)
            elif key == ord('d'):
                width = min(200, width + 5)
            elif key == ord('w'):
                height = max(20, height - 5)
            elif key == ord('s'):
                height = min(200, height + 5)
            elif key == ord(' '):
                # Probar detección
                numero = detect_number_from_image(roi)
                if numero:
                    print(f"✅ Detectado: {numero}")
                else:
                    print("❌ No se detectó número")
            elif key == 13:  # Enter
                # Guardar región
                absolute_region = {
                    'x': chrome_region['left'] + x,
                    'y': chrome_region['top'] + y,
                    'width': width,
                    'height': height
                }
                print(f"\n✅ Región guardada: {absolute_region}")
                cv2.destroyAllWindows()
                return absolute_region
        
        cv2.destroyAllWindows()
        return None
    
    def _show_stats(self):
        """Muestra estadísticas del monitoreo"""
        if self.stats['start_time']:
            duration = time.time() - self.stats['start_time']
            print("\n📊 ESTADÍSTICAS DEL MONITOR:")
            print(f"Duración: {duration:.1f} segundos")
            print(f"Total scans: {self.stats['total_scans']}")
            print(f"Scans por segundo: {self.stats['total_scans']/duration:.1f}")
            print(f"Detecciones ganador: {self.stats['winner_detections']}")
            print(f"Detecciones countdown: {self.stats['countdown_detections']}")


def run_monitor():
    """Función principal del monitor"""
    from tools.calibrator import Calibrator
    calibrator = Calibrator()
    
    monitor = Monitor()
    
    while True:
        print("\n👁️  HERRAMIENTA DE MONITOREO")
        print("=" * 50)
        print("1. Monitor de countdown")
        print("2. Monitor de velocidad (sin preview)")
        print("3. Monitor múltiple (ganador + countdown)")
        print("4. Buscar región del ganador")
        print("5. Salir")
        
        choice = input("\nSelecciona una opción (1-5): ").strip()
        
        if choice == '1':
            if calibrator.calibration_data.get('countdown_region'):
                monitor.monitor_countdown(calibrator.calibration_data['countdown_region'])
            else:
                print("❌ No hay región de countdown calibrada")
        elif choice == '2':
            if calibrator.calibration_data.get('winner_region'):
                monitor.monitor_speed(calibrator.calibration_data['winner_region'])
            else:
                print("❌ No hay región ganadora calibrada")
        elif choice == '3':
            winner_reg = calibrator.calibration_data.get('winner_region')
            countdown_reg = calibrator.calibration_data.get('countdown_region')
            if winner_reg:
                monitor.monitor_speed(winner_reg, countdown_reg)
            else:
                print("❌ No hay regiones calibradas")
        elif choice == '4':
            region = monitor.find_winner_region()
            if region:
                save = input("\n¿Guardar como región ganadora? (s/n): ").strip().lower()
                if save == 's':
                    calibrator.calibration_data['winner_region'] = region
                    calibrator.save_calibration()
        elif choice == '5':
            print("👋 Hasta luego!")
            break
        else:
            print("❌ Opción inválida")


if __name__ == "__main__":
    run_monitor()