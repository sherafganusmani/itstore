import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json, os
import datetime

FILE = "inventory.json"
USERS_FILE = "users.json"
SALES_FILE = "sales.json"

def load_data():
    if os.path.exists(FILE):
        if os.path.getsize(FILE) == 0:  # File is empty
            return []
        with open(FILE, "r") as f:
            return json.load(f)
    return []

def save_data():
    with open(FILE, "w") as f:
        json.dump(inventory, f)

def load_users():
    if os.path.exists(USERS_FILE):
        if os.path.getsize(USERS_FILE) == 0:
            return []
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return []

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def load_sales():
    if os.path.exists(SALES_FILE):
        if os.path.getsize(SALES_FILE) == 0:
            return []
        with open(SALES_FILE, "r") as f:
            return json.load(f)
    return []

def save_sales(sales):
    with open(SALES_FILE, "w") as f:
        json.dump(sales, f)

def add_item():
    name = name_var.get().strip()
    qty = qty_var.get().strip()
    price = price_var.get().strip()

    if name and qty.isdigit() and price.replace('.', '', 1).isdigit():
        inventory.append({"name": name, "qty": int(qty), "price": float(price)})
        save_data()
        refresh_table()
        clear_fields()
        # Show success message
        success_label.config(text="Successfully added!")
        add_item_frame.after(2000, lambda: success_label.config(text=""))  # Hide after 2 seconds
    else:
        messagebox.showwarning("Input Error", "Enter valid name, quantity and price")

def edit_item():
    selected = tree.selection()
    if selected:
        idx = int(selected[0])
        item = inventory[idx]

        new_name = simpledialog.askstring("Edit Name", "Name:", initialvalue=item["name"])
        new_qty = simpledialog.askstring("Edit Quantity", "Quantity:", initialvalue=str(item["qty"]))
        new_price = simpledialog.askstring("Edit Price", "Price:", initialvalue=str(item["price"]))

        if new_name and new_qty.isdigit() and new_price.replace('.', '', 1).isdigit():
            inventory[idx] = {"name": new_name, "qty": int(new_qty), "price": float(new_price)}
            save_data()
            refresh_table()

def delete_item():
    selected = tree.selection()
    if selected:
        idx = int(selected[0])
        item = inventory[idx]

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{item['name']}'?")
        if confirm:
            inventory.pop(idx)
            save_data()
            refresh_table()

def refresh_table(filtered=None):
    tree.delete(*tree.get_children())
    data = filtered if filtered is not None else inventory
    for i, item in enumerate(data):
        tree.insert("", "end", iid=i, values=(item["name"], item["qty"], f"₹{item['price']}"))

def clear_fields():
    name_var.set("")
    qty_var.set("")
    price_var.set("")

def on_exit():
    if messagebox.askokcancel("Exit", "Do you really want to exit?"):
        root.destroy()

def search_items(*args):
    query = search_var.get().strip().lower()
    if query == "":
        refresh_table()
    else:
        filtered = [item for item in inventory if query in item["name"].lower()]
        refresh_table(filtered)

def register_user():
    username = reg_username_var.get().strip()
    password = reg_password_var.get().strip()
    role = reg_role_var.get()
    users = load_users()
    if not username or not password or not role:
        messagebox.showwarning("Input Error", "Enter username, password and select role")
        return
    if any(u['username'] == username for u in users):
        messagebox.showwarning("Register Error", "Username already exists")
        return
    users.append({"username": username, "password": password, "role": role})
    save_users(users)
    messagebox.showinfo("Success", "Registration successful! Please login.")
    show_login()

