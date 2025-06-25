import customtkinter as ctk
from .leagueReviewer import LeagueEditorPopup
from .lotteryPicker import open_lottery_picker
from .divisionDecider import get_divisions_from_file
import sys
import os

def open_league_menu(result, config, root):
    league_name = result.get('json', {}).get('name')
    menu_popup = ctk.CTkToplevel(root)
    menu_popup.title(f"{league_name} Menu")
    menu_popup.geometry('350x300')
    menu_popup.resizable(False, False)
    menu_popup.transient(root)
    menu_popup.focus_force()
    label = ctk.CTkLabel(menu_popup, text=f"{league_name} Options", font=("Consolas", 15, "bold"))
    label.pack(pady=(30, 20))
    def review_and_close():
        menu_popup.destroy()
        LeagueEditorPopup(result, config, parent=root)
    def lottery_and_close():
        menu_popup.destroy()
        open_lottery_picker(result, config, root)
    def division_decider_and_close():
        menu_popup.destroy()
        show_division_decider_popup(root)
    def league_scheduler_and_close():
        menu_popup.destroy()
        from .leagueScheduler import run_league_scheduler_gui
        run_league_scheduler_gui()

    def show_division_decider_popup(parent):
        try:
            divisions = get_divisions_from_file()
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
        # Main frame for padding
        main_frame = ctk.CTkFrame(popup)
        main_frame.pack(fill="both", expand=True, padx=24, pady=24)
        # Two columns for Odds and Evens
        columns = ctk.CTkFrame(main_frame)
        columns.pack(fill="both", expand=True)
        odds_frame = ctk.CTkFrame(columns)
        evens_frame = ctk.CTkFrame(columns)
        odds_frame.pack(side="left", fill="both", expand=True, padx=(0, 12))
        evens_frame.pack(side="right", fill="both", expand=True, padx=(12, 0))
        # Odds Division
        ctk.CTkLabel(odds_frame, text="Odds Division", font=("Consolas", 16, "bold"), text_color="#0074D9").pack(pady=(0, 8))
        for team in divisions['odds']:
            ctk.CTkLabel(odds_frame, text=team, font=("Consolas", 14)).pack(anchor="w", padx=12, pady=2)
        # Evens Division
        ctk.CTkLabel(evens_frame, text="Evens Division", font=("Consolas", 16, "bold"), text_color="#2ECC40").pack(pady=(0, 8))
        for team in divisions['evens']:
            ctk.CTkLabel(evens_frame, text=team, font=("Consolas", 14)).pack(anchor="w", padx=12, pady=2)
        # Close button
        ctk.CTkButton(main_frame, text="Close", command=popup.destroy).pack(pady=(18, 0))

    btn_review = ctk.CTkButton(menu_popup, text="Review League", width=220, height=40, font=("Consolas", 13), command=review_and_close)
    btn_review.pack(pady=8)
    btn_lottery = ctk.CTkButton(menu_popup, text="Lottery Picker", width=220, height=40, font=("Consolas", 13), command=lottery_and_close)
    btn_lottery.pack(pady=8)
    btn_division = ctk.CTkButton(menu_popup, text="Division Decider", width=220, height=40, font=("Consolas", 13), command=division_decider_and_close)
    btn_division.pack(pady=8)
    btn_scheduler = ctk.CTkButton(menu_popup, text="League Scheduler", width=220, height=40, font=("Consolas", 13), command=league_scheduler_and_close)
    btn_scheduler.pack(pady=8)
