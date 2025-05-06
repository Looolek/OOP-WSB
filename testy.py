import tkinter as tk
from tkinter import ttk
import requests
from PIL import Image, ImageTk
import io
from obiekreq import NasaImageFetcher


#Paleta kolorów
COLOR_BG = '#000000' 
COLOR_FG = '#00FF00'
COLOR_FG_DIM = '#008F00'
COLOR_ENTRY_BG = '#000000'
COLOR_CURSOR = '#00FF00'
COLOR_BUTTON_BG = '#1A1A1A'
COLOR_BUTTON_ACTIVE = '#333333'
COLOR_SCROLL_TROUGH = '#000000'
COLOR_SCROLL_BG = '#1A1A1A'


def open_image_window(image_url, image_title):
    log_message(f"Otwieranie okna dla: {image_title}")

    img_window = tk.Toplevel(root)
    img_window.title(image_title)
    img_window.configure(bg=COLOR_BG)
    img_window.geometry("600x450")
    img_window.resizable(False, False)
    img_window.attributes('-topmost', True)
    status_label = ttk.Label(img_window, text="Pobieranie obrazka...", anchor='center')
    status_label.pack(padx=0, pady=0, fill=tk.BOTH, expand=True)

    try:
        log_message(f"Pobieranie pełnego obrazka: {image_url}")
        photo = fetch_and_process_image(image_url, size=None)
    
        if photo:
            status_label.configure(image=photo, text="")
            status_label.image = photo
        else:
            status_label.configure(text="Nie udało się załadować obrazka.", foreground="red")
            log_message("Nie udało się załadować obrazka.")

    except Exception as e:
        log_message(f"Nieoczekiwany błąd w open_image_window: {e}")
        status_label.configure(text=f"Wystąpił nieoczekiwany błąd:\n{e}", foreground="red")


#Funkcja obsługująca kliknięcie przycisku
def search_nasa():
    query = entry.get()
    if not query:
        log_message("Proszę podać zapytanie.")
        return

    log_message(f"Rozpoczynam wyszukiwanie dla: {query}")

    for widget in output_frame.winfo_children():
        if widget != text_output:
            widget.destroy()

    try:
        data = fetcher.fetch_data(query)
        items = data.get("collection", {}).get("items", [])

        if not items:
            log_message("Nie znaleziono żadnych wyników.")
            ttk.Label(output_frame, text="Brak wyników.").grid(row=1, column=0, columnspan=3, pady=10)
            return

        log_message(f"Znaleziono {len(items)} wyników. Próba wyświetlenia do 9.")

        results_to_display = []
        for item in items[:9]: #Limit do 9 wyników
            item_data = item.get("data", [])
            links = item.get("links", [])
            title = "Brak tytułu"
            href = None
            if item_data:
                title = item_data[0].get("title", "Brak tytułu")
            # Sprawdzamy czy links nie jest None przed iteracją
            if links:
                 preview_link = next((link.get('href') for link in links if link.get('rel') == 'preview'), None)
                 if preview_link: href = preview_link
            if href: results_to_display.append({'title': title, 'url': href})

        if not results_to_display:
            log_message("Nie znaleziono wyników z obrazkami do wyświetlenia.")
            ttk.Label(output_frame, text="Brak wyników z obrazkami.").grid(row=1, column=0, columnspan=3, pady=10)
            return


        # Tworzenie siatki 3x3
        for i, result in enumerate(results_to_display):
            row = (i // 3) + 1
            col = i % 3
            cell_frame = ttk.Frame(output_frame, padding=5, style='ImageCard.TFrame')
            cell_frame.grid(row=row, column=col, padx=5, pady=5, sticky="n")
            cell_frame.rowconfigure(0, weight=0); cell_frame.rowconfigure(1, weight=0)
            cell_frame.columnconfigure(0, weight=1)
            img_label = ttk.Label(cell_frame, text="Ładowanie...", anchor='center', background=COLOR_BG)
            img_label.grid(row=0, column=0, sticky="ew")
            title_label = ttk.Label(cell_frame, text=result['title'], anchor="center", wraplength=150, background=COLOR_BG)
            title_label.grid(row=1, column=0, sticky="ew", pady=(5,0))

            photo_thumbnail = fetch_and_process_image(result['url'], size=(150, 150))
            if photo_thumbnail:
                img_label.configure(image=photo_thumbnail, text="")
                img_label.image = photo_thumbnail
                current_url = result['url']
                current_title = result['title']
                img_label.bind("<Button-1>", lambda event, url=current_url, title=current_title: open_image_window(url, title))
                img_label.configure(cursor="hand2") # Zmiana kursora na "rączkę" po najechaniu
            else:
                img_label.configure(text="Błąd obrazka")
            
            

        log_message("Wyświetlanie wyników zakończone.")
        for c in range(3): output_frame.columnconfigure(c, weight=1)
        num_rows_needed = (len(results_to_display) + 2) // 3
        for r in range(1, num_rows_needed + 1): output_frame.rowconfigure(r, weight=1)


    except Exception as error:
        log_message(f"Błąd podczas wyszukiwania lub przetwarzania: {error}")
        ttk.Label(output_frame, text=f"Wystąpił błąd:\n{error}").grid(row=1, column=0, columnspan=3, pady=10)


#Funkcje pomocnicze
def fetch_and_process_image(url, size=None):
    try:
        response = requests.get(url, stream=True, timeout=15)
        response.raise_for_status()
        image_data = response.content
        if not image_data: log_message(f"Puste dane obrazka z {url}"); return None
        img = Image.open(io.BytesIO(image_data))
        if img.mode not in ("RGB", "L"): img = img.convert("RGB")
        if size:
            img.thumbnail(size)
        return ImageTk.PhotoImage(img)
    except requests.exceptions.Timeout: log_message(f"Timeout: {url}")
    except requests.exceptions.RequestException as e: log_message(f"Błąd sieci: {url}: {e}")
    except Exception as e: log_message(f"Błąd przetwarzania obrazka {url}: {e}")
    return None


def append_log_message(widget, text):
    if widget.winfo_exists():
        try:
            widget.configure(state=tk.NORMAL)
            widget.insert(tk.END, str(text) + "\n")
            widget.see(tk.END)
            widget.configure(state=tk.DISABLED)
        except tk.TclError as e:
            print(f"Błąd Tkinter log: {e}")
            print(f"LOG (awaryjny): {text}")
    else: print(f"LOG (widget nie istnieje): {text}")


def log_message(text):
    if 'text_log_widget' in globals() and isinstance(text_log_widget, tk.Text) and text_log_widget.winfo_exists():
         append_log_message(text_log_widget, text)
    else: print(f"LOG: {text}")


#Główna część GUI
root = tk.Tk()
root.title("NASA images")
root.configure(bg=COLOR_BG)


#Konfiguracja stylów
style = ttk.Style(root)
style.theme_use('clam')


#Styl ramki obrazka
style.configure('ImageCard.TFrame', background=COLOR_BG, relief=tk.SOLID, borderwidth=1, bordercolor=COLOR_FG)


#Konfiguracja stylów
style.configure('.', background=COLOR_BG, foreground=COLOR_FG, bordercolor=COLOR_FG_DIM)
style.configure('TFrame', background=COLOR_BG)
style.configure('TLabel', background=COLOR_BG, foreground=COLOR_FG, padding=2)
style.configure('TButton', background=COLOR_BUTTON_BG, foreground=COLOR_FG, padding=5, borderwidth=1, relief=tk.RAISED, bordercolor=COLOR_FG_DIM)
style.map('TButton', background=[('active', COLOR_BUTTON_ACTIVE)])
style.configure('TEntry', fieldbackground=COLOR_ENTRY_BG, foreground=COLOR_FG, insertcolor=COLOR_CURSOR, bordercolor=COLOR_FG_DIM, borderwidth=1)
style.configure('Vertical.TScrollbar', background=COLOR_SCROLL_BG, troughcolor=COLOR_SCROLL_TROUGH, bordercolor=COLOR_BG, arrowcolor=COLOR_FG)
style.map('Vertical.TScrollbar', background=[('active', COLOR_BUTTON_ACTIVE)])


#grid
root.rowconfigure(0, weight=0)
root.rowconfigure(1, weight=1)
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=2, minsize=300)
root.columnconfigure(2, weight=1, minsize=300) 


