# 🎯 Mejoras de Detección para Stake.com en Windows

## Problema Solucionado ✅

**El bot no detectaba la ventana de Stake.com en Windows** porque estaba buscando específicamente "Chrome" en el título de ventana, pero Stake.com puede tener títulos como:
- "Stake - Google Chrome"
- "Stake.com - Microsoft Edge" 
- "Live Casino - Stake - Firefox"
- etc.

## Mejoras Implementadas 🔧

### 1. Detección Multi-Navegador Inteligente
- **Prioridad a Stake.com**: Busca primero ventanas con "Stake" en el título
- **Múltiples navegadores**: Chrome, Edge, Firefox, Brave, Opera
- **Búsqueda flexible**: Case-insensitive, busca patrones parciales
- **Filtrado inteligente**: Ignora ventanas muy pequeñas o no visibles

### 2. Diagnóstico Mejorado para Windows
- **Lista todas las ventanas** disponibles en el sistema
- **Identifica ventanas de navegador** automáticamente
- **Debug detallado** para resolver problemas de detección
- **Sugerencias específicas** para Stake.com

### 3. Normalización Multi-Navegador
- **Funciona con cualquier navegador**, no solo Chrome
- **Detección automática** de la ventana correcta
- **Redimensionamiento inteligente** para cualquier navegador

## Patrones de Búsqueda (Por Prioridad) 🎯

1. **"Stake"** - Cualquier ventana con Stake (máxima prioridad)
2. **"stake.com"** - Específicamente stake.com
3. **"Chrome"** - Google Chrome genérico
4. **"Google Chrome"** - Chrome completo
5. **"Microsoft Edge"** - Edge
6. **"Edge"** - Edge corto
7. **"Firefox"** - Firefox
8. **"Mozilla Firefox"** - Firefox completo
9. **"Brave"** - Brave Browser
10. **"Opera"** - Opera

## Cómo Usar las Mejoras 🚀

### Paso 1: Verificar Detección
```bash
python test_windows_detection.py
```

### Paso 2: Diagnóstico Completo
```bash
python roullebot.py --mode calibrate
# Seleccionar opción 9: "Diagnosticar posición de Chrome"
```

### Paso 3: Calibración Normal
```bash
python roullebot.py --mode calibrate
# Seleccionar opción 1: "Calibración visual completa"
```

## Salida Esperada 📊

### Detección Exitosa ✅
```
🔍 Ventana encontrada: 'Stake - Google Chrome' (patrón: Stake)
✅ Usando ventana: 'Stake - Google Chrome' (patrón: Stake)
```

### Diagnóstico en Windows 🪟
```
🪟 LISTANDO TODAS LAS VENTANAS DISPONIBLES (Windows):
   Total ventanas encontradas: 127
   1. 'Stake - Google Chrome'
      Posición: (100, 50), Tamaño: 1200x800
   ✅ Encontradas 1 ventanas de navegador
```

## Beneficios 🎉

1. **Detección automática de Stake.com** en cualquier navegador
2. **Sin necesidad de configuración manual** de títulos de ventana
3. **Debug mejorado** para resolver problemas rápidamente
4. **Compatibilidad ampliada** con todos los navegadores populares
5. **Priorización inteligente** de ventanas de Stake.com

## Para Usuarios de Stake.com 🎰

### Antes (❌)
- Solo funcionaba si Chrome tenía exactamente "Chrome" en el título
- Fallaba con otros navegadores
- Sin feedback sobre qué ventanas estaban disponibles

### Después (✅)
- Detecta automáticamente Stake.com en cualquier navegador
- Prioriza ventanas de Stake sobre navegadores genéricos
- Diagnóstico detallado muestra todas las opciones disponibles
- Funciona con Chrome, Edge, Firefox, Brave, Opera

## Solución de Problemas 🔧

Si aún no detecta Stake.com:

1. **Verifica que Stake esté en el título**: Cambia a la pestaña de Stake.com
2. **Ejecuta diagnóstico**: Opción 9 del calibrador para ver todas las ventanas
3. **Asegúrate que esté visible**: No minimizada, no oculta detrás de otras ventanas
4. **Prueba diferentes navegadores**: Si uno no funciona, prueba otro

¡Ahora RouletteBot debería detectar Stake.com automáticamente en Windows! 🎯