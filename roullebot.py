#!/usr/bin/env python3
"""
RouletteBot - Bot multiplataforma para automatización de ruleta
Soporta Windows, macOS y Linux
"""

import sys
import os
import platform
import argparse
from pathlib import Path

# Configuración del path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.platform_config import config


def check_dependencies():
    """Verifica que todas las dependencias estén instaladas"""
    print(f"🖥️  Sistema operativo detectado: {platform.system()} ({platform.platform()})")
    print(f"🐍 Python version: {sys.version.split()[0]}")
    print("-" * 50)
    
    # Verificar dependencias del sistema
    deps = config.verify_dependencies()
    all_ok = True
    
    for dep, installed in deps.items():
        status = "✅" if installed else "❌"
        print(f"{status} {dep}: {'Instalado' if installed else 'No encontrado'}")
        if not installed:
            all_ok = False
    
    if not all_ok:
        print("\n⚠️  Faltan dependencias. Instrucciones de instalación:")
        instructions = config.get_install_instructions()
        for dep, instruction in instructions.items():
            if dep in deps and not deps[dep]:
                print(f"\n{dep}:")
                print(instruction)
    
    # Verificar módulos Python
    print("\n📦 Verificando módulos Python...")
    python_modules = {
        'cv2': 'opencv-python',
        'pytesseract': 'pytesseract',
        'pyautogui': 'pyautogui',
        'mss': 'mss',
        'numpy': 'numpy'
    }
    
    if config.is_windows:
        python_modules['pygetwindow'] = 'pygetwindow'
    
    missing_modules = []
    for module, package in python_modules.items():
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            missing_modules.append(package)
            all_ok = False
    
    if missing_modules:
        print(f"\n⚠️  Instala los módulos faltantes con:")
        print(f"pip install {' '.join(missing_modules)}")
    
    return all_ok


def main():
    """Función principal del bot"""
    parser = argparse.ArgumentParser(description='RouletteBot - Bot de automatización de ruleta')
    parser.add_argument('--mode', choices=['run', 'fast', 'calibrate', 'scan', 'monitor', 'preview'],
                        default='run', help='Modo de operación')
    parser.add_argument('--debug', action='store_true', help='Activar modo debug')
    parser.add_argument('--dry-run', action='store_true', help='Ejecutar sin hacer clicks reales')
    parser.add_argument('--config-file', type=str, help='Archivo de configuración personalizado')
    
    args = parser.parse_args()
    
    # Verificar dependencias
    print("🎰 RouletteBot - Inicializando...\n")
    if not check_dependencies():
        print("\n❌ Por favor instala las dependencias faltantes antes de continuar.")
        return 1
    
    print("\n✅ Todas las dependencias están instaladas!")
    print("-" * 50)
    
    # Importar módulos según el modo
    if args.mode == 'run':
        print("\n🚀 Iniciando bot principal (CON PREVIEW)...")
        from main import main as run_main
        run_main()
    
    elif args.mode == 'fast':
        print("\n⚡ Iniciando bot ultra rápido (SIN PREVIEW)...")
        from main_no_preview import main_fast
        main_fast()
    
    elif args.mode == 'calibrate':
        print("\n🎯 Iniciando modo calibración...")
        from tools.calibrator import run_calibration
        run_calibration()
    
    elif args.mode == 'scan':
        print("\n🔍 Iniciando modo escaneo...")
        from tools.scanner import run_scanner
        run_scanner(show_preview=not args.dry_run)
    
    elif args.mode == 'monitor':
        print("\n👁️  Iniciando modo monitor...")
        from tools.monitor import run_monitor
        run_monitor()
    
    elif args.mode == 'preview':
        print("\n📺 Iniciando preview de Chrome...")
        from preview_chrome import main as preview_main
        preview_main()
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Detenido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)