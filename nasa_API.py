# Importowanie niezbędnych bibliotek
import tkinter as tk  # Główna biblioteka do tworzenia GUI
from tkinter import ttk  # Rozszerzenie tkinter z nowocześniejszymi widgetami
import requests  # Biblioteka do wykonywania zapytań HTTP
from PIL import Image, ImageTk  # Biblioteki do obsługi obrazów
import io  # Biblioteka do operacji wejścia/wyjścia
from obiekreq import NasaImageFetcher  # Import własnej klasy do pobierania danych z API NASA


# Definicja palety kolorów w stylu terminala (czarne tło, zielony tekst)
COLOR_BG = '#000000'  # Kolor tła - czarny
COLOR_FG = '#00FF00'  # Kolor tekstu - jaskrawozielony
COLOR_FG_DIM = '#008F00'  # Przyciemniony zielony do elementów drugorzędnych
COLOR_ENTRY_BG = '#000000'  # Tło pola wprowadzania - czarne
COLOR_CURSOR = '#00FF00'  # Kolor kursora - zielony
COLOR_BUTTON_BG = '#1A1A1A'  # Tło przycisków - ciemnoszare
COLOR_BUTTON_ACTIVE = '#333333'  # Kolor aktywnego przycisku - jaśniejszy szary
COLOR_SCROLL_TROUGH = '#000000'  # Tło paska przewijania - czarne
COLOR_SCROLL_BG = '#1A1A1A'  # Kolor suwaka przewijania - ciemnoszary


# Funkcja do otwierania nowego okna z powiększonym obrazem
def open_image_window(image_url, image_title):
    log_message(f"Otwieranie okna dla: {image_title}")  # Logowanie informacji o otwarciu okna
    
    img_window = tk.Toplevel(root)  # Tworzenie nowego okna jako okna podrzędnego do głównego okna
    img_window.title(image_title)  # Ustawienie tytułu okna na tytuł obrazu
    img_window.configure(bg=COLOR_BG)  # Ustawienie koloru tła okna
    img_window.geometry("600x450")  # Ustawienie początkowego rozmiaru okna
    img_window.resizable(False, False)  # Wyłączenie możliwości zmiany rozmiaru okna
    img_window.attributes('-topmost', True)  # Ustawienie okna zawsze na wierzchu
    status_label = ttk.Label(img_window, text="Pobieranie obrazka...", anchor='center')  # Etykieta informująca o pobieraniu
    status_label.pack(padx=0, pady=0, fill=tk.BOTH, expand=True)  # Umieszczenie etykiety w oknie

    try:  # Rozpoczęcie bloku obsługi wyjątków
        log_message(f"Pobieranie pełnego obrazka: {image_url}")  # Logowanie informacji o pobieraniu obrazu
        photo = fetch_and_process_image(image_url, size=None)  # Pobranie obrazu w pełnym rozmiarze
    
        if photo:  # Jeśli obraz został poprawnie pobrany
            status_label.configure(image=photo, text="")  # Wyświetlenie obrazu w etykiecie
            status_label.image = photo  # Zachowanie referencji do obrazu (zapobiega usunięciu przez garbage collector)
        else:  # Jeśli nie udało się pobrać obrazu
            status_label.configure(text="Nie udało się załadować obrazka.", foreground="red")  # Wyświetlenie komunikatu o błędzie
            log_message("Nie udało się załadować obrazka.")  # Logowanie informacji o błędzie

    except Exception as e:  # Obsługa wszystkich wyjątków
        log_message(f"Nieoczekiwany błąd w open_image_window: {e}")  # Logowanie informacji o błędzie
        status_label.configure(text=f"Wystąpił nieoczekiwany błąd:\n{e}", foreground="red")  # Wyświetlenie komunikatu o błędzie


