from functools import partial
from lib.utils import make_request
from lib.utils import load_config
from lib.leagueReviewer import LeagueEditorPopup
from lib.leagueMenu import open_league_menu
import json
import tkinter as tk
import customtkinter as ctk
from types import SimpleNamespace
import os

# New: Load results_keys_descriptions.json directly
with open(os.path.join('conf', 'results_keys_descriptions.json'), encoding='utf-8') as f:
    results_descriptions = json.load(f)

def main():
    config = load_config()
    leagues = config.leagues
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.title("Leagues")
    root.geometry('400x600')
    main_frame = ctk.CTkFrame(root)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    title_label = ctk.CTkLabel(main_frame, text="Leagues", font=("Consolas", 18, "bold"))
    title_label.pack(pady=(0, 20))
    for url in leagues:
        try:
            result = make_request(url)
            league_name = result.get('json', {}).get('name')
            btn = ctk.CTkButton(main_frame, text=league_name, width=300, height=40, font=("Consolas", 14), command=lambda r=result: open_league_menu(r, config, root))
            btn.pack(pady=8)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            continue
    root.mainloop()

if __name__ == '__main__':
    main()