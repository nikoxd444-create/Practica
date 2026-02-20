import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector

# ------------------ CONEXIÓN ------------------
conexion = mysql.connector.connect(
    host="localhost",
    user="root",   # cambia si usas root
    password="",
    database="billetera"
)

cursor = conexion.cursor()

usuario_actual = None
nombre_actual = None

# ------------------ ESTILO ------------------
BG_COLOR = "#0f0f1a"
FG_COLOR = "#00f7ff"
BTN_COLOR = "#1a1a2e"
FONT_TITLE = ("Consolas", 22, "bold")
FONT_NORMAL = ("Consolas", 14)

# ------------------ OBTENER BALANCE ------------------
def obtener_balance_usuario():
    cursor.execute("""
        SELECT 
        SUM(CASE WHEN tipo='Ingreso' THEN monto ELSE 0 END),
        SUM(CASE WHEN tipo='Gasto' THEN monto ELSE 0 END)
        FROM movimientos
        WHERE usuario_id=%s
    """, (usuario_actual,))
    
    ingresos, gastos = cursor.fetchone()
    ingresos = ingresos or 0
    gastos = gastos or 0
    return ingresos - gastos


# ------------------ REGISTRO ------------------
def registrar():
    nombre = entry_nombre.get()
    email = entry_email.get()
    password = entry_password.get()

    try:
        sql = "INSERT INTO usuarios (nombre, email, password) VALUES (%s,%s,%s)"
        cursor.execute(sql, (nombre, email, password))
        conexion.commit()
        messagebox.showinfo("Éxito", "Usuario registrado 🚀")
    except:
        messagebox.showerror("Error", "El email ya existe")


# ------------------ LOGIN ------------------
def login():
    global usuario_actual, nombre_actual

    email = entry_email.get()
    password = entry_password.get()

    sql = "SELECT id, nombre FROM usuarios WHERE email=%s AND password=%s"
    cursor.execute(sql, (email, password))
    resultado = cursor.fetchone()

    if resultado:
        usuario_actual = resultado[0]
        nombre_actual = resultado[1]
        ventana_login.destroy()
        abrir_sistema()
    else:
        messagebox.showerror("Error", "Datos incorrectos")


