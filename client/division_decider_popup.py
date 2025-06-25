import customtkinter as ctk
import requests

API_BASE_URL = 'http://127.0.0.1:5000/api'

def show_division_decider_popup(parent):
    try:
        resp = requests.get(f'{API_BASE_URL}/divisions')
        resp.raise_for_status()
        divisions = resp.json()
    except Exception as e:
        popup = ctk.CTkToplevel(parent)
        popup.title("Division Decider Error")
        ctk.CTkLabel(popup, text=f"Error: {e}", font=("Consolas", 13), text_color="red").pack(padx=20, pady=20)
        ctk.CTkButton(popup, text="Close", command=popup.destroy).pack(pady=10)
        return
    popup = ctk.CTkToplevel(parent)
    popup.title("Division Decider Results")
    popup.geometry('600x420')
    popup.resizable(False, False)
    popup.transient(parent)
    popup.focus_force()
    main_frame = ctk.CTkFrame(popup)
    main_frame.pack(fill="both", expand=True, padx=24, pady=24)
    columns = ctk.CTkFrame(main_frame)
    columns.pack(fill="both", expand=True)
    odds_frame = ctk.CTkFrame(columns)
    evens_frame = ctk.CTkFrame(columns)
    odds_frame.pack(side="left", fill="both", expand=True, padx=(0, 12))
    evens_frame.pack(side="right", fill="both", expand=True, padx=(12, 0))
    ctk.CTkLabel(odds_frame, text="Odds Division", font=("Consolas", 16, "bold"), text_color="#0074D9").pack(pady=(0, 8))
    for team in divisions['odds']:
        ctk.CTkLabel(odds_frame, text=team, font=("Consolas", 14)).pack(anchor="w", padx=12, pady=2)
    ctk.CTkLabel(evens_frame, text="Evens Division", font=("Consolas", 16, "bold"), text_color="#2ECC40").pack(pady=(0, 8))
    for team in divisions['evens']:
        ctk.CTkLabel(evens_frame, text=team, font=("Consolas", 14)).pack(anchor="w", padx=12, pady=2)
    ctk.CTkButton(main_frame, text="Close", command=popup.destroy).pack(pady=(18, 0))
