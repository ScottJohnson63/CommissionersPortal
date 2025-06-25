# API entry point for backend logic
from flask import Flask, request, jsonify
from lib import utils, validateSchedule, divisionDecider, leagueScheduler, lotteryPicker
from lib.utils import load_config
from lib.lotteryPicker import run_lottery_backend
from lib.leagueScheduler import generate_schedule_backend
from lib.validateSchedule import validate_schedule_backend
from lib.leagueReviewer import review_league_backend
import os

app = Flask(__name__)

@app.route('/api/config', methods=['GET'])
def get_config():
    config = utils.load_config()
    return jsonify(config)

@app.route('/api/league/review', methods=['POST'])
def review_league():
    data = request.get_json()
    result = data.get('result')
    config = data.get('config')
    review = review_league_backend(result, config)
    return jsonify(review)

@app.route('/api/lottery', methods=['POST'])
def run_lottery():
    data = request.get_json()
    league_name = data.get('league_name')
    result = run_lottery_backend(league_name)
    return jsonify(result)

@app.route('/api/divisions', methods=['GET'])
def get_divisions():
    divisions = divisionDecider.get_divisions_from_file()
    return jsonify(divisions)

@app.route('/api/scheduler/generate', methods=['POST'])
def generate_schedule():
    config = request.get_json()
    schedule = generate_schedule_backend(config)
    return jsonify({'schedule': schedule})

@app.route('/api/scheduler/validate', methods=['POST'])
def validate_schedule():
    data = request.get_json()
    schedule = data.get('schedule')
    config = data.get('config')
    results = validate_schedule_backend(schedule, config)
    return jsonify({'validation': results})

# Add more endpoints for each backend function as needed

if __name__ == '__main__':
    app.run(debug=True, port=5000)