# Funkcja wywoływana po kliknięciu przycisku "Szukaj"
def search_nasa():
    query = entry.get()  # Pobranie tekstu z pola wprowadzania
    if not query:  # Sprawdzenie czy pole nie jest puste
        log_message("Proszę podać zapytanie.")  # Logowanie informacji o pustym polu
        return  # Przerwanie wykonywania funkcji

    log_message(f"Rozpoczynam wyszukiwanie dla: {query}")  # Logowanie rozpoczęcia wyszukiwania

    # Usunięcie poprzednich wyników (wszystkich widgetów oprócz etykiety "Wyniki:")
    for widget in output_frame.winfo_children():
        if widget != text_output:
            widget.destroy()

    try:  # Rozpoczęcie bloku obsługi wyjątków
        data = fetcher.fetch_data(query)  # Pobranie danych z API NASA
        items = data.get("collection", {}).get("items", [])  # Wyodrębnienie elementów z odpowiedzi
        
        # Sprawdzenie czy znaleziono jakiekolwiek wyniki
        if not items:
            log_message("Nie znaleziono żadnych wyników.")  # Logowanie informacji o braku wyników
            ttk.Label(output_frame, text="Brak wyników.").grid(row=1, column=0, columnspan=3, pady=10)  # Wyświetlenie komunikatu
            return  # Przerwanie wykonywania funkcji

        log_message(f"Znaleziono {len(items)} wyników. Próba wyświetlenia do 9.")  # Logowanie informacji o liczbie wyników

        # Przygotowanie listy wyników do wyświetlenia
        results_to_display = []
        for item in items[:9]:  # Ograniczenie do maksymalnie 9 wyników
            item_data = item.get("data", [])  # Pobranie danych elementu
            links = item.get("links", [])  # Pobranie linków elementu
            title = "Brak tytułu"  # Domyślny tytuł
            href = None  # Domyślny URL obrazu
            if item_data:  # Jeśli są dane elementu
                title = item_data[0].get("title", "Brak tytułu")  # Pobranie tytułu
            # Pobranie URL obrazu podglądu
            if links:  # Jeśli są linki
                preview_link = next((link.get('href') for link in links if link.get('rel') == 'preview'), None)  # Pobranie linku podglądu
                if preview_link: href = preview_link  # Przypisanie URL obrazu
            if href: results_to_display.append({'title': title, 'url': href})  # Dodanie wyniku do listy

        # Sprawdzenie czy znaleziono obrazki do wyświetlenia
        if not results_to_display:
            log_message("Nie znaleziono wyników z obrazkami do wyświetlenia.")  # Logowanie informacji o braku obrazków
            ttk.Label(output_frame, text="Brak wyników z obrazkami.").grid(row=1, column=0, columnspan=3, pady=10)  # Wyświetlenie komunikatu
            return  # Przerwanie wykonywania funkcji


        # Tworzenie siatki 3x3 z wynikami
        for i, result in enumerate(results_to_display):
            row = (i // 3) + 1  # Obliczenie wiersza (dzielenie całkowite)
            col = i % 3  # Obliczenie kolumny (reszta z dzielenia)
            cell_frame = ttk.Frame(output_frame, padding=5, style='ImageCard.TFrame')  # Tworzenie ramki dla wyniku
            cell_frame.grid(row=row, column=col, padx=5, pady=5, sticky="n")  # Umieszczenie ramki w siatce
            cell_frame.rowconfigure(0, weight=0); cell_frame.rowconfigure(1, weight=0)  # Konfiguracja wierszy ramki
            cell_frame.columnconfigure(0, weight=1)  # Konfiguracja kolumny ramki
            img_label = ttk.Label(cell_frame, text="Ładowanie...", anchor='center', background=COLOR_BG)  # Etykieta na obraz
            img_label.grid(row=0, column=0, sticky="ew")  # Umieszczenie etykiety w ramce
            title_label = ttk.Label(cell_frame, text=result['title'], anchor="center", wraplength=150, background=COLOR_BG)  # Etykieta na tytuł
            title_label.grid(row=1, column=0, sticky="ew", pady=(5,0))  # Umieszczenie etykiety w ramce

            # Pobranie i wyświetlenie miniatury obrazu
            photo_thumbnail = fetch_and_process_image(result['url'], size=(150, 150))  # Pobranie miniatury obrazu
            if photo_thumbnail:  # Jeśli miniatura została poprawnie pobrana
                img_label.configure(image=photo_thumbnail, text="")  # Wyświetlenie miniatury w etykiecie
                img_label.image = photo_thumbnail  # Zachowanie referencji do miniatury
                current_url = result['url']  # Zapamiętanie URL obrazu
                current_title = result['title']  # Zapamiętanie tytułu obrazu
                # Dodanie obsługi kliknięcia na miniaturę (otwarcie powiększonego obrazu)
                img_label.bind("<Button-1>", lambda event, url=current_url, title=current_title: open_image_window(url, title))
                img_label.configure(cursor="hand2")  # Zmiana kursora na "rączkę" po najechaniu na miniaturę
            else:  # Jeśli nie udało się pobrać miniatury
                img_label.configure(text="Błąd obrazka")  # Wyświetlenie komunikatu o błędzie
            
            

        log_message("Wyświetlanie wyników zakończone.")  # Logowanie zakończenia wyświetlania wyników
        # Konfiguracja kolumn w ramce wyników
        for c in range(3): output_frame.columnconfigure(c, weight=1)
        # Konfiguracja wierszy w ramce wyników
        num_rows_needed = (len(results_to_display) + 2) // 3
        for r in range(1, num_rows_needed + 1): output_frame.rowconfigure(r, weight=1)

    except Exception as error:  # Obsługa wszystkich wyjątków
        log_message(f"Błąd podczas wyszukiwania lub przetwarzania: {error}")  # Logowanie informacji o błędzie
        ttk.Label(output_frame, text=f"Wystąpił błąd:\n{error}").grid(row=1, column=0, columnspan=3, pady=10)  # Wyświetlenie komunikatu o błędzie


# Funkcja do pobierania i przetwarzania obrazów
def fetch_and_process_image(url, size=None):
    try:  # Rozpoczęcie bloku obsługi wyjątków
        response = requests.get(url, stream=True, timeout=15)  # Pobranie obrazu z podanego URL
        response.raise_for_status()  # Rzucenie wyjątku jeśli wystąpił błąd HTTP
        image_data = response.content  # Pobranie danych obrazu
        if not image_data: log_message(f"Puste dane obrazka z {url}"); return None  # Sprawdzenie czy dane nie są puste
        img = Image.open(io.BytesIO(image_data))  # Konwersja danych binarnych na obiekt Image
        if img.mode not in ("RGB", "L"): img = img.convert("RGB")  # Konwersja do RGB jeśli potrzebna
        if size:  # Jeśli podano rozmiar
            img.thumbnail(size)  # Zmiana rozmiaru z zachowaniem proporcji
        return ImageTk.PhotoImage(img)  # Konwersja na format obsługiwany przez tkinter
    except requests.exceptions.Timeout: log_message(f"Timeout: {url}")  # Obsługa błędu przekroczenia czasu
    except requests.exceptions.RequestException as e: log_message(f"Błąd sieci: {url}: {e}")  # Obsługa błędu zapytania HTTP
    except Exception as e: log_message(f"Błąd przetwarzania obrazka {url}: {e}")  # Obsługa innych błędów
    return None  # Zwrócenie None w przypadku błędu


# Funkcja do dodawania wiadomości do widgetu logów
def append_log_message(widget, text):
    if widget.winfo_exists():  # Sprawdzenie czy widget istnieje
        try:  # Rozpoczęcie bloku obsługi wyjątków
            widget.configure(state=tk.NORMAL)  # Odblokowanie widgetu do edycji
            widget.insert(tk.END, str(text) + "\n")  # Dodanie tekstu na końcu
            widget.see(tk.END)  # Przewinięcie do końca
            widget.configure(state=tk.DISABLED)  # Zablokowanie widgetu przed edycją
        except tk.TclError as e:  # Obsługa błędów Tkinter
            print(f"Błąd Tkinter log: {e}")  # Wypisanie błędu do konsoli
            print(f"LOG (awaryjny): {text}")  # Awaryjne logowanie do konsoli
    else: print(f"LOG (widget nie istnieje): {text}")  # Awaryjne logowanie do konsoli


# Funkcja do logowania wiadomości
def log_message(text):
    # Sprawdzenie czy widget logów istnieje i jest poprawnego typu
    if 'text_log_widget' in globals() and isinstance(text_log_widget, tk.Text) and text_log_widget.winfo_exists():
         append_log_message(text_log_widget, text)  # Dodanie wiadomości do widgetu logów
    else: print(f"LOG: {text}")  # Awaryjne logowanie do konsoli


# Utworzenie głównego okna aplikacji
root = tk.Tk()  # Inicjalizacja głównego okna
root.title("NASA images")  # Ustawienie tytułu okna
root.configure(bg=COLOR_BG)  # Ustawienie koloru tła


# Konfiguracja stylów widgetów
style = ttk.Style(root)  # Inicjalizacja obiektu stylu
style.theme_use('clam')  # Ustawienie motywu


# Styl ramki dla obrazków
style.configure('ImageCard.TFrame', background=COLOR_BG, relief=tk.SOLID, borderwidth=1, bordercolor=COLOR_FG)  # Konfiguracja stylu ramki obrazka


# Konfiguracja stylów dla różnych typów widgetów
style.configure('.', background=COLOR_BG, foreground=COLOR_FG, bordercolor=COLOR_FG_DIM)  # Konfiguracja domyślnego stylu
style.configure('TFrame', background=COLOR_BG)  # Konfiguracja stylu ramki
style.configure('TLabel', background=COLOR_BG, foreground=COLOR_FG, padding=2)  # Konfiguracja stylu etykiety
style.configure('TButton', background=COLOR_BUTTON_BG, foreground=COLOR_FG, padding=5, borderwidth=1, relief=tk.RAISED, bordercolor=COLOR_FG_DIM)  # Konfiguracja stylu przycisku
style.map('TButton', background=[('active', COLOR_BUTTON_ACTIVE)])  # Konfiguracja stylu aktywnego przycisku
style.configure('TEntry', fieldbackground=COLOR_ENTRY_BG, foreground=COLOR_FG, insertcolor=COLOR_CURSOR, bordercolor=COLOR_FG_DIM, borderwidth=1)  # Konfiguracja stylu pola wprowadzania
style.configure('Vertical.TScrollbar', background=COLOR_SCROLL_BG, troughcolor=COLOR_SCROLL_TROUGH, bordercolor=COLOR_BG, arrowcolor=COLOR_FG)  # Konfiguracja stylu paska przewijania
style.map('Vertical.TScrollbar', background=[('active', COLOR_BUTTON_ACTIVE)])  # Konfiguracja stylu aktywnego paska przewijania


# Konfiguracja siatki głównego okna
root.rowconfigure(0, weight=0)  # Wiersz na panel wejściowy (stała wysokość)
root.rowconfigure(1, weight=1)  # Wiersz na panel wyników i logów (rozciągliwy)
root.columnconfigure(0, weight=1)  # Kolumna na panel wyników (rozciągliwa)
root.columnconfigure(1, weight=2, minsize=300)  # Kolumna środkowa (nieużywana)
root.columnconfigure(2, weight=1, minsize=300)  # Kolumna na panel logów (rozciągliwa)


# Utworzenie panelu wejściowego
input_frame = ttk.Frame(master=root)  # Inicjalizacja ramki panelu wejściowego
input_frame.grid(row=0, column=0, columnspan=3, sticky="new", padx=10, pady=10)  # Umieszczenie ramki w siatce
# Konfiguracja kolumn panelu wejściowego
input_frame.columnconfigure(0, weight=1); input_frame.columnconfigure(1, weight=0)
input_frame.columnconfigure(2, weight=0); input_frame.columnconfigure(3, weight=0)
input_frame.columnconfigure(4, weight=1)
# Etykieta "Podaj zapytanie:"
text_zap = ttk.Label(input_frame, text="Podaj zapytanie:")  # Inicjalizacja etykiety
text_zap.grid(row=0, column=1, padx=5, pady=5, sticky='e')  # Umieszczenie etykiety w siatce
# Pole wprowadzania tekstu
entry = ttk.Entry(input_frame, width=30)  # Inicjalizacja pola wprowadzania
entry.grid(row=0, column=2, padx=5, pady=5, sticky='ew')  # Umieszczenie pola w siatce
# Przycisk "Szukaj"
button = ttk.Button(input_frame, text="Szukaj", command=search_nasa)  # Inicjalizacja przycisku
button.grid(row=0, column=3, padx=5, pady=5, sticky='w')  # Umieszczenie przycisku w siatce


# Utworzenie panelu wyników
output_frame = ttk.Frame(master = root)  # Inicjalizacja ramki panelu wyników
output_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 0), pady=(0, 10))  # Umieszczenie ramki w siatce
# Etykieta "Wyniki:"
text_output = ttk.Label(output_frame, text="Wyniki:")  # Inicjalizacja etykiety
text_output.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="nw")  # Umieszczenie etykiety w siatce


