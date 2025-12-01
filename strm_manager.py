"""GUI tool to download and organize STRM playlists."""
# pylint: disable=too-many-instance-attributes, too-many-locals, too-many-arguments
# pylint: disable=broad-exception-caught, line-too-long, unspecified-encoding
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import os
import json
import threading
import traceback

import requests
import base64

# Probeer Windows encryptie te laden voor veilige wachtwoordopslag
try:
    import win32crypt
    WIN_CRYPTO_AVAILABLE = True
except ImportError:
    WIN_CRYPTO_AVAILABLE = False

# We doen ons voor als een browser om blokkades te voorkomen
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# --- VERTAALSYSTEEM ---
LANGUAGES = {
    'nl': {
        'app_title': "STRM Bibliotheek Manager - Compleet & Fixed",
        'settings_frame': "Xtream Codes & Instellingen",
        'provider_label': "Provider:",
        'manage_accounts_button': "Beheer Accounts",
        'tmdb_api_key_label': "TMDB API Key:",
        'load_list_button': "Lijst Laden (Xtream Codes)",
        'live_tv_frame': "1. Live TV",
        'movies_frame': "2. Films (VOD)",
        'series_frame': "3. Series",
        'export_m3u_button': "Exporteer M3U",
        'create_movies_button': "Maak Films",
        'create_series_button': "Maak Series",
        'clear_selection_button': "Wis Selectie",
        'status_frame': "Status & Log",
        'ready_status': "Klaar voor gebruik.",
        'language_label': "Taal:",
        'connecting_status': "Verbinden met provider...",
        'getting_live_tv_status': "Live TV ophalen...",
        'getting_movies_status': "Films ophalen...",
        'getting_series_status': "Series ophalen...",
        'done_status': "Klaar! Live: {live} | Films: {movies} | Series: {series}",
        'no_provider_warning': "Geen provider geselecteerd! Kies er een of voeg toe via 'Beheer'.",
        'no_live_groups_warning': "Geen Live groepen geselecteerd.",
        'no_movie_groups_warning': "Geen Film groepen geselecteerd.",
        'no_series_groups_warning': "Geen Serie groepen geselecteerd.",
        'export_live_status': "Bezig met Live TV M3U genereren...",
        'export_live_done': "Klaar! {count} kanalen in M3U gezet.",
        'export_movies_status': "Films worden verwerkt...",
        'export_movies_done': "Klaar! {count} films verwerkt.",
        'export_series_status': "Starten met verwerken van {total} series... (Dit kan even duren)",
        'export_series_progress': "Serie {current}/{total}: {name}",
        'export_series_done': "Klaar! {episodes} afleveringen verwerkt van {series} series.",
        'ask_movie_dir_title': "Waar moeten de Films opgeslagen worden?",
        'ask_series_dir_title': "Waar moeten de Series opgeslagen worden?",
    },
    'en': {
        'app_title': "STRM Library Manager - Complete & Fixed",
        'settings_frame': "Xtream Codes & Settings",
        'provider_label': "Provider:",
        'manage_accounts_button': "Manage Accounts",
        'tmdb_api_key_label': "TMDB API Key:",
        'load_list_button': "Load List (Xtream Codes)",
        'live_tv_frame': "1. Live TV",
        'movies_frame': "2. Movies (VOD)",
        'series_frame': "3. Series",
        'export_m3u_button': "Export M3U",
        'create_movies_button': "Create Movies",
        'create_series_button': "Create Series",
        'clear_selection_button': "Clear Selection",
        'status_frame': "Status & Log",
        'ready_status': "Ready to use.",
        'language_label': "Language:",
        'connecting_status': "Connecting to provider...",
        'getting_live_tv_status': "Fetching Live TV...",
        'getting_movies_status': "Fetching Movies...",
        'getting_series_status': "Fetching Series...",
        'done_status': "Done! Live: {live} | Movies: {movies} | Series: {series}",
        'no_provider_warning': "No provider selected! Please select one or add one via 'Manage'.",
        'no_live_groups_warning': "No Live TV groups selected.",
        'no_movie_groups_warning': "No Movie groups selected.",
        'no_series_groups_warning': "No Series groups selected.",
        'export_live_status': "Generating Live TV M3U...",
        'export_live_done': "Done! {count} channels added to M3U.",
        'export_movies_status': "Processing movies...",
        'export_movies_done': "Done! {count} movies processed.",
        'export_series_status': "Starting to process {total} series... (This may take a while)",
        'export_series_progress': "Series {current}/{total}: {name}",
        'export_series_done': "Done! {episodes} episodes processed from {series} series.",
        'ask_movie_dir_title': "Where should the Movies be saved?",
        'ask_series_dir_title': "Where should the Series be saved?",
    }
}

