"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie

author: Václav Jaroš
email: vaclav.jaros93@gmail.com
"""

import sys
import requests
import bs4
import csv

registered_voters = []
envelopes_issued = []
valid_votes = []


def fetch_html(url):
    """Stáhne HTML z URL a vrátí objekt BeautifulSoup."""
    response = requests.get(url)
    html_content = bs4.BeautifulSoup(response.text, "html.parser")
    print("STAHUJI DATA Z URL:", url)
    return html_content


if len(sys.argv) == 3:
    main_html = fetch_html(sys.argv[1])  # Uložení HTML pro další zpracování
else:
    print(
        "Zadal jsi nesprávný počet argumentů. Argumenty musí být 3: "
        "název souboru, URL adresa v uvozovkách a název výstupního CSV."
    )
    quit()


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
    parsed_html = bs4.BeautifulSoup(sample_html.text, "html.parser")
    party_elements = parsed_html.find_all("td", "overflow_name")
    for element in party_elements:
        party_names.append(element.text)
    return party_names


def collect_voting_data():
    """Načítá data o voličích a hlasování pro každou obec."""
    town_links = extract_town_links()
    for link in town_links:
        html_content = requests.get(link)
        parsed_html = bs4.BeautifulSoup(html_content.text, "html.parser")

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
        print("UKLÁDÁM DATA DO SOUBORU:", output_file)
        header.extend(parties)

        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            writer.writerows(content)
        print("UKONČUJI PROGRAM.")
    except IndexError:
        print("Chyba: Zkontrolujte, zda je odkaz správně zadaný a v uvozovkách.")
        quit()


if __name__ == "__main__":
    input_url = sys.argv[1]
    output_filename = sys.argv[2]
    save_election_results_to_csv(input_url, output_filename)
