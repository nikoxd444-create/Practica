import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

#CONEXION MYSQL

conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="wallet"
)

cursor = conexion.cursor()

#FUNCIONES BALANCE

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


def insertar_movimiento(tipo, tipo_de_gasto, monto):
    cursor.execute("""
        INSERT INTO movimientos (tipo, concepto, monto)
        VALUES (%s, %s, %s)
    """, (tipo, tipo_de_gasto, monto))
    conexion.commit()


def obtener_historial():
    cursor.execute("""
        SELECT id, tipo, concepto, monto, fecha 
        FROM movimientos 
        ORDER BY fecha DESC
    """)
    return cursor.fetchall()


#FUNCIONES INTERFAZ

def actualizar_balance():
    balance, ingresos, gastos = obtener_balance()

    lbl_balance.config(text=f"Balance actual: $ {balance:,.2f}")
    lbl_ingresos.config(text=f"Ingresos: $ {ingresos:,.2f}")
    lbl_gastos.config(text=f"Gastos: $ {gastos:,.2f}")


def actualizar_historial():

    for fila in tabla.get_children():
        tabla.delete(fila)

    for fila in obtener_historial():

        id_, tipo, tipo_de_gasto, monto, fecha = fila

        if tipo == "GASTO":
            monto = f"-${monto:,.2f}"
        else:
            monto = f"+${monto:,.2f}"

        tabla.insert("", "end", values=(id_, tipo, tipo_de_gasto, monto, fecha))


def ingresar_dinero():

    tipo_de_gasto = entry_tipo.get()
    monto = entry_monto.get()

    if not tipo_de_gasto or not monto:
        messagebox.showerror("Error", "Completa los campos")
        return

    try:
        monto = float(monto)
    except:
        messagebox.showerror("Error", "Monto inválido")
        return

    insertar_movimiento("INGRESO", tipo_de_gasto, monto)

    limpiar_campos()
    actualizar_balance()
    actualizar_historial()


def retirar_dinero():

    tipo_de_gasto = entry_tipo.get()
    monto = entry_monto.get()

    if not tipo_de_gasto or not monto:
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

    insertar_movimiento("GASTO", tipo_de_gasto, monto)

    limpiar_campos()
    actualizar_balance()
    actualizar_historial()


def limpiar_campos():
    entry_tipo.delete(0, tk.END)
    entry_monto.delete(0, tk.END)


#INTERFAZ

ventana = tk.Tk()
ventana.title("TU BILLETERA DE CONFIANZA")
ventana.geometry("950x520")
ventana.configure(bg="#1e1e2f")

#Estilo tabla

style = ttk.Style()
style.theme_use("default")

style.configure("Treeview",
                background="#2c2f33",
                foreground="white",
                rowheight=25,
                fieldbackground="#2c2f33")

style.map("Treeview",
          background=[("selected", "#00b894")])

style.configure("Treeview.Heading",
                background="#00b894",
                foreground="white",
                font=("Arial", 10, "bold"))

#Balance

frame_balance = tk.Frame(ventana, bg="#1e1e2f")
frame_balance.pack(pady=10)

lbl_balance = tk.Label(frame_balance, font=("Arial", 20, "bold"),
                       fg="#00ff88", bg="#1e1e2f")
lbl_balance.pack()

lbl_ingresos = tk.Label(frame_balance, fg="white", bg="#1e1e2f")
lbl_ingresos.pack()

lbl_gastos = tk.Label(frame_balance, fg="white", bg="#1e1e2f")
lbl_gastos.pack()

#Frame izquierdo

frame_izq = tk.Frame(ventana, bg="#1e1e2f")
frame_izq.pack(side="left", padx=30)

tk.Label(frame_izq, text="Tipo de gasto",
         fg="white", bg="#1e1e2f").pack()

entry_tipo = tk.Entry(frame_izq)
entry_tipo.pack(pady=5)

tk.Label(frame_izq, text="Monto",
         fg="white", bg="#1e1e2f").pack()

entry_monto = tk.Entry(frame_izq)
entry_monto.pack(pady=5)

tk.Button(
    frame_izq,
    text="INGRESAR DINERO",
    bg="#00b894",
    fg="white",
    activebackground="#019875",
    command=ingresar_dinero
).pack(pady=10, fill="x")

tk.Button(
    frame_izq,
    text="RETIRAR DINERO",
    bg="#d63031",
    fg="white",
    activebackground="#b71c1c",
    command=retirar_dinero
).pack(pady=10, fill="x")

#Historial

frame_historial = tk.Frame(ventana, bg="#1e1e2f")
frame_historial.pack(side="right", padx=20)

tk.Label(
    frame_historial,
    text="Historial de Transacciones",
    font=("Arial", 14, "bold"),
    fg="white",
    bg="#1e1e2f"
).pack()

columnas = ("ID", "Tipo", "Tipo de gasto", "Monto", "Fecha")

tabla = ttk.Treeview(frame_historial, columns=columnas,
                     show="headings", height=18)

for col in columnas:
    tabla.heading(col, text=col)
    tabla.column(col, width=130)

tabla.pack()

#Inicializar

actualizar_balance()
actualizar_historial()

ventana.mainloop()
#fin