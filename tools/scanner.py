"""
Scanner unificado multiplataforma
Combina scan.py y scan_rapido.py con opción de preview
"""

import cv2
import numpy as np
import time
import sys
import os
from collections import Counter

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision.screen_capture import capturar_pantalla_region
from vision.detector import detect_number_from_image
from config.platform_config import config


class Scanner:
    def __init__(self, show_preview=True, preview_interval=10):
        self.show_preview = show_preview
        self.preview_interval = preview_interval
        self.scan_count = 0
        self.detected_numbers = []
        
    def scan_winner(self, region, duration=None):
        """Escanea la región del ganador"""
        print("\n🔍 ESCANEANDO NÚMERO GANADOR")
        print("=" * 50)
        print("Presiona Ctrl+C para detener")
        
        if self.show_preview:
            cv2.namedWindow('Preview Scanner')
        
        start_time = time.time()
        
        try:
            while True:
                # Verificar duración si está especificada
                if duration and (time.time() - start_time) > duration:
                    break
                
                # Capturar región
                screenshot = capturar_pantalla_region(region)
                img = np.array(screenshot)
                
                # Detectar número
                numero = detect_number_from_image(img)
                
                self.scan_count += 1
                
                if numero:
                    self.detected_numbers.append(numero)
                    print(f"✅ Scan #{self.scan_count}: Detectado número {numero}")
                else:
                    print(f"❌ Scan #{self.scan_count}: No se detectó número")
                
                # Mostrar preview si está habilitado
                if self.show_preview and self.scan_count % self.preview_interval == 0:
                    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                    # Hacer imagen más grande
                    img_bgr = cv2.resize(img_bgr, (img_bgr.shape[1]*4, img_bgr.shape[0]*4), 
                                        interpolation=cv2.INTER_NEAREST)
                    
                    # Añadir texto
                    cv2.putText(img_bgr, f"Scan #{self.scan_count}", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    if numero:
                        cv2.putText(img_bgr, f"Número: {numero}", (10, 60),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    cv2.imshow('Preview Scanner', img_bgr)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                time.sleep(0.1)  # Pequeña pausa entre scans
                
        except KeyboardInterrupt:
            print("\n⏹️  Escaneo detenido")
        
        if self.show_preview:
            cv2.destroyAllWindows()
        
        # Mostrar estadísticas
        self.show_statistics()
    
    def scan_multiple_regions(self, regions_dict):
        """Escanea múltiples regiones simultáneamente"""
        print("\n🔍 ESCANEANDO MÚLTIPLES REGIONES")
        print("=" * 50)
        print("Presiona Ctrl+C para detener")
        
        if self.show_preview:
            cv2.namedWindow('Multi-Scanner')
        
        results = {name: [] for name in regions_dict.keys()}
        
        try:
            while True:
                self.scan_count += 1
                combined_img = None
                
                for name, region in regions_dict.items():
                    # Capturar región
                    screenshot = capturar_pantalla_region(region)
                    img = np.array(screenshot)
                    
                    # Detectar contenido según el tipo
                    if name == 'winner':
                        content = detect_number_from_image(img)
                        if content:
                            results[name].append(content)
                    else:
                        # Para otras regiones, simplemente guardar si hay contenido
                        results[name].append(img.size > 0)
                    
                    # Preparar imagen para preview
                    if self.show_preview:
                        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                        img_bgr = cv2.resize(img_bgr, (200, 100), 
                                           interpolation=cv2.INTER_NEAREST)
                        
                        # Añadir label
                        cv2.putText(img_bgr, name, (5, 15),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                        
                        if combined_img is None:
                            combined_img = img_bgr
                        else:
                            combined_img = np.hstack((combined_img, img_bgr))
                
                # Mostrar preview combinado
                if self.show_preview and self.scan_count % self.preview_interval == 0:
                    cv2.putText(combined_img, f"Scan #{self.scan_count}", (10, 90),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.imshow('Multi-Scanner', combined_img)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                # Imprimir resultados
                status = f"Scan #{self.scan_count}: "
                for name in regions_dict.keys():
                    if name == 'winner' and results[name]:
                        status += f"{name}={results[name][-1]} "
                    else:
                        status += f"{name}={'✓' if results[name] and results[name][-1] else '✗'} "
                
                print(status)
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n⏹️  Escaneo detenido")
        
        if self.show_preview:
            cv2.destroyAllWindows()
        
        # Mostrar estadísticas por región
        print("\n📊 ESTADÍSTICAS POR REGIÓN:")
        for name, data in results.items():
            if name == 'winner':
                numbers = [n for n in data if n]
                if numbers:
                    counter = Counter(numbers)
                    print(f"\n{name}:")
                    for num, count in counter.most_common(5):
                        print(f"  Número {num}: {count} veces")
            else:
                valid = sum(1 for d in data if d)
                print(f"{name}: {valid}/{len(data)} detecciones")
    
    def show_statistics(self):
        """Muestra estadísticas del escaneo"""
        print("\n📊 ESTADÍSTICAS DEL ESCANEO:")
        print(f"Total de scans: {self.scan_count}")
        
        if self.detected_numbers:
            # Contar frecuencia de números
            counter = Counter(self.detected_numbers)
            print(f"Números detectados: {len(self.detected_numbers)}")
            print(f"Tasa de detección: {len(self.detected_numbers)/self.scan_count*100:.1f}%")
            
            print("\n🎯 Números más frecuentes:")
            for numero, frecuencia in counter.most_common(10):
                porcentaje = frecuencia / len(self.detected_numbers) * 100
                print(f"  Número {numero}: {frecuencia} veces ({porcentaje:.1f}%)")
        else:
            print("No se detectaron números")


def run_scanner(show_preview=True):
    """Función principal del scanner"""
    # Cargar calibración
    from tools.calibrator import Calibrator
    calibrator = Calibrator()
    
    if not calibrator.calibration_data.get('winner_region'):
        print("❌ No hay calibración guardada. Ejecuta primero la calibración.")
        return
    
    scanner = Scanner(show_preview=show_preview)
    
    while True:
        print("\n🔍 HERRAMIENTA DE ESCANEO")
        print("=" * 50)
        print("1. Escanear número ganador")
        print("2. Escaneo rápido (sin preview)")
        print("3. Escanear múltiples regiones")
        print("4. Escaneo con duración específica")
        print("5. Salir")
        
        choice = input("\nSelecciona una opción (1-5): ").strip()
        
        if choice == '1':
            scanner.show_preview = True
            scanner.scan_winner(calibrator.calibration_data['winner_region'])
        elif choice == '2':
            scanner.show_preview = False
            scanner.scan_winner(calibrator.calibration_data['winner_region'])
        elif choice == '3':
            regions = {
                'winner': calibrator.calibration_data['winner_region']
            }
            if calibrator.calibration_data.get('countdown_region'):
                regions['countdown'] = calibrator.calibration_data['countdown_region']
            scanner.scan_multiple_regions(regions)
        elif choice == '4':
            duration = input("Duración en segundos (default: 60): ").strip()
            duration = int(duration) if duration else 60
            scanner.scan_winner(calibrator.calibration_data['winner_region'], duration)
        elif choice == '5':
            print("👋 Hasta luego!")
            break
        else:
            print("❌ Opción inválida")


if __name__ == "__main__":
    run_scanner()