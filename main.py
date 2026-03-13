import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
from database import Database
from billing import BillingManager
from tkcalendar import DateEntry
from datetime import datetime
import os

# Set UI appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DROPApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DROP | Premium Billing")
        self.geometry("1100x700")
        
        # Initialize Database
        self.db = Database()
        
        # UI State
        self.cart = []
        self.current_user_type = None # "staff" or "admin"
        self.pay_mode = ctk.StringVar(value="cash")
        
        # Configure Grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.show_login_screen()

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

    # --- SCREENS ---

    def show_login_screen(self):
        self.clear_screen()
        
        frame = ctk.CTkFrame(self, corner_radius=20, fg_color="transparent")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        label = ctk.CTkLabel(frame, text="DROP", font=ctk.CTkFont(family="Helvetica", size=80, weight="bold"))
        label.pack(pady=(0, 10))
        
        sub_label = ctk.CTkLabel(frame, text="PREMIUM CLOTHING SYSTEM", font=ctk.CTkFont(family="Helvetica", size=14, slant="italic"))
        sub_label.pack(pady=(0, 50))

        staff_btn = ctk.CTkButton(frame, text="Staff Login", height=50, width=250, 
                                 font=ctk.CTkFont(size=16, weight="bold"),
                                 command=lambda: self.login("staff"))
        staff_btn.pack(pady=10)

        admin_btn = ctk.CTkButton(frame, text="Admin Login", height=50, width=250, 
                                 font=ctk.CTkFont(size=16, weight="bold"),
                                 fg_color="#333333", hover_color="#444444",
                                 command=lambda: self.login("admin"))
        admin_btn.pack(pady=10)

    def login(self, user_type):
        self.current_user_type = user_type
        if user_type == "staff":
            self.show_staff_panel()
        else:
            self.show_admin_panel()

    # --- STAFF PANEL ---

    def show_staff_panel(self):
        self.clear_screen()
        self.cart = []
        
        # Main Layout
        self.grid_columnconfigure(0, weight=6) # Content
        self.grid_columnconfigure(1, weight=4) # Cart
        self.grid_rowconfigure(0, weight=1)

        # Content Side
        content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#1a1a1a")
        content_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        title_label = ctk.CTkLabel(content_frame, text="STAFF PANEL", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20, padx=20, anchor="w")

        # Product Search
        search_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        search_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(search_frame, text="Product Search (ID/Code):").pack(side="left", padx=5)
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Type to filter...")
        self.search_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self.update_suggestions)
        self.search_entry.bind("<Return>", lambda e: self.search_product())
        
        search_btn = ctk.CTkButton(search_frame, text="Add Top", width=80, command=self.search_product)
        search_btn.pack(side="left", padx=5)

        # Dropdown Selection
        dropdown_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        dropdown_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(dropdown_frame, text="Select Product:").pack(side="left", padx=5)
        # Cache full list for filtering
        self.all_inventory = self.db.get_all_clothes()
        self.product_names = [item['name'] for item in self.all_inventory]
        
        self.product_dropdown = ctk.CTkComboBox(dropdown_frame, values=self.product_names, 
                                               command=self.dropdown_added, state="readonly")
        self.product_dropdown.pack(side="left", padx=5, fill="x", expand=True)
        self.product_dropdown.set("— Select Clothing —")
        self.product_dropdown.configure(text_color="gray50")

        # Manual Entry
        manual_frame = ctk.CTkLabel(content_frame, text="— Manual Entry —", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        m_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        m_frame.pack(pady=10, padx=20, fill="x")
        
        self.m_name = ctk.CTkEntry(m_frame, placeholder_text="Cloth Name")
        self.m_name.pack(side="left", padx=2, fill="x", expand=True)
        self.m_price = ctk.CTkEntry(m_frame, placeholder_text="Price", width=100)
        self.m_price.pack(side="left", padx=2)
        self.m_qty = ctk.CTkEntry(m_frame, placeholder_text="Qty", width=80)
        self.m_qty.pack(side="left", padx=2)
        
        add_manual_btn = ctk.CTkButton(content_frame, text="Add Manually", command=self.add_manual_item)
        add_manual_btn.pack(pady=10)

        # Back to login
        back_btn = ctk.CTkButton(content_frame, text="Logout", fg_color="transparent", border_width=1, command=self.show_login_screen)
        back_btn.pack(side="bottom", pady=20)

        # Cart Side
        self.cart_frame = ctk.CTkFrame(self, corner_radius=0, border_width=2, border_color="#333333")
        self.cart_frame.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        
        self.render_cart()

    def render_cart(self):
        for widget in self.cart_frame.winfo_children():
            widget.destroy()

        title = ctk.CTkLabel(self.cart_frame, text="SHOPPING CART", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=15)

        # Scrollable area for items
        items_container = ctk.CTkScrollableFrame(self.cart_frame, fg_color="transparent", height=350)
        items_container.pack(fill="both", expand=True, padx=10)

        grand_total = 0
        for i, item in enumerate(self.cart):
            item_row = ctk.CTkFrame(items_container, fg_color="#252525", corner_radius=5)
            item_row.pack(fill="x", pady=5)
            
            ctk.CTkLabel(item_row, text=item['name'], font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
            
            # Line Total
            lt = item['price'] * item['quantity']
            grand_total += lt
            ctk.CTkLabel(item_row, text=f"₹{lt:.2f}").pack(side="right", padx=10)
            
            # Remove
            btn_remove = ctk.CTkButton(item_row, text="X", width=25, height=25, fg_color="#880000", hover_color="#aa0000",
                                      command=lambda idx=i: self.remove_cart_item(idx))
            btn_remove.pack(side="right", padx=5)

            # Qty adjustment
            qty_frame = ctk.CTkFrame(item_row, fg_color="transparent")
            qty_frame.pack(side="right", padx=10)
            
            ctk.CTkButton(qty_frame, text="-", width=20, height=20, command=lambda idx=i: self.update_qty(idx, -1)).pack(side="left")
            ctk.CTkLabel(qty_frame, text=str(item['quantity']), width=30).pack(side="left")
            ctk.CTkButton(qty_frame, text="+", width=20, height=20, command=lambda idx=i: self.update_qty(idx, 1)).pack(side="left")

        # Bottom section: Total & Payment
        bottom_frame = ctk.CTkFrame(self.cart_frame, fg_color="transparent")
        bottom_frame.pack(fill="x", pady=20, padx=20)

        total_label = ctk.CTkLabel(bottom_frame, text=f"GRAND TOTAL: ₹{grand_total:.2f}", 
                                  font=ctk.CTkFont(size=22, weight="bold"), text_color="#00ffcc")
        total_label.pack(pady=10)
        self.grand_total = grand_total

        # Payment selection
        ctk.CTkLabel(bottom_frame, text="Payment Method:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 0))
        
        pay_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        pay_frame.pack(pady=5)
        
        ctk.CTkRadioButton(pay_frame, text="Cash", variable=self.pay_mode, value="cash", command=self.update_payment_ui).pack(side="left", padx=10)
        ctk.CTkRadioButton(pay_frame, text="UPI", variable=self.pay_mode, value="upi", command=self.update_payment_ui).pack(side="left", padx=10)
        ctk.CTkRadioButton(pay_frame, text="Both", variable=self.pay_mode, value="both", command=self.update_payment_ui).pack(side="left", padx=10)

        # Container for Cash/UPI split entries
        self.breakdown_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent", height=40)
        self.breakdown_frame.pack(fill="x", pady=5)
        self.breakdown_frame.pack_propagate(False) # Keep height stable
        
        self.cash_entry = ctk.CTkEntry(self.breakdown_frame, placeholder_text="Cash Amount", width=120)
        self.upi_entry = ctk.CTkEntry(self.breakdown_frame, placeholder_text="UPI Amount", width=120)

        # Fixed Buttons Frame
        btn_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))

        ctk.CTkButton(btn_frame, text="Clear Cart", fg_color="transparent", border_width=1, 
                     command=lambda: [self.cart.clear(), self.render_cart()]).pack(pady=5)
        
        create_bill_btn = ctk.CTkButton(btn_frame, text="CREATE BILL", height=55, 
                                       font=ctk.CTkFont(size=20, weight="bold"),
                                       fg_color="#0066ff", hover_color="#0055ee",
                                       command=self.create_bill)
        create_bill_btn.pack(fill="x", pady=5)
        
        # Initial sync
        self.update_payment_ui()

    def update_qty(self, idx, delta):
        self.cart[idx]['quantity'] += delta
        if self.cart[idx]['quantity'] < 1:
            self.cart[idx]['quantity'] = 1
        self.render_cart()

    def remove_cart_item(self, idx):
        self.cart.pop(idx)
        self.render_cart()

    def update_payment_ui(self):
        for widget in self.breakdown_frame.winfo_children():
            widget.pack_forget()
        
        if self.pay_mode.get() == "both":
            # Centering the entries within the breakdown_frame
            self.cash_entry.pack(side="left", expand=True, padx=(20, 5))
            self.upi_entry.pack(side="left", expand=True, padx=(5, 20))

    def update_suggestions(self, event):
        val = self.search_entry.get().strip().lower()
        if not val:
            self.product_dropdown.configure(values=self.product_names, text_color="gray50")
            self.product_dropdown.set("— Select Clothing —")
            return

        # Filter names that start with typed characters
        filtered = [name for name in self.product_names if name.lower().startswith(val)]
        
        if filtered:
            self.product_dropdown.configure(values=filtered, text_color="white")
            self.product_dropdown.set(filtered[0]) # Auto-highlight the first result
        else:
            self.product_dropdown.configure(values=[], text_color="gray50")
            self.product_dropdown.set("No matches found...")

    def search_product(self):
        code = self.search_entry.get().strip()
        if not code: return
        
        # Look up in all clothes
        clothes = self.db.get_all_clothes()
        match = next((item for item in clothes if item['name'].lower() == code.lower()), None)
        
        if match:
            self.add_to_cart(match['name'], match['price'])
            self.search_entry.delete(0, 'end')
        else:
            messagebox.showerror("Not Found", f"Product '{code}' not found in database.")

    def dropdown_added(self, choice):
        if choice in ["— Select Clothing —", "No matches found..."]:
            return
            
        clothes = self.db.get_all_clothes()
        match = next((item for item in clothes if item['name'] == choice), None)
        if match:
            self.add_to_cart(match['name'], match['price'])
            self.product_dropdown.configure(text_color="gray50")
            self.product_dropdown.set("— Select Clothing —")
            self.search_entry.delete(0, 'end') # Clear search bar too
            self.product_dropdown.configure(values=self.product_names) # Reset list

    def add_manual_item(self):
        name = self.m_name.get().strip()
        price = self.m_price.get().strip()
        qty = self.m_qty.get().strip()
        
        if not name or not price or not qty:
            messagebox.showwarning("Input Error", "All fields are required.")
            return
        
        try:
            self.add_to_cart(name, float(price), int(qty))
            self.m_name.delete(0, 'end')
            self.m_price.delete(0, 'end')
            self.m_qty.delete(0, 'end')
        except:
            messagebox.showerror("Input Error", "Price must be number and Qty must be integer.")

    def add_to_cart(self, name, price, qty=1):
        # Check if item exists
        for item in self.cart:
            if item['name'] == name:
                item['quantity'] += qty
                self.render_cart()
                return
        
        self.cart.append({
            "name": name,
            "price": price,
            "quantity": qty,
            "line_total": price * qty
        })
        self.render_cart()

    def create_bill(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Add items to cart first.")
            return

        method = self.pay_mode.get()
        cash_amt = 0
        upi_amt = 0
        
        if method == "both":
            try:
                cash_amt = float(self.cash_entry.get())
                upi_amt = float(self.upi_entry.get())
                if round(cash_amt + upi_amt, 2) != round(self.grand_total, 2):
                    messagebox.showerror("Validation Error", f"Sum of Cash and UPI must equal Grand Total (₹{self.grand_total:.2f})")
                    return
            except:
                messagebox.showerror("Validation Error", "Please enter valid numbers for breakdown.")
                return
        elif method == "cash":
            cash_amt = self.grand_total
        else:
            upi_amt = self.grand_total

        # Save to DB
        bill_data = {
            "items": self.cart,
            "total": self.grand_total,
            "payment_method": method,
            "cash_amount": cash_amt,
            "upi_amount": upi_amt,
            "timestamp": datetime.now() # Temp local for UI, DB will use SERVER_TIMESTAMP
        }
        
        if not self.db.connected:
            messagebox.showerror("DB Error", "Not connected to Firebase.")
            return

        success, res = self.db.save_bill(bill_data)
        if success:
            bill_data['id'] = res
            self.show_receipt_popup(bill_data)
            self.cart = []
            self.render_cart()
        else:
            messagebox.showerror("Firebase Error", f"Failed to save bill to Firebase:\n\n{res}")

    def show_receipt_popup(self, bill_data):
        popup = ctk.CTkToplevel(self)
        popup.title("Receipt Preview")
        popup.geometry("450x650")
        popup.attributes("-topmost", True)
        
        # Format text for display
        ts = bill_data.get('timestamp', datetime.now())
        ts_str = ts.strftime('%Y-%m-%d %H:%M:%S') if hasattr(ts, 'strftime') else str(ts)
        
        receipt_text = "            DROP\n"
        receipt_text += "  City Center Kunnamkulam, Thrissur\n"
        receipt_text += " Near Private Bus Stand, Kunnamkulam\n"
        receipt_text += "-" * 40 + "\n"
        receipt_text += f"Date & Time: {ts_str}\n"
        receipt_text += f"Bill ID: {bill_data.get('id', 'N/A')}\n"
        receipt_text += "-" * 40 + "\n"
        receipt_text += f"{'Item':<20} {'Qty':>3} {'Price':>8} {'Total':>8}\n"
        receipt_text += "-" * 40 + "\n"
        
        for item in bill_data.get('items', []):
            name = item['name'][:18]
            receipt_text += f"{name:<20} {item['quantity']:>3} {item['price']:>8.2f} {item['line_total']:>8.2f}\n"
            
        receipt_text += "-" * 40 + "\n"
        receipt_text += f"{'GRAND TOTAL:':<30} ₹{bill_data.get('total', 0):>8.2f}\n"
        receipt_text += f"{'Payment Method:':<30} {bill_data.get('payment_method', '').upper():>8}\n"
        
        if bill_data.get('payment_method') == 'both':
            receipt_text += f" Cash: ₹{bill_data.get('cash_amount', 0):.2f} / UPI: ₹{bill_data.get('upi_amount', 0):.2f}\n"
            
        receipt_text += "-" * 40 + "\n"
        receipt_text += "    Thank you for shopping at DROP\n"

        # Display area
        display_frame = ctk.CTkFrame(popup, fg_color="#1a1a1a", corner_radius=10)
        display_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        lbl = ctk.CTkLabel(display_frame, text=receipt_text, font=ctk.CTkFont(family="Courier", size=13), 
                          justify="left", text_color="white")
        lbl.pack(pady=20, padx=10, fill="both")
        
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(side="bottom", pady=20)
        
        print_btn = ctk.CTkButton(btn_frame, text="Print Bill", 
                                 command=lambda: [BillingManager.generate_pdf(bill_data), 
                                                messagebox.showinfo("Success", "Sending bill to printer...")])
        print_btn.pack(side="left", padx=10)
        
        close_btn = ctk.CTkButton(btn_frame, text="Close", fg_color="#333", command=popup.destroy)
        close_btn.pack(side="left", padx=10)

    # --- ADMIN PANEL ---

    def show_admin_panel(self):
        self.clear_screen()
        
        # Tabs
        tabview = ctk.CTkTabview(self)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_dashboard = tabview.add("Dashboard")
        self.tab_bills = tabview.add("Manage Bills")
        self.tab_inventory = tabview.add("Inventory")
        
        self.setup_admin_dashboard()
        self.setup_admin_bills()
        self.setup_admin_inventory()
        
        # Footer
        footer = ctk.CTkFrame(self, height=30, fg_color="#111")
        footer.pack(fill="x", side="bottom")
        
        status_text = "Firebase: Connected ✅" if self.db.connected else "Firebase: Not Connected ❌"
        status_color = "#00ff00" if self.db.connected else "#ff0000"
        ctk.CTkLabel(footer, text=status_text, text_color=status_color, font=ctk.CTkFont(size=12)).pack(side="left", padx=10)
        
        ctk.CTkButton(footer, text="Logout", width=60, height=20, font=ctk.CTkFont(size=10),
                     command=self.show_login_screen).pack(side="right", padx=10, pady=2)

    def setup_admin_dashboard(self):
        sales, count = self.db.get_today_stats()
        
        # Refresh container
        self.dash_frame = ctk.CTkFrame(self.tab_dashboard, fg_color="transparent")
        self.dash_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(self.dash_frame, text="TODAY'S OVERVIEW", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=30)
        
        stats_box = ctk.CTkFrame(self.dash_frame, fg_color="#222", corner_radius=15, width=600, height=200)
        stats_box.pack(pady=10)
        
        s_frame = ctk.CTkFrame(stats_box, fg_color="transparent")
        s_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(s_frame, text=f"Total Sales: ₹{sales:.2f}", font=ctk.CTkFont(size=30, weight="bold"), text_color="#00ffcc").pack(pady=10)
        ctk.CTkLabel(s_frame, text=f"Number of Bills: {count}", font=ctk.CTkFont(size=20)).pack(pady=10)

        refresh_btn = ctk.CTkButton(self.dash_frame, text="Refresh Data", command=self.setup_admin_dashboard)
        refresh_btn.pack(pady=20)

    def setup_admin_bills(self):
        for widget in self.tab_bills.winfo_children():
            widget.destroy()

        top_bar = ctk.CTkFrame(self.tab_bills, fg_color="transparent")
        top_bar.pack(fill="x", pady=10)
        
        ctk.CTkLabel(top_bar, text="Filter by Date:").pack(side="left", padx=5)
        self.filter_date = DateEntry(top_bar, width=12, background='darkblue',
                                     foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.filter_date.pack(side="left", padx=5)

        ctk.CTkLabel(top_bar, text="Pay Method:").pack(side="left", padx=5)
        self.filter_pay = ctk.CTkComboBox(top_bar, values=["All", "Cash", "UPI", "Both"], width=100)
        self.filter_pay.pack(side="left", padx=5)
        self.filter_pay.set("All")
        
        ctk.CTkButton(top_bar, text="Filter", command=self.load_bills_list).pack(side="left", padx=10)
        
        # Treeview for bills
        columns = ("id", "date", "method", "total")
        self.bill_tree = ttk.Treeview(self.tab_bills, columns=columns, show="headings")
        self.bill_tree.heading("id", text="Bill ID")
        self.bill_tree.heading("date", text="Date & Time")
        self.bill_tree.heading("method", text="Method")
        self.bill_tree.heading("total", text="Total")
        self.bill_tree.column("id", width=150)
        self.bill_tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.bill_tree.bind("<Double-1>", lambda e: self.show_bill_detail())

        # Actions
        act_frame = ctk.CTkFrame(self.tab_bills, fg_color="transparent")
        act_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(act_frame, text="Delete Selected", fg_color="#660000", command=self.confirm_delete_bill).pack(side="left", padx=10)
        ctk.CTkButton(act_frame, text="Delete All Bills", fg_color="#aa0000", command=self.confirm_delete_all_bills).pack(side="left", padx=10)
        
        self.load_bills_list()

    def load_bills_list(self):
        # Clear existing
        for item in self.bill_tree.get_children():
            self.bill_tree.delete(item)
            
        method = self.filter_pay.get()
        selected_date = self.filter_date.get_date()
        
        bills = self.db.get_bills(date=selected_date, payment_method=method)
        
        for b in bills:
            ts = b.get('timestamp')
            date_str = ts.strftime("%Y-%m-%d %H:%M") if hasattr(ts, 'strftime') else "N/A"
            self.bill_tree.insert("", "end", values=(b['id'], date_str, b.get('payment_method', '').upper(), f"₹{b.get('total', 0):.2f}"))

    def show_bill_detail(self):
        sel = self.bill_tree.selection()
        if not sel: return
        bill_id = self.bill_tree.item(sel[0])['values'][0]
        
        # Fetch full details
        bills = self.db.get_bills()
        bill = next((b for b in bills if b['id'] == bill_id), None)
        if bill:
            self.show_receipt_popup(bill)

    def confirm_delete_bill(self):
        sel = self.bill_tree.selection()
        if not sel:
            messagebox.showwarning("Selection", "Select a bill to delete.")
            return
        
        self.ask_password(lambda: self.do_delete_bill(self.bill_tree.item(sel[0])['values'][0]))

    def confirm_delete_all_bills(self):
        def proceed():
            if messagebox.askyesno("Confirm", "Are you sure? This cannot be undone."):
                success, msg = self.db.delete_all_bills()
                if success:
                    messagebox.showinfo("Success", msg)
                    self.load_bills_list()
                    self.setup_admin_dashboard()
                else:
                    messagebox.showerror("Error", f"Failed to delete bills: {msg}")
        
        self.ask_password(proceed)

    def do_delete_bill(self, bill_id):
        success, msg = self.db.delete_bill(bill_id)
        if success:
            messagebox.showinfo("Success", msg)
            self.load_bills_list()
            self.setup_admin_dashboard()
        else:
            messagebox.showerror("Error", f"Failed to delete bill: {msg}")

    def ask_password(self, callback):
        dlg = ctk.CTkInputDialog(text="Enter Admin Password to continue:", title="Security Check")
        pwd = dlg.get_input()
        if pwd == "ArJuN":
            callback()
        elif pwd is not None:
            messagebox.showerror("Incorrect password", "Incorrect password. Action cancelled.")

    def setup_admin_inventory(self):
        for widget in self.tab_inventory.winfo_children():
            widget.destroy()
            
        # Form
        form = ctk.CTkFrame(self.tab_inventory)
        form.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(form, text="Add New Item", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=3, pady=5)
        
        self.inv_name = ctk.CTkEntry(form, placeholder_text="Cloth Name / ID")
        self.inv_name.grid(row=1, column=0, padx=5, pady=5)
        self.inv_cat = ctk.CTkEntry(form, placeholder_text="Category")
        self.inv_cat.grid(row=1, column=1, padx=5, pady=5)
        self.inv_price = ctk.CTkEntry(form, placeholder_text="Price")
        self.inv_price.grid(row=1, column=2, padx=5, pady=5)
        
        ctk.CTkButton(form, text="Add Item", command=self.admin_add_cloth).grid(row=1, column=3, padx=10)

        # List
        self.inv_tree = ttk.Treeview(self.tab_inventory, columns=("name", "cat", "price"), show="headings")
        self.inv_tree.heading("name", text="Cloth Name (ID)")
        self.inv_tree.heading("cat", text="Category")
        self.inv_tree.heading("price", text="Price")
        self.inv_tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkButton(self.tab_inventory, text="Delete Selected Item", fg_color="#660000", 
                     command=self.admin_delete_cloth).pack(pady=10)
        
        self.load_inventory_list()

    def load_inventory_list(self):
        for item in self.inv_tree.get_children():
            self.inv_tree.delete(item)
        
        clothes = self.db.get_all_clothes()
        for c in clothes:
            self.inv_tree.insert("", "end", values=(c['name'], c.get('category', 'N/A'), f"₹{c.get('price', 0):.2f}"))

    def admin_add_cloth(self):
        name = self.inv_name.get().strip()
        cat = self.inv_cat.get().strip()
        price = self.inv_price.get().strip()
        
        if not name or not price:
            messagebox.showwarning("Error", "Name and Price are required.")
            return
            
        try:
            success, msg = self.db.add_cloth(name, cat, float(price))
            if success:
                messagebox.showinfo("Success", "Item added.")
                self.inv_name.delete(0, 'end')
                self.inv_cat.delete(0, 'end')
                self.inv_price.delete(0, 'end')
                self.load_inventory_list()
            else:
                messagebox.showerror("Firebase Error", f"Failed to add to Firebase:\n\n{msg}")
        except Exception as e:
            messagebox.showerror("Error", f"Price must be a number.\n({str(e)})")

    def admin_delete_cloth(self):
        sel = self.inv_tree.selection()
        if not sel: return
        cloth_id = self.inv_tree.item(sel[0])['values'][0]
        
        if messagebox.askyesno("Confirm", f"Delete {cloth_id}?"):
            if self.db.delete_cloth(cloth_id):
                self.load_inventory_list()
            else:
                messagebox.showerror("Error", "Failed to delete.")

if __name__ == "__main__":
    app = DROPApp()
    app.mainloop()
