import os
import sys
# Ensure project root is in sys.path for lib imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import random
from collections import deque, defaultdict
from lib import utils
import customtkinter as ctk
import json
import io
import contextlib
from lib import validateSchedule as validator
from datetime import datetime

def run_league_scheduler_gui():
    schedule = None  # Local to the function
    # Create the main application window
    root = ctk.CTk()
    root.title("League Scheduler Client")
    root.geometry("600x500")

    # Output label (use a CTkLabel for multi-line output)
    output_label = ctk.CTkLabel(root, text="Schedule Output:", font=("Consolas", 15, "bold"))
    output_label.pack(pady=(20, 0))

    output_box = ctk.CTkTextbox(root, height=15, width=70, font=("Consolas", 13))
    output_box.pack(pady=10, padx=20, fill="both", expand=True)

    def set_output_text(text):
        output_box.delete("1.0", "end")
        output_box.insert("end", text)

    def save_schedule_to_file(schedule_str, filename_prefix="schedule_output"):
        results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
        os.makedirs(results_dir, exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d_time_%H-%M-%S")
        filename = f"{filename_prefix}_{date_str}.txt"
        file_path = os.path.join(results_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(schedule_str)

    def save_validation_results_to_file(results_str, filename_prefix="validation_results"):
        results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
        os.makedirs(results_dir, exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d_time_%H-%M-%S")
        filename = f"{filename_prefix}_{date_str}.txt"
        file_path = os.path.join(results_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(results_str)

    # Progress bar
    progress = ctk.CTkProgressBar(root, orientation="horizontal", width=400, height=18)
    progress.set(0)
    progress.pack(pady=10)

    def on_generate_schedule():
        nonlocal schedule
        progress.set(0)
        root.update_idletasks()
        # Run scheduling in a thread to keep UI responsive
        import threading
        def run_scheduler():
            nonlocal schedule
            config = utils.load_scheduler_config()
            max_retries = config.max_retries
            for attempt in range(1, max_retries + 1):
                matchups = utils.leagueScheduler.generate_matchups(config)
                schedule_, leftover = utils.leagueScheduler.relaxed_greedy_schedule_with_unscheduled(matchups, config)
                final_schedule, final_unscheduled = utils.leagueScheduler.post_process_schedule(schedule_, leftover, config)
                progress.set(attempt / max_retries)
                root.update_idletasks()
                if not final_unscheduled:
                    schedule = final_schedule
                    break
            else:
                schedule = final_schedule
            schedule_str = utils.leagueScheduler.format_schedule(schedule)
            save_schedule_to_file(schedule_str)
            set_output_text(schedule_str)
            progress.set(1)
            root.update_idletasks()
        threading.Thread(target=run_scheduler).start()

    def on_validate_schedule():
        nonlocal schedule
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            validation_results = validator.build_validation_results(schedule=schedule, config=utils.load_configs())
        output = buf.getvalue()
        results_str = validator.format_validation_results(validation_results) + "\n\n" + utils.leagueScheduler.format_schedule(schedule)
        set_output_text(results_str)
        save_validation_results_to_file(results_str)

    # Generate Schedule button
    generate_btn = ctk.CTkButton(root, text="Generate Schedule", command=on_generate_schedule, font=("Consolas", 13))
    generate_btn.pack(pady=5)

    # Validate Schedule button
    validate_btn = ctk.CTkButton(root, text="Validate Schedule", command=on_validate_schedule, font=("Consolas", 13))
    validate_btn.pack(pady=5)

    def copy_selection():
        try:
            selected = output_box.get("sel.first", "sel.last")
        except Exception:
            selected = output_box.get("1.0", "end-1c")
        root.clipboard_clear()
        root.clipboard_append(selected)

    # CustomTkinter does not have a built-in context menu, so use Tkinter's Menu
    import tkinter as tk
    context_menu = tk.Menu(root, tearoff=0)
    context_menu.add_command(label="Copy", command=copy_selection)

    def show_context_menu(event):
        context_menu.tk_popup(event.x_root, event.y_root)

    output_box.bind("<Button-3>", show_context_menu)

    root.mainloop()

def generate_matchups(config):
    """
    Generates all possible matchups for the season.
    - Each pair of teams in the division plays twice (home and away).
    Returns:
        List of tuples, where each tuple is a matchup (home_team, away_team).
    """
    division = getattr(config, 'division', None)
    if not division or not isinstance(division, list) or len(division) < 2:
        raise ValueError("Config must contain a 'division' list with at least two teams.")
    matchups = set()
    # Each pair plays twice (home/away)
    for i in range(len(division)):
        for j in range(i + 1, len(division)):
            matchups.add((division[i], division[j]))
            matchups.add((division[j], division[i]))
    return list(matchups)

def relaxed_greedy_schedule_with_unscheduled(matchups, config):
    """
    Attempts to schedule all matchups into weeks using a greedy algorithm.
    - Tries to avoid teams playing more than once per week.
    - Tries to avoid back-to-back matchups between the same teams.
    - If a matchup can't be scheduled in the current week, it is retried in the next week.
    Args:
        matchups: List of all matchups to schedule.
        config: Configuration object.
    Returns:
        schedule: Dict mapping week number to list of games scheduled that week.
        unscheduled: List of matchups that could not be scheduled.
    """
    games_per_week = config.games_per_week
    num_weeks = config.num_weeks

    schedule = defaultdict(list)
    pending_matchups = deque(matchups.copy())
    random.shuffle(pending_matchups)
    previous_week_matchups = set()
    unscheduled = []

    for week in range(1, num_weeks + 1):
        weekly_teams = set()
        scheduled_this_week = []
        retry_matchups = deque()

        while pending_matchups and len(scheduled_this_week) < games_per_week:
            matchup = pending_matchups.popleft()
            t1, t2 = matchup
            if (t1 not in weekly_teams and t2 not in weekly_teams and
                (t1, t2) not in previous_week_matchups and (t2, t1) not in previous_week_matchups):
                schedule[week].append(matchup)
                scheduled_this_week.append(matchup)
                weekly_teams.update([t1, t2])
            else:
                retry_matchups.append(matchup)

        pending_matchups.extend(retry_matchups)
        previous_week_matchups = set(scheduled_this_week)

    unscheduled = list(pending_matchups)
    return schedule, unscheduled

def is_valid_insertion(schedule, week, game, previous_week, next_week):
    """
    Checks if a game can be inserted into a given week without conflicts.
    - Ensures neither team is already scheduled that week.
    - Ensures the same matchup does not occur in adjacent weeks.
    Args:
        schedule: Current schedule dict.
        week: Week number to check.
        game: Tuple (team1, team2) representing the matchup.
        previous_week: Previous week number.
        next_week: Next week number.
    Returns:
        True if the game can be inserted, False otherwise.
    """
    t1, t2 = game
    teams_in_week = {team for g in schedule[week] for team in g}
    if t1 in teams_in_week or t2 in teams_in_week:
        return False
    for g in schedule.get(previous_week, []) + schedule.get(next_week, []):
        if set(g) == set(game):
            return False
    return True

def try_swap(schedule, week, game, previous_week, next_week):
    """
    Attempts to swap an existing game in a week with a new game if it allows the new game to be scheduled.
    - Ensures no team plays twice in a week.
    - Ensures no back-to-back matchups.
    Args:
        schedule: Current schedule dict.
        week: Week number to attempt the swap.
        game: Tuple (team1, team2) representing the new matchup.
        previous_week: Previous week number.
        next_week: Next week number.
    Returns:
        The removed game if a swap was successful, None otherwise.
    """
    for i, existing in enumerate(schedule[week]):
        if set(game) & set(existing):
            continue
        temp_week = schedule[week][:i] + schedule[week][i+1:]
        temp_teams = {team for g in temp_week for team in g}
        if game[0] in temp_teams or game[1] in temp_teams:
            continue
        if not is_valid_insertion({week: temp_week}, week, game, previous_week, next_week):
            continue
        schedule[week][i] = game
        return existing
    return None

def post_process_schedule(schedule, unscheduled, config):
    """
    Attempts to place any unscheduled games into the schedule after the initial greedy scheduling.
    - Tries to insert unscheduled games into weeks with available slots.
    - May swap games to make room for unscheduled games.
    Args:
        schedule: Current schedule dict.
        unscheduled: List of games not yet scheduled.
        config: Configuration object.
    Returns:
        Updated schedule and list of any games still unscheduled.
    """
    games_per_week = config.games_per_week
    num_weeks = config.num_weeks

    for game in unscheduled[:]:
        placed = False
        for week in range(1, num_weeks + 1):
            prev_wk, next_wk = week - 1, week + 1
            if len(schedule[week]) < games_per_week:
                if is_valid_insertion(schedule, week, game, prev_wk, next_wk):
                    schedule[week].append(game)
                    unscheduled.remove(game)
                    placed = True
                    break
            else:
                removed = try_swap(schedule, week, game, prev_wk, next_wk)
                if removed:
                    unscheduled.remove(game)
                    unscheduled.append(removed)
                    placed = True
                    break
    return schedule, unscheduled

def build_schedule(config):
    """
    API endpoint to build a complete schedule.
    - Tries up to max_retries to generate a schedule with no unscheduled games.
    Returns:
        The final schedule as a dict mapping week numbers to lists of games.
    """
    max_retries = config.max_retries
    for attempt in range(1, max_retries + 1):
        matchups = generate_matchups(config)
        schedule, leftover = relaxed_greedy_schedule_with_unscheduled(matchups, config)
        final_schedule, final_unscheduled = post_process_schedule(schedule, leftover, config)
        if not final_unscheduled:
            print(f"Success on attempt {attempt}")
            return final_schedule
    print("Failed to schedule all matchups after max retries.")
    return final_schedule

def print_schedule(schedule):
    """
    Prints the schedule in a readable format, showing games for each week.
    Args:
        schedule: Dict mapping week number to list of games.
    """
    for week in sorted(schedule):
        print(f"Week {week}:")
        for game in schedule[week]:
            print(f" {game[0]} vs {game[1]}")

def format_schedule(schedule):
    """
    Formats the schedule as a string with week sections and lines like:
    Week {week}:
        Team {Name} vs Team {Name}
    Handles both list and dict schedule structures.
    """
    lines = []
    if isinstance(schedule, dict):
        for week, games in schedule.items():
            lines.append(f"Week {week}:")
            for game in games:
                if isinstance(game, (tuple, list)) and len(game) == 2:
                    lines.append(f"\t{game[0]} vs {game[1]}")
                elif isinstance(game, dict):
                    home = game.get('home', 'TBD')
                    away = game.get('away', 'TBD')
                    lines.append(f"\t{home} vs {away}")
                else:
                    lines.append(f"\t{str(game)}")
    elif isinstance(schedule, list):
        # If the list contains week info, e.g., [{'week': 1, 'home': 'A', 'away': 'B'}, ...]
        current_week = None
        for game in schedule:
            week = None
            if isinstance(game, dict):
                week = game.get('week')
            if week is not None and week != current_week:
                lines.append(f"Week {week}:")
                current_week = week
            if isinstance(game, (tuple, list)) and len(game) == 2:
                lines.append(f"\t{game[0]} vs {game[1]}")
            elif isinstance(game, dict):
                home = game.get('home', 'TBD')
                away = game.get('away', 'TBD')
                lines.append(f"\t{home} vs {away}")
            else:
                lines.append(f"\t{str(game)}")
    else:
        lines.append(str(schedule))
    return "\n".join(lines)

if __name__ == "__main__":
    config = utils.load_scheduler_config()
    schedule = build_schedule(config)
    print_schedule(schedule)
