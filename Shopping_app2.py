import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import mysql.connector

# ---------------- DATABASE SETTINGS ----------------
# Yahan apna MySQL root password likho
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Koray@123",
    "database": "online_shopping",
}

# ---------------- COLORS AND FONT ----------------
BG = "#f4f6f8"
SIDEBAR = "#1f2a44"
SIDEBAR_HOVER = "#2d3b5e"
ACCENT = "#ff6b35"
CARD = "#ffffff"
TEXT = "#2c3e50"
MUTED = "#7f8c8d"
FONT = "Segoe UI"


# ---------------- DATABASE HELPERS ----------------
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def run_query(sql, params=None, fetch=True):
    """SELECT ke liye fetch=True, INSERT/UPDATE ke liye fetch=False"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        if fetch:
            return cur.fetchall()
        conn.commit()
    finally:
        conn.close()


# ---------------- UI HELPERS ----------------
def setup_style(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(
        "Treeview",
        background="white",
        fieldbackground="white",
        foreground=TEXT,
        rowheight=30,
        font=(FONT, 10),
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=SIDEBAR,
        foreground="white",
        font=(FONT, 10, "bold"),
        relief="flat",
        padding=6,
    )
    style.map("Treeview.Heading", background=[("active", SIDEBAR_HOVER)])
    style.map(
        "Treeview",
        background=[("selected", ACCENT)],
        foreground=[("selected", "white")],
    )
    style.configure("TCombobox", padding=5)
    style.configure("TEntry", padding=5)


def make_button(parent, text, command, color=ACCENT):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=color,
        fg="white",
        activebackground=color,
        activeforeground="white",
        font=(FONT, 10, "bold"),
        relief="flat",
        bd=0,
        padx=18,
        pady=8,
        cursor="hand2",
    )


def white_card(parent):
    return tk.Frame(parent, bg=CARD, highlightbackground="#e1e5ea", highlightthickness=1)


def page_title(parent, title, subtitle=""):
    tk.Label(parent, text=title, font=(FONT, 20, "bold"), bg=BG, fg=TEXT).pack(
        anchor="w", padx=25, pady=(20, 0)
    )
    tk.Label(parent, text=subtitle, font=(FONT, 10), bg=BG, fg=MUTED).pack(
        anchor="w", padx=25, pady=(0, 10)
    )


def make_tree(parent, columns, widths, height=8):
    frame = tk.Frame(parent, bg=CARD, highlightbackground="#e1e5ea", highlightthickness=1)
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=height)
    for col, w in zip(columns, widths):
        tree.heading(col, text=col)
        tree.column(col, width=w)
    tree.tag_configure("odd", background="#f7f9fb")
    tree.tag_configure("even", background="white")
    tree.tag_configure("low", foreground="#c0392b")
    sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    return frame, tree


def fill_tree(tree, rows, low_index=None):
    """low_index: us column ki value 10 se kam ho to row laal dikhegi"""
    tree.delete(*tree.get_children())
    for i, r in enumerate(rows):
        tags = ["even" if i % 2 == 0 else "odd"]
        if low_index is not None and r[low_index] < 10:
            tags.append("low")
        tree.insert("", "end", values=r, tags=tags)


# ---------------- MAIN APP ----------------
class ShopApp:
    def __init__(self, root):
        self.root = root
        self.prod_info = {}
        root.title("Online Shopping System")
        root.geometry("1150x700")
        root.minsize(1000, 600)
        root.configure(bg=BG)
        setup_style(root)

        # Status bar (sabse neeche)
        self.status = tk.Label(
            root, text="Ready", anchor="w", bg="#dfe4ea", fg=TEXT,
            font=(FONT, 9), padx=10, pady=4,
        )
        self.status.pack(side="bottom", fill="x")

        # Sidebar
        sidebar = tk.Frame(root, bg=SIDEBAR, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text="ONLINE SHOP", bg=SIDEBAR, fg="white",
                 font=(FONT, 16, "bold")).pack(pady=(30, 2))
        tk.Label(sidebar, text="Management System", bg=SIDEBAR, fg="#aab4c8",
                 font=(FONT, 9)).pack(pady=(0, 25))

        # Content area
        self.content = tk.Frame(root, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)
        self.content.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=1)

        pages = [
            ("dashboard", "Dashboard"),
            ("products", "Products"),
            ("customers", "Customers"),
            ("order", "Place Order"),
            ("orders", "All Orders"),
            ("report", "Reports"),
        ]
        self.pages = {}
        self.nav_buttons = {}
        self.current = None
        for key, label in pages:
            page = tk.Frame(self.content, bg=BG)
            page.grid(row=0, column=0, sticky="nsew")
            self.pages[key] = page

            btn = tk.Button(
                sidebar, text="   " + label, anchor="w", bg=SIDEBAR, fg="white",
                activebackground=ACCENT, activeforeground="white",
                font=(FONT, 11), relief="flat", bd=0, padx=15, pady=12,
                cursor="hand2", command=lambda k=key: self.show_page(k),
            )
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, k=key: self.nav_hover(k, True))
            btn.bind("<Leave>", lambda e, k=key: self.nav_hover(k, False))
            self.nav_buttons[key] = btn

        self.build_dashboard()
        self.build_products()
        self.build_customers()
        self.build_order()
        self.build_orders()
        self.build_report()

        self.refresh_all()
        self.show_page("dashboard")

    # ---------- navigation ----------
    def show_page(self, key):
        self.current = key
        self.pages[key].tkraise()
        for k, b in self.nav_buttons.items():
            b.config(bg=ACCENT if k == key else SIDEBAR)

    def nav_hover(self, key, entering):
        if key == self.current:
            return
        self.nav_buttons[key].config(bg=SIDEBAR_HOVER if entering else SIDEBAR)

    def set_status(self, msg):
        self.status.config(text=msg)

    # ---------- DASHBOARD ----------
    def build_dashboard(self):
        p = self.pages["dashboard"]
        page_title(p, "Dashboard", "Store ka quick overview")

        row = tk.Frame(p, bg=BG)
        row.pack(fill="x", padx=17, pady=10)
        self.stat_labels = {}
        cards = [
            ("customers", "Total Customers", "#3498db"),
            ("products", "Total Products", "#9b59b6"),
            ("orders", "Total Orders", "#e67e22"),
            ("revenue", "Total Revenue", "#27ae60"),
        ]
        for i, (key, title, color) in enumerate(cards):
            card = tk.Frame(row, bg=color)
            card.grid(row=0, column=i, padx=8, sticky="nsew")
            row.columnconfigure(i, weight=1)
            tk.Label(card, text=title, bg=color, fg="white",
                     font=(FONT, 10)).pack(anchor="w", padx=18, pady=(15, 0))
            lbl = tk.Label(card, text="0", bg=color, fg="white",
                           font=(FONT, 24, "bold"))
            lbl.pack(anchor="w", padx=18, pady=(0, 15))
            self.stat_labels[key] = lbl

        tk.Label(p, text="Recent Orders", bg=BG, fg=TEXT,
                 font=(FONT, 13, "bold")).pack(anchor="w", padx=25, pady=(15, 5))
        frame, self.d_tree = make_tree(
            p, ("Order ID", "Customer", "Product", "Qty", "Total", "Date", "Status"),
            (80, 180, 220, 60, 100, 110, 100), height=8)
        frame.pack(fill="both", expand=True, padx=25, pady=(0, 20))

    def load_dashboard(self):
        self.stat_labels["customers"].config(
            text=str(run_query("SELECT COUNT(*) FROM customers")[0][0]))
        self.stat_labels["products"].config(
            text=str(run_query("SELECT COUNT(*) FROM products")[0][0]))
        self.stat_labels["orders"].config(
            text=str(run_query("SELECT COUNT(*) FROM orders")[0][0]))
        revenue = run_query(
            "SELECT COALESCE(SUM(quantity * price), 0) FROM order_items")[0][0]
        self.stat_labels["revenue"].config(text="Rs. {:,.0f}".format(revenue))

        rows = run_query(
            "SELECT o.order_id, c.name, p.name, oi.quantity, "
            "oi.quantity * oi.price, o.order_date, o.status "
            "FROM orders o "
            "JOIN customers c ON o.customer_id = c.customer_id "
            "JOIN order_items oi ON o.order_id = oi.order_id "
            "JOIN products p ON oi.product_id = p.product_id "
            "ORDER BY o.order_id DESC LIMIT 8")
        fill_tree(self.d_tree, rows)

    # ---------- PRODUCTS ----------
    def build_products(self):
        p = self.pages["products"]
        page_title(p, "Products", "Stock 10 se kam ho to row laal dikhegi")

        bar = tk.Frame(p, bg=BG)
        bar.pack(fill="x", padx=25)
        tk.Label(bar, text="Search:", bg=BG, fg=TEXT, font=(FONT, 10)).pack(side="left")
        self.p_search = tk.StringVar()
        entry = ttk.Entry(bar, textvariable=self.p_search, width=30)
        entry.pack(side="left", padx=8)
        entry.bind("<KeyRelease>", lambda e: self.load_products())

        frame, self.p_tree = make_tree(
            p, ("ID", "Name", "Price", "Stock", "Category"),
            (60, 300, 120, 100, 180), height=6)
        frame.pack(fill="both", expand=True, padx=25, pady=10)

        form = white_card(p)
        form.pack(fill="x", padx=25, pady=(0, 20))
        tk.Label(form, text="Add New Product", bg=CARD, fg=TEXT,
                 font=(FONT, 11, "bold")).grid(row=0, column=0, columnspan=5,
                                               sticky="w", padx=15, pady=(12, 4))
        self.p_name = tk.StringVar()
        self.p_price = tk.StringVar()
        self.p_stock = tk.StringVar()

        labels = ["Name", "Price", "Stock", "Category"]
        for i, text in enumerate(labels):
            tk.Label(form, text=text, bg=CARD, fg=MUTED,
                     font=(FONT, 9)).grid(row=1, column=i, sticky="w", padx=15)
        ttk.Entry(form, textvariable=self.p_name, width=28).grid(
            row=2, column=0, padx=15, pady=(0, 15))
        ttk.Entry(form, textvariable=self.p_price, width=12).grid(
            row=2, column=1, padx=15, pady=(0, 15))
        ttk.Entry(form, textvariable=self.p_stock, width=12).grid(
            row=2, column=2, padx=15, pady=(0, 15))
        self.p_cat = ttk.Combobox(form, state="readonly", width=18)
        self.p_cat.grid(row=2, column=3, padx=15, pady=(0, 15))
        make_button(form, "Add Product", self.add_product).grid(
            row=2, column=4, padx=15, pady=(0, 15))

        # Stock add karne ka card
        stock_form = white_card(p)
        stock_form.pack(fill="x", padx=25, pady=(0, 20))
        tk.Label(stock_form, text="Add Stock (pehle upar list se product select karo)",
                 bg=CARD, fg=TEXT, font=(FONT, 11, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", padx=15, pady=(12, 4))
        tk.Label(stock_form, text="Kitna stock add karna hai", bg=CARD, fg=MUTED,
                 font=(FONT, 9)).grid(row=1, column=0, sticky="w", padx=15)
        self.stock_add = tk.StringVar()
        ttk.Entry(stock_form, textvariable=self.stock_add, width=14).grid(
            row=2, column=0, padx=15, pady=(0, 15))
        make_button(stock_form, "Add Stock", self.add_stock, "#27ae60").grid(
            row=2, column=1, padx=15, pady=(0, 15))

    def load_products(self):
        search = "%" + self.p_search.get().strip() + "%"
        rows = run_query(
            "SELECT p.product_id, p.name, p.price, p.stock, c.category_name "
            "FROM products p LEFT JOIN categories c ON p.category_id = c.category_id "
            "WHERE p.name LIKE %s ORDER BY p.product_id", (search,))
        fill_tree(self.p_tree, rows, low_index=3)

    def add_product(self):
        name = self.p_name.get().strip()
        cat = self.p_cat.get()
        try:
            price = float(self.p_price.get())
            stock = int(self.p_stock.get())
        except ValueError:
            messagebox.showerror("Error", "Price aur Stock sahi number mein likho")
            return
        if not name or not cat or price <= 0 or stock < 0:
            messagebox.showerror("Error", "Saari details sahi bharo")
            return
        cat_id = int(cat.split(" - ")[0])
        try:
            run_query(
                "INSERT INTO products (name, price, stock, category_id) "
                "VALUES (%s, %s, %s, %s)", (name, price, stock, cat_id), fetch=False)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
            return
        for var in (self.p_name, self.p_price, self.p_stock):
            var.set("")
        self.set_status("Product add ho gaya: " + name)
        self.refresh_all()

    def add_stock(self):
        sel = self.p_tree.selection()
        if not sel:
            messagebox.showerror("Error", "Pehle list se koi product select karo")
            return
        try:
            qty = int(self.stock_add.get())
        except ValueError:
            messagebox.showerror("Error", "Quantity sahi number mein likho")
            return
        if qty <= 0:
            messagebox.showerror("Error", "Quantity 0 se zyada honi chahiye")
            return
        values = self.p_tree.item(sel[0])["values"]
        pid, name = values[0], values[1]
        try:
            run_query("UPDATE products SET stock = stock + %s WHERE product_id = %s",
                      (qty, pid), fetch=False)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
            return
        self.stock_add.set("")
        self.set_status("{} mein {} stock add ho gaya".format(name, qty))
        self.refresh_all()

    # ---------- CUSTOMERS ----------
    def build_customers(self):
        p = self.pages["customers"]
        page_title(p, "Customers", "Saare registered customers")

        frame, self.c_tree = make_tree(
            p, ("ID", "Name", "Email", "Phone", "Address"),
            (60, 200, 260, 140, 240), height=8)
        frame.pack(fill="both", expand=True, padx=25, pady=10)

        bar = tk.Frame(p, bg=BG)
        bar.pack(fill="x", padx=25, pady=(0, 10))
        make_button(bar, "Delete Selected Customer",
                    self.delete_customer, "#e74c3c").pack(side="left")
        tk.Label(bar, text="  (pehle list se customer select karo)", bg=BG,
                 fg=MUTED, font=(FONT, 9)).pack(side="left")

        form = white_card(p)
        form.pack(fill="x", padx=25, pady=(0, 20))
        tk.Label(form, text="Add New Customer", bg=CARD, fg=TEXT,
                 font=(FONT, 11, "bold")).grid(row=0, column=0, columnspan=5,
                                               sticky="w", padx=15, pady=(12, 4))
        self.c_name = tk.StringVar()
        self.c_email = tk.StringVar()
        self.c_phone = tk.StringVar()
        self.c_addr = tk.StringVar()

        fields = [("Name", self.c_name, 20), ("Email", self.c_email, 26),
                  ("Phone", self.c_phone, 14), ("Address", self.c_addr, 24)]
        for i, (text, var, width) in enumerate(fields):
            tk.Label(form, text=text, bg=CARD, fg=MUTED,
                     font=(FONT, 9)).grid(row=1, column=i, sticky="w", padx=15)
            ttk.Entry(form, textvariable=var, width=width).grid(
                row=2, column=i, padx=15, pady=(0, 15))
        make_button(form, "Add Customer", self.add_customer).grid(
            row=2, column=4, padx=15, pady=(0, 15))

    def load_customers(self):
        rows = run_query(
            "SELECT customer_id, name, email, phone, address "
            "FROM customers ORDER BY customer_id")
        fill_tree(self.c_tree, rows)

    def add_customer(self):
        name = self.c_name.get().strip()
        email = self.c_email.get().strip()
        if not name or not email:
            messagebox.showerror("Error", "Name aur Email zaroori hain")
            return
        try:
            run_query(
                "INSERT INTO customers (name, email, phone, address) "
                "VALUES (%s, %s, %s, %s)",
                (name, email, self.c_phone.get().strip(), self.c_addr.get().strip()),
                fetch=False)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
            return
        for var in (self.c_name, self.c_email, self.c_phone, self.c_addr):
            var.set("")
        self.set_status("Customer add ho gaya: " + name)
        self.refresh_all()

    def delete_customer(self):
        sel = self.c_tree.selection()
        if not sel:
            messagebox.showerror("Error", "Pehle list se koi customer select karo")
            return
        values = self.c_tree.item(sel[0])["values"]
        cid, name = values[0], values[1]

        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM orders WHERE customer_id = %s", (cid,))
            order_count = cur.fetchone()[0]

            if order_count > 0:
                ok = messagebox.askyesno(
                    "Confirm Delete",
                    "{} ke {} order(s) hain.\n\nCustomer ke saare orders, payments "
                    "aur reviews bhi delete ho jayenge.\n\nKya sach mein delete karna hai?"
                    .format(name, order_count),
                    icon="warning")
            else:
                ok = messagebox.askyesno(
                    "Confirm Delete", "Customer '{}' ko delete karein?".format(name))
            if not ok:
                return

            # Foreign key ki wajah se pehle child tables, phir customer delete hota hai
            cur.execute(
                "DELETE FROM payments WHERE order_id IN "
                "(SELECT order_id FROM orders WHERE customer_id = %s)", (cid,))
            cur.execute(
                "DELETE FROM order_items WHERE order_id IN "
                "(SELECT order_id FROM orders WHERE customer_id = %s)", (cid,))
            cur.execute("DELETE FROM reviews WHERE customer_id = %s", (cid,))
            cur.execute("DELETE FROM orders WHERE customer_id = %s", (cid,))
            cur.execute("DELETE FROM customers WHERE customer_id = %s", (cid,))
            conn.commit()
            self.set_status("Customer delete ho gaya: " + str(name))
            self.refresh_all()
        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
            messagebox.showerror("Database Error", str(e))
        finally:
            if conn:
                conn.close()

    # ---------- PLACE ORDER ----------
    def build_order(self):
        p = self.pages["order"]
        page_title(p, "Place Order", "Customer aur product chuno, order ho jayega")

        card = white_card(p)
        card.pack(anchor="nw", padx=25, pady=10)
        inner = tk.Frame(card, bg=CARD)
        inner.pack(padx=35, pady=30)

        def label(text, row):
            tk.Label(inner, text=text, bg=CARD, fg=TEXT,
                     font=(FONT, 10, "bold")).grid(row=row, column=0, sticky="w",
                                                   pady=10, padx=(0, 25))

        label("Customer", 0)
        self.o_cust = ttk.Combobox(inner, state="readonly", width=40)
        self.o_cust.grid(row=0, column=1, sticky="w")

        label("Product", 1)
        self.o_prod = ttk.Combobox(inner, state="readonly", width=40)
        self.o_prod.grid(row=1, column=1, sticky="w")
        self.o_prod.bind("<<ComboboxSelected>>", lambda e: self.update_summary())

        label("Quantity", 2)
        self.o_qty = tk.StringVar(value="1")
        self.o_qty.trace_add("write", lambda *a: self.update_summary())
        ttk.Entry(inner, textvariable=self.o_qty, width=10).grid(row=2, column=1, sticky="w")

        label("Payment Method", 3)
        self.o_method = ttk.Combobox(inner, state="readonly", width=20,
                                     values=["UPI", "Card", "Cash on Delivery"])
        self.o_method.current(0)
        self.o_method.grid(row=3, column=1, sticky="w")

        self.o_summary = tk.Label(
            inner, text="Product chuno to price aur stock yahan dikhega",
            bg="#fff4ec", fg=ACCENT, font=(FONT, 11, "bold"),
            padx=14, pady=12, anchor="w")
        self.o_summary.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(15, 5))

        make_button(inner, "Place Order", self.place_order).grid(
            row=5, column=0, columnspan=2, pady=(15, 0))

    def update_summary(self):
        prod = self.o_prod.get()
        if not prod:
            return
        pid = int(prod.split(" - ")[0])
        price, stock = self.prod_info.get(pid, (0, 0))
        try:
            qty = int(self.o_qty.get())
        except ValueError:
            qty = 0
        total = price * qty
        self.o_summary.config(
            text="Price: Rs. {:.2f}   |   Stock: {}   |   Total: Rs. {:.2f}".format(
                price, stock, total))

    def place_order(self):
        cust = self.o_cust.get()
        prod = self.o_prod.get()
        method = self.o_method.get()
        try:
            qty = int(self.o_qty.get())
        except ValueError:
            messagebox.showerror("Error", "Quantity number honi chahiye")
            return
        if not cust or not prod or qty <= 0:
            messagebox.showerror("Error", "Customer, Product aur sahi Quantity chuno")
            return

        cid = int(cust.split(" - ")[0])
        pid = int(prod.split(" - ")[0])

        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("SELECT price, stock FROM products WHERE product_id = %s", (pid,))
            price, stock = cur.fetchone()
            if qty > stock:
                messagebox.showerror("Error", "Itna stock nahi hai. Available: " + str(stock))
                return

            cur.execute(
                "INSERT INTO orders (customer_id, order_date, status) VALUES (%s, %s, %s)",
                (cid, date.today(), "Pending"))
            order_id = cur.lastrowid

            # Is insert par trigger chalega aur stock apne aap kam hoga
            cur.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, price) "
                "VALUES (%s, %s, %s, %s)", (order_id, pid, qty, price))

            cur.execute(
                "INSERT INTO payments (order_id, amount, method, payment_date) "
                "VALUES (%s, %s, %s, %s)",
                (order_id, price * qty, method, date.today()))
            conn.commit()
            messagebox.showinfo(
                "Order Placed",
                "Order ho gaya!\n\nOrder ID: {}\nTotal: Rs. {:.2f}".format(order_id, price * qty))
            self.o_qty.set("1")
            self.set_status("Order #{} place ho gaya".format(order_id))
            self.refresh_all()
            self.update_summary()
        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
            messagebox.showerror("Database Error", str(e))
        finally:
            if conn:
                conn.close()

    # ---------- ALL ORDERS ----------
    def build_orders(self):
        p = self.pages["orders"]
        page_title(p, "All Orders", "Order select karke uska status badlo")

        frame, self.o_tree = make_tree(
            p, ("Order ID", "Customer", "Product", "Qty", "Total", "Date", "Status"),
            (80, 180, 220, 60, 100, 110, 100), height=14)
        frame.pack(fill="both", expand=True, padx=25, pady=10)

        bar = tk.Frame(p, bg=BG)
        bar.pack(fill="x", padx=25, pady=(0, 20))
        make_button(bar, "Mark as Shipped",
                    lambda: self.update_status("Shipped"), "#3498db").pack(side="left")
        make_button(bar, "Mark as Delivered",
                    lambda: self.update_status("Delivered"), "#27ae60").pack(side="left", padx=10)

    def load_orders(self):
        rows = run_query(
            "SELECT o.order_id, c.name, p.name, oi.quantity, "
            "oi.quantity * oi.price, o.order_date, o.status "
            "FROM orders o "
            "JOIN customers c ON o.customer_id = c.customer_id "
            "JOIN order_items oi ON o.order_id = oi.order_id "
            "JOIN products p ON oi.product_id = p.product_id "
            "ORDER BY o.order_id DESC")
        fill_tree(self.o_tree, rows)

    def update_status(self, status):
        sel = self.o_tree.selection()
        if not sel:
            messagebox.showerror("Error", "Pehle list se koi order select karo")
            return
        order_id = self.o_tree.item(sel[0])["values"][0]
        try:
            run_query("UPDATE orders SET status = %s WHERE order_id = %s",
                      (status, order_id), fetch=False)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))
            return
        self.set_status("Order #{} ka status ab {} hai".format(order_id, status))
        self.refresh_all()

    # ---------- REPORTS ----------
    def build_report(self):
        p = self.pages["report"]
        page_title(p, "Reports", "GROUP BY aur JOIN queries ke results")

        tk.Label(p, text="Customer-wise Total Spending", bg=BG, fg=TEXT,
                 font=(FONT, 12, "bold")).pack(anchor="w", padx=25, pady=(5, 5))
        frame, self.r_tree = make_tree(
            p, ("Customer", "Total Orders", "Total Spent"), (260, 140, 160), height=6)
        frame.pack(fill="x", padx=25)

        tk.Label(p, text="Top Selling Products", bg=BG, fg=TEXT,
                 font=(FONT, 12, "bold")).pack(anchor="w", padx=25, pady=(20, 5))
        frame2, self.t_tree = make_tree(
            p, ("Product", "Units Sold", "Revenue"), (260, 140, 160), height=6)
        frame2.pack(fill="x", padx=25)

    def load_report(self):
        rows = run_query(
            "SELECT c.name, COUNT(DISTINCT o.order_id), "
            "COALESCE(SUM(oi.quantity * oi.price), 0) "
            "FROM customers c "
            "LEFT JOIN orders o ON c.customer_id = o.customer_id "
            "LEFT JOIN order_items oi ON o.order_id = oi.order_id "
            "GROUP BY c.customer_id, c.name ORDER BY 3 DESC")
        fill_tree(self.r_tree, rows)

        rows = run_query(
            "SELECT p.name, SUM(oi.quantity), SUM(oi.quantity * oi.price) "
            "FROM products p JOIN order_items oi ON p.product_id = oi.product_id "
            "GROUP BY p.product_id, p.name ORDER BY 2 DESC")
        fill_tree(self.t_tree, rows)

    # ---------- COMMON ----------
    def load_dropdowns(self):
        cats = run_query("SELECT category_id, category_name FROM categories")
        self.p_cat["values"] = [str(i) + " - " + n for i, n in cats]

        custs = run_query("SELECT customer_id, name FROM customers")
        self.o_cust["values"] = [str(i) + " - " + n for i, n in custs]

        prods = run_query("SELECT product_id, name, price, stock FROM products")
        self.o_prod["values"] = [str(i) + " - " + n for i, n, pr, st in prods]
        self.prod_info = {i: (pr, st) for i, n, pr, st in prods}

    def refresh_all(self):
        try:
            self.load_dashboard()
            self.load_products()
            self.load_customers()
            self.load_orders()
            self.load_report()
            self.load_dropdowns()
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = ShopApp(root)
    root.mainloop()