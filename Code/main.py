# coffee2.py
# -------------------------------
# Cafe logic + PDF receipt
# -------------------------------

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import os
from uuid import uuid4
import webbrowser


# -------------------------------
# Item class
# -------------------------------
class Item:
    def __init__(self, name, price):
        self.name = name
        self.price = price


# -------------------------------
# Order class
# -------------------------------
class Order:
    def __init__(self):
        self.items = {}   # item_name -> [Item, qty]
        self.order_id = str(uuid4())[:8]
        self.created_at = datetime.now()

    def add_item(self, item):
        if item.name in self.items:
            self.items[item.name][1] += 1
        else:
            self.items[item.name] = [item, 1]

    def remove_item(self, item_name):
        if item_name not in self.items:
            return

        self.items[item_name][1] -= 1
        if self.items[item_name][1] == 0:
            del self.items[item_name]

    def total(self):
        return sum(item.price * qty for item, qty in self.items.values())

    def calculate_tax(self):
        return self.total() * 0.05

    def final_total(self):
        return self.total() + self.calculate_tax()

    def clear_cart(self):
        self.items.clear()

    # -------------------------------
    # Save receipt as PDF
    # -------------------------------
    def save_receipt_pdf(self, payment_method):
        if not self.items:
            return None

        filename = f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(os.getcwd(), filename)

        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4

        y = height - 50
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, "Café Receipt")

        y -= 25
        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"Order ID: {self.order_id}")

        c.drawString(50,y, f"Payment Method:, {payment_method}")
        y -= 20

        y -= 40
        c.setFont("Helvetica", 11)

        for item, qty in self.items.values():
            c.drawString(50, y, f"{item.name} x{qty}")
            c.drawRightString(550, y, f"Rs. {item.price * qty:.2f}")
            y -= 20

        y -= 10
        c.line(50, y, 550, y)

        y -= 30
        c.drawString(50, y, "Subtotal:")
        c.drawRightString(550, y, f"Rs. {self.total():.2f}")

        y -= 20
        c.drawString(50, y, "GST (5%):")
        c.drawRightString(550, y, f"Rs. {self.calculate_tax():.2f}")

        y -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Total:")
        c.drawRightString(550, y, f"Rs. {self.final_total():.2f}")

        c.showPage()
        c.save()

        webbrowser.open(filepath)
        return filename


# -------------------------------
# Menu items
# -------------------------------
coffee_items = [
    Item("Espresso", 120),
    Item("Latte", 135),
    Item("Cappuccino", 113),
    Item("Americano", 140),
    Item("Mocha", 155),
]

tea_items = [
    Item("Masala Chai", 15),
    Item("Green Tea", 20),
    Item("Lemon Tea", 25),
]

cold_beverages = [
    Item("Cold Coffee", 40),
    Item("Iced Latte", 55),
    Item("Milkshake", 65),
]

non_coffee_drinks = [
    Item("Hot Chocolate", 80),
    Item("Matcha Latte", 88),
    Item("Fresh Lime Soda", 33),
]

add_ons = [
    Item("Extra Milk", 12),
    Item("Soy Milk", 41),
    Item("Whipped Cream", 32),
]
