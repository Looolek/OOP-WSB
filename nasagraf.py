import tkinter as tk
from tkinter import ttk
import requests
from obiekreq import NasaImageFetcher

root = tk.Tk()
root.title("NASA images")
root.geometry("1000x1000")

#grid
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.columnconfigure(3, weight=1)
root.columnconfigure(4, weight=1)


#inputy
input_frame = ttk.Frame(master = root)
input_frame.grid(row=0, column=0, columnspan=3, sticky="new", padx=10, pady=10)

input_frame.columnconfigure(0, weight=1)
input_frame.columnconfigure(1, weight=0)
input_frame.columnconfigure(2, weight=0)
input_frame.columnconfigure(3, weight=0)
input_frame.columnconfigure(4, weight=1)

text_zap = ttk.Label(input_frame, text="Podaj zapytanie:")
text_zap.grid(row=0, column=1, padx=5, pady=5)

entry = ttk.Entry(input_frame, width=30)
entry.grid(row=0, column=2, padx=5, pady=5)

button = ttk.Button(input_frame, text="Szukaj")
button.grid(row=0, column=3, padx=5, pady=5)



#output
output_frame = ttk.Frame(master = root)
output_frame.grid(row=1, column=0, columnspan=3, rowspan = 3, sticky="n")
text_output = ttk.Label(output_frame, text="Wyniki:")
text_output.grid(row=1, column=0, padx=5, pady=5)

#logi
log_frame = ttk.Frame(master = root)
log_frame.grid(row=1, column=5, columnspan=2, rowspan = 3, sticky="n")
text_log = ttk.Label(log_frame, text="Logi:")
text_log.grid(row=1, column=5, padx=5, pady=5)
text_log = tk.Text(log_frame, width=40, height=40)
text_log.grid(row=2, column=5, padx=5, pady=5)

root.mainloop()
