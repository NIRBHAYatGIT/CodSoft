import tkinter as tk
import random
import string

def generate_password():
    try:
        length = int(entry_length.get())
        if length <= 0:
            result_label.config(text="Enter a positive number")
            return
        characters = string.ascii_letters + string.digits + string.punctuation
        password = "".join(random.choice(characters) for _ in range(length))
        result_label.config(text=password)
    except ValueError:
        result_label.config(text="Enter a valid number")

# GUI Setup
root = tk.Tk()
root.title("Password Generator")
root.geometry("400x250")
root.config(bg="#2c3e50")

title_label = tk.Label(root, text="Password Generator", font=("Arial", 16, "bold"), bg="#2c3e50", fg="white")
title_label.pack(pady=10)

frame = tk.Frame(root, bg="#2c3e50")
frame.pack(pady=10)

label_length = tk.Label(frame, text="Password Length:", font=("Arial", 12), bg="#2c3e50", fg="white")
label_length.grid(row=0, column=0, padx=5)

entry_length = tk.Entry(frame, font=("Arial", 12), width=10)
entry_length.grid(row=0, column=1, padx=5)

generate_button = tk.Button(root, text="Generate", font=("Arial", 12, "bold"), bg="#27ae60", fg="white", command=generate_password)
generate_button.pack(pady=10)

result_label = tk.Label(root, text="", font=("Arial", 14, "bold"), bg="#34495e", fg="yellow", wraplength=350, relief="ridge", padx=10, pady=5)
result_label.pack(pady=10)

root.mainloop()


