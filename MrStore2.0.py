import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk
import os
import sqlite3
import datetime
import csv

class StoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mr Store - Administrador")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f5f5f5")
        
        # Configurar tema moderno
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Colores modernos
        self.primary_color = "#4CAF50"  # Verde moderno
        self.secondary_color = "#607D8B"  # Azul grisáceo
        self.accent_color = "#FF9800"  # Naranja
        self.dark_color = "#333333"
        
        # Configuraciones de estilo personalizadas
        self.style.configure("TButton", padding=6, relief="flat", 
                           background=self.primary_color, foreground="white", 
                           font=("Arial", 10, "bold"))
        self.style.map("TButton", 
                      background=[("active", "#45a049")])
        
        self.style.configure("TLabel", background="#f5f5f5", 
                           font=("Arial", 11))
        self.style.configure("TFrame", background="#f5f5f5")
        self.style.configure("TCombobox", padding=5, font=("Arial", 10))
        self.style.configure("TEntry", padding=5, font=("Arial", 10))
        
        # Configurar estilo para Treeview (Tablas)
        self.style.configure("Treeview", 
                            background="#FFFFFF", 
                            foreground="#333333",
                            rowheight=25, 
                            fieldbackground="#FFFFFF",
                            font=("Arial", 10))
        self.style.map("Treeview", background=[("selected", self.primary_color)])

        self.style.configure("Treeview.Heading", 
                           font=("Arial", 10, "bold"),
                           background=self.secondary_color,
                           foreground="white",
                           relief="flat")

        self.style.configure("Accent.TButton", 
                           background=self.accent_color,
                           foreground="white")
        self.style.map("Accent.TButton", 
                     background=[("active", "#E65100")])
        
        # Configuración de archivos
        self.config_file = "config.txt"
        self.background_path = self.load_background_path()
        self.set_background(self.background_path)

        # Conexión a la base de datos
        self.db_connection = sqlite3.connect("mr_store.db")
        self.db_cursor = self.db_connection.cursor()
        self.create_tables()

        # Variables para selección
        self.selected_record = None
        self.selected_table = None
        self.sale_items = []

        # Diccionario para rastrear ventanas abiertas
        self.open_windows = {}

        # Mostrar la ventana de inicio de sesión
        self.show_login_window()

    def create_tables(self):
        # Crear las tablas si no existen
        self.db_cursor.execute("""CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            marca TEXT,
            precio REAL,
            unidad TEXT,
            stock INTEGER,
            imagen TEXT,
            proveedor_id INTEGER,
            FOREIGN KEY (proveedor_id) REFERENCES proveedores (id))""")
        self.db_cursor.execute("""CREATE TABLE IF NOT EXISTS proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            contacto TEXT)""")
        self.db_cursor.execute("""CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto TEXT,
            cantidad REAL,
            total REAL,
            fecha TEXT)""")
        self.db_cursor.execute("""CREATE TABLE IF NOT EXISTS cortes_de_caja (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            num_ventas INTEGER,
            total_ingresos REAL)""")
        
        # Agregar la columna proveedor_id si no existe
        try:
            self.db_cursor.execute("ALTER TABLE productos ADD COLUMN proveedor_id INTEGER")
        except sqlite3.OperationalError:
            pass

        self.db_connection.commit()

    def load_background_path(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as file:
                return file.read().strip()
        return ""

    def save_background_path(self, image_path):
        with open(self.config_file, "w") as file:
            file.write(image_path)

    def set_background(self, image_path):
        if not image_path:
            return
            
        try:
            image = Image.open(image_path)
            image = image.resize((1000, 700), Image.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(image)
            self.bg_label = tk.Label(self.root, image=self.bg_image)
            self.bg_label.place(relwidth=1, relheight=1)
        except Exception as e:
            messagebox.showwarning("Error", f"No se pudo cargar la imagen de fondo: {e}")

    def change_background(self):
        file_path = filedialog.askopenfilename(filetypes=[("Imágenes", "*.jpg;*.png;*.jpeg")])
        if file_path:
            self.background_path = file_path
            self.set_background(self.background_path)
            self.save_background_path(self.background_path)

    def change_theme(self):
        themes = ["clam", "alt", "default", "vista"]
        current_theme = self.style.theme_use()
        next_theme = themes[(themes.index(current_theme) + 1)] if current_theme in themes else themes[0]
        self.style.theme_use(next_theme)
        
        # Actualizar algunos estilos específicos
        self.style.configure("TButton", background=self.primary_color, foreground="white")
        self.style.configure("Accent.TButton", background=self.accent_color, foreground="white")
        self.style.configure("Treeview.Heading", background=self.secondary_color, foreground="white")
        
        messagebox.showinfo("Tema cambiado", f"Tema actual: {next_theme.capitalize()}")

    def create_ui(self):
        # Crear barra de menú con estilo moderno
        menu_bar = tk.Menu(self.root, bg="#f5f5f5", fg=self.dark_color, 
                          activebackground=self.primary_color, 
                          activeforeground="white")
        self.root.config(menu=menu_bar)
        
        # Menú Productos
        prod_menu = tk.Menu(menu_bar, tearoff=0, bg="#f5f5f5", fg=self.dark_color,
                           activebackground=self.primary_color, 
                           activeforeground="white")
        prod_menu.add_command(label="Agregar producto", command=self.add_product)
        prod_menu.add_command(label="Ver inventario", command=self.view_inventory)
        menu_bar.add_cascade(label="Productos", menu=prod_menu)
        
        # Menú Proveedores
        prov_menu = tk.Menu(menu_bar, tearoff=0, bg="#f5f5f5", fg=self.dark_color,
                           activebackground=self.primary_color, 
                           activeforeground="white")
        prov_menu.add_command(label="Agregar proveedor", command=self.add_provider)
        prov_menu.add_command(label="Lista de proveedores", command=self.view_providers)
        menu_bar.add_cascade(label="Proveedores", menu=prov_menu)
        
        # Menú Ventas
        sales_menu = tk.Menu(menu_bar, tearoff=0, bg="#f5f5f5", fg=self.dark_color,
                            activebackground=self.primary_color, 
                            activeforeground="white")
        sales_menu.add_command(label="Registrar venta", command=self.register_sale)
        sales_menu.add_command(label="Historial de ventas", command=self.view_sales_history)
        menu_bar.add_cascade(label="Ventas", menu=sales_menu)
        
        # Menú Configuración
        config_menu = tk.Menu(menu_bar, tearoff=0, bg="#f5f5f5", fg=self.dark_color,
                             activebackground=self.primary_color, 
                             activeforeground="white")
        config_menu.add_command(label="Cambiar fondo", command=self.change_background)
        config_menu.add_command(label="Ver Base de Datos", command=self.view_database)
        config_menu.add_separator()
        config_menu.add_command(label="Cambiar tema", command=self.change_theme)
        config_menu.add_command(label="Exportar datos", command=self.export_data)
        menu_bar.add_cascade(label="Configuración", menu=config_menu)
        
        # Menú Corte de Caja
        corte_menu = tk.Menu(menu_bar, tearoff=0, bg="#f5f5f5", fg=self.dark_color,
                            activebackground=self.primary_color, 
                            activeforeground="white")
        corte_menu.add_command(label="Ver Historial de Cortes", command=self.view_cortes)
        corte_menu.add_command(label="Iniciar Nuevo Corte", command=self.nuevo_corte)
        corte_menu.add_command(label="Ver Ventas de Hoy", command=self.ver_ventas_de_hoy)
        menu_bar.add_cascade(label="Corte de Caja", menu=corte_menu)
        
        # Barra de estado
        self.status_var = tk.StringVar()
        self.status_var.set("Listo")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                             relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x")
        
        # Frame principal para contenido
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Mostrar dashboard inicial
        self.show_dashboard()

    def show_dashboard(self):
        # Limpiar frame principal
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Título
        title_frame = ttk.Frame(self.main_frame)
        title_frame.pack(fill="x", pady=(0, 20))
        ttk.Label(title_frame, text="Panel de Control", 
                 font=("Arial", 16, "bold")).pack(side="left")
        
        # Estadísticas rápidas
        stats_frame = ttk.LabelFrame(self.main_frame, text="Estadísticas Rápidas")
        stats_frame.pack(fill="x", pady=10)
        
        # Obtener datos
        self.db_cursor.execute("SELECT COUNT(*) FROM productos")
        total_products = self.db_cursor.fetchone()[0]
        
        self.db_cursor.execute("SELECT COUNT(*) FROM proveedores")
        total_providers = self.db_cursor.fetchone()[0]
        
        today = datetime.date.today().strftime("%Y-%m-%d")
        self.db_cursor.execute("SELECT COUNT(*), SUM(total) FROM ventas WHERE fecha LIKE ?", (today + "%",))
        sales_today = self.db_cursor.fetchone()
        total_sales = sales_today[0] if sales_today[0] else 0
        total_amount = sales_today[1] if sales_today[1] else 0.0
        
        # Crear tarjetas de estadísticas
        cards_frame = ttk.Frame(stats_frame)
        cards_frame.pack(fill="x", pady=5)
        
        def create_stat_card(parent, title, value, color):
            card = ttk.Frame(parent, relief="solid", borderwidth=1)
            card.pack(side="left", expand=True, fill="both", padx=5)
            
            ttk.Label(card, text=title, font=("Arial", 10), 
                     foreground="#666").pack(pady=(5, 0))
            ttk.Label(card, text=str(value), font=("Arial", 14, "bold"), 
                     foreground=color).pack(pady=(0, 5))
            return card
        
        create_stat_card(cards_frame, "Productos", total_products, self.primary_color)
        create_stat_card(cards_frame, "Proveedores", total_providers, self.secondary_color)
        create_stat_card(cards_frame, "Ventas Hoy", total_sales, self.accent_color)
        create_stat_card(cards_frame, "Total Hoy", f"${total_amount:.2f}", "#E91E63")
        
        # Acciones rápidas
        actions_frame = ttk.LabelFrame(self.main_frame, text="Acciones Rápidas")
        actions_frame.pack(fill="x", pady=10)
        
        btn_frame = ttk.Frame(actions_frame)
        btn_frame.pack(pady=5)
        
        ttk.Button(btn_frame, text="Agregar Producto", command=self.add_product,
                  style="Accent.TButton").grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(btn_frame, text="Registrar Venta", command=self.register_sale,
                  style="Accent.TButton").grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(btn_frame, text="Ver Inventario", command=self.view_inventory,
                  style="Accent.TButton").grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(btn_frame, text="Nuevo Corte", command=self.nuevo_corte,
                  style="Accent.TButton").grid(row=0, column=3, padx=5, pady=5)
        
        # Últimas ventas
        sales_frame = ttk.LabelFrame(self.main_frame, text="Últimas Ventas")
        sales_frame.pack(fill="both", expand=True, pady=10)
        
        # Crear tabla para últimas ventas
        columns = ("#", "Producto", "Cantidad", "Total", "Hora")
        self.sales_tree = ttk.Treeview(sales_frame, columns=columns, show="headings", height=5)
        
        for col in columns:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=100, anchor="center")
        
        self.sales_tree.column("#", width=40)
        self.sales_tree.column("Producto", width=200)
        
        self.sales_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Obtener últimas ventas
        self.db_cursor.execute("SELECT producto, cantidad, total, SUBSTR(fecha,12,8) as hora FROM ventas ORDER BY fecha DESC LIMIT 10")
        sales = self.db_cursor.fetchall()
        
        for i, sale in enumerate(sales, start=1):
            self.sales_tree.insert("", "end", values=(i, sale[0], sale[1], f"${sale[2]:.2f}", sale[3]))
        
        # Configurar scrollbar
        scrollbar = ttk.Scrollbar(sales_frame, orient="vertical", command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def show_login_window(self):
        self.close_window("login")
        login_window = tk.Toplevel(self.root)
        login_window.title("Iniciar Sesión - Mr Store")
        login_window.geometry("400x300")
        login_window.resizable(False, False)
        self.open_windows["login"] = login_window
        
        # Frame principal con sombra visual
        main_frame = ttk.Frame(login_window, style="TFrame")
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Logo o título
        title_label = ttk.Label(main_frame, text="MR STORE", 
                              font=("Arial", 20, "bold"), 
                              foreground=self.primary_color)
        title_label.pack(pady=(0, 20))
        
        # Frame de formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(pady=10, padx=10, fill="x")
        
        ttk.Label(form_frame, text="Usuario:").grid(row=0, column=0, pady=5, sticky="w")
        username_entry = ttk.Entry(form_frame, font=("Arial", 11))
        username_entry.grid(row=1, column=0, pady=5, sticky="ew")
        
        ttk.Label(form_frame, text="Contraseña:").grid(row=2, column=0, pady=5, sticky="w")
        password_entry = ttk.Entry(form_frame, show="*", font=("Arial", 11))
        password_entry.grid(row=3, column=0, pady=5, sticky="ew")
        
        # Botón de login con estilo moderno
        login_btn = ttk.Button(main_frame, text="Iniciar Sesión", 
                              command=lambda: self.login(username_entry, password_entry, login_window),
                              style="Accent.TButton")
        login_btn.pack(pady=20, ipady=5, ipadx=20)
        
        # Configurar el enfoque y eventos
        username_entry.focus_set()
        password_entry.bind("<Return>", lambda e: self.login(username_entry, password_entry, login_window))
        
        self.root.withdraw()

    def login(self, username_entry, password_entry, login_window):
        username = username_entry.get()
        password = password_entry.get()
        if username == "Admin" and password == "Root":
            login_window.destroy()
            self.root.deiconify()
            self.create_ui()
            del self.open_windows["login"]
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.", parent=login_window)

    def close_window(self, window_name):
        if window_name in self.open_windows:
            self.open_windows[window_name].destroy()
            del self.open_windows[window_name]

    def add_product(self):
        self.close_window("add_product")
        win = tk.Toplevel(self.root)
        win.title("Agregar Producto")
        win.geometry("500x600")
        win.resizable(False, False)
        self.open_windows["add_product"] = win
        
        # Frame principal
        main_frame = ttk.Frame(win)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        ttk.Label(main_frame, text="Nuevo Producto", font=("Arial", 14, "bold"),
                 foreground=self.primary_color).pack(pady=(0, 20))
        
        # Formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill="x", pady=5)
        
        # Campos del formulario
        fields = [
            {"label": "Nombre:", "type": "entry"},
            {"label": "Marca:", "type": "entry"},
            {"label": "Precio:", "type": "entry"},
            {"label": "Unidad:", "type": "combobox", "options": ["Piezas", "Kilos"]},
            {"label": "Stock:", "type": "entry"},
            {"label": "Proveedor:", "type": "combobox", "options": []}
        ]
        
        self.db_cursor.execute("SELECT id, nombre FROM proveedores")
        proveedores = self.db_cursor.fetchall()
        proveedor_options = [f"{row[1]} (ID: {row[0]})" for row in proveedores]
        fields[5]["options"] = proveedor_options
        
        entries = {}
        for i, field in enumerate(fields):
            row_frame = ttk.Frame(form_frame)
            row_frame.pack(fill="x", pady=5)
            
            ttk.Label(row_frame, text=field["label"], width=15, anchor="e").pack(side="left", padx=5)
            
            if field["type"] == "entry":
                entry = ttk.Entry(row_frame)
                entry.pack(side="left", fill="x", expand=True, padx=5)
                entries[field["label"].replace(":", "").lower()] = entry
            elif field["type"] == "combobox":
                combo = ttk.Combobox(row_frame, values=field["options"], state="readonly")
                combo.pack(side="left", fill="x", expand=True, padx=5)
                combo.current(0)
                entries[field["label"].replace(":", "").lower()] = combo
        
        # Selector de imagen
        img_frame = ttk.Frame(main_frame)
        img_frame.pack(fill="x", pady=10)
        
        self.img_path = tk.StringVar()
        self.img_preview = None
        
        def select_img():
            path = filedialog.askopenfilename(filetypes=[("Imágenes", "*.jpg;*.png;*.jpeg")])
            if path:
                self.img_path.set(path)
                try:
                    img = Image.open(path)
                    img.thumbnail((150, 150))
                    self.img_preview = ImageTk.PhotoImage(img)
                    img_label.config(image=self.img_preview)
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo cargar la imagen: {e}")
        
        ttk.Button(img_frame, text="Seleccionar Imagen", command=select_img).pack(side="left", padx=5)
        img_label = ttk.Label(img_frame)
        img_label.pack(side="left", padx=10)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        def save_product():
            try:
                nombre = entries["nombre"].get()
                marca = entries["marca"].get()
                precio = float(entries["precio"].get())
                unidad = entries["unidad"].get()
                stock = int(entries["stock"].get())
                
                selected_proveedor = entries["proveedor"].get()
                proveedor_id = int(selected_proveedor.split(" (ID: ")[1][:-1])
                
                imagen = self.img_path.get()
                
                self.db_cursor.execute(
                    "INSERT INTO productos (nombre, marca, precio, unidad, stock, imagen, proveedor_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (nombre, marca, precio, unidad, stock, imagen, proveedor_id)
                )
                self.db_connection.commit()
                messagebox.showinfo("Éxito", "Producto guardado correctamente.", parent=win)
                win.destroy()
            except ValueError as e:
                messagebox.showerror("Error", f"Datos inválidos: {str(e)}", parent=win)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el producto: {str(e)}", parent=win)
        
        ttk.Button(btn_frame, text="Guardar", command=save_product, 
                  style="Accent.TButton").pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Cancelar", command=win.destroy).pack(side="left", padx=10)

    def add_provider(self):
        self.close_window("add_provider")
        win = tk.Toplevel(self.root)
        win.title("Agregar Proveedor")
        win.geometry("400x300")
        win.resizable(False, False)
        self.open_windows["add_provider"] = win
        
        # Frame principal
        main_frame = ttk.Frame(win)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        ttk.Label(main_frame, text="Nuevo Proveedor", font=("Arial", 14, "bold"),
                 foreground=self.primary_color).pack(pady=(0, 20))
        
        # Formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill="x", pady=10)
        
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, pady=5, sticky="w")
        name_entry = ttk.Entry(form_frame)
        name_entry.grid(row=0, column=1, pady=5, sticky="ew")
        
        ttk.Label(form_frame, text="Contacto:").grid(row=1, column=0, pady=5, sticky="w")
        contact_entry = ttk.Entry(form_frame)
        contact_entry.grid(row=1, column=1, pady=5, sticky="ew")
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        def save_provider():
            nombre = name_entry.get()
            contacto = contact_entry.get()
            if not nombre or not contacto:
                messagebox.showwarning("Advertencia", "Por favor, complete todos los campos.", parent=win)
                return
            
            try:
                self.db_cursor.execute(
                    "INSERT INTO proveedores (nombre, contacto) VALUES (?, ?)", 
                    (nombre, contacto)
                )
                self.db_connection.commit()
                messagebox.showinfo("Éxito", "Proveedor guardado correctamente.", parent=win)
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el proveedor: {str(e)}", parent=win)
        
        ttk.Button(btn_frame, text="Guardar", command=save_provider,
                  style="Accent.TButton").pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Cancelar", command=win.destroy).pack(side="left", padx=10)

    def register_sale(self):
        self.close_window("register_sale")
        win = tk.Toplevel(self.root)
        win.title("Registrar Venta")
        win.geometry("800x600")
        self.open_windows["register_sale"] = win
        
        # Frame principal
        main_frame = ttk.Frame(win)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        ttk.Label(main_frame, text="Registrar Nueva Venta", 
                 font=("Arial", 14, "bold"),
                 foreground=self.primary_color).pack(pady=(0, 10))
        
        # Frame de productos disponibles
        available_frame = ttk.LabelFrame(main_frame, text="Productos Disponibles")
        available_frame.pack(fill="x", pady=5)
        
        # Treeview para productos
        columns = ("ID", "Nombre", "Marca", "Precio", "Stock", "Unidad")
        self.products_tree = ttk.Treeview(available_frame, columns=columns, show="headings", height=5)
        
        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=80, anchor="center")
        
        self.products_tree.column("Nombre", width=150)
        self.products_tree.column("Marca", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(available_frame, orient="vertical", command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar.set)
        self.products_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Cargar productos
        self.db_cursor.execute("SELECT id, nombre, marca, precio, stock, unidad FROM productos ORDER BY nombre")
        products = self.db_cursor.fetchall()
        
        # Convertir precios a float
        converted_products = []
        for product in products:
            product = list(product)
            product[3] = float(product[3])  # Convertir precio a float
            converted_products.append(product)
            self.products_tree.insert("", "end", values=product)
        
        # Frame para agregar producto a la venta
        add_frame = ttk.Frame(main_frame)
        add_frame.pack(fill="x", pady=10)
        
        ttk.Label(add_frame, text="Cantidad:").pack(side="left", padx=5)
        self.qty_entry = ttk.Entry(add_frame, width=10)
        self.qty_entry.pack(side="left", padx=5)
        
        def add_to_sale():
            selected = self.products_tree.focus()
            if not selected:
                messagebox.showwarning("Advertencia", "Seleccione un producto primero.", parent=win)
                return
            
            try:
                qty = float(self.qty_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Cantidad inválida.", parent=win)
                return
            
            product = self.products_tree.item(selected)["values"]
            product_id = product[0]
            
            # Convertir precio a float
            precio = float(product[3])
            
            existing_qty = sum(item["cantidad"] for item in self.sale_items if item["id"] == product_id)
            if (existing_qty + qty) > product[4]:
                messagebox.showerror("Error", "Stock insuficiente considerando cantidades ya agregadas.", parent=win)
                return
            
            self.sale_items.append({
                "id": product_id,
                "nombre": product[1],
                "precio": precio,
                "cantidad": qty,
                "unidad": product[5]
            })
            self.update_sale_list()
        
        ttk.Button(add_frame, text="Agregar a Venta", command=add_to_sale,
                  style="Accent.TButton").pack(side="left", padx=10)
        
        # Frame de productos en la venta
        sale_frame = ttk.LabelFrame(main_frame, text="Productos en la Venta")
        sale_frame.pack(fill="both", expand=True, pady=5)
        
        # Treeview para productos en la venta
        columns = ("Nombre", "Precio Unitario", "Cantidad", "Subtotal")
        self.sale_tree = ttk.Treeview(sale_frame, columns=columns, show="headings", height=5)
        
        for col in columns:
            self.sale_tree.heading(col, text=col)
            self.sale_tree.column(col, width=100, anchor="center")
        
        self.sale_tree.column("Nombre", width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(sale_frame, orient="vertical", command=self.sale_tree.yview)
        self.sale_tree.configure(yscrollcommand=scrollbar.set)
        self.sale_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Total
        total_frame = ttk.Frame(main_frame)
        total_frame.pack(fill="x", pady=10)
        
        self.total_var = tk.StringVar()
        self.total_var.set("Total: $0.00")
        ttk.Label(total_frame, textvariable=self.total_var, 
                 font=("Arial", 12, "bold")).pack(side="right", padx=10)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        def remove_item():
            selected = self.sale_tree.focus()
            if not selected:
                return
            
            index = int(self.sale_tree.item(selected)["tags"][0])
            del self.sale_items[index]
            self.update_sale_list()
        
        ttk.Button(btn_frame, text="Eliminar Seleccionado", command=remove_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Finalizar Venta", command=self.finalize_sale,
                  style="Accent.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=win.destroy).pack(side="left", padx=5)
        
        # Inicializar lista de productos en la venta
        self.sale_items = []
        self.update_sale_list()

    def update_sale_list(self):
        # Actualizar la lista de productos en la venta
        self.sale_tree.delete(*self.sale_tree.get_children())
        total = 0.0
        
        for i, item in enumerate(self.sale_items):
            # CORRECCIÓN APLICADA: Conversión explícita a float
            precio = float(item["precio"])
            cantidad = float(item["cantidad"])
            
            subtotal = precio * cantidad
            total += subtotal
            
            self.sale_tree.insert("", "end", 
                                values=(item["nombre"], 
                                      f"${precio:.2f}", 
                                      f"{cantidad} {item['unidad']}", 
                                      f"${subtotal:.2f}"),
                                tags=(i,))
        
        self.total_var.set(f"Total: ${total:.2f}")

    def finalize_sale(self):
        if not self.sale_items:
            messagebox.showwarning("Advertencia", "No hay productos en la venta.")
            return
        
        # Crear detalle de la venta
        detalle = []
        total_cantidad = 0
        total_venta = 0.0
        
        for item in self.sale_items:
            # CORRECCIÓN APLICADA: Conversión explícita a float
            precio = float(item["precio"])
            cantidad = float(item["cantidad"])
            
            subtotal = precio * cantidad
            detalle.append(f"{item['nombre']}: {cantidad} {item['unidad']} - ${subtotal:.2f}")
            total_cantidad += cantidad
            total_venta += subtotal
            
            # Actualizar stock
            self.db_cursor.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", 
                                  (cantidad, item["id"]))
        
        detalle_str = "; ".join(detalle)
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Guardar en la base de datos
        self.db_cursor.execute(
            "INSERT INTO ventas (producto, cantidad, total, fecha) VALUES (?, ?, ?, ?)",
            (detalle_str, total_cantidad, total_venta, fecha)
        )
        self.db_connection.commit()
        
        messagebox.showinfo("Éxito", f"Venta registrada por ${total_venta:.2f}")
        self.show_dashboard()  # Actualizar dashboard
        
        # Cerrar ventana
        if "register_sale" in self.open_windows:
            self.open_windows["register_sale"].destroy()
            del self.open_windows["register_sale"]

    def view_database(self):
        self.close_window("db_view")
        win = tk.Toplevel(self.root)
        win.title("Base de Datos - Mr Store")
        win.geometry("900x700")
        self.open_windows["db_view"] = win
        
        # Notebook (pestañas)
        notebook = ttk.Notebook(win)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pestaña de Productos
        prod_frame = ttk.Frame(notebook)
        notebook.add(prod_frame, text="Productos")
        
        # Treeview para productos
        columns = ("ID", "Nombre", "Marca", "Precio", "Unidad", "Stock", "Proveedor ID")
        self.prod_tree = ttk.Treeview(prod_frame, columns=columns, show="headings")
        
        for col in columns:
            self.prod_tree.heading(col, text=col)
            self.prod_tree.column(col, width=100, anchor="center")
        
        self.prod_tree.column("Nombre", width=150)
        self.prod_tree.column("Marca", width=120)
        self.prod_tree.column("Precio", width=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(prod_frame, orient="vertical", command=self.prod_tree.yview)
        self.prod_tree.configure(yscrollcommand=scrollbar.set)
        self.prod_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Cargar productos
        self.db_cursor.execute("SELECT id, nombre, marca, precio, unidad, stock, proveedor_id FROM productos")
        products = self.db_cursor.fetchall()
        
        for product in products:
            self.prod_tree.insert("", "end", values=product)
        
        # Pestaña de Proveedores
        prov_frame = ttk.Frame(notebook)
        notebook.add(prov_frame, text="Proveedores")
        
        # Treeview para proveedores
        columns = ("ID", "Nombre", "Contacto")
        self.prov_tree = ttk.Treeview(prov_frame, columns=columns, show="headings")
        
        for col in columns:
            self.prov_tree.heading(col, text=col)
            self.prov_tree.column(col, width=100, anchor="center")
        
        self.prov_tree.column("Nombre", width=200)
        self.prov_tree.column("Contacto", width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(prov_frame, orient="vertical", command=self.prov_tree.yview)
        self.prov_tree.configure(yscrollcommand=scrollbar.set)
        self.prov_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Cargar proveedores
        self.db_cursor.execute("SELECT id, nombre, contacto FROM proveedores")
        providers = self.db_cursor.fetchall()
        
        for provider in providers:
            self.prov_tree.insert("", "end", values=provider)
        
        # Pestaña de Ventas
        sales_frame = ttk.Frame(notebook)
        notebook.add(sales_frame, text="Ventas")
        
        # Treeview para ventas
        columns = ("ID", "Productos", "Cantidad", "Total", "Fecha")
        self.sales_tree = ttk.Treeview(sales_frame, columns=columns, show="headings")
        
        for col in columns:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=100, anchor="center")
        
        self.sales_tree.column("Productos", width=250)
        self.sales_tree.column("Fecha", width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(sales_frame, orient="vertical", command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=scrollbar.set)
        self.sales_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Cargar ventas
        self.db_cursor.execute("SELECT id, producto, cantidad, total, fecha FROM ventas ORDER BY fecha DESC")
        sales = self.db_cursor.fetchall()
        
        for sale in sales:
            self.sales_tree.insert("", "end", values=sale)
        
        # Botones de acción
        btn_frame = ttk.Frame(win)
        btn_frame.pack(pady=10)
        
        def edit_selected():
            notebook_index = notebook.index(notebook.select())
            if notebook_index == 0:  # Productos
                selected = self.prod_tree.focus()
                if not selected:
                    messagebox.showwarning("Advertencia", "Seleccione un producto primero.", parent=win)
                    return
                record = self.prod_tree.item(selected)["values"]
                self.edit_record("productos", record, win)
            elif notebook_index == 1:  # Proveedores
                selected = self.prov_tree.focus()
                if not selected:
                    messagebox.showwarning("Advertencia", "Seleccione un proveedor primero.", parent=win)
                    return
                record = self.prov_tree.item(selected)["values"]
                self.edit_record("proveedores", record, win)
            elif notebook_index == 2:  # Ventas
                messagebox.showinfo("Información", "Las ventas no se pueden editar.", parent=win)
        
        def delete_selected():
            notebook_index = notebook.index(notebook.select())
            if notebook_index == 0:  # Productos
                selected = self.prod_tree.focus()
                if not selected:
                    messagebox.showwarning("Advertencia", "Seleccione un producto primero.", parent=win)
                    return
                record = self.prod_tree.item(selected)["values"]
                self.confirm_delete(record[0], "productos", win)
            elif notebook_index == 1:  # Proveedores
                selected = self.prov_tree.focus()
                if not selected:
                    messagebox.showwarning("Advertencia", "Seleccione un proveedor primero.", parent=win)
                    return
                record = self.prov_tree.item(selected)["values"]
                self.confirm_delete(record[0], "proveedores", win)
            elif notebook_index == 2:  # Ventas
                selected = self.sales_tree.focus()
                if not selected:
                    messagebox.showwarning("Advertencia", "Seleccione una venta primero.", parent=win)
                    return
                record = self.sales_tree.item(selected)["values"]
                self.confirm_delete(record[0], "ventas", win)
        
        ttk.Button(btn_frame, text="Editar", command=edit_selected).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=delete_selected).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cerrar", command=win.destroy).pack(side="left", padx=5)

    def edit_record(self, table, record, parent_win):
        win = tk.Toplevel(parent_win)
        win.title(f"Editar Registro - {table.capitalize()}")
        win.geometry("400x500")
        
        self.db_cursor.execute(f"PRAGMA table_info({table})")
        cols = [col[1] for col in self.db_cursor.fetchall()]
        campos = cols[1:]  # Excluir el ID
        
        entries = {}
        for i, campo in enumerate(campos):
            ttk.Label(win, text=campo.capitalize() + ":").grid(row=i, column=0, padx=5, pady=5, sticky="e")
            ent = ttk.Entry(win)
            ent.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            ent.insert(0, record[i+1])  # +1 para saltar el ID
            entries[campo] = ent
        
        def guardar_cambios():
            nuevos_valores = [ent.get() for ent in entries.values()]
            set_clause = ", ".join([f"{campo} = ?" for campo in entries.keys()])
            
            try:
                self.db_cursor.execute(
                    f"UPDATE {table} SET {set_clause} WHERE id = ?",
                    (*nuevos_valores, record[0])
                )
                self.db_connection.commit()
                messagebox.showinfo("Éxito", "Registro actualizado correctamente.", parent=win)
                win.destroy()
                
                if "db_view" in self.open_windows and self.open_windows["db_view"].winfo_exists():
                    self.open_windows["db_view"].destroy()
                    self.view_database()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar el registro: {str(e)}", parent=win)
        
        ttk.Button(win, text="Guardar Cambios", command=guardar_cambios,
                  style="Accent.TButton").grid(row=len(campos), column=0, columnspan=2, pady=10)

    def confirm_delete(self, reg_id, table, parent_win):
        if not messagebox.askyesno("Confirmar", "¿Está seguro que desea eliminar este registro?", parent=parent_win):
            return
        
        try:
            self.db_cursor.execute(f"DELETE FROM {table} WHERE id = ?", (reg_id,))
            self.db_connection.commit()
            messagebox.showinfo("Éxito", "Registro eliminado correctamente.", parent=parent_win)
            
            if "db_view" in self.open_windows and self.open_windows["db_view"].winfo_exists():
                self.open_windows["db_view"].destroy()
                self.view_database()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el registro: {str(e)}", parent=parent_win)

    def nuevo_corte(self):
        today = datetime.date.today().strftime("%Y-%m-%d")
        self.db_cursor.execute("SELECT * FROM ventas WHERE fecha LIKE ?", (today + "%",))
        ventas = self.db_cursor.fetchall()
        total_ingresos = sum(v[3] for v in ventas)
        num_ventas = len(ventas)
        
        self.db_cursor.execute("SELECT * FROM cortes_de_caja WHERE fecha = ?", (today,))
        corte_existente = self.db_cursor.fetchone()
        
        if corte_existente:
            if messagebox.askyesno("Actualizar", "Ya existe un corte de caja para hoy. ¿Desea actualizarlo?"):
                self.db_cursor.execute(
                    "UPDATE cortes_de_caja SET num_ventas = ?, total_ingresos = ? WHERE fecha = ?",
                    (num_ventas, total_ingresos, today)
                )
                self.db_connection.commit()
                messagebox.showinfo("Éxito", f"Corte de caja actualizado para {today}.")
            else:
                return
        else:
            self.db_cursor.execute(
                "INSERT INTO cortes_de_caja (fecha, num_ventas, total_ingresos) VALUES (?, ?, ?)",
                (today, num_ventas, total_ingresos)
            )
            self.db_connection.commit()
            messagebox.showinfo("Éxito", f"Corte de caja registrado para {today}.")

    def view_cortes(self):
        self.close_window("view_cortes")
        win = tk.Toplevel(self.root)
        win.title("Historial de Cortes de Caja")
        win.geometry("800x600")
        self.open_windows["view_cortes"] = win
        
        # Frame principal
        main_frame = ttk.Frame(win)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        ttk.Label(main_frame, text="Historial de Cortes de Caja", 
                 font=("Arial", 14, "bold"),
                 foreground=self.primary_color).pack(pady=(0, 10))
        
        # Frame de filtros
        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(fill="x", pady=5)
        
        ttk.Label(filter_frame, text="Filtrar por fecha:").pack(side="left", padx=5)
        
        self.start_date_var = tk.StringVar()
        ttk.Label(filter_frame, text="Desde:").pack(side="left", padx=5)
        start_entry = ttk.Entry(filter_frame, textvariable=self.start_date_var, width=10)
        start_entry.pack(side="left", padx=5)
        
        self.end_date_var = tk.StringVar()
        ttk.Label(filter_frame, text="Hasta:").pack(side="left", padx=5)
        end_entry = ttk.Entry(filter_frame, textvariable=self.end_date_var, width=10)
        end_entry.pack(side="left", padx=5)
        
        def apply_filters():
            start_date = self.start_date_var.get()
            end_date = self.end_date_var.get()
            
            query = "SELECT DISTINCT SUBSTR(fecha,1,10) as dia FROM ventas"
            params = []
            
            if start_date or end_date:
                query += " WHERE"
                conditions = []
                
                if start_date:
                    conditions.append(" fecha >= ?")
                    params.append(start_date + " 00:00:00")
                
                if end_date:
                    conditions.append(" fecha <= ?")
                    params.append(end_date + " 23:59:59")
                
                query += " AND".join(conditions)
            
            query += " ORDER BY dia DESC"
            
            self.db_cursor.execute(query, tuple(params))
            dias = self.db_cursor.fetchall()
            
            # Limpiar frame de resultados
            for widget in results_frame.winfo_children():
                widget.destroy()
            
            # Mostrar resultados filtrados
            if not dias:
                ttk.Label(results_frame, text="No se encontraron resultados").pack(pady=10)
                return
            
            # Encabezados
            header_frame = ttk.Frame(results_frame)
            header_frame.pack(fill="x", pady=5)
            
            headers = ["Fecha", "Ventas", "Total Ventas", "Acciones"]
            for i, header in enumerate(headers):
                ttk.Label(header_frame, text=header, font=("Arial", 10, "bold"), 
                         width=20 if i < 3 else 15).pack(side="left", padx=2)
            
            # Resultados
            for d in dias:
                dia = d[0]
                row_frame = ttk.Frame(results_frame, relief="solid", borderwidth=1)
                row_frame.pack(fill="x", pady=2)
                
                self.db_cursor.execute(
                    "SELECT COUNT(*), SUM(total) FROM ventas WHERE fecha LIKE ?", 
                    (dia + "%",)
                )
                result = self.db_cursor.fetchone()
                num_ventas = result[0] if result[0] else 0
                total_ventas = result[1] if result[1] else 0.0
                
                ttk.Label(row_frame, text=dia, width=20).pack(side="left", padx=2)
                ttk.Label(row_frame, text=str(num_ventas), width=20).pack(side="left", padx=2)
                ttk.Label(row_frame, text=f"${total_ventas:.2f}", width=20).pack(side="left", padx=2)
                
                ttk.Button(row_frame, text="Detalle", width=10,
                          command=lambda f=dia: self.ver_detalle_corte(f)).pack(side="left", padx=2)
        
        ttk.Button(filter_frame, text="Filtrar", command=apply_filters,
                  style="Accent.TButton").pack(side="left", padx=10)
        
        # Botón para generar reporte
        def generate_report():
            start_date = self.start_date_var.get()
            end_date = self.end_date_var.get()
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                title="Guardar reporte como"
            )
            
            if not filename:
                return
            
            try:
                with open(filename, "w") as f:
                    f.write("Reporte de Cortes de Caja - Mr Store\n")
                    f.write("="*50 + "\n\n")
                    
                    if start_date or end_date:
                        f.write(f"Periodo: {start_date if start_date else 'Inicio'} - {end_date if end_date else 'Hoy'}\n\n")
                    
                    query = "SELECT DISTINCT SUBSTR(fecha,1,10) as dia FROM ventas"
                    params = []
                    
                    if start_date or end_date:
                        query += " WHERE"
                        conditions = []
                        
                        if start_date:
                            conditions.append(" fecha >= ?")
                            params.append(start_date + " 00:00:00")
                        
                        if end_date:
                            conditions.append(" fecha <= ?")
                            params.append(end_date + " 23:59:59")
                        
                        query += " AND".join(conditions)
                    
                    query += " ORDER BY dia DESC"
                    
                    self.db_cursor.execute(query, tuple(params))
                    dias = self.db_cursor.fetchall()
                    
                    if not dias:
                        f.write("No se encontraron resultados para el periodo seleccionado.\n")
                    else:
                        total_general = 0
                        ventas_general = 0
                        
                        for d in dias:
                            dia = d[0]
                            self.db_cursor.execute(
                                "SELECT COUNT(*), SUM(total) FROM ventas WHERE fecha LIKE ?", 
                                (dia + "%",)
                            )
                            result = self.db_cursor.fetchone()
                            num_ventas = result[0] if result[0] else 0
                            total_ventas = result[1] if result[1] else 0.0
                            
                            f.write(f"Fecha: {dia}\n")
                            f.write(f"Ventas: {num_ventas}\n")
                            f.write(f"Total: ${total_ventas:.2f}\n")
                            f.write("-"*50 + "\n")
                            
                            total_general += total_ventas
                            ventas_general += num_ventas
                        
                        f.write("\nRESUMEN GENERAL\n")
                        f.write("-"*50 + "\n")
                        f.write(f"Total de ventas: {ventas_general}\n")
                        f.write(f"Ingresos totales: ${total_general:.2f}\n")
                
                messagebox.showinfo("Éxito", "Reporte generado correctamente.", parent=win)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo generar el reporte: {str(e)}", parent=win)
        
        ttk.Button(filter_frame, text="Generar Reporte", command=generate_report).pack(side="left", padx=5)
        
        # Frame de resultados
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(fill="both", expand=True, pady=10)
        
        # Aplicar filtros iniciales (mostrar todo)
        apply_filters()
        
        # Botón para cerrar
        ttk.Button(main_frame, text="Cerrar", command=win.destroy).pack(pady=10)
        
        # Configurar evento de búsqueda al presionar Enter
        start_entry.bind("<Return>", lambda e: apply_filters())
        end_entry.bind("<Return>", lambda e: apply_filters())

    def ver_detalle_corte(self, fecha):
        self.close_window(f"detalle_{fecha}")
        win = tk.Toplevel(self.root)
        win.title(f"Detalle de Ventas - {fecha}")
        win.geometry("800x600")
        self.open_windows[f"detalle_{fecha}"] = win
        
        # Frame principal
        main_frame = ttk.Frame(win)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        ttk.Label(main_frame, text=f"Detalle de Ventas - {fecha}", 
                 font=("Arial", 14, "bold"),
                 foreground=self.primary_color).pack(pady=(0, 10))
        
        # Treeview para ventas
        columns = ("Hora", "Productos", "Cantidad", "Total")
        sales_tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            sales_tree.heading(col, text=col)
            sales_tree.column(col, width=100, anchor="center")
        
        sales_tree.column("Productos", width=300)
        sales_tree.column("Hora", width=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=sales_tree.yview)
        sales_tree.configure(yscrollcommand=scrollbar.set)
        sales_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Cargar ventas
        self.db_cursor.execute(
            "SELECT producto, cantidad, total, SUBSTR(fecha,12,8) as hora " 
            "FROM ventas WHERE fecha LIKE ? ORDER BY fecha",
            (fecha + "%",)
        )
        ventas = self.db_cursor.fetchall()
        
        total_dia = 0.0
        for venta in ventas:
            sales_tree.insert("", "end", values=(venta[3], venta[0], venta[1], f"${venta[2]:.2f}"))
            total_dia += venta[2]
        
        # Total del día
        total_frame = ttk.Frame(main_frame)
        total_frame.pack(fill="x", pady=10)
        
        ttk.Label(total_frame, text=f"Total del día: ${total_dia:.2f}", 
                 font=("Arial", 12, "bold")).pack(side="right", padx=10)
        
        # Botón para cerrar
        ttk.Button(main_frame, text="Cerrar", command=win.destroy).pack(pady=10)

    def ver_ventas_de_hoy(self):
        today = datetime.date.today().strftime("%Y-%m-%d")
        self.db_cursor.execute("SELECT id, producto, total, SUBSTR(fecha,12,8) as hora FROM ventas WHERE fecha LIKE ?", (today + "%",))
        ventas = self.db_cursor.fetchall()
        
        self.close_window("today_sales")
        win = tk.Toplevel(self.root)
        win.title("Ventas de Hoy")
        win.geometry("800x600")
        self.open_windows["today_sales"] = win
        
        # Frame principal
        main_frame = ttk.Frame(win)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        ttk.Label(main_frame, text=f"Ventas del Día: {today}", 
                 font=("Arial", 14, "bold"),
                 foreground=self.primary_color).pack(pady=(0, 10))
        
        # Treeview para ventas
        columns = ("ID", "Productos", "Total", "Hora")
        sales_tree = ttk.Treeview(main_frame, columns=columns, show="headings")
        
        for col in columns:
            sales_tree.heading(col, text=col)
            sales_tree.column(col, width=100, anchor="center")
        
        sales_tree.column("Productos", width=300)
        sales_tree.column("Hora", width=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=sales_tree.yview)
        sales_tree.configure(yscrollcommand=scrollbar.set)
        sales_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Cargar ventas
        total_dia = 0.0
        for venta in ventas:
            sales_tree.insert("", "end", values=(venta[0], venta[1], f"${venta[2]:.2f}", venta[3]))
            total_dia += venta[2]
        
        # Total del día
        total_frame = ttk.Frame(main_frame)
        total_frame.pack(fill="x", pady=10)
        
        ttk.Label(total_frame, text=f"Total del día: ${total_dia:.2f}", 
                 font=("Arial", 12, "bold")).pack(side="right", padx=10)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        def delete_sale():
            selected = sales_tree.focus()
            if not selected:
                messagebox.showwarning("Advertencia", "Seleccione una venta primero.", parent=win)
                return
            
            sale_id = sales_tree.item(selected)["values"][0]
            
            if not messagebox.askyesno("Confirmar", "¿Está seguro que desea eliminar esta venta?", parent=win):
                return
            
            try:
                self.db_cursor.execute("DELETE FROM ventas WHERE id = ?", (sale_id,))
                self.db_connection.commit()
                
                messagebox.showinfo("Éxito", "Venta eliminada correctamente.", parent=win)
                
                # Actualizar la vista
                win.destroy()
                self.ver_ventas_de_hoy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la venta: {str(e)}", parent=win)
        
        ttk.Button(btn_frame, text="Eliminar Venta", command=delete_sale).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cerrar", command=win.destroy).pack(side="right", padx=5)

    def view_inventory(self):
        self.close_window("inventory")
        win = tk.Toplevel(self.root)
        win.title("Inventario - Mr Store")
        win.geometry("900x600")
        self.open_windows["inventory"] = win
        
        # Frame principal
        main_frame = ttk.Frame(win)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título y filtros
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(header_frame, text="Inventario de Productos", 
                 font=("Arial", 14, "bold"),
                 foreground=self.primary_color).pack(side="left")
        
        search_frame = ttk.Frame(header_frame)
        search_frame.pack(side="right")
        
        ttk.Label(search_frame, text="Buscar:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=5)
        
        def apply_search():
            search_term = self.search_var.get()
            self.inventory_tree.delete(*self.inventory_tree.get_children())
            
            if search_term:
                query = """
                    SELECT p.id, p.nombre, p.marca, p.precio, p.unidad, p.stock, pr.nombre 
                    FROM productos p 
                    LEFT JOIN proveedores pr ON p.proveedor_id = pr.id 
                    WHERE p.nombre LIKE ? OR p.marca LIKE ? OR pr.nombre LIKE ?
                    ORDER BY p.nombre
                """
                params = (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")
            else:
                query = """
                    SELECT p.id, p.nombre, p.marca, p.precio, p.unidad, p.stock, pr.nombre 
                    FROM productos p 
                    LEFT JOIN proveedores pr ON p.proveedor_id = pr.id 
                    ORDER BY p.nombre
                """
                params = ()
            
            self.db_cursor.execute(query, params)
            productos = self.db_cursor.fetchall()
            
            for prod in productos:
                stock_color = ""
                if prod[5] <= 0:  # Stock agotado
                    stock_color = "red"
                elif prod[5] < 10:  # Stock bajo
                    stock_color = "orange"
                
                values = (prod[0], prod[1], prod[2], f"${prod[3]:.2f}", 
                          prod[4], prod[5], prod[6] if prod[6] else "N/A")
                
                self.inventory_tree.insert("", "end", values=values, tags=(stock_color,))
        
        ttk.Button(search_frame, text="Buscar", command=apply_search,
                  style="Accent.TButton").pack(side="left", padx=5)
        
        # Treeview para inventario
        columns = ("ID", "Nombre", "Marca", "Precio", "Unidad", "Stock", "Proveedor")
        self.inventory_tree = ttk.Treeview(main_frame, columns=columns, show="headings")
        
        for col in columns:
            self.inventory_tree.heading(col, text=col)
            self.inventory_tree.column(col, width=80, anchor="center")
        
        self.inventory_tree.column("Nombre", width=150)
        self.inventory_tree.column("Marca", width=100)
        self.inventory_tree.column("Proveedor", width=120)
        
        # Configurar colores para stock
        self.inventory_tree.tag_configure("red", foreground="red")
        self.inventory_tree.tag_configure("orange", foreground="orange")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)
        self.inventory_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Aplicar búsqueda inicial (mostrar todo)
        apply_search()
        
        # Botones de acción
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=10)
        
        def update_stock():
            selected = self.inventory_tree.focus()
            if not selected:
                messagebox.showwarning("Advertencia", "Seleccione un producto primero.", parent=win)
                return
            
            product_id = self.inventory_tree.item(selected)["values"][0]
            current_stock = self.inventory_tree.item(selected)["values"][5]
            
            update_win = tk.Toplevel(win)
            update_win.title("Actualizar Stock")
            update_win.geometry("300x150")
            
            ttk.Label(update_win, text="Nuevo stock:").pack(pady=5)
            stock_entry = ttk.Entry(update_win)
            stock_entry.pack(pady=5)
            stock_entry.insert(0, current_stock)
            
            def save_stock():
                try:
                    new_stock = int(stock_entry.get())
                    self.db_cursor.execute(
                        "UPDATE productos SET stock = ? WHERE id = ?",
                        (new_stock, product_id)
                    )
                    self.db_connection.commit()
                    messagebox.showinfo("Éxito", "Stock actualizado correctamente.", parent=update_win)
                    update_win.destroy()
                    apply_search()  # Refrescar la vista
                except ValueError:
                    messagebox.showerror("Error", "Ingrese un valor numérico válido.", parent=update_win)
            
            ttk.Button(update_win, text="Guardar", command=save_stock,
                      style="Accent.TButton").pack(pady=10)
        
        ttk.Button(btn_frame, text="Actualizar Stock", command=update_stock).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Exportar", command=self.export_data).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cerrar", command=win.destroy).pack(side="right", padx=5)
        
        # Configurar evento de búsqueda al presionar Enter
        search_entry.bind("<Return>", lambda e: apply_search())

    def view_providers(self):
        self.close_window("providers")
        win = tk.Toplevel(self.root)
        win.title("Lista de Proveedores - Mr Store")
        win.geometry("800x500")
        self.open_windows["providers"] = win
        
        # Frame principal
        main_frame = ttk.Frame(win)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título y botón de agregar
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(header_frame, text="Lista de Proveedores", 
                 font=("Arial", 14, "bold"),
                 foreground=self.primary_color).pack(side="left")
        
        ttk.Button(header_frame, text="Agregar Proveedor", 
                  command=self.add_provider,
                  style="Accent.TButton").pack(side="right")
        
        # Treeview para proveedores
        columns = ("ID", "Nombre", "Contacto", "Productos")
        self.providers_tree = ttk.Treeview(main_frame, columns=columns, show="headings")
        
        for col in columns:
            self.providers_tree.heading(col, text=col)
            self.providers_tree.column(col, width=100, anchor="center")
        
        self.providers_tree.column("Nombre", width=150)
        self.providers_tree.column("Contacto", width=150)
        self.providers_tree.column("Productos", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.providers_tree.yview)
        self.providers_tree.configure(yscrollcommand=scrollbar.set)
        self.providers_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Cargar proveedores
        self.db_cursor.execute("SELECT id, nombre, contacto FROM proveedores ORDER BY nombre")
        providers = self.db_cursor.fetchall()
        
        for prov in providers:
            # Contar productos por proveedor
            self.db_cursor.execute(
                "SELECT COUNT(*) FROM productos WHERE proveedor_id = ?",
                (prov[0],)
            )
            product_count = self.db_cursor.fetchone()[0]
            
            self.providers_tree.insert("", "end", 
                                     values=(prov[0], prov[1], prov[2], product_count))
        
        # Botones de acción
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=10)
        
        def view_provider_products():
            selected = self.providers_tree.focus()
            if not selected:
                messagebox.showwarning("Advertencia", "Seleccione un proveedor primero.", parent=win)
                return
            
            provider_id = self.providers_tree.item(selected)["values"][0]
            provider_name = self.providers_tree.item(selected)["values"][1]
            
            self.close_window(f"provider_products_{provider_id}")
            products_win = tk.Toplevel(win)
            products_win.title(f"Productos de {provider_name}")
            products_win.geometry("600x400")
            self.open_windows[f"provider_products_{provider_id}"] = products_win
            
            # Frame principal
            main_frame = ttk.Frame(products_win)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Título
            ttk.Label(main_frame, text=f"Productos de {provider_name}", 
                     font=("Arial", 14, "bold"),
                     foreground=self.primary_color).pack(pady=(0, 10))
            
            # Treeview para productos
            columns = ("ID", "Nombre", "Marca", "Precio", "Stock")
            products_tree = ttk.Treeview(main_frame, columns=columns, show="headings")
            
            for col in columns:
                products_tree.heading(col, text=col)
                products_tree.column(col, width=80, anchor="center")
            
            products_tree.column("Nombre", width=150)
            products_tree.column("Marca", width=100)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=products_tree.yview)
            products_tree.configure(yscrollcommand=scrollbar.set)
            products_tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Cargar productos del proveedor
            self.db_cursor.execute(
                "SELECT id, nombre, marca, precio, stock FROM productos WHERE proveedor_id = ? ORDER BY nombre",
                (provider_id,)
            )
            products = self.db_cursor.fetchall()
            
            for prod in products:
                products_tree.insert("", "end", values=prod)
            
            # Botón para cerrar
            ttk.Button(main_frame, text="Cerrar", command=products_win.destroy).pack(pady=10)
        
        ttk.Button(btn_frame, text="Ver Productos", command=view_provider_products).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Exportar", command=self.export_data).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cerrar", command=win.destroy).pack(side="right", padx=5)

    def view_sales_history(self):
        self.close_window("sales_history")
        win = tk.Toplevel(self.root)
        win.title("Historial de Ventas - Mr Store")
        win.geometry("1000x700")
        self.open_windows["sales_history"] = win
        
        # Frame principal
        main_frame = ttk.Frame(win)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título y filtros
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(header_frame, text="Historial de Ventas", 
                 font=("Arial", 14, "bold"),
                 foreground=self.primary_color).pack(side="left")
        
        filter_frame = ttk.Frame(header_frame)
        filter_frame.pack(side="right")
        
        ttk.Label(filter_frame, text="Filtrar por fecha:").pack(side="left", padx=5)
        
        self.sales_start_date = tk.StringVar()
        ttk.Label(filter_frame, text="Desde:").pack(side="left", padx=5)
        start_entry = ttk.Entry(filter_frame, textvariable=self.sales_start_date, width=10)
        start_entry.pack(side="left", padx=5)
        
        self.sales_end_date = tk.StringVar()
        ttk.Label(filter_frame, text="Hasta:").pack(side="left", padx=5)
        end_entry = ttk.Entry(filter_frame, textvariable=self.sales_end_date, width=10)
        end_entry.pack(side="left", padx=5)
        
        def apply_filters():
            start_date = self.sales_start_date.get()
            end_date = self.sales_end_date.get()
            
            query = "SELECT id, producto, cantidad, total, fecha FROM ventas"
            params = []
            
            if start_date or end_date:
                query += " WHERE"
                conditions = []
                
                if start_date:
                    conditions.append(" fecha >= ?")
                    params.append(start_date + " 00:00:00")
                
                if end_date:
                    conditions.append(" fecha <= ?")
                    params.append(end_date + " 23:59:59")
                
                query += " AND".join(conditions)
            
            query += " ORDER BY fecha DESC"
            
            self.sales_history_tree.delete(*self.sales_history_tree.get_children())
            self.db_cursor.execute(query, tuple(params))
            sales = self.db_cursor.fetchall()
            
            total_sales = 0.0
            for sale in sales:
                self.sales_history_tree.insert("", "end", values=(
                    sale[0],
                    sale[4].split()[0],  # Fecha
                    sale[4].split()[1],  # Hora
                    sale[1],  # Productos
                    sale[2],  # Cantidad
                    f"${sale[3]:.2f}"  # Total
                ))
                total_sales += sale[3]
            
            self.sales_total_var.set(f"Total: ${total_sales:.2f}")
        
        ttk.Button(filter_frame, text="Filtrar", command=apply_filters,
                  style="Accent.TButton").pack(side="left", padx=5)
        
        # Treeview para ventas
        columns = ("ID", "Fecha", "Hora", "Productos", "Cantidad", "Total")
        self.sales_history_tree = ttk.Treeview(main_frame, columns=columns, show="headings")
        
        for col in columns:
            self.sales_history_tree.heading(col, text=col)
            self.sales_history_tree.column(col, width=80, anchor="center")
        
        self.sales_history_tree.column("Productos", width=250)
        self.sales_history_tree.column("Fecha", width=80)
        self.sales_history_tree.column("Hora", width=60)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.sales_history_tree.yview)
        self.sales_history_tree.configure(yscrollcommand=scrollbar.set)
        self.sales_history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Total y botones
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill="x", pady=10)
        
        self.sales_total_var = tk.StringVar()
        self.sales_total_var.set("Total: $0.00")
        ttk.Label(footer_frame, textvariable=self.sales_total_var, 
                 font=("Arial", 12, "bold")).pack(side="left")
        
        btn_frame = ttk.Frame(footer_frame)
        btn_frame.pack(side="right")
        
        def view_sale_details():
            selected = self.sales_history_tree.focus()
            if not selected:
                messagebox.showwarning("Advertencia", "Seleccione una venta primero.", parent=win)
                return
            
            sale_id = self.sales_history_tree.item(selected)["values"][0]
            
            self.db_cursor.execute(
                "SELECT producto, total, fecha FROM ventas WHERE id = ?",
                (sale_id,)
            )
            sale = self.db_cursor.fetchone()
            
            if not sale:
                return
            
            detail_win = tk.Toplevel(win)
            detail_win.title(f"Detalle de Venta #{sale_id}")
            detail_win.geometry("500x300")
            
            ttk.Label(detail_win, text=f"Venta #{sale_id}", 
                     font=("Arial", 14, "bold"),
                     foreground=self.primary_color).pack(pady=10)
            
            ttk.Label(detail_win, text=f"Fecha: {sale[2]}", 
                     font=("Arial", 11)).pack(pady=5)
            
            ttk.Label(detail_win, text="Productos:", 
                     font=("Arial", 11, "bold")).pack(pady=5)
            
            text_frame = ttk.Frame(detail_win)
            text_frame.pack(fill="both", expand=True, padx=10, pady=5)
            
            scrollbar = ttk.Scrollbar(text_frame)
            scrollbar.pack(side="right", fill="y")
            
            text_area = tk.Text(text_frame, wrap="word", yscrollcommand=scrollbar.set)
            text_area.pack(fill="both", expand=True)
            scrollbar.config(command=text_area.yview)
            
            text_area.insert("end", sale[0])
            text_area.config(state="disabled")
            
            ttk.Label(detail_win, text=f"Total: ${sale[1]:.2f}", 
                     font=("Arial", 12, "bold")).pack(pady=10)
            
            ttk.Button(detail_win, text="Cerrar", command=detail_win.destroy).pack(pady=5)
        
        ttk.Button(btn_frame, text="Ver Detalle", command=view_sale_details).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Exportar", command=self.export_data).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cerrar", command=win.destroy).pack(side="left", padx=5)
        
        # Aplicar filtros iniciales (mostrar todo)
        apply_filters()
        
        # Configurar evento de búsqueda al presionar Enter
        start_entry.bind("<Return>", lambda e: apply_filters())
        end_entry.bind("<Return>", lambda e: apply_filters())

    def export_data(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
            title="Guardar datos como"
        )
        
        if not file_path:
            return
        
        try:
            # Determinar qué datos exportar basado en la ventana actual
            if "inventory" in self.open_windows and self.open_windows["inventory"].winfo_exists():
                # Exportar inventario
                self.db_cursor.execute("""
                    SELECT p.id, p.nombre, p.marca, p.precio, p.unidad, p.stock, pr.nombre as proveedor
                    FROM productos p
                    LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
                    ORDER BY p.nombre
                """)
                data = self.db_cursor.fetchall()
                headers = ["ID", "Nombre", "Marca", "Precio", "Unidad", "Stock", "Proveedor"]
                
            elif "providers" in self.open_windows and self.open_windows["providers"].winfo_exists():
                # Exportar proveedores
                self.db_cursor.execute("""
                    SELECT id, nombre, contacto, 
                    (SELECT COUNT(*) FROM productos WHERE proveedor_id = proveedores.id) as num_productos
                    FROM proveedores
                    ORDER BY nombre
                """)
                data = self.db_cursor.fetchall()
                headers = ["ID", "Nombre", "Contacto", "Núm. Productos"]
                
            elif "sales_history" in self.open_windows and self.open_windows["sales_history"].winfo_exists():
                # Exportar ventas
                start_date = self.sales_start_date.get()
                end_date = self.sales_end_date.get()
                
                query = """
                    SELECT id, producto, cantidad, total, fecha
                    FROM ventas
                """
                params = []
                
                if start_date or end_date:
                    query += " WHERE"
                    conditions = []
                    
                    if start_date:
                        conditions.append(" fecha >= ?")
                        params.append(start_date + " 00:00:00")
                    
                    if end_date:
                        conditions.append(" fecha <= ?")
                        params.append(end_date + " 23:59:59")
                    
                    query += " AND".join(conditions)
                
                query += " ORDER BY fecha DESC"
                
                self.db_cursor.execute(query, tuple(params))
                data = self.db_cursor.fetchall()
                headers = ["ID", "Productos", "Cantidad", "Total", "Fecha"]
                
            else:
                # Exportar todo por defecto
                self.db_cursor.execute("SELECT * FROM productos")
                products = self.db_cursor.fetchall()
                
                self.db_cursor.execute("SELECT * FROM proveedores")
                providers = self.db_cursor.fetchall()
                
                self.db_cursor.execute("SELECT * FROM ventas ORDER BY fecha DESC")
                sales = self.db_cursor.fetchall()
                
                data = {
                    "productos": (["ID", "Nombre", "Marca", "Precio", "Unidad", "Stock", "Imagen", "Proveedor ID"], products),
                    "proveedores": (["ID", "Nombre", "Contacto"], providers),
                    "ventas": (["ID", "Producto", "Cantidad", "Total", "Fecha"], sales)
                }
                
                # Guardar en múltiples hojas si es Excel o en múltiples archivos CSV
                if file_path.endswith(".csv"):
                    base_path = file_path[:-4]  # Quitar .csv
                    for table_name, (headers, table_data) in data.items():
                        with open(f"{base_path}_{table_name}.csv", "w", newline="", encoding="utf-8") as f:
                            writer = csv.writer(f)
                            writer.writerow(headers)
                            writer.writerows(table_data)
                    
                    messagebox.showinfo("Éxito", f"Datos exportados en múltiples archivos:\n{base_path}_*.csv")
                    return
            
            # Guardar datos en un solo archivo CSV
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(data)
            
            messagebox.showinfo("Éxito", "Datos exportados correctamente.")
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar los datos: {str(e)}")

    def __del__(self):
        self.db_connection.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = StoreApp(root)
    root.mainloop()