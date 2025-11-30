# STRM Bibliotheek Manager

Een grafische (GUI) tool voor Windows, ontworpen om IPTV-afspeellijsten van Xtream Codes providers te downloaden, te organiseren en te exporteren naar een structuur die perfect is voor mediacenters zoals Kodi, Plex of Jellyfin.

De tool scheidt content in Live TV, Films (VOD) en Series, en genereert `.strm`-bestanden en `.nfo`-metadata, waardoor je mediacenter de bibliotheek correct kan scannen en verrijken met covers, omschrijvingen en andere informatie.

## Features

- **Grafische Gebruikersinterface**: Eenvoudig te bedienen interface gebouwd met Tkinter.
- **Provider Beheer**: Voeg meerdere Xtream Codes providers toe en wissel eenvoudig tussen accounts.
- **Veilige Opslag**: Wachtwoorden worden versleuteld opgeslagen met behulp van de Windows Data Protection API (DPAPI).
- **Gescheiden Content**: Duidelijke scheiding tussen Live TV, Films en Series in de interface.
- **Selectieve Export**: Kies per type welke categorieën je wilt exporteren.
- **M3U voor Live TV**: Genereert een `.m3u`-bestand voor live kanalen, inclusief groepen en logo's.
- **STRM voor VOD/Series**: Maakt `.strm`-bestanden aan voor films en series.
- **Automatische NFO-generatie**: Haalt metadata (zoals plot, rating, etc.) op van The Movie Database (TMDB) en maakt `tvshow.nfo` en aflevering `.nfo`-bestanden aan voor series.
- **Logische Mappenstructuur**: Exporteert bestanden in een schone hiërarchie die door mediacenters wordt herkend:
  - **Films**: `[Doelmap]\Categorienaam\Filmnaam (Jaar)\Filmnaam.strm`
  - **Series**: `[Doelmap]\Categorienaam\Serienaam\Season XX\Serienaam - SXXEXX.strm`
- **Configuratieopslag**: Al je providers, selecties en je TMDB API-sleutel worden opgeslagen in een `config.json`-bestand.

## Specificaties & Vereisten

Dit script is ontwikkeld en getest op **Windows**. De functionaliteit voor het versleutelen van wachtwoorden is specifiek voor Windows.

### Python-bibliotheken

De volgende Python-pakketten zijn vereist:

- `requests`: Voor het maken van API-aanroepen naar de Xtream Codes provider en TMDB.
- `pywin32`: Voor het veilig versleutelen en ontsleutelen van wachtwoorden op Windows.

## Installatie

1.  **Zorg dat je Python hebt geïnstalleerd.** Je kunt Python downloaden van python.org.
2.  **Installeer de vereiste bibliotheken.** Open een terminal of command prompt en voer het volgende commando uit:

    ```bash
    pip install requests pywin32
    ```

3.  **Plaats het script.** Zorg ervoor dat `strm_manager.py` in een eigen map staat. Het `config.json`-bestand wordt automatisch in dezelfde map aangemaakt.

## Configuratie & Eerste Gebruik

Voordat je lijsten kunt laden, moet je de applicatie configureren.

1.  **TMDB API Sleutel (Aanbevolen)**
    - Om metadata (.nfo-bestanden) voor series te genereren, heb je een gratis API-sleutel van The Movie Database nodig.
    - Maak een account aan op www.themoviedb.org, ga naar je accountinstellingen en vraag een API-sleutel aan.
    - Kopieer deze sleutel en plak deze in het veld "TMDB API Key" in de applicatie.

2.  **Provider Toevoegen**
    - Klik op de knop **"Beheer Accounts"**.
    - Klik op **"Nieuw"**.
    - Vul de gegevens van je Xtream Codes provider in:
      - **Naam**: Een zelfgekozen naam voor deze provider (bv. "Mijn Provider").
      - **Server**: De server URL, inclusief `http://` en de poort (bv. `http://provider.tv:8080`).
      - **Gebruikersnaam**: Je IPTV-gebruikersnaam.
      - **Wachtwoord**: Je IPTV-wachtwoord.
    - Klik op **"Opslaan"**. Je kunt meerdere providers toevoegen.
    - Klik op **"Sluiten"** om terug te keren naar het hoofdscherm.

## Hoe te Gebruiken

1.  **Selecteer een Provider**: Kies de gewenste provider uit het dropdown-menu.
2.  **Lijst Laden**: Klik op de grote knop **"Lijst Laden (Xtream Codes)"**. De applicatie zal nu alle categorieën en streams ophalen en in de drie kolommen plaatsen. De statusbalk onderaan toont de voortgang.
3.  **Categorieën Selecteren**: Vink in de kolommen "Live TV", "Films" en "Series" de categorieën aan die je wilt exporteren.
4.  **Exporteren**:
    - Klik op **"Exporteer M3U"** onder de Live TV-kolom om een `.m3u`-bestand voor je live kanalen te maken.
    - Klik op **"Maak Films"** onder de Film-kolom om de `.strm`-bestanden voor films te genereren.
    - Klik op **"Maak Series"** onder de Serie-kolom om de `.strm`- en `.nfo`-bestanden voor series te maken.
5.  **Kies een Locatie**: Voor elke exportactie zal een venster verschijnen waarin je de opslaglocatie kunt kiezen.

Je bent nu klaar! De bestanden staan in de door jou gekozen mappen, klaar om te worden toegevoegd aan je mediacenter-bibliotheek.

---

*Dit script is bedoeld voor persoonlijk gebruik om legale en persoonlijk aangeschafte IPTV-abonnementen te beheren.*