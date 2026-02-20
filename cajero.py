import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# =========================
# CONEXION MYSQL
# =========================

conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="billetera"
)

cursor = conexion.cursor()

# =========================
# FUNCIONES BALANCE
# =========================

def obtener_balance():
    cursor.execute("""
        SELECT 
        SUM(CASE WHEN tipo='INGRESO' THEN monto ELSE 0 END),
        SUM(CASE WHEN tipo='GASTO' THEN monto ELSE 0 END)
        FROM movimientos
    """)
    
    ingresos, gastos = cursor.fetchone()

    ingresos = ingresos or 0
    gastos = gastos or 0

    return ingresos - gastos, ingresos, gastos


def insertar_movimiento(tipo, concepto, monto):
    cursor.execute("""
        INSERT INTO movimientos (tipo, concepto, monto)
        VALUES (%s, %s, %s)
    """, (tipo, concepto, monto))
    conexion.commit()


def obtener_historial():
    cursor.execute("""
        SELECT id, tipo, concepto, monto, fecha 
        FROM movimientos 
        ORDER BY fecha DESC
    """)
    return cursor.fetchall()


# =========================
# FUNCIONES INTERFAZ
# =========================

def actualizar_balance():
    balance, ingresos, gastos = obtener_balance()

    lbl_balance.config(text=f"BALANCE: $ {balance:,.2f}")
    lbl_ingresos.config(text=f"INGRESOS: $ {ingresos:,.2f}")
    lbl_gastos.config(text=f"GASTOS: $ {gastos:,.2f}")


def actualizar_historial():
    for fila in tabla.get_children():
        tabla.delete(fila)

    for fila in obtener_historial():
        id_, tipo, concepto, monto, fecha = fila

        if tipo == "GASTO":
            monto = f"-${monto:,.2f}"
        else:
            monto = f"+${monto:,.2f}"

        tabla.insert("", "end", values=(id_, tipo, concepto, monto, fecha))


def ingresar_dinero():
    concepto = entry_concepto.get()
    monto = entry_monto.get()

    if not concepto or not monto:
        messagebox.showerror("Error", "Completa los campos")
        return

    try:
        monto = float(monto)
    except:
        messagebox.showerror("Error", "Monto inválido")
        return

    insertar_movimiento("INGRESO", concepto, monto)

    limpiar_campos()
    actualizar_balance()
    actualizar_historial()


def retirar_dinero():
    concepto = entry_concepto.get()
    monto = entry_monto.get()

    if not concepto or not monto:
        messagebox.showerror("Error", "Completa los campos")
        return

    try:
        monto = float(monto)
    except:
        messagebox.showerror("Error", "Monto inválido")
        return

    balance, _, _ = obtener_balance()

    if monto > balance:
        messagebox.showerror("Error", "Saldo insuficiente")
        return

    insertar_movimiento("GASTO", concepto, monto)

    limpiar_campos()
    actualizar_balance()
    actualizar_historial()


def limpiar_campos():
    entry_concepto.delete(0, tk.END)
    entry_monto.delete(0, tk.END)


# =========================
# INTERFAZ FUTURISTA
# =========================

ventana = tk.Tk()
ventana.title("BILLETERA DIGITAL v2.0")
ventana.geometry("1050x560")
ventana.configure(bg="#0d0d1a")

style = ttk.Style()
style.theme_use("clam")

style.configure("Treeview",
                background="#141428",
                foreground="#00ffee",
                rowheight=28,
                fieldbackground="#141428")

style.map("Treeview",
          background=[("selected", "#00ffee")],
          foreground=[("selected", "#000000")])

style.configure("Treeview.Heading",
                background="#1f1f3d",
                foreground="#00ffee",
                font=("Consolas", 10, "bold"))

# ===== BALANCE =====

frame_balance = tk.Frame(ventana, bg="#0d0d1a")
frame_balance.pack(pady=15)

lbl_balance = tk.Label(frame_balance,
                       font=("Consolas", 22, "bold"),
                       fg="#00ffcc",
                       bg="#0d0d1a")
lbl_balance.pack()

lbl_ingresos = tk.Label(frame_balance,
                        font=("Consolas", 12),
                        fg="#00ff88",
                        bg="#0d0d1a")
lbl_ingresos.pack()

lbl_gastos = tk.Label(frame_balance,
                      font=("Consolas", 12),
                      fg="#ff4c4c",
                      bg="#0d0d1a")
lbl_gastos.pack()

# ===== PANEL IZQUIERDO =====

frame_izq = tk.Frame(ventana, bg="#0d0d1a")
frame_izq.pack(side="left", padx=50)

tk.Label(frame_izq, text="CONCEPTO",
         font=("Consolas", 11),
         fg="#00ffee",
         bg="#0d0d1a").pack()

entry_concepto = tk.Entry(frame_izq,
                          font=("Consolas", 11),
                          bg="#1a1a2e",
                          fg="#00ffee",
                          insertbackground="white",
                          relief="flat")
entry_concepto.pack(pady=8, ipadx=12, ipady=6)

tk.Label(frame_izq, text="MONTO",
         font=("Consolas", 11),
         fg="#00ffee",
         bg="#0d0d1a").pack()

entry_monto = tk.Entry(frame_izq,
                       font=("Consolas", 11),
                       bg="#1a1a2e",
                       fg="#00ffee",
                       insertbackground="white",
                       relief="flat")
entry_monto.pack(pady=8, ipadx=12, ipady=6)

tk.Button(frame_izq,
          text="➕ INGRESAR",
          font=("Consolas", 11, "bold"),
          bg="#00ff88",
          fg="#000000",
          activebackground="#00cc6a",
          command=ingresar_dinero).pack(pady=12, fill="x")

tk.Button(frame_izq,
          text="➖ RETIRAR",
          font=("Consolas", 11, "bold"),
          bg="#ff4c4c",
          fg="#000000",
          activebackground="#cc0000",
          command=retirar_dinero).pack(pady=8, fill="x")

# ===== HISTORIAL =====

frame_historial = tk.Frame(ventana, bg="#0d0d1a")
frame_historial.pack(side="right", padx=30)

tk.Label(frame_historial,
         text="HISTORIAL DE TRANSACCIONES",
         font=("Consolas", 14, "bold"),
         fg="#00ffee",
         bg="#0d0d1a").pack(pady=5)

columnas = ("ID", "Tipo", "Concepto", "Monto", "Fecha")

tabla = ttk.Treeview(frame_historial,
                     columns=columnas,
                     show="headings",
                     height=18)

for col in columnas:
    tabla.heading(col, text=col)
    tabla.column(col, width=140)

tabla.pack()

# ===== INICIALIZAR =====

actualizar_balance()
actualizar_historial()

ventana.mainloop()