class StrmManagerApp:
    """De hoofdapplicatie voor het beheren van STRM-bestanden van Xtream Codes."""
    def __init__(self, root):
        self.root = root
        self.root.geometry("1100x750")
        
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

        # --- DATA OPSLAG (STRIKT GESCHEIDEN) ---
        self.streams_live = []
        self.streams_movies = []
        self.streams_series = []
        
        self.live_groups = []
        self.movie_groups = []
        self.series_groups = []

        # UI Variabelen & Selecties
        self.live_vars = {}
        self.movie_vars = {}
        self.series_vars = {}

        self.selected_live = set()
        self.selected_movies = set()
        self.selected_series = set()

        # Provider & API data
        self.providers = []
        self.current_provider_name = tk.StringVar()
        self.tmdb_api_key = tk.StringVar()
        self.epg_url = None
        
        # Taalinstellingen
        self.current_lang = 'nl' # Standaard
        self.lang_var = tk.StringVar()

        self._setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.load_config()

    def _setup_ui(self):
        # --- Bovenbalk ---
        self.frame_top = tk.LabelFrame(self.root, pady=5, padx=10)
        self.frame_top.pack(fill=tk.X, padx=10, pady=5)

        # Taal selectie
        frame_lang = tk.Frame(self.frame_top)
        frame_lang.pack(fill=tk.X, expand=True, pady=2)
        self.lbl_lang = tk.Label(frame_lang, width=12, anchor='w')
        self.lbl_lang.pack(side=tk.LEFT)
        self.lang_menu = ttk.Combobox(frame_lang, textvariable=self.lang_var, values=list(LANGUAGES.keys()), state="readonly")
        self.lang_menu.pack(side=tk.LEFT, padx=5)
        self.lang_var.trace_add('write', self.change_language)

        # Provider selectie
        frame_inputs = tk.Frame(self.frame_top)
        frame_inputs.pack(fill=tk.X, expand=True, pady=2)

        self.lbl_provider = tk.Label(frame_inputs, width=12, anchor='w')
        self.lbl_provider.grid(row=0, column=0, sticky='w')
        self.combo_providers = ttk.Combobox(frame_inputs, textvariable=self.current_provider_name, state="readonly")
        self.combo_providers.grid(row=0, column=1, sticky='ew', padx=5)
        
        self.btn_manage = tk.Button(frame_inputs, command=self.open_provider_manager)
        self.btn_manage.grid(row=0, column=2, padx=5)

        frame_inputs.grid_columnconfigure(1, weight=1)

        # TMDB Key
        frame_api = tk.Frame(self.frame_top)
        frame_api.pack(fill=tk.X, expand=True, pady=2)
        self.lbl_tmdb = tk.Label(frame_api, width=12, anchor='w')
        self.lbl_tmdb.pack(side=tk.LEFT)
        tk.Entry(frame_api, textvariable=self.tmdb_api_key).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Load knop
        self.btn_load = tk.Button(self.frame_top, command=self.start_load_from_xtream, bg="#dddddd", height=2)
        self.btn_load.pack(fill=tk.X, pady=(10, 0))

        # --- Midden: 3 Kolommen ---
        frame_middle = tk.Frame(self.root)
        frame_middle.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        frame_middle.grid_columnconfigure(0, weight=1)
        frame_middle.grid_columnconfigure(1, weight=1)
        frame_middle.grid_columnconfigure(2, weight=1)
        frame_middle.grid_rowconfigure(0, weight=1)

        # 1. LIVE
        self.frame_live, self.canvas_live = self._create_category_frame(frame_middle, 0, "#e6f2ff")
        self.btn_export_live, self.btn_clear_live = self._add_action_buttons(self.frame_live, self.start_export_live, "live")

        # 2. FILMS
        self.frame_movies, self.canvas_movies = self._create_category_frame(frame_middle, 1, "#e6ffe6")
        self.btn_export_movies, self.btn_clear_movies = self._add_action_buttons(self.frame_movies, self.start_export_movies, "movies")

        # 3. SERIES
        self.frame_series, self.canvas_series = self._create_category_frame(frame_middle, 2, "#fff0e6")
        self.btn_export_series, self.btn_clear_series = self._add_action_buttons(self.frame_series, self.start_export_series, "series")

        # --- Onderbalk ---
        self.frame_bottom = tk.LabelFrame(self.root, padx=10, pady=5)
        self.frame_bottom.pack(fill=tk.X, padx=10, pady=10)

        self.lbl_status = tk.Label(self.frame_bottom, fg="blue", anchor="w")
        self.lbl_status.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.progress = ttk.Progressbar(self.frame_bottom, mode="indeterminate", length=200)
        self.progress.pack(side=tk.RIGHT, padx=10)

    def _create_category_frame(self, parent, col, bg_color):
        container = tk.LabelFrame(parent, padx=5, pady=5, bg=bg_color)
        container.grid(row=0, column=col, sticky='nsew', padx=5)
        
        list_frame = tk.Frame(container)
        list_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(list_frame, bg="white")
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        return container, scrollable_frame

    def _add_action_buttons(self, parent, export_cmd, type_key):
        btn_frame = tk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=5)
        
        btn_export = tk.Button(btn_frame, command=export_cmd, font=("Arial", 9, "bold"))
        btn_export.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        btn_clear = tk.Button(btn_frame, command=lambda: self.clear_selection(type_key), font=("Arial", 8))
        btn_clear.pack(side=tk.LEFT, padx=2)
        return btn_export, btn_clear

    def _(self, key, **kwargs):
        """Vertaalt een key naar de huidige taal, met optionele placeholders."""
        return LANGUAGES.get(self.current_lang, LANGUAGES['en']).get(key, key).format(**kwargs)

    def change_language(self, *args):
        new_lang = self.lang_var.get()
        if new_lang != self.current_lang:
            self.current_lang = new_lang
            self.update_ui_text()

    def update_ui_text(self):
        """Werkt alle teksten in de UI bij naar de huidige taal."""
        self.root.title(self._('app_title'))
        self.frame_top.config(text=self._('settings_frame'))
        self.lbl_lang.config(text=self._('language_label'))
        self.lbl_provider.config(text=self._('provider_label'))
        self.btn_manage.config(text=self._('manage_accounts_button'))
        self.lbl_tmdb.config(text=self._('tmdb_api_key_label'))
        self.btn_load.config(text=self._('load_list_button'))
        self.frame_live.config(text=self._('live_tv_frame'))
        self.frame_movies.config(text=self._('movies_frame'))
        self.frame_series.config(text=self._('series_frame'))
        self.btn_export_live.config(text=self._('export_m3u_button'))
        self.btn_export_movies.config(text=self._('create_movies_button'))
        self.btn_export_series.config(text=self._('create_series_button'))
        for btn in [self.btn_clear_live, self.btn_clear_movies, self.btn_clear_series]:
            btn.config(text=self._('clear_selection_button'))
        self.frame_bottom.config(text=self._('status_frame'))
        self.lbl_status.config(text=self._('ready_status'))

    # --- HULP FUNCTIES ---
    def log(self, message):
        self.root.after(0, self.lbl_status.config, {'text': message})

    def set_busy(self, busy):
        state = tk.DISABLED if busy else tk.NORMAL
        self.btn_load.config(state=state)
        if busy:
            self.progress.start(10)
        else:
            self.progress.stop()

    def run_in_thread(self, func):
        def wrapper():
            self.root.after(0, lambda: self.set_busy(True))
            try:
                func()
            except Exception as e:
                self.log(f"Onverwachte Fout: {e}")
                # Print volledige error naar console voor debugging
                traceback.print_exc() # Keep for debugging
                messagebox.showerror("Fout in achtergrondtaak", f"Er is een fout opgetreden:\n\n{e}")
            finally:
                self.root.after(0, lambda: self.set_busy(False))
        threading.Thread(target=wrapper, daemon=True).start()

    def sanitize_filename(self, name):
        return re.sub(r'[<>:"/\\|?*]', '', str(name)).strip()

    # --- CRYPTO & CONFIG ---
    def _encrypt_pass(self, password):
        if not WIN_CRYPTO_AVAILABLE or not password: return password
        try:
            data = win32crypt.CryptProtectData(password.encode(), None, None, None, None, 0)
            return base64.b64encode(data).decode()
        except: return password

    def _decrypt_pass(self, encrypted):
        if not WIN_CRYPTO_AVAILABLE or not encrypted: return encrypted
        try: # pywintypes.error kan optreden als data corrupt is
            data = base64.b64decode(encrypted.encode())
            return win32crypt.CryptUnprotectData(data, None, None, None, 0)[1].decode()
        except: return encrypted

    def load_config(self):
        if not os.path.exists(self.config_path): return
        try:
            with open(self.config_path, "r") as f:
                data = json.load(f)
            self.selected_live = set(data.get("selected_live", []))
            self.selected_movies = set(data.get("selected_movies", []))
            self.selected_series = set(data.get("selected_series", []))
            self.providers = data.get("providers", [])
            self.tmdb_api_key.set(data.get("tmdb_api_key", ""))
            self.current_lang = data.get("language", "nl")
            self.lang_var.set(self.current_lang)
            
            self.combo_providers['values'] = [p['name'] for p in self.providers]
            if data.get("last_provider"):
                self.current_provider_name.set(data.get("last_provider"))
            
            self.update_ui_text() # Pas taal toe na laden
        except (json.JSONDecodeError, OSError):
            self.lang_var.set(self.current_lang) # Zorg dat de UI consistent is
            self.update_ui_text()

    def save_config(self):
        self._sync_vars_to_sets()
        data = {
            "selected_live": list(self.selected_live),
            "selected_movies": list(self.selected_movies),
            "selected_series": list(self.selected_series),
            "providers": self.providers,
            "last_provider": self.current_provider_name.get(),
            "tmdb_api_key": self.tmdb_api_key.get(),
            "language": self.current_lang
        }
        try:
            with open(self.config_path, "w") as f:
                json.dump(data, f, indent=2)
        except OSError: pass

    def on_close(self):
        self.save_config()
        self.root.destroy()

    # --- XTREAM CODES LOGICA ---
    def start_load_from_xtream(self):
        self.run_in_thread(self.load_from_xtream)

    def _api_get(self, url, params):
        # requests.packages.urllib3.disable_warnings() # Optioneel
        try:
            r = requests.get(url, params=params, headers=DEFAULT_HEADERS, timeout=30, verify=False)
            r.raise_for_status()
            return r.json() # Kan een JSONDecodeError geven als de response geen JSON is
        except Exception as e:
            return None

    def load_from_xtream(self):
        name = self.current_provider_name.get()
        provider = next((p for p in self.providers if p['name'] == name), None)
        
        if not provider:
            self.log(self._('no_provider_warning'))
            return

        server = provider['server'].rstrip('/')
        username = provider['username']
        password = self._decrypt_pass(provider.get('password', ''))
        
        base_url = f"{server}/player_api.php" # Let op: auth wordt hieronder toegevoegd
        self.epg_url = f"{server}/xmltv.php?username={username}&password={password}"
        auth = {"username": username, "password": password}

        self.log("Verbinden met provider...")

        # 1. Categorieën ophalen
        live_cats = self._api_get(base_url, {**auth, "action": "get_live_categories"}) or []

        vod_cats = self._api_get(base_url, {**auth, "action": "get_vod_categories"}) or []
        series_cats = self._api_get(base_url, {**auth, "action": "get_series_categories"}) or []

        map_live = {c['category_id']: c['category_name'] for c in live_cats}
        map_vod = {c['category_id']: c['category_name'] for c in vod_cats}
        map_series = {c['category_id']: c['category_name'] for c in series_cats}

        # 2. Data ophalen & opslaan
        self.log(self._('getting_live_tv_status'))
        self.streams_live = []
        raw_live = self._api_get(base_url, {**auth, "action": "get_live_streams"}) or []
        for s in raw_live:
            cat_name = map_live.get(s['category_id'], "Onbekend")
            self.streams_live.append({
                'name': s['name'],
                'group': cat_name,
                'url': f"{server}/live/{username}/{password}/{s['stream_id']}.ts",
                'logo': s.get('stream_icon', ''),
                'epg_id': s.get('epg_channel_id', '')
            })

        self.log(self._('getting_movies_status'))
        self.streams_movies = []
        raw_vod = self._api_get(base_url, {**auth, "action": "get_vod_streams"}) or []
        for s in raw_vod:
            cat_name = map_vod.get(s['category_id'], "Onbekend")
            ext = s.get('container_extension', 'mp4')
            self.streams_movies.append({
                'name': s['name'],
                'group': cat_name,
                'url': f"{server}/movie/{username}/{password}/{s['stream_id']}.{ext}"
            })

        self.log(self._('getting_series_status'))
        self.streams_series = []
        raw_series = self._api_get(base_url, {**auth, "action": "get_series"}) or []
        for s in raw_series:
            cat_name = map_series.get(s['category_id'], "Onbekend")
            # --- WIJZIGING: We slaan nu het series_id en metadata op ---
            self.streams_series.append({
                'name': s['name'],
                'group': cat_name,
                'series_id': s['series_id'], # CRUCIAAL voor de volgende stap
                'cover': s.get('cover', ''),
                'plot': s.get('plot', '')
            })

        self.root.after(0, self._update_ui_lists, sorted(map_live.values()), sorted(map_vod.values()), sorted(map_series.values()))

    def _update_ui_lists(self, l_groups, m_groups, s_groups):
        self._fill_canvas(self.canvas_live, l_groups, self.live_vars, self.selected_live)
        self._fill_canvas(self.canvas_movies, m_groups, self.movie_vars, self.selected_movies)
        self._fill_canvas(self.canvas_series, s_groups, self.series_vars, self.selected_series)

        count_msg = self._('done_status', 
                           live=len(self.streams_live), 
                           movies=len(self.streams_movies), 
                           series=len(self.streams_series)
                          )
        self.log(count_msg)

    def _fill_canvas(self, canvas, groups, var_dict, selected_set):
        """Vult een canvas met een lijst van checkboxes voor de categorieën."""
        for widget in canvas.winfo_children(): widget.destroy() # Maak eerst leeg
        var_dict.clear()
        unique_groups = sorted(list(set(groups)))
        for g in unique_groups:
            var = tk.BooleanVar(value=(g in selected_set))
            cb = tk.Checkbutton(canvas, text=g, variable=var, anchor='w', bg="white")
            cb.pack(fill=tk.X)
            var_dict[g] = var

    def _sync_vars_to_sets(self):
        """Synchroniseert de status van de checkboxes naar de 'selected' sets."""
        self.selected_live = {g for g, v in self.live_vars.items() if v.get()}
        self.selected_movies = {g for g, v in self.movie_vars.items() if v.get()}
        self.selected_series = {g for g, v in self.series_vars.items() if v.get()}

    def clear_selection(self, type_key):
        target = getattr(self, f"{type_key}_vars")
        for v in target.values(): v.set(False)

    # --- EXPORT FUNCTIES ---
    def start_export_live(self):
        self._sync_vars_to_sets()
        if not self.selected_live: return messagebox.showwarning("Let op", self._('no_live_groups_warning'))
        path = filedialog.asksaveasfilename(defaultextension=".m3u", filetypes=[("M3U Playlist", "*.m3u")])
        if path: self.run_in_thread(lambda: self.export_live_logic(path))

    def export_live_logic(self, filename):
        self.log(self._('export_live_status'))
        count = 0
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f'#EXTM3U x-tvg-url="{self.epg_url}"\n')
            for s in self.streams_live:
                if s['group'] in self.selected_live:
                    epg_id = s.get('epg_id', '')
                    f.write(f'#EXTINF:-1 tvg-id="{epg_id}" tvg-name="{s["name"]}" tvg-logo="{s["logo"]}" group-title="{s["group"]}",{s["name"]}\n')
                    f.write(f"{s['url']}\n")
                    count += 1
        self.log(self._('export_live_done', count=count))

    def start_export_movies(self):
        self._sync_vars_to_sets()
        if not self.selected_movies: return messagebox.showwarning("Let op", self._('no_movie_groups_warning'))
        path = filedialog.askdirectory(title=self._('ask_movie_dir_title'))
        if path: self.run_in_thread(lambda: self.export_movies_logic(path))

    def export_movies_logic(self, base_dir):
        self.log(self._('export_movies_status'))
        count = 0
        for s in self.streams_movies:
            if s['group'] in self.selected_movies:
                cat_folder = self.sanitize_filename(s['group'])
                title = self.sanitize_filename(s['name'])
                year = re.search(r'[\(\[](\d{4})[\)\]]', title)
                folder_name = f"{title} ({year.group(1)})" if year else title
                full_path = os.path.join(base_dir, cat_folder, folder_name)
                try:
                    os.makedirs(full_path, exist_ok=True)
                    with open(os.path.join(full_path, f"{title}.strm"), 'w', encoding='utf-8') as f:
                        f.write(s['url'])
                    count += 1
                except OSError: pass
        self.log(self._('export_movies_done', count=count))

    def start_export_series(self):
        self._sync_vars_to_sets()
        if not self.selected_series: return messagebox.showwarning("Let op", self._('no_series_groups_warning'))
        path = filedialog.askdirectory(title=self._('ask_series_dir_title'))
        if path: self.run_in_thread(lambda: self.export_series_logic(path))

    def _tmdb_call(self, endpoint, params={}):
        key = self.tmdb_api_key.get()
        if not key: return None
        try:
            url = f"https://api.themoviedb.org/3/{endpoint}"
            p = {**params, "api_key": key, "language": "nl-NL"}
            return requests.get(url, params=p, timeout=5).json()
        except: return None

    def export_series_logic(self, base_dir):
        """Orchestreert het volledige exportproces voor series."""
        name = self.current_provider_name.get()
        provider = next((p for p in self.providers if p['name'] == name), None)
        if not provider: return

        server = provider['server'].rstrip('/')
        username = provider['username']
        password = self._decrypt_pass(provider.get('password', ''))
        base_api_url = f"{server}/player_api.php"
        auth = {"username": username, "password": password, "server": server}

        series_to_process = [s for s in self.streams_series if s['group'] in self.selected_series]
        total_series = len(series_to_process)
        self.log(self._('export_series_status', total=total_series))

        count_episodes = 0
        for index, s in enumerate(series_to_process):
            self.log(self._('export_series_progress', current=index + 1, total=total_series, name=s['name']))
            try:
                ep_count = self._process_single_series(s, base_dir, base_api_url, auth)
                count_episodes += ep_count
            except requests.RequestException as e:
                self.log(f"Netwerkfout bij {s['name']}: {e}")
            except Exception as e: # Vang onverwachte fouten per serie
                self.log(f"Fout bij verwerken van {s['name']}: {e}")

        self.log(self._('export_series_done', episodes=count_episodes, series=total_series))

    def _process_single_series(self, series_data, base_dir, api_url, auth):
        """Haalt info en afleveringen voor één serie op en schrijft de bestanden."""
        info_response = self._api_get(api_url, {**auth, "action": "get_series_info", "series_id": series_data['series_id']})
        if not info_response or 'episodes' not in info_response:
            return 0

        episodes_data = info_response['episodes']
        provider_info = info_response.get('info', {})
        
        series_name = self.sanitize_filename(series_data['name'])
        cat_folder = self.sanitize_filename(series_data['group'])
        series_dir = os.path.join(base_dir, cat_folder, series_name)
        os.makedirs(series_dir, exist_ok=True)

        self._create_tvshow_nfo(series_dir, series_data, provider_info)

        episode_count = 0
        for season_num, ep_list in episodes_data.items():
            for ep in ep_list:
                self._create_episode_files(series_dir, series_name, season_num, ep, auth)
                episode_count += 1
        return episode_count

    def _create_tvshow_nfo(self, series_dir, series_data, provider_info):
        """Maakt het tvshow.nfo bestand, met TMDB als prioriteit."""
        nfo_path = os.path.join(series_dir, "tvshow.nfo")
        
        # Probeer eerst TMDB data te gebruiken voor betere metadata
        if self.tmdb_api_key.get():
            search_term = re.sub(r'[\(\[]\d{4}[\)\]]', '', series_data['name']).strip()
            res = self._tmdb_call("search/tv", {"query": search_term})
            if res and res.get('results'):
                show_id = res['results'][0]['id']
                details = self._tmdb_call(f"tv/{show_id}") or {}
                nfo_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<tvshow>
    <title>{details.get('name', '')}</title>
    <plot>{details.get('overview', '')}</plot>
    <premiered>{details.get('first_air_date', '')}</premiered>
    <rating>{details.get('vote_average', '')}</rating>
