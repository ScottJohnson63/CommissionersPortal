import customtkinter as ctk
from division_decider_popup import show_division_decider_popup
from leagueReviewer import show_league_reviewer
from lotteryPicker import show_lottery_picker

def open_league_menu(result, parent):
    print(f"DEBUG: open_league_menu received result: {result}")
    popup = ctk.CTkToplevel(parent)
    popup.title("League Menu")
    popup.geometry('350x350')
    popup.resizable(False, False)
    popup.transient(parent)
    popup.focus_force()
    label = ctk.CTkLabel(popup, text="League Options", font=("Consolas", 15, "bold"))
    label.pack(pady=(30, 20))
    ctk.CTkButton(popup, text="League Reviewer", command=lambda: show_league_reviewer(result, popup)).pack(pady=10)
    ctk.CTkButton(popup, text="Division Decider", command=lambda: show_division_decider_popup(popup)).pack(pady=10)
    ctk.CTkButton(popup, text="Lottery Picker", command=lambda: show_lottery_picker(result, popup)).pack(pady=10)
    ctk.CTkButton(popup, text="Close", command=popup.destroy).pack(pady=10)
