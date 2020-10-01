import tkinter as tk
import tkinter.font as tkfont

window = tk.Tk()
FONT = tkfont.Font(window, ("Courier New", 12))

WIDTH = window.winfo_screenwidth()
HEIGHT = window.winfo_screenheight()

window.title("Cellular Text")
window.geometry(f"{WIDTH}x{HEIGHT}+0+0")

window.columnconfigure(0, minsize = 50, weight = 1)
window.columnconfigure(1, minsize = 500, weight = 1)
window.columnconfigure(2, minsize = 500, weight = 1)
window.rowconfigure(0, minsize = 600, weight = 1)

# NOTES: I probably want to have this as a horizontal bar
# across the top.
# It's kinda ugly on the left side, and it won't format
# correctly there.
buttonframe = tk.Frame(window, bg = "gray16")
buttonframe.grid(row = 0, column = 0, sticky = "nsew")

textframe = tk.Frame(window)
textframe.grid(row = 0, column = 1, sticky = "nsew")

displayframe = tk.Frame(window, bg = "gray16")
displayframe.grid(row = 0, column = 2, sticky = "nsew")

# I also need some kind of space for extra debugging
# information, on either side of the text.
widths = [70, 60, 70, 30, 70, 500]
for i, w in enumerate(widths):
    textframe.columnconfigure(i, minsize = w, weight = 1)

lines = []

# Number of lines should probably depend on the
# height of the window.
for r in range(40):
    textframe.rowconfigure(r, minsize = 24, weight = 1)
    line = []
    for c in range(len(widths)):
        sec = tk.Text(textframe, height = 1, relief = tk.RIDGE, font = FONT, bg = "gray10", fg = "white", insertbackground = "white")
        sec.grid(row = r, column = c, sticky = "nsew")
        line.append(sec)
    lines.append(line)

testb = tk.Button(buttonframe, text = "Test")
testb.grid(row = 0, column = 0, sticky = "ew", padx = 5, pady = 5)

window.mainloop()
