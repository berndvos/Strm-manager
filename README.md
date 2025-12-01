# STRM Library Manager

A graphical (GUI) tool for Windows, designed to download, organize, and export IPTV playlists from Xtream Codes providers into a structure that is perfect for media centers like Kodi, Plex, or Jellyfin.

The tool separates content into Live TV, Movies (VOD), and Series, and generates `.strm` files and `.nfo` metadata. This allows your media center to correctly scan and enrich your library with covers, descriptions, and other information.

## Features

- **Graphical User Interface**: Easy-to-use interface built with Tkinter.
- **Multi-language Support**: Switch between English and Dutch directly in the UI.
- **Provider Management**: Add multiple Xtream Codes providers and easily switch between accounts.
- **Secure Storage**: Passwords are securely encrypted using the Windows Data Protection API (DPAPI).
- **Separated Content**: Clear separation between Live TV, Movies, and Series in the interface.
- **Selective Export**: Choose which categories to export for each content type.
- **M3U for Live TV**: Generates an `.m3u` file for live channels, including groups, logos, and EPG data.
- **STRM for VOD/Series**: Creates `.strm` files for movies and series.
- **Automatic NFO Generation**: Fetches metadata (like plot, rating, etc.) from The Movie Database (TMDB) and creates `tvshow.nfo` and episode `.nfo` files for series.
- **Logical Folder Structure**: Exports files in a clean hierarchy recognized by media centers:
  - **Movies**: `[Target Folder]\[Category Name]\[Movie Title (Year)]\[Movie Title].strm`
  - **Series**: `[Target Folder]\[Category Name]\[Series Title]\Season XX\[Series Title] - SXXEXX.strm`
- **Configuration Storage**: All your providers, selections, language preference, and your TMDB API key are saved in a `config.json` file.

## Specifications & Requirements

This script is developed and tested on **Windows**. The password encryption functionality is specific to Windows.

### Python Libraries

The following Python packages are required:

- `requests`: For making API calls to the Xtream Codes provider and TMDB.
- `pywin32`: For securely encrypting and decrypting passwords on Windows.

## Installation

1.  **Ensure you have Python installed.** You can download Python from python.org.
2.  **Install the required libraries.** Open a terminal or command prompt and run the following command:

    ```bash
    pip install requests pywin32
    ```

3.  **Place the script.** Make sure `strm_manager.py` is in its own folder. The `config.json` file will be created automatically in the same folder.

## Configuration & First Use

Before you can load lists, you need to configure the application.

1.  **TMDB API Key (Recommended)**
    - To generate metadata (.nfo files) for series, you need a free API key from The Movie Database.
    - Create an account at www.themoviedb.org, go to your account settings, and request an API key.
    - Copy this key and paste it into the "TMDB API Key" field in the application.

2.  **Add a Provider**
    - Click the **"Manage Accounts"** button.
    - Click **"New"**.
    - Fill in your Xtream Codes provider details:
      - **Name**: A custom name for this provider (e.g., "My Provider").
      - **Server**: The server URL, including `http://` and the port (e.g., `http://provider.tv:8080`).
      - **Username**: Your IPTV username.
      - **Password**: Your IPTV password.
    - Click **"Save"**. You can add multiple providers.
    - Click **"Close"** to return to the main screen.

## How to Use

1.  **Select Language**: Choose your preferred language from the "Language" dropdown menu.
2.  **Select a Provider**: Choose the desired provider from the dropdown menu.
3.  **Load List**: Click the large **"Load List (Xtream Codes)"** button. The application will now fetch all categories and streams and place them in the three columns. The status bar at the bottom shows the progress.
4.  **Select Categories**: In the "Live TV", "Movies", and "Series" columns, check the categories you want to export.
5.  **Export**:
    - Click **"Export M3U"** under the Live TV column to create an `.m3u` file for your live channels.
    - Click **"Create Movies"** under the Movies column to generate the `.strm` files for movies.
    - Click **"Create Series"** under the Series column to create the `.strm` and `.nfo` files for series.
6.  **Choose a Location**: For each export action, a window will appear asking you to choose the save location.

You're all set! The files are now in your chosen folders, ready to be added to your media center library.

---

*This script is intended for personal use to manage legally and personally purchased IPTV subscriptions.*

---

## STRM Bibliotheek Manager (Nederlands)

Een grafische (GUI) tool voor Windows, ontworpen om IPTV-afspeellijsten van Xtream Codes providers te downloaden, te organiseren en te exporteren naar een structuur die perfect is voor mediacenters zoals Kodi, Plex of Jellyfin.

