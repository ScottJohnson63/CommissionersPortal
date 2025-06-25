import customtkinter as ctk
from .leagueReviewer import LeagueEditorPopup
from .lotteryPicker import open_lottery_picker

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
    btn_review = ctk.CTkButton(menu_popup, text="Review League", width=220, height=40, font=("Consolas", 13), command=review_and_close)
    btn_review.pack(pady=8)
    btn_lottery = ctk.CTkButton(menu_popup, text="Lottery Picker", width=220, height=40, font=("Consolas", 13), command=lottery_and_close)
    btn_lottery.pack(pady=8)
    btn_division = ctk.CTkButton(menu_popup, text="Division Decider", width=220, height=40, font=("Consolas", 13))
    btn_division.pack(pady=8)
    btn_scheduler = ctk.CTkButton(menu_popup, text="League Scheduler", width=220, height=40, font=("Consolas", 13))
    btn_scheduler.pack(pady=8)
