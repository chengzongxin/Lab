import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("测试 ttk")
root.geometry("300x200")

label = ttk.Label(root, text="Hello from ttk!", font=("Helvetica", 14))
label.pack(padx=20, pady=20)

root.mainloop()
