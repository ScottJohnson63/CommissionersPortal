import customtkinter as ctk
import threading
import pygame
import os
import json
from api_client import API_BASE_URL
import requests
import time

def show_lottery_picker(result, parent=None):
    league_name = result['data'].get('name', 'Unknown League') if result.get('data') else 'Unknown League'
    league_id = result['data'].get('league_id', '') if result.get('data') else ''
    popup = ctk.CTkToplevel(parent) if parent else ctk.CTkToplevel()
    popup.title(f"{league_name} Lottery Picker")
    popup.geometry('400x350')
    popup.resizable(False, False)
    popup.transient(parent)
    popup.focus_force()
    label = ctk.CTkLabel(popup, text=f"Lottery Picker for {league_name}", font=("Consolas", 15, "bold"))
    label.pack(pady=(30, 20))
    progress = ctk.CTkProgressBar(popup, width=300)
    progress.pack(pady=10)
    progress.set(0)
    congrats_label = ctk.CTkLabel(popup, text="", font=("Consolas", 28, "bold"), text_color="#2ecc40")
    congrats_label.pack(pady=(16, 6))
    result_frame = ctk.CTkFrame(popup)
    result_frame.pack(pady=10)
    # Load team names from API (or fallback to conf/lotteryTeams.json)
    try:
        resp = requests.get(f"{API_BASE_URL}/lottery_teams?league_id={league_id}")
        resp.raise_for_status()
        lottery_teams = resp.json()
    except Exception:
        try:
            with open(os.path.join('conf', 'lotteryTeams.json'), encoding='utf-8') as f:
                lottery_teams = json.load(f)
        except Exception:
            lottery_teams = []
    # Load league-specific sounds from conf/lotterySounds.json
    try:
        with open(os.path.join('conf', 'lotterySounds.json'), encoding='utf-8') as f:
            sound_config = json.load(f)
    except Exception:
        sound_config = {}
    def run_lottery():
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception as e:
            print(f"Error initializing pygame mixer: {e}")
        # Always select sounds based on league name (not team name)
        league_sounds = sound_config.get(league_name) or sound_config.get('default', {})
        spin_sound_file = league_sounds.get('loading', 'lotteryLoading2.mp3')
        winner_sound_file = league_sounds.get('winner', 'winnerWinner.mp3')
        workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        spin_sound_path = os.path.join(workspace_root, 'assets', spin_sound_file)
        winner_sound_path = os.path.join(workspace_root, 'assets', winner_sound_file)
        print(f"Spin sound path: {spin_sound_path}")
        print(f"Winner sound path: {winner_sound_path}")
        spin_channel = None
        winner_sound = None
        try:
            if not os.path.exists(spin_sound_path):
                print(f"Spin sound file does not exist: {spin_sound_path}")
            if not os.path.exists(winner_sound_path):
                print(f"Winner sound file does not exist: {winner_sound_path}")
            spin_sound = pygame.mixer.Sound(spin_sound_path)
            spin_sound.set_volume(0.7)
            winner_sound = pygame.mixer.Sound(winner_sound_path)
            winner_sound.set_volume(0.7)
            spin_channel = spin_sound.play(loops=-1)
        except Exception as e:
            print(f"Error loading/playing sound: {e}")
            spin_channel = None
            winner_sound = None
        # Use backend API for lottery results
        try:
            resp = requests.get(f"{API_BASE_URL}/lottery?league_id={league_id}")
            resp.raise_for_status()
            api_result = resp.json()
            results = api_result.get('results', {1: 0, 2: 0, 3: 0})
            winner_num = max(results, key=results.get)
            team_name = api_result.get('winner', None)
        except Exception:
            # fallback to local simulation
            import random
            results = {1: 0, 2: 0, 3: 0}
            total = 100_000_000
            update_interval = 100_000
            for i in range(1, total + 1):
                pick = random.randint(1, 3)
                results[pick] += 1
                if i % update_interval == 0 or i == total:
                    progress.set(i / total)
                    popup.update_idletasks()
            winner_num = max(results, key=results.get)
            team_name = None
            if lottery_teams and len(lottery_teams) >= winner_num:
                team = lottery_teams[winner_num - 1]
                team_name = team.get('name') if isinstance(team, dict) else str(team)
            if not team_name:
                team_name = f"Team {winner_num}"
        if spin_channel:
            spin_channel.stop()
        if winner_sound:
            winner_sound.play()
            print("Winner sound played!")
            time.sleep(2)  # Give time for the sound to play
        for widget in result_frame.winfo_children():
            widget.destroy()
        # Sort teams by results (descending)
        sorted_teams = sorted(results.items(), key=lambda x: x[1], reverse=True)
        for idx, (num, count) in enumerate(sorted_teams, 1):
            # Get team name
            tname = None
            if lottery_teams and len(lottery_teams) >= num:
                t = lottery_teams[num - 1]
                tname = t.get('name') if isinstance(t, dict) else str(t)
            if not tname:
                tname = f"Team {num}"
            # Highlight the winner
            if num == winner_num:
                ctk.CTkLabel(result_frame, text=f"{idx}. {tname}: {count:,}", font=("Consolas", 16, "bold"), text_color="#e67e22").pack(pady=4)
            else:
                ctk.CTkLabel(result_frame, text=f"{idx}. {tname}: {count:,}", font=("Consolas", 13)).pack(pady=2)
        congrats_label.configure(text=f"Congrats, {team_name}!")
        progress.pack_forget()
        ctk.CTkButton(popup, text="Close", command=popup.destroy).pack(pady=20)
    threading.Thread(target=run_lottery, daemon=True).start()
