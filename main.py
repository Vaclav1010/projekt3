"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie

author: Václav Jaroš
email: vaclav.jaros93@gmail.com
"""
import csv
import sys
import requests
from bs4 import BeautifulSoup
import logging


# Nastavení loggingu
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Logy do konzole
    ]
)

registered_voters = []
envelopes_issued = []
valid_votes = []


def fetch_html(url, is_main_url = False):
    """Stáhne HTML z URL a vrátí objekt BeautifulSoup."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Zkontroluje, zda nenastala chyba při požadavku
        html_content = BeautifulSoup(response.text, "html.parser")
        if is_main_url:
            logging.info(f"Stahuji data z vybrané URL: {url}")
        else:
            logging.debug(f"Stahuji data z URL: {url}")
        return html_content
    except requests.RequestException as e:
        logging.error(f"Chyba při stahování URL {url}: {e}")
        sys.exit(1)


if len(sys.argv) == 3:
    logging.info(f"Program spuštěn s argumenty: {sys.argv}")
    main_html = fetch_html(sys.argv[1], is_main_url=True)  # Uložení HTML pro další zpracování
else:
    logging.error(
        "Nesprávný počet argumentů. Musí být 3: název souboru, URL adresa a název CSV."
    )
    sys.exit(1)


def extract_town_names():
    """Vrací seznam názvů měst v daném okrese."""
    town_names = []
    town_elements = main_html.find_all("td", "overflow_name")
    for element in town_elements:
        town_names.append(element.text)
    return town_names


def extract_town_links():
    """Vrací seznam URL adres jednotlivých obcí."""
    links = []
    link_elements = main_html.find_all("td", "cislo")
    for element in link_elements:
        href = element.a["href"]
        links.append(f"https://volby.cz/pls/ps2017nss/{href}")
    return links


def extract_town_ids():
    """Vrací seznam identifikačních čísel jednotlivých obcí."""
    town_ids = []
    id_elements = main_html.find_all("td", "cislo")
    for element in id_elements:
        town_ids.append(element.text)
    return town_ids


def extract_party_names():
    """Vrací seznam názvů kandidujících stran."""
    party_names = []
    town_links = extract_town_links()
    sample_html = requests.get(town_links[0])
    parsed_html = BeautifulSoup(sample_html.text, "html.parser")
    party_elements = parsed_html.find_all("td", "overflow_name")
    for element in party_elements:
        party_names.append(element.text)
    return party_names


def collect_voting_data():
    """Načítá data o voličích a hlasování pro každou obec."""
    town_links = extract_town_links()
    for index, link in enumerate(town_links):
        # Logování každé dvě sekundy
        if index % 50 == 0:  # Každých 5 iterací
            logging.info(f"Stahuji data...")

        parsed_html = fetch_html(link)

        # Registrovaní voliči
        voters_elements = parsed_html.find_all("td", headers="sa2")
        for element in voters_elements:
            registered_voters.append(element.text.replace("\xa0", " "))

        # Vydané obálky
        attendance_elements = parsed_html.find_all("td", headers="sa3")
        for element in attendance_elements:
            envelopes_issued.append(element.text.replace("\xa0", " "))

        # Platné hlasy
        valid_elements = parsed_html.find_all("td", headers="sa6")
        for element in valid_elements:
            valid_votes.append(element.text.replace("\xa0", " "))

def extract_votes():
    """Vrací seznam hlasů pro každou stranu v jednotlivých obcích."""
    town_links = extract_town_links()
    vote_data = []
    for link in town_links:
        html_content = fetch_html(link)
        vote_elements = html_content.find_all("td", headers=["t1sb4", "t2sb4"])
        votes = [element.text + " %" for element in vote_elements]
        vote_data.append(votes)
    return vote_data


def prepare_csv_rows():
    """Vytváří seznam řádků pro CSV obsahující data o obcích a výsledcích stran."""
    rows = []
    collect_voting_data()
    town_names = extract_town_names()
    town_ids = extract_town_ids()
    vote_results = extract_votes()
    combined_data = zip(
        town_ids, town_names, registered_voters, envelopes_issued, valid_votes
    )

    for base_data, votes in zip(combined_data, vote_results):
        rows.append(list(base_data) + votes)
    logging.info("CSV řádky připraveny.")
    return rows


def save_election_results_to_csv(url, output_file):
    """Hlavní funkce pro stažení dat a uložení výsledků voleb do CSV souboru."""
    try:
        header = [
            "Kód obce",
            "Název obce",
            "Registrovaní voliči",
            "Vydané obálky",
            "Platné hlasy",
        ]
        content = prepare_csv_rows()
        parties = extract_party_names()
        logging.info(f"Ukládám data do souboru: {output_filename}")
        header.extend(parties)

        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            writer.writerows(content)
        logging.info("Data úspěšně uložena. Ukončuji program")

    except IndexError:
        logging.error("Chyba: Zkontrolujte, zda je odkaz správně zadaný a v uvozovkách.")
        sys.exit(1)


if __name__ == "__main__":
    input_url = sys.argv[1]
    output_filename = sys.argv[2]
    save_election_results_to_csv(input_url, output_filename)
