import pygetwindow as gw

def obtener_region_chrome():
    ventanas = gw.getWindowsWithTitle("Chrome")
    if not ventanas:
        raise Exception("❌ No se encontró ninguna ventana de Chrome.")

    ventana = ventanas[0]
    if ventana.isMinimized:
        ventana.restore()

    return {
        "left": ventana.left,
        "top": ventana.top,
        "width": ventana.width,
        "height": ventana.height
    }
