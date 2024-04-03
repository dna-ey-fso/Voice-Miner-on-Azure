from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import json
import csv
import time
import pygame

app = Flask(__name__)

# Initialize pygame mixer
pygame.init()

# Create uploads folder if it doesn't exist
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# Create feedback.csv if it doesn't exist
CSV_FILE_PATH = 'feedback.csv'
if not os.path.exists(CSV_FILE_PATH):
    with open(CSV_FILE_PATH, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ['Run Date', 'JSON File Name', 'Accuracy', 'Completeness', 'Coherence', 'Relevancy', 'Time Savings',
             'Feedback from the user', 'Liked'])


# Function to load JSON file
def load_json(filename):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return None


# Function to save feedback to CSV
def save_feedback(data):
    with open(CSV_FILE_PATH, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)


# Global variables
transcription_lines = []
summary = ''
operator_summary = ''


@app.route('/', methods=['GET', 'POST'])
def index():
    global transcription_lines, summary, operator_summary

    if request.method == 'POST':
        # Check if user wants to play audio
        play_audio = request.form.get('play_audio')

        if 'pause_audio' in request.form:
            pygame.mixer.music.stop()
            return redirect(url_for('index'))

        # Get audio file from request
        audio_file = request.files['audio_file']

        # Check if the file is selected
        if audio_file.filename == '':
            return render_template('index.html')

        # Save audio file
        audio_filename = secure_filename(audio_file.filename)
        audio_file_path = os.path.join('uploads', audio_filename)
        audio_file.save(audio_file_path)

        # Find corresponding JSON file
        json_filename = os.path.splitext(audio_filename)[0] + '.json'
        json_file_path = os.path.join('result', json_filename)

        # Load JSON data
        json_data = load_json(json_file_path)
        if json_data is not None:
            transcription = json_data.get('transcription', 'No transcription available.')
            transcription_lines = []
            for line in transcription.split('\n'):
                if line.strip().startswith('AG Operator:'):
                    transcription_lines.append({'speaker': 'AG Operator', 'text': line.strip()[12:], 'color': 'blue'})
                elif line.strip().startswith('Caller:'):
                    transcription_lines.append({'speaker': 'Caller', 'text': line.strip()[7:], 'color': 'green'})
            summary = json_data.get('summary', 'No summary available.')
            operator_summary = json_data.get('operator summary', 'No operator summary available.')
        else:
            transcription_lines = [{'speaker': 'No speaker', 'text': 'No transcription available.', 'color': 'black'}]
            summary = 'No summary available.'
            operator_summary = 'No operator summary available.'

        if play_audio == 'yes':
            # Play audio
            pygame.mixer.music.load(audio_file_path)
            pygame.mixer.music.play()

    return render_template('index.html', transcription_lines=transcription_lines, summary=summary,
                           operator_summary=operator_summary)


@app.route('/like', methods=['POST'])
def like():
    liked = request.form.get('liked', '')
    accuracy = int(request.form.get('accuracy', 0))
    completeness = int(request.form.get('completeness', 0))
    coherence = int(request.form.get('coherence', 0))
    relevancy = int(request.form.get('relevancy', 0))
    time_savings = request.form.get('time_savings', '')
    feedback_user = request.form.get('feedback_user', '')
    run_date = time.strftime('%Y-%m-%d %H:%M:%S')
    save_feedback([run_date, accuracy, completeness, coherence, relevancy, time_savings, feedback_user, liked])

    # Clear the fields
    transcription_lines = []
    summary = ''
    operator_summary = ''

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