def login_user():
    username = login_username_var.get().strip()
    password = login_password_var.get().strip()
    role = login_role_var.get()
    users = load_users()
    if any(u['username'] == username and u['password'] == password and u['role'] == role for u in users):
        login_frame.pack_forget()
        register_frame.pack_forget()
        # Clear sidebar
        for widget in sidebar.winfo_children():
            widget.destroy()
        if role == "Inventory Manager":
            tk.Button(sidebar, text="Add Item", width=18, command=show_add_item, bg="#4682b4", fg="white").pack(pady=10)
            tk.Button(sidebar, text="Inventory", width=18, command=show_main_content, bg="#4682b4", fg="white").pack(pady=10)
            tk.Button(sidebar, text="Selling History", width=18, command=show_selling_history, bg="#4682b4", fg="white").pack(pady=10)
        elif role == "Counter Staff":
            tk.Button(sidebar, text="Inventory", width=18, command=show_main_content, bg="#4682b4", fg="white").pack(pady=10)
            tk.Button(sidebar, text="Selling History", width=18, command=show_selling_history, bg="#4682b4", fg="white").pack(pady=10)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        show_main_content()
        # Update main content buttons for Counter Staff
        for widget in btn_frame.winfo_children():
            widget.destroy()
        if role == "Inventory Manager":
            tk.Button(btn_frame, text="Edit", command=edit_item, bg="#32cd32", fg="white", activebackground="#228b22").grid(row=0, column=0, padx=5)
            tk.Button(btn_frame, text="Delete", command=delete_item, bg="#ff6347", fg="white", activebackground="#cd5c5c").grid(row=0, column=1, padx=5)
        elif role == "Counter Staff":
            tk.Button(btn_frame, text="Sell Item", command=sell_item_window, bg="#4682b4", fg="white").grid(row=0, column=0, padx=5)
    else:
        messagebox.showerror("Login Failed", "Invalid username, password or role")

def show_login():
    register_frame.pack_forget()
    sidebar.pack_forget()  # Hide sidebar on login screen
    login_frame.pack(fill=tk.BOTH, expand=True)

def show_register():
    login_frame.pack_forget()
    sidebar.pack_forget()  # Hide sidebar on register screen
    register_frame.pack(fill=tk.BOTH, expand=True)

