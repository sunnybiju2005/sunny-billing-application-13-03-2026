# Removed A6 import
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
import os
import sys

class BillingManager:
    @staticmethod
    def resolve_path(filename):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, filename)

    @staticmethod
    def generate_pdf(bill_data, filename="receipt.pdf"):
        try:
            full_path = BillingManager.resolve_path(filename)
            pagesize = (80*mm, 210*mm)
            c = canvas.Canvas(full_path, pagesize=pagesize)
            width, height = pagesize
            
            # Header
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width/2, height - 20, "DROP")
            c.setFont("Helvetica", 10)
            c.drawCentredString(width/2, height - 35, "City Center Kunnamkulam, Thrissur")
            c.setFont("Helvetica", 9)
            c.drawCentredString(width/2, height - 48, "Near Private Bus Stand, Kunnamkulam")
            c.line(10, height - 55, width - 10, height - 55)
            
            # Bill Info
            c.setFont("Helvetica", 9)
            timestamp = bill_data.get('timestamp', '')
            if hasattr(timestamp, 'strftime'):
                timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            c.drawString(10, height - 70, f"Date & Time: {timestamp}")
            c.drawString(10, height - 82, f"Bill ID: {bill_data.get('id', 'N/A')}")
            
            # Table Header
            c.setFont("Helvetica-Bold", 9)
            c.drawString(10, height - 100, "Item")
            c.drawRightString(width - 55, height - 100, "Qty")
            c.drawRightString(width - 35, height - 100, "Price")
            c.drawRightString(width - 10, height - 100, "Total")
            c.line(10, height - 103, width - 10, height - 103)
            
            # Items
            y = height - 118
            c.setFont("Helvetica", 9)
            for item in bill_data.get('items', []):
                c.drawString(10, y, str(item['name'])[:20])
                c.drawRightString(width - 55, y, str(item['quantity']))
                c.drawRightString(width - 35, y, f"{item['price']:.2f}")
                c.drawRightString(width - 10, y, f"{item['line_total']:.2f}")
                y -= 12
                if y < 40: # Page break if needed (not expected for small receipts)
                    c.showPage()
                    y = height - 20
            
            # Total
            c.line(10, y, width - 10, y)
            y -= 15
            c.setFont("Helvetica-Bold", 10)
            c.drawString(10, y, "GRAND TOTAL")
            c.drawRightString(width - 10, y, f"INR {bill_data.get('total', 0):.2f}")
            
            if bill_data.get('payment_method') == 'both':
                y -= 12
                c.setFont("Helvetica", 7)
                c.drawString(10, y, f"Cash: {bill_data.get('cash_amount', 0):.2f} | UPI: {bill_data.get('upi_amount', 0):.2f}")

            # Footer
            c.setFont("Helvetica-Oblique", 7)
            c.drawCentredString(width/2, 20, "Thank you for shopping at DROP")
            
            c.save()
            
            # Send to default printer on Windows
            # Provide raw text to win32print if possible for POS thermal printers
            try:
                import win32print
                text = "            DROP\n"
                text += "  City Center Kunnamkulam, Thrissur\n"
                text += " Near Private Bus Stand, Kunnamkulam\n"
                text += "-" * 40 + "\n"
                ts = bill_data.get('timestamp', '')
                ts_str = ts.strftime('%Y-%m-%d %H:%M:%S') if hasattr(ts, 'strftime') else str(ts)
                text += f"Date & Time: {ts_str}\n"
                text += f"Bill ID: {bill_data.get('id', 'N/A')}\n"
                text += "-" * 40 + "\n"
                text += f"{'Item':<20} {'Qty':>3} {'Price':>8} {'Total':>8}\n"
                text += "-" * 40 + "\n"
                for item in bill_data.get('items', []):
                    name = str(item['name'])[:18]
                    text += f"{name:<20} {int(item['quantity']):>3} {float(item['price']):>8.2f} {float(item['line_total']):>8.2f}\n"
                text += "-" * 40 + "\n"
                text += f"{'GRAND TOTAL:':<30} INR {float(bill_data.get('total', 0)):>5.2f}\n"
                if bill_data.get('payment_method') == 'both':
                    text += f"Cash: {float(bill_data.get('cash_amount', 0)):.2f} / UPI: {float(bill_data.get('upi_amount', 0)):.2f}\n"
                text += "-" * 40 + "\n"
                text += "    Thank you for shopping at DROP\n\n\n\n\n"
                text += "\x1d\x56\x00" # ESC/POS full cut command

                printer_name = win32print.GetDefaultPrinter()
                hPrinter = win32print.OpenPrinter(printer_name)
                try:
                    win32print.StartDocPrinter(hPrinter, 1, ("Receipt", None, "RAW"))
                    win32print.StartPagePrinter(hPrinter)
                    win32print.WritePrinter(hPrinter, text.encode('cp1252', errors='replace'))
                    win32print.EndPagePrinter(hPrinter)
                    win32print.EndDocPrinter(hPrinter)
                finally:
                    win32print.ClosePrinter(hPrinter)
                return True
            except Exception as e:
                print(f"Direct raw print failed: {e}")
                try:
                    os.startfile(full_path, "print")
                    return True
                except Exception as pe:
                    print(f"Printing error: {pe}")
                    return True # PDF was still saved at least
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return False
