import os
import json
from lib import utils  # Ensure the lib directory is in the Python path

def validate_no_back_to_back(schedule):
    """
    Checks for back-to-back games between the same teams in consecutive weeks.
    Args:
        schedule: Dict mapping week numbers to lists of games (tuples of teams).
    Returns:
        List of tuples (week_before, week_after, repeated_games) where back-to-back games are found.
    """
    errors = []
    weeks = sorted(schedule.keys())
    for i in range(1, len(weeks)):
        previous_week = set(frozenset(g) for g in schedule[weeks[i-1]])
        current_week = set(frozenset(g) for g in schedule[weeks[i]])
        repeat = previous_week & current_week
        if repeat:
            errors.append((weeks[i-1], weeks[i], list(repeat)))

    return errors

def validate_total_division_games(schedule, config):
    """
    Counts the total number of games played between teams within the same division.
    Args:
        schedule: Dict mapping week numbers to lists of games.
        config: Config object containing divisions (list of lists).
    Returns:
        Integer count of all intra-division games scheduled.
    """
    counter = 0
    division_a, division_b = config.divisions[0], config.divisions[1]
    for games in schedule.values():
        for t1, t2 in games:
            if t1 in division_a and t2 in division_a:
                counter += 1
            elif t1 in division_b and t2 in division_b:
                counter += 1
    return counter

def validate_total_interdivision_games(schedule, config):
    """
    Counts the total number of games played between teams from different divisions.
    Args:
        schedule: Dict mapping week numbers to lists of games.
        config: Config object containing divisions (list of lists).
    Returns:
        Integer count of all inter-division games scheduled.
    """
    counter = 0
    division_a, division_b = config.divisions[0], config.divisions[1]
    for games in schedule.values():
        for t1, t2 in games:
            if (t1 in division_a and t2 in division_b) or (t1 in division_b and t2 in division_a):
                counter += 1
    return counter

def validate_individual_division_games(schedule, expected_games, config):
    """
    Validates the number of division (intra-division) games played by each team.
    Args:
        schedule: Dict mapping week numbers to lists of games.
        expected_games: Integer, expected number of division games per team.
        config: Config object containing divisions (list of lists).
    Returns:
        team_counts: Dict mapping team name to number of division games played.
        mismatched: List of teams not matching the expected number of games.
    """
    division_teams = config.divisions[0] + config.divisions[1]
    division_sets = [set(config.divisions[0]), set(config.divisions[1])]
    team_counts = {team: 0 for team in division_teams}
    for games in schedule.values():
        for t1, t2 in games:
            for div in division_sets:
                if t1 in div and t2 in div:
                    team_counts[t1] += 1
                    team_counts[t2] += 1
    # Each game is counted twice (once for each team), so divide by 2
    for team in team_counts:
        team_counts[team] //= 2
    mismatched = [team for team, count in team_counts.items() if count != expected_games]
    return team_counts, mismatched

def validate_individual_interdivision_games(schedule, expected_games, config):
    """
    Validates the number of inter-division games played by each team.
    Args:
        schedule: Dict mapping week numbers to lists of games.
        expected_games: Integer, expected number of inter-division games per team.
        config: Config object containing divisions (list of lists).
    Returns:
        team_counts: Dict mapping team name to number of inter-division games played.
        mismatched: List of teams not matching the expected number of games.
    """
    division_a, division_b = config.divisions[0], config.divisions[1]
    division_teams = division_a + division_b
    team_counts = {team: 0 for team in division_teams}
    for games in schedule.values():
        for t1, t2 in games:
            if (t1 in division_a and t2 in division_b) or (t1 in division_b and t2 in division_a):
                team_counts[t1] += 1
                team_counts[t2] += 1
    mismatched = [team for team, count in team_counts.items() if count != expected_games]
    return team_counts, mismatched

def validate_individual_intradivision_games(schedule, config):
    """
    Counts how many division (intra-division) games each team played.
    Args:
        schedule: Dict mapping week numbers to lists of games.
        config: Config object containing divisions (list of lists).
    Returns:
        team_counts: Dict mapping team name to number of division games played.
    """
    division_a, division_b = config.divisions[0], config.divisions[1]
    division_teams = division_a + division_b
    division_sets = [set(division_a), set(division_b)]
    team_counts = {team: 0 for team in division_teams}
    for games in schedule.values():
        for t1, t2 in games:
            for div in division_sets:
                if t1 in div and t2 in div:
                    team_counts[t1] += 1
                    team_counts[t2] += 1
    return team_counts

def build_validation_results(schedule=None, config=None):
    """
    Builds validation results for the given schedule and returns them as a dict (for JSON).
    If no schedule is provided, it will generate one.
    """
    # Load configs if not provided
    if config is None:
        config = utils.load_configs()

    # Print validation config if debug_mode is enabled
    if config.debug_mode:
        print("DEBUG: validation_config.json contents:")
        print(json.dumps(config.__dict__, indent=2))

    # Generate schedule if not provided
    if schedule is None:
        return {
            "error": "No schedule provided",
            "message": "Please generate a schedule by running the LeagueScheduler first."
        }

    # Perform validations
    total_division_games = validate_total_division_games(schedule, config)
    total_interdivision_games = validate_total_interdivision_games(schedule, config)
    indiv_inter = validate_individual_interdivision_games(schedule, config.individual_interdivision_games, config)
    indiv_intra = validate_individual_intradivision_games(schedule, config)
    back_to_back = None
    if config.check_back_to_back:
        back_to_back = validate_no_back_to_back(schedule)

    # Build results dictionary
    results = {
        "total_division_games": total_division_games,
        "total_interdivision_games": total_interdivision_games,
        "individual_interdivision_games": indiv_inter,
        "individual_intradivision_games": indiv_intra,
        "back_to_back": back_to_back
    }
    return results

def format_validation_results(validation_results):
    """
    Formats validation results for clear, readable output with the schedule at the end,
    and no curly brackets at the start or end.
    """
    lines = []
    # Print each validation result except schedule
    for key in validation_results:
        if key == "schedule":
            continue
        value = validation_results[key]
        if isinstance(value, dict):
            lines.append(f"{key}:")
            for subkey, subval in value.items():
                lines.append(f"  {subkey}: {subval}")
        elif isinstance(value, list):
            if value:  # Only print non-empty lists
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  {item}")
            else:
                lines.append(f"{key}: []")
        elif isinstance(value, tuple) and len(value) == 2 and isinstance(value[0], dict):
            # Special case for (dict, list) tuple
            lines.append(f"{key}:")
            for subkey, subval in value[0].items():
                lines.append(f"  {subkey}: {subval}")
            if value[1]:
                for item in value[1]:
                    lines.append(f"  {item}")
        else:
            lines.append(f"{key}: {value}")

    return "\n".join(lines)

def validate_schedule_backend(schedule, config):
    # Extracted backend logic from validateSchedule.py (no UI)
    # This is a placeholder; replace with actual validation logic
    # Example: results = validateSchedule.validate(schedule, config)
    results = {'valid': True, 'issues': []}
    return results

if __name__ == "__main__":
    config = utils.load_configs()
    results = build_validation_results(config=config)
    print(json.dumps(results, indent=2))
