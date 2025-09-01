import tkinter as tk
from tkinter import ttk, messagebox

def calculate(event=None):
    try:
        a = float(num1_var.get())
        b = float(num2_var.get())
        op = op_var.get()
        if op == "+":
            res = a + b
        elif op == "-":
            res = a - b
        elif op == "*":
            res = a * b
        elif op == "/":
            if b == 0:
                messagebox.showerror("Error", "Division by zero is not allowed.")
                return
            res = a / b
        else:
            messagebox.showerror("Error", "Choose an operation.")
            return
        result_var.set(str(res))
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers.")

def clear_all():
    num1_var.set("")
    num2_var.set("")
    result_var.set("")
    op_var.set("+")

root = tk.Tk()
root.title("Elegant Calculator")
root.minsize(380, 260)

style = ttk.Style()
try:
    style.theme_use("clam")
except:
    pass

container = ttk.Frame(root, padding=16)
container.pack(fill="both", expand=True)

title = ttk.Label(container, text="Basic Calculator", font=("Segoe UI", 16, "bold"))
title.grid(row=0, column=0, columnspan=3, pady=(0, 12))

num1_var = tk.StringVar()
num2_var = tk.StringVar()
result_var = tk.StringVar()
op_var = tk.StringVar(value="+")

ttk.Label(container, text="First number").grid(row=1, column=0, sticky="w")
e1 = ttk.Entry(container, textvariable=num1_var, justify="center", font=("Segoe UI", 11))
e1.grid(row=2, column=0, padx=(0, 8), sticky="ew")

ttk.Label(container, text="Operation").grid(row=1, column=1, sticky="w")
op_box = ttk.Combobox(container, textvariable=op_var, values=["+", "-", "*", "/"], state="readonly", justify="center")
op_box.grid(row=2, column=1, padx=8, sticky="ew")

ttk.Label(container, text="Second number").grid(row=1, column=2, sticky="w")
e2 = ttk.Entry(container, textvariable=num2_var, justify="center", font=("Segoe UI", 11))
e2.grid(row=2, column=2, padx=(8, 0), sticky="ew")

btn_calc = ttk.Button(container, text="Calculate", command=calculate)
btn_clear = ttk.Button(container, text="Clear", command=clear_all)
btn_calc.grid(row=3, column=0, columnspan=2, pady=12, sticky="ew")
btn_clear.grid(row=3, column=2, pady=12, sticky="ew")

ttk.Label(container, text="Result").grid(row=4, column=0, columnspan=3, sticky="w")
out = ttk.Entry(container, textvariable=result_var, justify="center", font=("Segoe UI", 12), state="readonly")
out.grid(row=5, column=0, columnspan=3, sticky="ew")

container.columnconfigure(0, weight=1)
container.columnconfigure(1, weight=1)
container.columnconfigure(2, weight=1)

e1.bind("<Return>", calculate)
e2.bind("<Return>", calculate)
op_box.bind("<Return>", calculate)

root.mainloop()
