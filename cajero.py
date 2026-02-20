import tkinter as tk
from tkinter import messagebox
import sqlite3
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import fonts
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import letter
import os

# ================= BASE DE DATOS =================

conn = sqlite3.connect("finanzas.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)python --version
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS movimientos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    tipo TEXT,
    descripcion TEXT,
    monto REAL
)
""")

conn.commit()

usuario_actual = None

# ================= COLORES TIPO NU =================

BG_COLOR = "#121212"
CARD_COLOR = "#1E1E1E"
PRIMARY = "#8A05BE"
TEXT_COLOR = "#FFFFFF"

# ================= FUNCIONES =================

def registrar():
    user = entry_user.get()
    pwd = entry_pass.get()

    try:
        cursor.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", (user, pwd))
        conn.commit()
        messagebox.showinfo("Éxito", "Usuario registrado correctamente")
    except:
        messagebox.showerror("Error", "El usuario ya existe")

def login():
    global usuario_actual
    user = entry_user.get()
    pwd = entry_pass.get()

    cursor.execute("SELECT id FROM usuarios WHERE username=? AND password=?", (user, pwd))
    resultado = cursor.fetchone()

    if resultado:
        usuario_actual = resultado[0]
        mostrar_interfaz_principal()
    else:
        messagebox.showerror("Error", "Datos incorrectos")

def cerrar_sesion():
    global usuario_actual
    usuario_actual = None
    frame_principal.pack_forget()
    frame_login.pack(pady=50)

def agregar_movimiento(tipo):
    descripcion = entry_desc.get()
    monto = entry_monto.get()

    if descripcion == "" or monto == "":
        messagebox.showerror("Error", "Complete todos los campos")
        return

    cursor.execute("INSERT INTO movimientos (usuario_id, tipo, descripcion, monto) VALUES (?, ?, ?, ?)",
                   (usuario_actual, tipo, descripcion, float(monto)))
    conn.commit()
    mostrar_movimientos()
    entry_desc.delete(0, tk.END)
    entry_monto.delete(0, tk.END)

def mostrar_movimientos():
    lista_movimientos.delete(0, tk.END)
    cursor.execute("SELECT id, tipo, descripcion, monto FROM movimientos WHERE usuario_id=?", (usuario_actual,))
    for mov in cursor.fetchall():
        lista_movimientos.insert(tk.END, f"{mov[0]} | {mov[1]} | {mov[2]} | ${mov[3]}")

def borrar_movimiento():
    seleccion = lista_movimientos.get(tk.ACTIVE)
    if seleccion:
        mov_id = seleccion.split("|")[0].strip()
        cursor.execute("DELETE FROM movimientos WHERE id=?", (mov_id,))
        conn.commit()
        mostrar_movimientos()

def exportar_pdf():
    cursor.execute("SELECT tipo, descripcion, monto FROM movimientos WHERE usuario_id=?", (usuario_actual,))
    datos = cursor.fetchall()

    if not datos:
        messagebox.showwarning("Vacío", "No hay datos para exportar")
        return

    filename = f"Historial_usuario_{usuario_actual}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elementos = []

    estilos = getSampleStyleSheet()
    elementos.append(Paragraph("Historial Financiero", estilos["Heading1"]))
    elementos.append(Spacer(1, 0.3 * inch))

    tabla_datos = [["Tipo", "Descripción", "Monto"]]
    for d in datos:
        tabla_datos.append([d[0], d[1], f"${d[2]}"])

    tabla = Table(tabla_datos)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.purple),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 1, colors.grey)
    ]))

    elementos.append(tabla)
    doc.build(elementos)

    messagebox.showinfo("PDF generado", f"Se creó {filename}")

def mostrar_interfaz_principal():
    frame_login.pack_forget()
    frame_principal.pack(fill="both", expand=True)
    mostrar_movimientos()

# ================= INTERFAZ =================

root = tk.Tk()
root.title("Sistema Financiero")
root.geometry("700x500")
root.configure(bg=BG_COLOR)

# ================= LOGIN =================

frame_login = tk.Frame(root, bg=BG_COLOR)

tk.Label(frame_login, text="Iniciar Sesión", font=("Arial", 20, "bold"), bg=BG_COLOR, fg=PRIMARY).pack(pady=20)

entry_user = tk.Entry(frame_login, font=("Arial", 14))
entry_user.pack(pady=5)

entry_pass = tk.Entry(frame_login, font=("Arial", 14), show="*")
entry_pass.pack(pady=5)

tk.Button(frame_login, text="Login", bg=PRIMARY, fg="white", width=20, command=login).pack(pady=10)
tk.Button(frame_login, text="Registrar", bg=CARD_COLOR, fg="white", width=20, command=registrar).pack()

frame_login.pack(pady=50)

# ================= PRINCIPAL =================

frame_principal = tk.Frame(root, bg=BG_COLOR)

tk.Label(frame_principal, text="Panel Financiero", font=("Arial", 20, "bold"), bg=BG_COLOR, fg=PRIMARY).pack(pady=10)

frame_form = tk.Frame(frame_principal, bg=CARD_COLOR)
frame_form.pack(pady=10)

entry_desc = tk.Entry(frame_form, width=25)
entry_desc.grid(row=0, column=0, padx=5, pady=5)

entry_monto = tk.Entry(frame_form, width=15)
entry_monto.grid(row=0, column=1, padx=5, pady=5)

tk.Button(frame_form, text="Agregar Ingreso", bg=PRIMARY, fg="white",
          command=lambda: agregar_movimiento("Ingreso")).grid(row=1, column=0, pady=5)

tk.Button(frame_form, text="Agregar Gasto", bg="#B00020", fg="white",
          command=lambda: agregar_movimiento("Gasto")).grid(row=1, column=1, pady=5)

lista_movimientos = tk.Listbox(frame_principal, width=80)
lista_movimientos.pack(pady=10)

tk.Button(frame_principal, text="Borrar Movimiento", bg=CARD_COLOR, fg="white",
          command=borrar_movimiento).pack(pady=5)

tk.Button(frame_principal, text="Exportar a PDF", bg=PRIMARY, fg="white",
          command=exportar_pdf).pack(pady=5)

tk.Button(frame_principal, text="Cerrar Sesión", bg="#333333", fg="white",
          command=cerrar_sesion).pack(pady=10)

root.mainloop()