#inputy
input_frame = ttk.Frame(master=root)
input_frame.grid(row=0, column=0, columnspan=3, sticky="new", padx=10, pady=10)
input_frame.columnconfigure(0, weight=1); input_frame.columnconfigure(1, weight=0)
input_frame.columnconfigure(2, weight=0); input_frame.columnconfigure(3, weight=0)
input_frame.columnconfigure(4, weight=1)
text_zap = ttk.Label(input_frame, text="Podaj zapytanie:")
text_zap.grid(row=0, column=1, padx=5, pady=5, sticky='e')
entry = ttk.Entry(input_frame, width=30)
entry.grid(row=0, column=2, padx=5, pady=5, sticky='ew')
button = ttk.Button(input_frame, text="Szukaj", command=search_nasa)
button.grid(row=0, column=3, padx=5, pady=5, sticky='w')


#output
output_frame = ttk.Frame(master = root)
output_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 0), pady=(0, 10))
text_output = ttk.Label(output_frame, text="Wyniki:")
text_output.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="nw")


#logi
log_frame = ttk.Frame(master = root)
log_frame.grid(row=1, column=2, sticky="nsew", padx=(0, 10), pady=(0, 10))
log_frame.rowconfigure(0, weight=0); log_frame.rowconfigure(1, weight=1)
log_frame.columnconfigure(0, weight=1); log_frame.columnconfigure(1, weight=0)
text_log_label = ttk.Label(log_frame, text="Logi:")
text_log_label.grid(row=0, column=0, padx=5, pady=5, sticky="nw")

text_log_widget = tk.Text(log_frame, width=30, height=10, wrap=tk.WORD,
    bg=COLOR_ENTRY_BG, fg=COLOR_FG,
    insertbackground=COLOR_CURSOR, borderwidth=1, 
    relief=tk.SOLID, highlightthickness=1,
    highlightcolor=COLOR_FG_DIM, highlightbackground=COLOR_BG)

text_log_widget.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=text_log_widget.yview, style='Vertical.TScrollbar') 
log_scrollbar.grid(row=1, column=1, sticky="ns", pady=(5,5), padx=(0,5))
text_log_widget['yscrollcommand'] = log_scrollbar.set


fetcher = NasaImageFetcher()
log_message("Aplikacja gotowa.")


#Główna pętla
root.mainloop()