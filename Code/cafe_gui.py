# cafe_gui.py
# -------------------------------
# Tkinter GUI
# -------------------------------

import tkinter as tk
from tkinter import ttk, messagebox
from coffee2 import (
    Order,
    coffee_items,
    tea_items,
    cold_beverages,
    non_coffee_drinks,
    add_ons,
)

CATEGORIES = {
    "Coffee": coffee_items,
    "Tea": tea_items,
    "Cold Beverages": cold_beverages,
    "Non-Coffee Drinks": non_coffee_drinks,
    "Add-ons": add_ons,
}


class CafeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Café Machine")
        self.root.geometry("600x620")

        # -------------------------------
        # UI COLORS
        # -------------------------------
        self.bg_color = "#FFF8E7"
        self.btn_color = "#8B4513"
        self.btn_text = "white"
        self.frame_color = "#F5DEB3"

        self.root.configure(bg=self.bg_color)

        # Main Frame
        self.main_frame = tk.Frame(self.root, bg=self.frame_color)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.order = Order()
        self.order_history = []

        # -------------------------------
        # HEADER
        # -------------------------------
        tk.Label(
            self.main_frame,
            text="Café Machine",
            font=("Arial", 20, "bold"),
            bg=self.frame_color
        ).pack(pady=10)

        # -------------------------------
        # CATEGORY SECTION
        # -------------------------------
        cat_frame = tk.Frame(self.main_frame, bg=self.frame_color)
        cat_frame.pack(pady=5)

        tk.Label(cat_frame, text="Category", bg=self.frame_color).grid(row=0, column=0, pady=5)

        self.category_var = tk.StringVar()

        self.category_box = ttk.Combobox(
            cat_frame, textvariable=self.category_var, state="readonly", width=30
        )
        self.category_box["values"] = list(CATEGORIES.keys())
        self.category_box.grid(row=1, column=0, padx=5)
        self.category_box.bind("<<ComboboxSelected>>", self.load_items)

        # -------------------------------
        # ITEM SECTION
        # -------------------------------
        item_frame = tk.Frame(self.main_frame, bg=self.frame_color)
        item_frame.pack(pady=5)

        tk.Label(item_frame, text="Item", bg=self.frame_color).grid(row=0, column=0, pady=5)

        self.item_var = tk.StringVar()

        self.item_box = ttk.Combobox(
            item_frame, textvariable=self.item_var, state="readonly", width=30
        )
        self.item_box.grid(row=1, column=0, padx=5)

        # -------------------------------
        # ACTION BUTTONS
        # -------------------------------
        btn_frame = tk.Frame(self.main_frame, bg=self.frame_color)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Item", width=20,
                  bg=self.btn_color, fg=self.btn_text,
                  command=self.add_item).grid(row=0, column=0, pady=3)

        tk.Button(btn_frame, text="Remove Item", width=20,
                  bg=self.btn_color, fg=self.btn_text,
                  command=self.remove_item).grid(row=1, column=0, pady=3)

        tk.Button(btn_frame, text="Clear Cart", width=20,
                  bg=self.btn_color, fg=self.btn_text,
                  command=self.clear_cart).grid(row=2, column=0, pady=3)

        tk.Button(btn_frame, text="View Order History", width=22,
                  bg=self.btn_color, fg=self.btn_text,
                  command=self.show_order_history).grid(row=3, column=0, pady=3)
        
        tk.Button(self.main_frame, text="View Analytics Dashboard", width=25, 
                  bg=self.btn_color, fg = self.btn_text,
                  command = self.show_dashboard
                  ).pack(pady=5)

        # -------------------------------
        # ORDER SUMMARY
        # -------------------------------
        tk.Label(
            self.main_frame, text="Order Summary",
            font=("Arial", 12, "bold"), bg=self.frame_color
        ).pack(pady=5)

        self.order_box = tk.Text(self.main_frame, height=12, width=55, state="disabled")
        self.order_box.pack()

        # CHECKOUT BUTTON
        self.checkout_btn = tk.Button(
            self.main_frame,
            text="Checkout & Save PDF",
            width=25,
            bg=self.btn_color,
            fg=self.btn_text,
            command=self.checkout,
            state=tk.DISABLED
        )
        self.checkout_btn.pack(pady=15)

    # -------------------------------
    # FUNCTIONS
    # -------------------------------

    def load_items(self, event=None):
        category = self.category_var.get()
        items = CATEGORIES.get(category, [])
        self.item_box["values"] = [f"{i.name} - Rs.{i.price}" for i in items]

    def add_item(self):
        if not self.item_var.get():
            return

        name = self.item_var.get().split(" - ")[0]
        for it in CATEGORIES[self.category_var.get()]:
            if it.name == name:
                self.order.add_item(it)
                break

        self.refresh_cart()
        self.update_checkout_state()

    def remove_item(self):
        if not self.item_var.get():
            return

        name = self.item_var.get().split(" - ")[0]
        self.order.remove_item(name)
        self.refresh_cart()
        self.update_checkout_state()

    def clear_cart(self):
        self.order = Order()
        self.refresh_cart()
        self.update_checkout_state()

    def refresh_cart(self):
        self.order_box.config(state="normal")
        self.order_box.delete("1.0", tk.END)

        if not self.order.items:
            self.order_box.insert(tk.END, "Cart is empty.")
        else:
            for item, qty in self.order.items.values():
                self.order_box.insert(
                    tk.END, f"{item.name} x{qty} - Rs.{item.price * qty}\n"
                )

            self.order_box.insert(
                tk.END,
                f"\nSubtotal: Rs.{self.order.total():.2f}"
                f"\nGST (5%): Rs.{self.order.calculate_tax():.2f}"
                f"\nTotal: Rs.{self.order.final_total():.2f}"
            )

        self.order_box.config(state="disabled")

    def update_checkout_state(self):
        if self.order.items:
            self.checkout_btn.config(state=tk.NORMAL)
        else:
            self.checkout_btn.config(state=tk.DISABLED)


    # -------------------------------
    # CHECKOUT + PAYMENT
    # -------------------------------

    def checkout(self):
        # prevents the check out if cart is empty
        if not self.order.items:
            messagebox.showwarning("Empty Cart", "No items in cart.")
            return

        payment_window = tk.Toplevel(self.root)
        payment_window.title("Select Payment Method")
        payment_window.geometry("300x250")

        method_var = tk.StringVar(value="Cash")

        tk.Label(payment_window, text="Choose Payment Method",
                 font=("Arial", 12, "bold")).pack(pady=10)

        tk.Radiobutton(payment_window, text="Cash",
                       variable=method_var, value="Cash").pack(anchor="w", padx=50)
        tk.Radiobutton(payment_window, text="UPI",
                       variable=method_var, value="UPI").pack(anchor="w", padx=50)
        tk.Radiobutton(payment_window, text="Card",
                       variable=method_var, value="Card").pack(anchor="w", padx=50)

        def confirm_payment():
            method = method_var.get()

            response = messagebox.askyesno(
                "Confirm Payment",
                f"Payment Method: {method}\n"
                f"Total Amount: Rs.{self.order.final_total():.2f}\n\n"
                f"Proceed with payment?"
            )

            if response:
                pdf = self.order.save_receipt_pdf(method)

                self.order_history.append({
                    "order_id": self.order.order_id,
                    "total": self.order.final_total()
                })

                messagebox.showinfo(
                    "Payment Successful",
                    f"Paid via {method}\n\nReceipt saved as:\n{pdf}"
                )

                self.order.clear_cart()
                self.refresh_cart()
                self.update_checkout_state()
                payment_window.destroy()

        tk.Button(payment_window, text="Pay Now", width=20,
                  command=confirm_payment).pack(pady=20)

    # -------------------------------
    # ORDER HISTORY
    # -------------------------------

    def show_order_history(self):
        if not self.order_history:
            messagebox.showinfo("Order History", "No past orders found.")
            return

        window = tk.Toplevel(self.root)
        window.title("Order History")
        window.geometry("400x300")

        text = tk.Text(window, width=45, height=15)
        text.pack(padx=10, pady=10)

        for i, order in enumerate(self.order_history, start=1):
            text.insert(
                tk.END,
                f"{i}. Order ID: {order['order_id']}\n"
                f"   Total: Rs.{order['total']:.2f}\n"
                "-----------------------------\n"
            )

        text.config(state="disabled")

    def show_dashboard(self):
        dashboard = tk.Toplevel(self.root)
        dashboard.title("Analytics Dashboard")
        dashboard.geometry("350x250")

        total_orders = len(self.order_history)
        total_revenue = sum(order["total"] for order in self.order_history)

        tk.Label(dashboard, text="Cafe Analytics", font=("Ariel", 14, "bold")).pack(pady=10)

        tk.Label(dashboard, text=f"Total Orders : {total_orders}")
        tk.Label(dashboard, text=f"Total Revenue : Rs.{total_revenue:.2f}")

        if total_orders == 0:
            tk.Label(dashboard, text="No Data Available yet.", fg="gray").pack(pady=10)
        
                 

# Run App
if __name__ == "__main__":
    root = tk.Tk()
    CafeGUI(root)
    root.mainloop()