De tool scheidt content in Live TV, Films (VOD) en Series, en genereert `.strm`-bestanden en `.nfo`-metadata, waardoor je mediacenter de bibliotheek correct kan scannen en verrijken met covers, omschrijvingen en andere informatie.

### Features

- **Grafische Gebruikersinterface**: Eenvoudig te bedienen interface gebouwd met Tkinter.
- **Meertalige Ondersteuning**: Schakel direct in de UI tussen Engels en Nederlands.
- **Provider Beheer**: Voeg meerdere Xtream Codes providers toe en wissel eenvoudig tussen accounts.
- **Veilige Opslag**: Wachtwoorden worden versleuteld opgeslagen met behulp van de Windows Data Protection API (DPAPI).
- **Gescheiden Content**: Duidelijke scheiding tussen Live TV, Films en Series in de interface.
- **Selectieve Export**: Kies per type welke categorieën je wilt exporteren.
- **M3U voor Live TV**: Genereert een `.m3u`-bestand voor live kanalen, inclusief groepen, logo's en EPG-data.
- **STRM voor VOD/Series**: Maakt `.strm`-bestanden aan voor films en series.
- **Automatische NFO-generatie**: Haalt metadata (zoals plot, rating, etc.) op van The Movie Database (TMDB) en maakt `tvshow.nfo` en aflevering `.nfo`-bestanden aan voor series.
- **Logische Mappenstructuur**: Exporteert bestanden in een schone hiërarchie die door mediacenters wordt herkend:
  - **Films**: `[Doelmap]\[Categorienaam]\[Filmnaam (Jaar)]\[Filmnaam].strm`
  - **Series**: `[Doelmap]\[Categorienaam]\[Serienaam]\Season XX\[Serienaam] - SXXEXX.strm`
- **Configuratieopslag**: Al je providers, selecties, taalvoorkeur en je TMDB API-sleutel worden opgeslagen in een `config.json`-bestand.

### Specificaties & Vereisten

Dit script is ontwikkeld en getest op **Windows**. De functionaliteit voor het versleutelen van wachtwoorden is specifiek voor Windows.

#### Python-bibliotheken

De volgende Python-pakketten zijn vereist:

- `requests`: Voor het maken van API-aanroepen naar de Xtream Codes provider en TMDB.
- `pywin32`: Voor het veilig versleutelen en ontsleutelen van wachtwoorden op Windows.

### Installatie

1.  **Zorg dat je Python hebt geïnstalleerd.** Je kunt Python downloaden van python.org.
2.  **Installeer de vereiste bibliotheken.** Open een terminal of command prompt en voer het volgende commando uit:

    ```bash
    pip install requests pywin32
    ```

3.  **Plaats het script.** Zorg ervoor dat `strm_manager.py` in een eigen map staat. Het `config.json`-bestand wordt automatisch in dezelfde map aangemaakt.

### Configuratie & Eerste Gebruik

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

### Hoe te Gebruiken

1.  **Selecteer Taal**: Kies je voorkeurstaal uit het "Taal" dropdown-menu.
2.  **Selecteer een Provider**: Kies de gewenste provider uit het dropdown-menu.
3.  **Lijst Laden**: Klik op de grote knop **"Lijst Laden (Xtream Codes)"**. De applicatie zal nu alle categorieën en streams ophalen en in de drie kolommen plaatsen. De statusbalk onderaan toont de voortgang.
4.  **Categorieën Selecteren**: Vink in de kolommen "Live TV", "Films" en "Series" de categorieën aan die je wilt exporteren.
5.  **Exporteren**:
    - Klik op **"Exporteer M3U"** onder de Live TV-kolom om een `.m3u`-bestand voor je live kanalen te maken.
    - Klik op **"Maak Films"** onder de Film-kolom om de `.strm`-bestanden voor films te genereren.
    - Klik op **"Maak Series"** onder de Serie-kolom om de `.strm`- en `.nfo`-bestanden voor series te maken.
6.  **Kies een Locatie**: Voor elke exportactie zal een venster verschijnen waarin je de opslaglocatie kunt kiezen.

Je bent nu klaar! De bestanden staan in de door jou gekozen mappen, klaar om te worden toegevoegd aan je mediacenter-bibliotheek.

---

*Dit script is bedoeld voor persoonlijk gebruik om legale en persoonlijk aangeschafte IPTV-abonnementen te beheren.*