import requests

class NasaImageFetcher:

    def __init__(self):
        self.base_url = "https://images-api.nasa.gov/search"


    def fetch_data(self, query):
        params_query = {
            'q': query # Parametr zapytania
        }
        response = requests.get(self.base_url, params=params_query)

        if response.status_code == 200:
            print("\nPobrano dane pomyślnie.")
            return response.json()
        else:
            raise Exception(f'Nie udało się, kod statusu: {response.status_code}')


    def display_results(self, data, limit=9):
        if not data:
             print("Brak danych")
             return

        items = data.get("collection", {}).get("items", [])

        if not items:
            print("Brak wyników")
            return

        print(f"\nZnaleziono {len(items)} wyników. Wyswietlono {limit} z nich:\n")
        print("")


        results_list = [] # Lista na wyniki jako stringi
        results_list.append(f"Znaleziono {len(items)} wyników. Wyświetlanie max {limit}:\n")

        for item in items[:limit]:
            item_data = item.get("data", [])
            links = item.get("links", [])

            title = "Brak tytułu"
            if item_data and isinstance(item_data, list) and len(item_data) > 0:
                title = item_data[0].get("title", "Brak tytułu")

            href = "Brak linku do obrazu"
            if links and isinstance(links, list) and len(links) > 0:
                 href = links[0].get("href", "Brak linku")

            results_list.append("-" * 40)
            results_list.append(f"Tytuł: {title}")
            results_list.append(f"Link : {href}")
            results_list.append("-" * 40)
            results_list.append("") # Dodatkowy odstęp

        return "\n".join(results_list) # Zwraca jeden długi string

    def run(self):
        query = input("Podaj zapytanie: ")
        try:
            data = self.fetch_data(query)
            self.display_results(data)
        except Exception as error:
            print(f"Błąd: {error}")

if __name__ == "__main__":
    fetcher = NasaImageFetcher() # Tworzymy obiekt
    fetcher.run() # Wywołujemy metodę