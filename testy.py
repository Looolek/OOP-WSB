import tkinter as tk
from tkinter import ttk
import requests
# from obiekreq import NasaImageFetcher # Zakładam, że ten import jest potrzebny

root = tk.Tk()
root.title("NASA images")
# root.geometry("1000x1000") # Usunięto, aby polegać na wagach siatki

#grid
root.rowconfigure(0, weight=0)
root.rowconfigure(1, weight=1)
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.columnconfigure(3, weight=1)
root.columnconfigure(4, weight=1)


#inputy
input_frame = ttk.Frame(master=root)
input_frame.grid(row=0, column=0, columnspan=5, sticky="new", padx=10, pady=10)

input_frame.columnconfigure(0, weight=1)
input_frame.columnconfigure(1, weight=0)
input_frame.columnconfigure(2, weight=0)
input_frame.columnconfigure(3, weight=0)
input_frame.columnconfigure(4, weight=1)

text_zap = ttk.Label(input_frame, text="Podaj zapytanie:")
text_zap.grid(row=0, column=1, padx=5, pady=5, sticky='e')

entry = ttk.Entry(input_frame, width=30)
entry.grid(row=0, column=2, padx=5, pady=5, sticky='ew')

button = ttk.Button(input_frame, text="Szukaj")
button.grid(row=0, column=3, padx=5, pady=5, sticky='w')


#output
output_frame = ttk.Frame(master = root)
output_frame.grid(row=1, column=0, columnspan=3, rowspan=1, sticky="nsew", padx=(10, 5), pady=(0, 10))
output_frame.rowconfigure(0, weight=0)
output_frame.rowconfigure(1, weight=1)
output_frame.columnconfigure(0, weight=1)
output_frame.columnconfigure(1, weight=0)
text_output = ttk.Label(output_frame, text="Wyniki:")
text_output.grid(row=0, column=0, padx=5, pady=5, sticky="nw")
results_area = tk.Text(output_frame, height=10, wrap=tk.WORD)
results_scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=results_area.yview)
results_area['yscrollcommand'] = results_scrollbar.set
results_area.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
results_scrollbar.grid(row=1, column=1, sticky="ns")
results_area.insert(tk.END, "Miejsce na wyniki...\n")
results_area.config(state=tk.DISABLED)


#logi
log_frame = ttk.Frame(master = root)
log_frame.grid(row=1, column=3, columnspan=2, rowspan=1, sticky="nsew", padx=(5, 10), pady=(0, 10))
log_frame.rowconfigure(0, weight=0)
log_frame.rowconfigure(1, weight=1)
log_frame.columnconfigure(0, weight=1)
log_frame.columnconfigure(1, weight=0)
text_log_label = ttk.Label(log_frame, text="Logi:")
text_log_label.grid(row=0, column=0, padx=5, pady=5, sticky="nw")
log_text_widget = tk.Text(log_frame, width=40, height=10, wrap=tk.WORD)
log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=log_text_widget.yview)
log_text_widget['yscrollcommand'] = log_scrollbar.set
log_text_widget.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
log_scrollbar.grid(row=1, column=1, sticky="ns")
log_text_widget.insert(tk.END, "Logi aplikacji...\n")
log_text_widget.config(state=tk.DISABLED)


root.mainloop()