def sell_item_window():
    billing_win = tk.Toplevel(root)
    billing_win.title("Billing System")
    billing_win.geometry("350x250")
    billing_win.configure(bg="#f0f4ff")

    tk.Label(billing_win, text="Select Item:", bg="#f0f4ff").pack(pady=5)
    item_var = tk.StringVar()
    item_names = [item["name"] for item in inventory]
    item_menu = ttk.Combobox(billing_win, textvariable=item_var, values=item_names, state="readonly")
    item_menu.pack(pady=5)

    tk.Label(billing_win, text="Quantity:", bg="#f0f4ff").pack(pady=5)
    qty_var = tk.StringVar()
    qty_entry = tk.Entry(billing_win, textvariable=qty_var)
    qty_entry.pack(pady=5)

    total_label = tk.Label(billing_win, text="Total: ₹0.00", bg="#f0f4ff", font=("Arial", 12, "bold"))
    total_label.pack(pady=10)

    def calculate_total():
        name = item_var.get()
        qty = qty_var.get()
        if name and qty.isdigit():
            for item in inventory:
                if item["name"] == name:
                    total = int(qty) * item["price"]
                    total_label.config(text=f"Total: ₹{total:.2f}")
                    return
        total_label.config(text="Total: ₹0.00")

    def confirm_sale():
        name = item_var.get()
        qty = qty_var.get()
        if name and qty.isdigit():
            for item in inventory:
                if item["name"] == name:
                    if int(qty) > item["qty"]:
                        messagebox.showwarning("Stock Error", "Not enough stock!")
                        return
                    item["qty"] -= int(qty)
                    save_data()
                    refresh_table()
                    # Save bill info to sales history
                    bill = {
                        "item": name,
                        "quantity": int(qty),
                        "total": int(qty) * item["price"],
                        "price_per_item": item["price"],
                        "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    sales_history.append(bill)
                    save_sales(sales_history)
                    messagebox.showinfo("Success", f"Sold {qty} x {name}\nTotal: ₹{int(qty)*item['price']:.2f}")
                    billing_win.destroy()
                    return
        messagebox.showwarning("Input Error", "Select item and enter valid quantity.")

    tk.Button(billing_win, text="Calculate", command=calculate_total, bg="#4682b4", fg="white").pack(pady=5)
    tk.Button(billing_win, text="Confirm Sale", command=confirm_sale, bg="#32cd32", fg="white").pack(pady=5)

def show_selling_history():
    history_win = tk.Toplevel(root)
    history_win.title("Selling History")
    history_win.geometry("500x350")
    history_win.configure(bg="#f0f4ff")

    cols = ("Date/Time", "Item", "Quantity", "Price/Item", "Total")
    tree_hist = ttk.Treeview(history_win, columns=cols, show="headings")
    for col in cols:
        tree_hist.heading(col, text=col)
        tree_hist.column(col, width=90, anchor="center")  # Center align
    tree_hist.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    for bill in sales_history:
        tree_hist.insert("", "end", values=(
            bill["datetime"], bill["item"], bill["quantity"], f"₹{bill['price_per_item']}", f"₹{bill['total']:.2f}"
        ))

# GUI setup
root = tk.Tk()
root.title("Inventory Manager")
root.geometry("700x580")  # Increased width for sidebar
root.configure(bg="#f0f4ff")
root.protocol("WM_DELETE_WINDOW", on_exit)

name_var, qty_var, price_var, search_var = tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()
inventory = load_data()
sales_history = load_sales()  # Load sales history

# Style
style = ttk.Style()
style.theme_use("default")
style.configure("Treeview", background="#ffffff", foreground="#000000", rowheight=25, fieldbackground="#ffffff")
style.map("Treeview", background=[("selected", "#cde1ff")])

# --- ADD ITEM FORM FRAME ---
add_item_frame = tk.Frame(root, bg="#f0f4ff", width=400, height=350)
add_item_frame.pack_propagate(False)  # Prevent frame from shrinking to fit contents

tk.Label(add_item_frame, text="Product Name:", bg="#f0f4ff", font=("Arial", 12)).pack(pady=10)
name_entry = tk.Entry(add_item_frame, textvariable=name_var, font=("Arial", 12), width=30)
name_entry.pack(pady=5)

tk.Label(add_item_frame, text="Quantity:", bg="#f0f4ff", font=("Arial", 12)).pack(pady=10)
qty_entry = tk.Entry(add_item_frame, textvariable=qty_var, font=("Arial", 12), width=30)
qty_entry.pack(pady=5)

tk.Label(add_item_frame, text="Price:", bg="#f0f4ff", font=("Arial", 12)).pack(pady=10)
price_entry = tk.Entry(add_item_frame, textvariable=price_var, font=("Arial", 12), width=30)
price_entry.pack(pady=5)

name_entry.bind("<Return>", lambda e: qty_entry.focus_set())
qty_entry.bind("<Return>", lambda e: price_entry.focus_set())
price_entry.bind("<Return>", lambda e: add_item())

tk.Button(add_item_frame, text="Add Item", command=add_item, bg="#87cefa", fg="white", activebackground="#4682b4", font=("Arial", 12), width=20, height=2).pack(pady=15)

success_label = tk.Label(add_item_frame, text="", fg="green", bg="#f0f4ff", font=("Arial", 10, "bold"))
success_label.pack(pady=5)

# --- OTHER MAIN CONTENT (put your search, treeview, etc. in another frame) ---
main_content_frame = tk.Frame(root, bg="#f0f4ff")

tk.Label(main_content_frame, text="Search:", bg="#f0f4ff").pack()
search_entry = tk.Entry(main_content_frame, textvariable=search_var)
search_entry.pack(pady=5)
search_var.trace_add("write", search_items)

frame = tk.Frame(main_content_frame, bg="#f0f4ff")
frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

tree_scroll = tk.Scrollbar(frame)
tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

tree = ttk.Treeview(frame, columns=("Name", "Qty", "Price"), show="headings", yscrollcommand=tree_scroll.set)
tree.heading("Name", text="Name")
tree.heading("Qty", text="Quantity")
tree.heading("Price", text="Price")
tree.column("Name", anchor="center")
tree.column("Qty", anchor="center")
tree.column("Price", anchor="center")
tree.pack(fill=tk.BOTH, expand=True)
tree_scroll.config(command=tree.yview)

btn_frame = tk.Frame(main_content_frame, bg="#f0f4ff")
btn_frame.pack(pady=5)
tk.Button(btn_frame, text="Edit", command=edit_item, bg="#32cd32", fg="white", activebackground="#228b22").grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Delete", command=delete_item, bg="#ff6347", fg="white", activebackground="#cd5c5c").grid(row=0, column=1, padx=5)

# --- SHOW/HIDE FUNCTIONS ---
def show_add_item():
    main_content_frame.pack_forget()
    add_item_frame.pack(fill=tk.BOTH, expand=True)

def show_main_content():
    add_item_frame.pack_forget()
    main_content_frame.pack(fill=tk.BOTH, expand=True)

# --- LOGIN FRAME ---
login_frame = tk.Frame(root, bg="#f0f4ff", width=400, height=350)
login_frame.pack_propagate(False)
tk.Label(login_frame, text="Login", font=("Arial", 16, "bold"), bg="#f0f4ff").pack(pady=20)
login_username_var = tk.StringVar()
login_password_var = tk.StringVar()
login_role_var = tk.StringVar()
tk.Label(login_frame, text="Username:", bg="#f0f4ff", font=("Arial", 12)).pack(pady=5)
tk.Entry(login_frame, textvariable=login_username_var, font=("Arial", 12), width=30).pack(pady=5)
tk.Label(login_frame, text="Password:", bg="#f0f4ff", font=("Arial", 12)).pack(pady=5)
tk.Entry(login_frame, textvariable=login_password_var, show="*", font=("Arial", 12), width=30).pack(pady=5)
tk.Label(login_frame, text="Role:", bg="#f0f4ff", font=("Arial", 12)).pack(pady=5)
tk.OptionMenu(login_frame, login_role_var, "Inventory Manager", "Counter Staff").pack(pady=5)
tk.Button(login_frame, text="Login", command=login_user, bg="#4682b4", fg="white", font=("Arial", 12), width=20, height=2).pack(pady=10)
tk.Button(login_frame, text="Register", command=show_register, fg="#4682b4", font=("Arial", 12), width=20, height=2).pack(pady=5)

# --- REGISTER FRAME ---
register_frame = tk.Frame(root, bg="#f0f4ff", width=400, height=350)
register_frame.pack_propagate(False)
tk.Label(register_frame, text="Register", font=("Arial", 16, "bold"), bg="#f0f4ff").pack(pady=20)
reg_username_var = tk.StringVar()
reg_password_var = tk.StringVar()
reg_role_var = tk.StringVar()
tk.Label(register_frame, text="Username:", bg="#f0f4ff", font=("Arial", 12)).pack(pady=5)
tk.Entry(register_frame, textvariable=reg_username_var, font=("Arial", 12), width=30).pack(pady=5)
tk.Label(register_frame, text="Password:", bg="#f0f4ff", font=("Arial", 12)).pack(pady=5)
tk.Entry(register_frame, textvariable=reg_password_var, show="*", font=("Arial", 12), width=30).pack(pady=5)
tk.Label(register_frame, text="Role:", bg="#f0f4ff", font=("Arial", 12)).pack(pady=5)
tk.OptionMenu(register_frame, reg_role_var, "Inventory Manager", "Counter Staff").pack(pady=5)
tk.Button(register_frame, text="Register", command=register_user, bg="#32cd32", fg="white", font=("Arial", 12), width=20, height=2).pack(pady=10)
tk.Button(register_frame, text="Back to Login", command=show_login, fg="#4682b4", font=("Arial", 12), width=20, height=2).pack(pady=5)

# --- SIDEBAR ---
sidebar = tk.Frame(root, bg="#dde7fa", width=150)
# Do NOT pack sidebar here! It will be packed after successful login.

# --- INITIAL VIEW ---
show_login()

refresh_table()
root.mainloop()