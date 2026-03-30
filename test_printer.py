import win32print

try:
    printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
    for p in printers:
        print(f"Printer: {p[2]}")
    default = win32print.GetDefaultPrinter()
    print(f"\nDefault printer: {default}")
except Exception as e:
    print(f"Error: {e}")
