import tkinter as tk  # Importuje główny moduł do tworzenia GUI w Pythonie
from tkinter import ttk  # Importuje rozszerzenie do tkintera z nowoczesnymi widgetami
from PIL import Image, ImageTk  # Importuje klasy do obsługi i wyświetlania obrazów
import requests  # Importuje bibliotekę do wykonywania zapytań HTTP
import io  # Importuje moduł do operacji na strumieniach (np. konwersja bajtów na obraz)
from obiekreq import NasaImageFetcher  # Importuje własną klasę do pobierania danych z NASA API

# --- Panel logów ---
class NasaLogPanel(ttk.Frame):  # Definiuje klasę panelu logów, dziedziczącą po ramce ttk
    def __init__(self, master, color_bg, color_fg):  # Konstruktor klasy
        super().__init__(master)  # Wywołuje konstruktor klasy bazowej
        # Tworzy etykietę "Logi:" z odpowiednimi kolorami
        self.label = ttk.Label(self, text="Logi:", background=color_bg, foreground=color_fg)
        self.label.grid(row=0, column=0, sticky="nw", padx=5, pady=5)  # Ustawia etykietę w siatce
        # Tworzy pole tekstowe do wyświetlania logów, wyłączone do edycji
        self.text = tk.Text(self, width=30, height=10, wrap=tk.WORD, state=tk.DISABLED,
                            bg=color_bg, fg=color_fg, insertbackground=color_fg, relief=tk.SOLID)
        self.text.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)  # Ustawia pole tekstowe w siatce
        # Dodaje pionowy pasek przewijania do pola tekstowego
        self.scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.text.yview)
        self.scroll.grid(row=1, column=1, sticky="ns", pady=5)  # Ustawia pasek przewijania w siatce
        self.text['yscrollcommand'] = self.scroll.set  # Łączy przewijanie paska z polem tekstowym
        self.rowconfigure(1, weight=1)  # Pozwala wierszowi 1 rozciągać się przy zmianie rozmiaru panelu
        self.columnconfigure(0, weight=1)  # Pozwala kolumnie 0 rozciągać się przy zmianie rozmiaru panelu

    def log(self, msg):  # Metoda do dodawania wiadomości do logów
        self.text.configure(state=tk.NORMAL)  # Odblokowuje pole tekstowe do edycji
        self.text.insert(tk.END, str(msg) + "\n")  # Dodaje wiadomość na końcu tekstu
        self.text.see(tk.END)  # Przewija do najnowszego wpisu
        self.text.configure(state=tk.DISABLED)  # Ponownie blokuje pole tekstowe