</tvshow>"""
                try:
                    with open(nfo_path, "w", encoding="utf-8") as f: f.write(nfo_content)
                    return # Stop hier als TMDB succesvol was
                except OSError: pass

        # Fallback naar de data van de provider als TMDB faalt of niet is ingesteld
        nfo_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<tvshow>
    <title>{series_data['name']}</title>
    <plot>{provider_info.get('plot', '')}</plot>
    <genre>{provider_info.get('genre', '')}</genre>
    <rating>{provider_info.get('rating', '')}</rating>
    <thumb>{provider_info.get('cover', '')}</thumb>
</tvshow>"""
        try:
            with open(nfo_path, "w", encoding="utf-8") as f: f.write(nfo_content)
        except OSError: pass

    def _create_episode_files(self, series_dir, series_name, season_num, ep_data, auth):
        """Maakt de .strm en .nfo bestanden voor een enkele aflevering."""
        try:
            season_folder = f"Season {int(season_num):02d}"
            full_dir = os.path.join(series_dir, season_folder)
            os.makedirs(full_dir, exist_ok=True)

            ep_num = ep_data.get('episode_num')
            ext = ep_data.get('container_extension', 'mp4')
            ep_id = ep_data.get('id')
            
            # Haal server, user, pass uit auth dict voor de URL
            server = auth['server'].rstrip('/')
            username = auth['username']
            password = auth['password']

            filename_base = f"{series_name} - S{int(season_num):02d}E{int(ep_num):02d}"
            stream_url = f"{server}/series/{username}/{password}/{ep_id}.{ext}"
            
            # .strm bestand
            with open(os.path.join(full_dir, filename_base + ".strm"), "w", encoding="utf-8") as f:
                f.write(stream_url)
            
            # .nfo voor aflevering
            nfo_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<episodedetails>
    <title>{ep_data.get('title', '')}</title>
    <plot>{ep_data.get('info', {}).get('plot', '')}</plot>
    <season>{season_num}</season>
    <episode>{ep_num}</episode>
    <thumb>{ep_data.get('info', {}).get('movie_image', '')}</thumb>
