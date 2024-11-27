


# Elections Scraper
Tento projekt scrappuje výsledky voleb z roku 2017 pro vybraný územní celek.

# Nainstaluj knihovny 
Použité knihovny třetích stran jsou uloženy v souboru requirements.txt

Doporučuji použít virtuální prostředí a v terminálu napsat:

pip install -r requirements.txt

# Spuštění
Spuštění souboru v příkazové řádce požaduje dva argumenty.

V příkazové řádce zadej: python main.py <URL územního celku> <výstupní soubor.csv>

Následně bude výsledek uložen do souboru s příponou .csv.

# Příklad
 python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101" "volby2017.csv"

 # Ukázka projektu
 Výsledky hlasování pro okres Benešov:
 
 1. argument : https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101
    
 2. argument: volby2017.csv
    
Spouštění programu:  python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101" "volby2017.csv"

![image](https://github.com/user-attachments/assets/bb09df68-ca47-47c4-a800-25e1be646cc5)

# Částečný výstup 

![image](https://github.com/user-attachments/assets/24c25f8c-eb64-415e-ac5c-8b05b5c97a27)




