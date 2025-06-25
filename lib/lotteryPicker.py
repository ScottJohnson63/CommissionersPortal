import customtkinter as ctk
import random
import threading
import pygame
import os
import math
import itertools
import json

def open_lottery_picker(result, config, root):
    league_name = result.get('json', {}).get('name', 'Unknown League')
    popup = ctk.CTkToplevel(root)
    popup.title(f"{league_name} Lottery Picker")
    popup.geometry('400x350')
    popup.resizable(False, False)
    popup.transient(root)
    popup.focus_force()
    label = ctk.CTkLabel(popup, text=f"Lottery Picker for {league_name}", font=("Consolas", 15, "bold"))
    label.pack(pady=(30, 20))

    # Add a progress bar
    progress = ctk.CTkProgressBar(popup, width=300)
    progress.pack(pady=10)
    progress.set(0)

    # Banner label (initially hidden)
    congrats_label = ctk.CTkLabel(popup, text="", font=("Consolas", 28, "bold"), text_color="#2ecc40")
    congrats_label.pack(pady=(16, 6))

    result_frame = ctk.CTkFrame(popup)
    result_frame.pack(pady=10)

    # Load team names from conf/lotteryTeams.json
    try:
        with open(os.path.join('conf', 'lotteryTeams.json'), encoding='utf-8') as f:
            lottery_teams = json.load(f)
    except Exception as e:
        print(f"Error loading lotteryTeams.json: {e}")
        lottery_teams = []

    def run_lottery():
        # Play slot machine sound
        pygame.mixer.init()
        spin_sound_path = os.path.join('assets', 'lotterySound.mp3')
        winner_sound_path = os.path.join('assets', 'winnerWinner.mp3')
        spin_channel = None
        try:
            spin_sound = pygame.mixer.Sound(spin_sound_path)
            winner_sound = pygame.mixer.Sound(winner_sound_path)
            spin_channel = spin_sound.play(loops=-1)
        except Exception as e:
            print(f"Error playing spin sound: {e}")
            spin_channel = None
            winner_sound = None
        results = {1: 0, 2: 0, 3: 0}
        total = 100_000_000
        update_interval = 100_000
        for i in range(1, total + 1):
            pick = random.randint(1, 3)
            results[pick] += 1
            if i % update_interval == 0 or i == total:
                progress.set(i / total)
                popup.update_idletasks()
        # Stop spin sound
        if spin_channel:
            spin_channel.stop()
        # Play winner sound
        if winner_sound:
            winner_sound.play()
        # Display results
        for widget in result_frame.winfo_children():
            widget.destroy()
        for num in range(1, 4):
            ctk.CTkLabel(result_frame, text=f"{num}: {results[num]:,}", font=("Consolas", 13)).pack(pady=2)
        # Find the winner (the number with the highest count)
        winner_num = max(results, key=results.get)
        # Pull the team name from lotteryTeams.json if available
        team_name = None
        if lottery_teams and len(lottery_teams) >= winner_num:
            team = lottery_teams[winner_num - 1]
            team_name = team.get('name') if isinstance(team, dict) else str(team)
        if not team_name:
            team_name = f"Team {winner_num}"
        congrats_label.configure(text=f"Congrats, {team_name}!")
        progress.pack_forget()
        ctk.CTkButton(popup, text="Close", command=popup.destroy).pack(pady=20)

    threading.Thread(target=run_lottery, daemon=True).start()