</episodedetails>"""
            with open(os.path.join(full_dir, filename_base + ".nfo"), "w", encoding="utf-8") as f:
                f.write(nfo_content)

        except (OSError, TypeError): # Vang bestandsfouten en fouten zoals int(None)
            pass

    # --- PROVIDER MANAGER POPUP ---
    def open_provider_manager(self):
        manager = ProviderManager(self.root, self.providers, self._encrypt_pass)
        if manager.saved_providers is not None:
            self.providers = manager.saved_providers
            self.combo_providers['values'] = [p['name'] for p in self.providers]
            if self.current_provider_name.get() not in [p['name'] for p in self.providers]:
                self.current_provider_name.set("")


class ProviderManager:
    """Een apart venster voor het beheren van provider-accounts."""
    def __init__(self, parent, providers, encrypt_func):
        self.top = tk.Toplevel(parent)
        self.top.title("Provider Beheer")
        self.top.geometry("600x350")
        self.top.transient(parent)
        self.top.grab_set()

        self.providers = [p.copy() for p in providers]
        self.encrypt_func = encrypt_func
        self.saved_providers = None

        # --- UI ---
        list_frame = tk.Frame(self.top, padx=10, pady=10)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox = tk.Listbox(list_frame, exportselection=False)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)

        btn_list_frame = tk.Frame(list_frame)
        btn_list_frame.pack(fill=tk.X, pady=5)
        tk.Button(btn_list_frame, text="Nieuw", command=self.new_provider).pack(side=tk.LEFT)
        tk.Button(btn_list_frame, text="Verwijder", command=self.delete_provider).pack(side=tk.LEFT, padx=5)

        details_frame = tk.LabelFrame(self.top, text="Details", padx=10, pady=10)
        details_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        tk.Label(details_frame, text="Naam:").grid(row=0, column=0, sticky='w', pady=2)
        self.entry_name = tk.Entry(details_frame, width=40)
        self.entry_name.grid(row=0, column=1, sticky='ew', pady=2)
        tk.Label(details_frame, text="Server (http://...):").grid(row=1, column=0, sticky='w', pady=2)
        self.entry_server = tk.Entry(details_frame)
        self.entry_server.grid(row=1, column=1, sticky='ew', pady=2)
        tk.Label(details_frame, text="Gebruikersnaam:").grid(row=2, column=0, sticky='w', pady=2)
        self.entry_user = tk.Entry(details_frame)
        self.entry_user.grid(row=2, column=1, sticky='ew', pady=2)
        tk.Label(details_frame, text="Wachtwoord:").grid(row=3, column=0, sticky='w', pady=2)
        self.entry_pass = tk.Entry(details_frame, show="*")
        self.entry_pass.grid(row=3, column=1, sticky='ew', pady=2)

        tk.Button(details_frame, text="Opslaan", command=self.save_provider, bg="#cceeff").grid(row=4, column=0, columnspan=2, sticky='ew', pady=10)
        tk.Button(details_frame, text="Sluiten", command=self.close).grid(row=5, column=0, columnspan=2, sticky='ew')

        self.populate_list()
        self.top.wait_window()

    def populate_list(self):
        self.listbox.delete(0, tk.END)
        for p in self.providers: self.listbox.insert(tk.END, p['name'])

    def on_select(self, event=None):
        sel = self.listbox.curselection()
        if not sel: return
        p = self.providers[sel[0]]
        self.entry_name.delete(0, tk.END); self.entry_name.insert(0, p.get('name', ''))
        self.entry_server.delete(0, tk.END); self.entry_server.insert(0, p.get('server', ''))
        self.entry_user.delete(0, tk.END); self.entry_user.insert(0, p.get('username', ''))
        self.entry_pass.delete(0, tk.END)

    def new_provider(self):
        self.listbox.selection_clear(0, tk.END)
        self.entry_name.delete(0, tk.END); self.entry_server.delete(0, tk.END)
        self.entry_user.delete(0, tk.END); self.entry_pass.delete(0, tk.END)
        self.entry_name.focus_set()

    def delete_provider(self):
        sel = self.listbox.curselection()
        if not sel: return
        if messagebox.askyesno("Verwijderen", "Weet je zeker dat je deze provider wilt verwijderen?", parent=self.top):
            del self.providers[sel[0]]
            self.populate_list()
            self.new_provider()

    def save_provider(self):
        name = self.entry_name.get().strip()
        if not name: return messagebox.showerror("Fout", "Provider naam is verplicht.", parent=self.top)

        new_data = {"name": name, "server": self.entry_server.get().strip(), "username": self.entry_user.get().strip()}
        pw = self.entry_pass.get()
        
        existing_provider = next((p for p in self.providers if p['name'] == name), None)

        if pw: new_data["password"] = self.encrypt_func(pw)
        elif existing_provider: new_data["password"] = existing_provider.get('password', '')

        if existing_provider:
            self.providers[self.providers.index(existing_provider)] = new_data
        else:
            self.providers.append(new_data)
        
        self.populate_list()
        for i, p in enumerate(self.providers):
            if p['name'] == name:
                self.listbox.selection_set(i)
                break

    def close(self):
        self.saved_providers = self.providers
        self.top.destroy()


if __name__ == "__main__":
    main_root = tk.Tk()
    app = StrmManagerApp(main_root)
    main_root.mainloop()