# ------------------ SISTEMA PRINCIPAL ------------------
def abrir_sistema():
    ventana = tk.Tk()
    ventana.title("Sistema Financiero")
    ventana.geometry("1000x650")
    ventana.configure(bg=BG_COLOR)

    # Título
    tk.Label(ventana,
             text=f"Bienvenido, {nombre_actual}",
             font=FONT_TITLE,
             fg=FG_COLOR,
             bg=BG_COLOR).pack(pady=20)

    # Balance
    lbl_balance = tk.Label(ventana,
                           font=("Consolas", 18, "bold"),
                           fg="#00ff88",
                           bg=BG_COLOR)
    lbl_balance.pack()

    frame_inputs = tk.Frame(ventana, bg=BG_COLOR)
    frame_inputs.pack(pady=20)

    tk.Label(frame_inputs, text="Descripción",
             font=FONT_NORMAL, fg=FG_COLOR, bg=BG_COLOR).grid(row=0, column=0, padx=15)

    tk.Label(frame_inputs, text="Monto",
             font=FONT_NORMAL, fg=FG_COLOR, bg=BG_COLOR).grid(row=1, column=0, padx=15)

    entry_desc = tk.Entry(frame_inputs, font=FONT_NORMAL, width=20)
    entry_desc.grid(row=0, column=1, pady=5)

    entry_monto = tk.Entry(frame_inputs, font=FONT_NORMAL, width=20)
    entry_monto.grid(row=1, column=1, pady=5)

    # -------- FUNCIONES INTERNAS --------
    def actualizar_balance():
        balance = obtener_balance_usuario()
        lbl_balance.config(text=f"Balance Actual: $ {balance:,.2f}")

    def agregar_ingreso():
        monto = float(entry_monto.get())
        cursor.execute("""
            INSERT INTO movimientos (usuario_id, tipo, descripcion, monto)
            VALUES (%s,'Ingreso',%s,%s)
        """, (usuario_actual, entry_desc.get(), monto))
        conexion.commit()
        mostrar()
        actualizar_balance()

    def retirar_dinero():
        try:
            monto = float(entry_monto.get())
        except:
            messagebox.showerror("Error", "Monto inválido")
            return

        balance = obtener_balance_usuario()

        if monto > balance:
            messagebox.showerror("Error", "Saldo insuficiente ❌")
            return

        cursor.execute("""
            INSERT INTO movimientos (usuario_id, tipo, descripcion, monto)
            VALUES (%s,'Gasto',%s,%s)
        """, (usuario_actual, entry_desc.get(), monto))
        conexion.commit()
        mostrar()
        actualizar_balance()

    def borrar():
        seleccionado = tabla.selection()
        if seleccionado:
            id_mov = tabla.item(seleccionado)['values'][0]
            cursor.execute("DELETE FROM movimientos WHERE id=%s", (id_mov,))
            conexion.commit()
            mostrar()
            actualizar_balance()

    def mostrar():
        for row in tabla.get_children():
            tabla.delete(row)

        cursor.execute("""
            SELECT m.id, u.nombre, m.tipo, m.descripcion, m.monto, m.fecha
            FROM movimientos m
            JOIN usuarios u ON m.usuario_id = u.id
            WHERE m.usuario_id=%s
        """, (usuario_actual,))

        for fila in cursor.fetchall():
            tabla.insert("", "end", values=fila)

    # -------- BOTONES --------
    tk.Button(frame_inputs, text="Agregar Ingreso",
              bg=BTN_COLOR, fg=FG_COLOR,
              font=FONT_NORMAL,
              command=agregar_ingreso).grid(row=2, column=0, pady=15)

    tk.Button(frame_inputs, text="Retirar Dinero",
              bg="#330000", fg="white",
              font=FONT_NORMAL,
              command=retirar_dinero).grid(row=2, column=1, pady=15)

    tk.Button(frame_inputs, text="Borrar Movimiento",
              bg="#550000", fg="white",
              font=FONT_NORMAL,
              command=borrar).grid(row=2, column=2, padx=10)

    # -------- TABLA --------
    tabla = ttk.Treeview(ventana,
                         columns=("ID","Usuario","Tipo","Desc","Monto","Fecha"),
                         show="headings",
                         height=15)

    for col in ("ID","Usuario","Tipo","Desc","Monto","Fecha"):
        tabla.heading(col, text=col)
        tabla.column(col, width=150)

    tabla.pack(pady=20)

    actualizar_balance()
    mostrar()
    ventana.mainloop()


# ------------------ VENTANA LOGIN ------------------
ventana_login = tk.Tk()
ventana_login.title("Login Futurista")
ventana_login.geometry("550x600")
ventana_login.configure(bg=BG_COLOR)

tk.Label(ventana_login,
         text="SISTEMA FINANCIERO",
         font=FONT_TITLE,
         fg=FG_COLOR,
         bg=BG_COLOR).pack(pady=40)

tk.Label(ventana_login, text="Nombre (Registro)",
         font=FONT_NORMAL, fg=FG_COLOR, bg=BG_COLOR).pack()

entry_nombre = tk.Entry(ventana_login, font=FONT_NORMAL, width=25)
entry_nombre.pack(pady=5)

tk.Label(ventana_login, text="Email",
         font=FONT_NORMAL, fg=FG_COLOR, bg=BG_COLOR).pack()

entry_email = tk.Entry(ventana_login, font=FONT_NORMAL, width=25)
entry_email.pack(pady=5)

tk.Label(ventana_login, text="Password",
         font=FONT_NORMAL, fg=FG_COLOR, bg=BG_COLOR).pack()

entry_password = tk.Entry(ventana_login, show="*", font=FONT_NORMAL, width=25)
entry_password.pack(pady=5)

tk.Button(ventana_login, text="Registrarse",
          bg=BTN_COLOR, fg=FG_COLOR,
          font=FONT_NORMAL,
          command=registrar).pack(pady=15)

tk.Button(ventana_login, text="Iniciar Sesión",
          bg=BTN_COLOR, fg=FG_COLOR,
          font=FONT_NORMAL,
          command=login).pack(pady=10)

ventana_login.mainloop()