# Utworzenie panelu logów
log_frame = ttk.Frame(master = root)  # Inicjalizacja ramki panelu logów
log_frame.grid(row=1, column=2, sticky="nsew", padx=(0, 10), pady=(0, 10))  # Umieszczenie ramki w siatce
# Konfiguracja wierszy i kolumn panelu logów
log_frame.rowconfigure(0, weight=0); log_frame.rowconfigure(1, weight=1)
log_frame.columnconfigure(0, weight=1); log_frame.columnconfigure(1, weight=0)
# Etykieta "Logi:"
text_log_label = ttk.Label(log_frame, text="Logi:")  # Inicjalizacja etykiety
text_log_label.grid(row=0, column=0, padx=5, pady=5, sticky="nw")  # Umieszczenie etykiety w siatce

# Widget tekstowy do wyświetlania logów
text_log_widget = tk.Text(log_frame, width=30, height=10, wrap=tk.WORD,
    bg=COLOR_ENTRY_BG, fg=COLOR_FG,
    insertbackground=COLOR_CURSOR, borderwidth=1, 
    relief=tk.SOLID, highlightthickness=1,
    highlightcolor=COLOR_FG_DIM, highlightbackground=COLOR_BG)  # Inicjalizacja widgetu tekstowego

text_log_widget.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")  # Umieszczenie widgetu w siatce
# Pasek przewijania dla logów
log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=text_log_widget.yview, style='Vertical.TScrollbar')  # Inicjalizacja paska przewijania
log_scrollbar.grid(row=1, column=1, sticky="ns", pady=(5,5), padx=(0,5))  # Umieszczenie paska w siatce
# Powiązanie paska przewijania z widgetem tekstowym
text_log_widget['yscrollcommand'] = log_scrollbar.set  # Konfiguracja przewijania


# Inicjalizacja obiektu do pobierania danych z API NASA
fetcher = NasaImageFetcher()  # Utworzenie obiektu klasy NasaImageFetcher
log_message("Aplikacja gotowa.")  # Logowanie informacji o gotowości aplikacji


# Uruchomienie głównej pętli aplikacji
root.mainloop()  # Uruchomienie głównej pętli zdarzeń Tkinter
