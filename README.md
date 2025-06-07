# RouletteBot - Bot Multiplataforma para Ruleta

Bot automatizado para apostar en ruleta online, compatible con Windows, macOS y Linux.

## 🚀 Características

- ✅ **Multiplataforma**: Funciona en Windows, macOS y Linux
- 🎯 **Detección OCR**: Detecta automáticamente números ganadores usando Tesseract
- 🎮 **Apuestas Automáticas**: Realiza apuestas automáticas después de detectar ganadores
- 📊 **Estadísticas**: Rastrea ganancias, pérdidas y tasa de éxito
- 🔧 **Calibración Visual**: Sistema de calibración intuitivo por clicks
- 🚀 **Alto Rendimiento**: ~50 FPS de detección

## 📋 Requisitos Previos

### Todas las Plataformas
- Python 3.8 o superior
- Google Chrome
- Tesseract OCR

### Windows
```bash
# Instalar Tesseract desde:
# https://github.com/UB-Mannheim/tesseract/wiki
# O con Chocolatey:
choco install tesseract
```

### macOS
```bash
# Instalar con Homebrew
brew install tesseract
brew install tesseract-lang  # Para soporte de español
```

### Linux
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr
sudo apt-get install xdotool  # Para manejo de ventanas

# Fedora
sudo dnf install tesseract
sudo dnf install xdotool
```

## 🔧 Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tuusuario/roullebot.git
cd roullebot
```

2. Crear entorno virtual (recomendado):
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## 🎮 Uso

### Verificar Dependencias
```bash
python roullebot.py
```
Esto verificará que todas las dependencias estén instaladas correctamente.

### Calibración (IMPORTANTE - Primer paso)
```bash
python roullebot.py --mode calibrate
```

Opciones de calibración:
1. **Calibración visual completa** (recomendado): Click en las áreas indicadas
2. **Calibrar posición específica**: Para números individuales
3. **Probar calibración**: Verifica que la calibración funcione

### Ejecutar el Bot
```bash
python roullebot.py --mode run
```

### Otros Modos

#### Escanear Números
```bash
python roullebot.py --mode scan
```

#### Monitor en Tiempo Real
```bash
python roullebot.py --mode monitor
```

#### Preview de Chrome
```bash
python roullebot.py --mode preview
```

## 🎯 Estructura del Proyecto

```
roullebot/
├── config/                 # Configuración multiplataforma
│   ├── __init__.py
│   └── platform_config.py  # Detección de SO y rutas
├── tools/                  # Herramientas unificadas
│   ├── __init__.py
│   ├── calibrator.py      # Sistema de calibración
│   ├── scanner.py         # Escáner de números
│   └── monitor.py         # Monitor en tiempo real
├── utils/                  # Utilidades
│   ├── acciones.py
│   ├── ventana_chrome.py
│   └── window_manager.py   # Manejo de ventanas multiplataforma
├── vision/                 # Módulos de visión
│   ├── detector.py        # OCR con Tesseract
│   ├── screen_capture.py  # Captura de pantalla
│   └── window_region.py   # Detección de ventanas
├── main.py                # Script principal del bot
├── roullebot.py          # Punto de entrada multiplataforma
└── requirements.txt       # Dependencias Python
```

## ⚙️ Configuración

La configuración se guarda automáticamente en:
- **Windows**: `%APPDATA%\roullebot\calibration.json`
- **macOS**: `~/Library/Application Support/roullebot/calibration.json`
- **Linux**: `~/.config/roullebot/calibration.json`

## 🐛 Solución de Problemas

### Tesseract no encontrado
- Verifica que Tesseract esté en el PATH del sistema
- En Windows, puede necesitar reiniciar después de instalar

### No detecta la ventana de Chrome
- Asegúrate de que Chrome esté abierto y visible
- En Linux, instala `xdotool` si no está instalado
- En macOS, puede necesitar permisos de accesibilidad

### No detecta números correctamente
- Ejecuta la calibración nuevamente
- Ajusta el zoom de Chrome al 100%
- Asegúrate de que la región capturada sea clara

## ⚠️ Advertencia Legal

Este software es solo para fines educativos. El uso de bots automatizados puede violar los términos de servicio de las plataformas de casino online. Úsalo bajo tu propio riesgo.

## 📄 Licencia

MIT License - Ver archivo LICENSE para más detalles.