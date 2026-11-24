import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
 
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tapchoa.db")
 
 
def get_conn():
    return sqlite3.connect(DB_FILE)
 
 
def init_db():
    conn = get_conn()
    conn.execute(
        """CREATE TABLE IF NOT EXISTS products (
            barcode TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL DEFAULT 0,
            stock INTEGER NOT NULL DEFAULT 0
        )"""
    )
    conn.commit()
    conn.close()
 
 
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quản Lý Bán Hàng Tạp Hóa")
        self.geometry("900x600")
        self.cart = []  # [{barcode, name, price, qty}]
 
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)
 
        self.sale_tab = ttk.Frame(notebook)
        self.product_tab = ttk.Frame(notebook)
        self.stats_tab = ttk.Frame(notebook)
        notebook.add(self.sale_tab, text="Bán hàng")
        notebook.add(self.product_tab, text="Sản phẩm")
        notebook.add(self.stats_tab, text="Thống kê")
        notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
 
        self.build_sale_tab()
        self.build_product_tab()
        self.build_stats_tab()
 
        self.refresh_products()
        self.refresh_stats()
 
    def on_tab_changed(self, event):
        tab_text = event.widget.tab(event.widget.select(), "text")
        if tab_text == "Sản phẩm":
            self.refresh_products()
        elif tab_text == "Thống kê":
            self.refresh_stats()
 
    # ---------------- TAB BÁN HÀNG ----------------
    def build_sale_tab(self):
        top = ttk.Frame(self.sale_tab)
        top.pack(fill="x", padx=10, pady=10)
        ttk.Label(top, text="Quét / nhập mã vạch:").pack(side="left")
        self.scan_var = tk.StringVar()
        entry = ttk.Entry(top, textvariable=self.scan_var, width=30)
        entry.pack(side="left", padx=6)
        entry.bind("<Return>", lambda e: self.scan_barcode())
        entry.focus()
        ttk.Button(top, text="Thêm", command=self.scan_barcode).pack(side="left")
 
        cols = ("name", "price", "qty", "subtotal")
        self.cart_tree = ttk.Treeview(self.sale_tab, columns=cols, show="headings", height=14)
        for c, txt in zip(cols, ["Sản phẩm", "Đơn giá", "SL", "Thành tiền"]):
            self.cart_tree.heading(c, text=txt)
        self.cart_tree.pack(fill="both", expand=True, padx=10)
 
        bottom = ttk.Frame(self.sale_tab)
        bottom.pack(fill="x", padx=10, pady=10)
        self.total_label = ttk.Label(bottom, text="Tổng cộng: 0đ", font=("Segoe UI", 14, "bold"))
        self.total_label.pack(side="left")
        ttk.Button(bottom, text="Xóa dòng đã chọn", command=self.remove_cart_item).pack(side="right", padx=4)
        ttk.Button(bottom, text="Thanh toán", command=self.checkout).pack(side="right", padx=4)
        ttk.Button(bottom, text="Xóa giỏ", command=self.clear_cart).pack(side="right", padx=4)
 
    def scan_barcode(self):
        code = self.scan_var.get().strip()
        self.scan_var.set("")
        if not code:
            return
        conn = get_conn()
        row = conn.execute(
            "SELECT barcode, name, price, stock FROM products WHERE barcode=?", (code,)
        ).fetchone()
        conn.close()
        if not row:
            messagebox.showerror("Lỗi", f"Không tìm thấy sản phẩm với mã: {code}")
            return
        barcode, name, price, stock = row
        if stock <= 0:
            messagebox.showwarning("Hết hàng", f"Sản phẩm '{name}' đã hết hàng!")
            return
        for item in self.cart:
            if item["barcode"] == barcode:
                if item["qty"] >= stock:
                    messagebox.showwarning("Cảnh báo", "Không đủ tồn kho!")
                    return
                item["qty"] += 1
                break
        else:
            self.cart.append({"barcode": barcode, "name": name, "price": price, "qty": 1})
        self.refresh_cart()
 
    def refresh_cart(self):
        self.cart_tree.delete(*self.cart_tree.get_children())
        total = 0
        for item in self.cart:
            subtotal = item["price"] * item["qty"]
            total += subtotal
            self.cart_tree.insert(
                "", "end", iid=item["barcode"],
                values=(item["name"], f"{item['price']:,.0f}đ", item["qty"], f"{subtotal:,.0f}đ"),
            )
        self.total_label.config(text=f"Tổng cộng: {total:,.0f}đ")
 
    def remove_cart_item(self):
        sel = self.cart_tree.selection()
        if not sel:
            return
        barcode = sel[0]
        self.cart = [i for i in self.cart if i["barcode"] != barcode]
        self.refresh_cart()
 
    def clear_cart(self):
        if self.cart and not messagebox.askyesno("Xác nhận", "Xóa toàn bộ giỏ hàng?"):
            return
        self.cart = []
        self.refresh_cart()
 
    def checkout(self):
        if not self.cart:
            messagebox.showinfo("Thông báo", "Giỏ hàng trống!")
            return
        conn = get_conn()
        for item in self.cart:
            conn.execute(
                "UPDATE products SET stock = stock - ? WHERE barcode=?", (item["qty"], item["barcode"])
            )
        conn.commit()
        conn.close()
        total = sum(i["price"] * i["qty"] for i in self.cart)
        messagebox.showinfo("Thành công", f"Thanh toán thành công!\nTổng tiền: {total:,.0f}đ")
        self.cart = []
        self.refresh_cart()
        self.refresh_products()
        self.refresh_stats()
 
    # ---------------- TAB SẢN PHẨM ----------------
    def build_product_tab(self):
        form = ttk.Frame(self.product_tab)
        form.pack(fill="x", padx=10, pady=10)
 
        self.p_barcode = tk.StringVar()
        self.p_name = tk.StringVar()
        self.p_price = tk.StringVar()
        self.p_stock = tk.StringVar()
 
        ttk.Label(form, text="Mã vạch").grid(row=0, column=0)
        ttk.Entry(form, textvariable=self.p_barcode, width=15).grid(row=1, column=0, padx=4)
        ttk.Label(form, text="Tên sản phẩm").grid(row=0, column=1)
        ttk.Entry(form, textvariable=self.p_name, width=20).grid(row=1, column=1, padx=4)
        ttk.Label(form, text="Giá bán").grid(row=0, column=2)
        ttk.Entry(form, textvariable=self.p_price, width=10).grid(row=1, column=2, padx=4)
        ttk.Label(form, text="Tồn kho").grid(row=0, column=3)
        ttk.Entry(form, textvariable=self.p_stock, width=10).grid(row=1, column=3, padx=4)
        ttk.Button(form, text="Thêm sản phẩm", command=self.add_product).grid(row=1, column=4, padx=8)
 
        cols = ("barcode", "name", "price", "stock")
        self.product_tree = ttk.Treeview(self.product_tab, columns=cols, show="headings", height=16)
        for c, txt in zip(cols, ["Mã vạch", "Tên", "Giá", "Tồn kho"]):
            self.product_tree.heading(c, text=txt)
        self.product_tree.pack(fill="both", expand=True, padx=10, pady=10)
 
        ttk.Button(self.product_tab, text="Xóa sản phẩm đã chọn", command=self.delete_product).pack(pady=4)
 
    def add_product(self):
        barcode = self.p_barcode.get().strip()
        name = self.p_name.get().strip()
        try:
            price = float(self.p_price.get() or 0)
            stock = int(self.p_stock.get() or 0)
        except ValueError:
            messagebox.showerror("Lỗi", "Giá và tồn kho phải là số!")
            return
        if not barcode or not name:
            messagebox.showerror("Lỗi", "Nhập mã vạch và tên sản phẩm!")
            return
        conn = get_conn()
        try:
            conn.execute(
                "INSERT INTO products (barcode, name, price, stock) VALUES (?,?,?,?)",
                (barcode, name, price, stock),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", "Mã vạch đã tồn tại!")
            return
        finally:
            conn.close()
        self.p_barcode.set("")
        self.p_name.set("")
        self.p_price.set("")
        self.p_stock.set("")
        self.refresh_products()
 
    def delete_product(self):
        sel = self.product_tree.selection()
        if not sel:
            return
        barcode = sel[0]
        if not messagebox.askyesno("Xác nhận", "Xóa sản phẩm này?"):
            return
        conn = get_conn()
        conn.execute("DELETE FROM products WHERE barcode=?", (barcode,))
        conn.commit()
        conn.close()
        self.refresh_products()
 
    def refresh_products(self):
        self.product_tree.delete(*self.product_tree.get_children())
        conn = get_conn()
        rows = conn.execute("SELECT barcode, name, price, stock FROM products ORDER BY name").fetchall()
        conn.close()
        for barcode, name, price, stock in rows:
            self.product_tree.insert(
                "", "end", iid=barcode, values=(barcode, name, f"{price:,.0f}đ", stock)
            )
 
    # ---------------- TAB THỐNG KÊ ----------------
    def build_stats_tab(self):
        self.stats_summary = ttk.Label(self.stats_tab, font=("Segoe UI", 12, "bold"))
        self.stats_summary.pack(pady=10)
        cols = ("barcode", "name", "stock", "status")
        self.stats_tree = ttk.Treeview(self.stats_tab, columns=cols, show="headings", height=16)
        for c, txt in zip(cols, ["Mã vạch", "Tên", "Tồn kho", "Trạng thái"]):
            self.stats_tree.heading(c, text=txt)
        self.stats_tree.pack(fill="both", expand=True, padx=10, pady=10)
 
    def refresh_stats(self):
        conn = get_conn()
        rows = conn.execute("SELECT barcode, name, stock FROM products ORDER BY name").fetchall()
        conn.close()
        self.stats_tree.delete(*self.stats_tree.get_children())
        in_stock = out_stock = 0
        for barcode, name, stock in rows:
            status = "Còn hàng" if stock > 0 else "Hết hàng"
            in_stock += stock > 0
            out_stock += stock <= 0
            self.stats_tree.insert("", "end", values=(barcode, name, stock, status))
        self.stats_summary.config(
            text=f"Tổng sản phẩm: {len(rows)}   |   Còn hàng: {in_stock}   |   Hết hàng: {out_stock}"
        )
 
 
if __name__ == "__main__":
    init_db()
    App().mainloop()
 
