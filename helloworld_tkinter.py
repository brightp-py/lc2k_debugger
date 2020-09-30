import tkinter as tk
from tkinter.filedialog import askopenfilename

def open_file():
    filepath = askopenfilename(
        filetypes = (("LC2K", "*.as"), ("All Files", "*.*"))
    )

    if not filepath:
        return
    
    txtEdit.delete(1.0, tk.END)

    with open(filepath, 'r') as f:
        text = f.read()
        txtEdit.insert(tk.END, text)
    window.title(f"Hello World! - {filepath}")

window = tk.Tk()
window.title("Hello World! Editor")

window.rowconfigure(0, minsize = 720, weight = 1)
window.columnconfigure(1, minsize = 1280, weight = 1)

txtEdit = tk.Text(window)
frButtons = tk.Frame(window)

button =  {
    "Open": tk.Button(frButtons, text = "Open", command = open_file),
    "Save": tk.Button(frButtons, text = "Save")
}

r = 1
for btn in button:
    button[btn].grid(row = r, column = 0, sticky = "ew", padx = 5, pady = 5)
    r += 1

frButtons.grid(row = 0, column = 0, sticky = "ns")
txtEdit.grid(row = 0, column = 1, sticky = "nsew")

window.mainloop()