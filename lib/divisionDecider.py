import json
import os

def get_divisions_from_file(json_path=None):
    if json_path is None:
        json_path = os.path.join('conf', 'divisionDecider.json')
    with open(json_path, encoding='utf-8') as f:
        teams = json.load(f)
    if len(teams) != 10:
        raise ValueError("divisionDecider.json must contain exactly 10 teams.")
    odds = [team for i, team in enumerate(teams, 1) if i % 2 == 1]
    evens = [team for i, team in enumerate(teams, 1) if i % 2 == 0]
    return {'odds': odds, 'evens': evens}

if __name__ == '__main__':
    divisions = get_divisions_from_file()
    print("Odds Division:")
    for team in divisions['odds']:
        print(team)
    print("\nEvens Division:")
    for team in divisions['evens']:
        print(team)