# --- Panel wyników ---
class NasaResultsPanel(ttk.Frame):  # Definiuje klasę panelu wyników
    def __init__(self, master, log_panel, image_fetcher, color_bg, color_fg, **kwargs):
        super().__init__(master, **kwargs)  # Wywołuje konstruktor klasy bazowej
        self.log_panel = log_panel  # Przechowuje referencję do panelu logów
        self.image_fetcher = image_fetcher  # Przechowuje referencję do fetchera obrazów
        self.color_bg = color_bg  # Przechowuje kolor tła
        self.color_fg = color_fg  # Przechowuje kolor tekstu
        # Tworzy etykietę "Wyniki:" na górze panelu
        self.label = ttk.Label(self, text="Wyniki:", background=color_bg, foreground=color_fg)
        self.label.grid(row=0, column=0, columnspan=3, sticky="nw", padx=5, pady=5)
        self.images = []  # Lista do przechowywania referencji do obrazków (by nie zostały usunięte przez GC)

    def clear(self):  # Metoda do czyszczenia panelu wyników
        for widget in self.winfo_children():  # Iteruje po wszystkich widgetach w panelu
            if widget != self.label:  # Pomija etykietę "Wyniki:"
                widget.destroy()  # Usuwa widget
        self.images.clear()  # Czyści listę obrazków

    def show_results(self, items):  # Metoda do wyświetlania wyników (obrazków)
        self.clear()  # Czyści panel przed wyświetleniem nowych wyników
        if not items:  # Jeśli lista wyników jest pusta
            # Wyświetla komunikat o braku wyników
            ttk.Label(self, text="Brak wyników.", background=self.color_bg, foreground=self.color_fg).grid(row=1, column=0, columnspan=3, pady=10)
            return  # Kończy działanie metody

        for i, result in enumerate(items):  # Iteruje po wynikach
            row = (i // 3) + 1  # Oblicza numer wiersza (3 kolumny na wiersz)
            col = i % 3  # Oblicza numer kolumny
            # Tworzy ramkę na pojedynczy wynik (obrazek + tytuł)
            frame = ttk.Frame(self, padding=5, style='ImageCard.TFrame')
            frame.grid(row=row, column=col, padx=5, pady=5, sticky="n")
            # Tworzy etykietę na miniaturę obrazka
            img_label = ttk.Label(frame, text="Ładowanie...", anchor='center', background=self.color_bg, foreground=self.color_fg)
            img_label.grid(row=0, column=0, sticky="ew")
            # Tworzy etykietę na tytuł obrazka
            title_label = ttk.Label(frame, text=result['title'], anchor="center", wraplength=150, background=self.color_bg, foreground=self.color_fg)
            title_label.grid(row=1, column=0, sticky="ew", pady=(5,0))

            # Pobiera miniaturę obrazka (150x150)
            photo = self.image_fetcher.fetch_image(result['url'], size=(150,150))
            if photo:  # Jeśli udało się pobrać obraz
                img_label.configure(image=photo, text="")  # Ustawia obrazek w etykiecie
                img_label.image = photo  # Przechowuje referencję do obrazka
                self.images.append(photo)  # Dodaje obrazek do listy, by nie został usunięty
                # Dodaje obsługę kliknięcia na miniaturę (otwiera powiększony obrazek)
                img_label.bind("<Button-1>", lambda e, url=result['url'], title=result['title']: self.show_full_image(url, title))
                img_label.configure(cursor="hand2")  # Ustawia kursor na "rączkę"
            else:  # Jeśli nie udało się pobrać obrazka
                img_label.configure(text="Błąd obrazka")  # Wyświetla komunikat o błędzie

    def show_full_image(self, url, title):  # Metoda do wyświetlania powiększonego obrazka w nowym oknie
        self.log_panel.log(f"Otwieranie okna dla: {title}")  # Loguje otwarcie nowego okna
        win = tk.Toplevel(self)  # Tworzy nowe okno podrzędne
        win.title(title)  # Ustawia tytuł okna
        win.geometry("600x450")  # Ustawia rozmiar okna
        win.configure(bg=self.color_bg)  # Ustawia kolor tła
        # Tworzy etykietę informującą o pobieraniu obrazka
        label = ttk.Label(win, text="Pobieranie obrazka...", anchor='center', background=self.color_bg, foreground=self.color_fg)
        label.pack(fill=tk.BOTH, expand=True)  # Umieszcza etykietę w oknie
        # Pobiera pełny obrazek (bez zmiany rozmiaru)
        photo = self.image_fetcher.fetch_image(url, size=None)
        if photo:  # Jeśli udało się pobrać obrazek
            label.configure(image=photo, text="")  # Wyświetla obrazek
            label.image = photo  # Przechowuje referencję do obrazka
        else:  # Jeśli nie udało się pobrać obrazka
            label.configure(text="Nie udało się załadować obrazka.", foreground="red")  # Wyświetla komunikat o błędzie

# --- Panel wyszukiwania ---
class NasaSearchPanel(ttk.Frame):  # Definiuje klasę panelu wyszukiwania
    def __init__(self, master, on_search, color_bg, color_fg, **kwargs):
        super().__init__(master, **kwargs)  # Wywołuje konstruktor klasy bazowej
        # Tworzy etykietę "Podaj zapytanie:"
        ttk.Label(self, text="Podaj zapytanie:", background=color_bg, foreground=color_fg).grid(row=0, column=0, padx=5, pady=5, sticky='e')
        # Tworzy pole do wpisywania zapytania
        self.entry = ttk.Entry(self, width=30)
        self.entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        # Tworzy przycisk "Szukaj"
        self.button = ttk.Button(self, text="Szukaj", command=self._search)
        self.button.grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.on_search = on_search  # Przechowuje referencję do funkcji obsługującej wyszukiwanie
        self.columnconfigure(1, weight=1)  # Pozwala kolumnie z polem Entry rozciągać się przy zmianie rozmiaru

    def _search(self):  # Metoda wywoływana po kliknięciu przycisku "Szukaj"
        query = self.entry.get()  # Pobiera tekst z pola Entry
        self.on_search(query)  # Wywołuje funkcję wyszukiwania z podanym zapytaniem

# --- Fetcher obrazków (adapter do NasaImageFetcher) ---
class ImageFetcher:  # Klasa pomocnicza do pobierania danych i obrazków
    def __init__(self):
        self.fetcher = NasaImageFetcher()  # Tworzy instancję klasy do pobierania danych z NASA API

    def fetch_data(self, query):  # Metoda do pobierania danych (JSON) z NASA API
        return self.fetcher.fetch_data(query)  # Wywołuje metodę z klasy NasaImageFetcher

    def fetch_image(self, url, size=None):  # Metoda do pobierania obrazka z podanego URL
        try:
            response = requests.get(url, stream=True, timeout=15)  # Wysyła żądanie HTTP GET do podanego URL
            response.raise_for_status()  # Sprawdza, czy odpowiedź jest poprawna (nie ma błędu HTTP)
            img = Image.open(io.BytesIO(response.content))  # Wczytuje obrazek z pobranych bajtów
            if img.mode not in ("RGB", "L"):  # Jeśli obrazek nie jest w trybie RGB lub L (czarno-białym)
                img = img.convert("RGB")  # Konwertuje obrazek do trybu RGB
            if size:  # Jeśli podano rozmiar miniatury
                img.thumbnail(size)  # Tworzy miniaturę obrazka
            return ImageTk.PhotoImage(img)  # Zwraca obrazek w formacie zgodnym z tkinterem
        except Exception as e:  # Obsługuje wszelkie błędy
            print(f"Błąd pobierania obrazka: {e}")  # Wypisuje błąd na konsolę
            return None  # Zwraca None w przypadku błędu

# --- Główna aplikacja ---
class NasaImageApp:  # Definiuje główną klasę aplikacji
    # Kolory jako stałe klasowe
    COLOR_BG = '#000000'  # Kolor tła
    COLOR_FG = '#00FF00'  # Kolor tekstu
    COLOR_FG_DIM = '#008F00'  # Przyciemniony zielony
    COLOR_ENTRY_BG = '#000000'  # Tło pola Entry
    COLOR_CURSOR = '#00FF00'  # Kolor kursora
    COLOR_BUTTON_BG = '#1A1A1A'  # Tło przycisków
    COLOR_BUTTON_ACTIVE = '#333333'  # Aktywny przycisk
    COLOR_SCROLL_TROUGH = '#000000'  # Tło paska przewijania
    COLOR_SCROLL_BG = '#1A1A1A'  # Tło suwaka przewijania

    def __init__(self, root):  # Konstruktor głównej klasy aplikacji
        self.root = root  # Przechowuje referencję do głównego okna
        self.root.title("NASA images")  # Ustawia tytuł okna
        self.root.configure(bg=self.COLOR_BG)  # Ustawia kolor tła okna
        self.setup_styles()  # Wywołuje metodę konfigurującą style widgetów

        self.image_fetcher = ImageFetcher()  # Tworzy instancję fetchera obrazków

        # Tworzy panel logów i umieszcza go w siatce
        self.log_panel = NasaLogPanel(root, self.COLOR_BG, self.COLOR_FG)
        self.log_panel.grid(row=1, column=2, sticky="nse", padx=(0,10), pady=(0,10))
        # Tworzy panel wyników i umieszcza go w siatce
        self.results_panel = NasaResultsPanel(root, self.log_panel, self.image_fetcher, self.COLOR_BG, self.COLOR_FG)
        self.results_panel.grid(row=1, column=0, sticky="nsew", padx=(10,0), pady=(0,10))
        # Tworzy panel wyszukiwania i umieszcza go w siatce
        self.search_panel = NasaSearchPanel(root, self.on_search, self.COLOR_BG, self.COLOR_FG)
        self.search_panel.grid(row=0, column=0, columnspan=3, sticky="n", padx=10, pady=10)

        # Konfiguruje siatkę głównego okna (rozciągliwość wierszy i kolumn)
        root.rowconfigure(0, weight=0)  # Wiersz 0 (panel wyszukiwania) nie rozciąga się
        root.rowconfigure(1, weight=1)  # Wiersz 1 (panele wyników i logów) rozciąga się
        root.columnconfigure(0, weight=1)  # Kolumna 0 (panel wyników) rozciąga się
        root.columnconfigure(2, weight=1, minsize=300)  # Kolumna 2 (panel logów) rozciąga się i ma minimalną szerokość

        self.log_panel.log("Aplikacja gotowa.")  # Loguje gotowość aplikacji

    def on_search(self, query):  # Metoda wywoływana po kliknięciu "Szukaj"
        if not query:  # Jeśli pole wyszukiwania jest puste
            self.log_panel.log("Proszę podać zapytanie.")  # Loguje prośbę o wpisanie zapytania
            return  # Kończy działanie metody
        self.log_panel.log(f"Rozpoczynam wyszukiwanie dla: {query}")  # Loguje rozpoczęcie wyszukiwania
        self.results_panel.clear()  # Czyści panel wyników
        try:
            data = self.image_fetcher.fetch_data(query)  # Pobiera dane z NASA API
            items = data.get("collection", {}).get("items", [])  # Pobiera listę wyników z odpowiedzi
            results = []  # Tworzy pustą listę na przetworzone wyniki
            for item in items[:9]:  # Przetwarza maksymalnie 9 wyników
                title = item.get("data", [{}])[0].get("title", "Brak tytułu")  # Pobiera tytuł obrazka
                links = item.get("links", [])  # Pobiera listę linków
                # Szuka linku do podglądu obrazka
                href = next((l.get('href') for l in links if l.get('rel') == 'preview'), None)
                if href:  # Jeśli link istnieje
                    results.append({'title': title, 'url': href})  # Dodaje wynik do listy
            self.results_panel.show_results(results)  # Wyświetla wyniki w panelu
            self.log_panel.log(f"Wyświetlono {len(results)} wyników.")  # Loguje liczbę wyświetlonych wyników
        except Exception as e:  # Obsługuje błędy
            self.log_panel.log(f"Błąd podczas wyszukiwania: {e}")  # Loguje błąd

    def setup_styles(self):  # Metoda konfigurująca style widgetów
        style = ttk.Style(self.root)  # Tworzy obiekt stylu
        style.theme_use('clam')  # Ustawia motyw "clam"
        # Konfiguruje styl ramki na obrazki
        style.configure('ImageCard.TFrame', background=self.COLOR_BG, relief=tk.SOLID, borderwidth=1, bordercolor=self.COLOR_FG)
        # Konfiguruje domyślny styl
        style.configure('.', background=self.COLOR_BG, foreground=self.COLOR_FG, bordercolor=self.COLOR_FG_DIM)
        # Konfiguruje styl ramek
        style.configure('TFrame', background=self.COLOR_BG)
        # Konfiguruje styl etykiet
        style.configure('TLabel', background=self.COLOR_BG, foreground=self.COLOR_FG, padding=2)
        # Konfiguruje styl przycisków
        style.configure('TButton', background=self.COLOR_BUTTON_BG, foreground=self.COLOR_FG, padding=5, borderwidth=1, relief=tk.RAISED, bordercolor=self.COLOR_FG_DIM)
        # Konfiguruje styl aktywnego przycisku
        style.map('TButton', background=[('active', self.COLOR_BUTTON_ACTIVE)])
        # Konfiguruje styl pola Entry
        style.configure('TEntry', fieldbackground=self.COLOR_ENTRY_BG, foreground=self.COLOR_FG, insertcolor=self.COLOR_CURSOR, bordercolor=self.COLOR_FG_DIM, borderwidth=1)
        # Konfiguruje styl paska przewijania
        style.configure('Vertical.TScrollbar', background=self.COLOR_SCROLL_BG, troughcolor=self.COLOR_SCROLL_TROUGH, bordercolor=self.COLOR_BG, arrowcolor=self.COLOR_FG)
        # Konfiguruje styl aktywnego paska przewijania
        style.map('Vertical.TScrollbar', background=[('active', self.COLOR_BUTTON_ACTIVE)])

# --- Uruchomienie ---
def main():  # Funkcja uruchamiająca aplikację
    root = tk.Tk()  # Tworzy główne okno aplikacji
    app = NasaImageApp(root)  # Tworzy instancję głównej klasy aplikacji
    root.mainloop()  # Uruchamia główną pętlę zdarzeń

if __name__ == '__main__':  # Sprawdza, czy plik jest uruchamiany jako główny program
    main()  # Wywołuje funkcję uruchamiającą aplikację
