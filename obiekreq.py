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


    def display_results(self, data, limit=5):
        if not data:
             print("Brak danych")
             return

        items = data.get("collection", {}).get("items", [])

        if not items:
            print("Brak wyników")
            return

        print(f"\nZnaleziono {len(items)} wyników. Wyswietlono {limit} z nich:\n")
        print("")

        for item in items[:limit]:  # limit wyników
            item_data = item.get("data", [])
            links = item.get("links", [])

            # Sprawdzamy czy lista nie jest pusta
            title = "Brak tytułu"
            if item_data and isinstance(item_data, list) and len(item_data) > 0:
                title = item_data[0].get("title", "Brak tytułu")

            # Sprawdzamy, czy lista nie jest pusta
            href = "Brak linku"
            if links and isinstance(links, list) and len(links) > 0:
                href = links[0].get("href", "Brak linku")

            print(f"\nTytuł: {title}")
            print(f"Link : {href}\n")
            print("/" * 40)

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