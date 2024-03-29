import os
import csv
import re
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from langdetect import detect
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

# Load pre-trained BERT models and tokenizer for Dutch and French sentiment analysis
tokenizer_nl = BertTokenizer.from_pretrained("wietsedv/bert-base-dutch-cased")
model_nl = BertForSequenceClassification.from_pretrained("wietsedv/bert-base-dutch-cased", num_labels=2)

tokenizer_fr = BertTokenizer.from_pretrained("dbmdz/bert-base-french-europeana-cased")
model_fr = BertForSequenceClassification.from_pretrained("dbmdz/bert-base-french-europeana-cased", num_labels=2)

# Initialize spaCy models for French and Dutch
nlp_fr = spacy.load("fr_core_news_sm")
nlp_nl = spacy.load("nl_core_news_sm")

# Initialize sentiment analyzer
analyzer = SentimentIntensityAnalyzer()


# Function to detect operator's helpfulness and tone evolution using BERT for sentiment analysis
def detect_helpfulness_and_tone_evolution(text, language):
    if language == 'nl':
        nlp = nlp_nl
    elif language == 'fr':
        nlp = nlp_fr
    else:
        raise ValueError("Invalid language. Supported languages are 'nl' for Dutch and 'fr' for French.")

    doc = nlp(text)

    # Detect politeness and escalation based on syntactic and semantic cues
    polite = any(token.text.lower() in ['please', 'dank', 'merci'] for token in doc)
    escalation = any(token.text.lower() in ['supervisor', 'escalate', 'probleem', 'non résolu'] for token in doc)

    # Determine helpfulness based on sentiment analysis
    # (Implementation of sentiment analysis using BERT or other models can be integrated here)
    helpfulness = True  # Placeholder, replace with actual sentiment analysis

    # Determine tone evolution
    tone_evolution = 'Neutral'  # Default to neutral
    if polite:
        tone_evolution = 'Polite'
    elif escalation:
        tone_evolution = 'Escalated'

    return helpfulness, tone_evolution


# Function to extract entities from text using spaCy
def extract_entities(text, language):
    entities = {
        'client_name': [],
        'operator_name': [],
        'broker_name': [],
        'contract_number': [],
        'offer_number': [],
        'premium_amount': [],
        'branch': [],
        'policy_effect_date': [],
        'dossier_type': [],
        'dossier_number': []
    }

    if language == 'nl':
        doc = nlp_nl(text.lower())
    elif language == 'fr':
        doc = nlp_fr(text.lower())
    else:
        raise ValueError("Invalid language. Supported languages are 'nl' for Dutch and 'fr' for French.")

    # Extract entities
    for ent in doc.ents:
        if ent.label_ == 'PER':  # Person's name
            entities['client_name'].append(ent.text.title())  # Capitalize first letter of each word
        elif ent.label_ == 'ORG':  # Organization name
            entities['broker_name'].append(ent.text.title())  # Capitalize first letter of each word
        elif ent.label_ == 'DATE':  # Date
            entities['policy_effect_date'].append(ent.text)
        elif ent.label_ == 'CARDINAL':  # Contract number, offer number, dossier number
            if len(ent.text) == 12:  # Contract number
                entities['contract_number'].append(ent.text)
            elif len(ent.text) == 9:  # Dossier number
                entities['dossier_number'].append(ent.text)
            else:  # Offer number (assuming it's numeric)
                entities['offer_number'].append(ent.text)
        elif ent.label_ == 'MONEY':  # Premium amount
            entities['premium_amount'].append(ent.text)
        elif ent.label_ == 'LOC':  # Branch
            entities['branch'].append(ent.text)
        elif ent.label_ == 'ORG':  # Dossier Type
            entities['dossier_type'].append(ent.text)
        # Add other entity types as needed

    return entities


# Function to perform sentiment analysis using Vader
def perform_sentiment_analysis(text):
    scores = analyzer.polarity_scores(text)
    compound_score = scores['compound']
    if compound_score >= 0.05:
        sentiment_description = 'positive'
    elif compound_score <= -0.05:
        sentiment_description = 'negative'
    else:
        sentiment_description = 'neutral'
    return sentiment_description


# Function to detect language
def detect_language(text):
    return detect(text)


# Function to process text files in directories
def process_files(root_dir, use_transformers=True):
    data = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.txt') and not file.endswith('_corrected.txt'):
                file_path = os.path.join(root, file)
                # Check if the file is empty
                if os.path.getsize(file_path) == 0:
                    continue
                with open(file_path, 'r', encoding='utf-8',errors='ignore') as f:
                    text = f.read()
                    # Skip processing if the text is empty
                    if not text.strip():
                        continue

                    # Automatically detect language of the text
                    language = detect_language(text)

                    # Perform sentiment analysis and detect operator's helpfulness and tone evolution
                    if use_transformers:
                        helpfulness, tone_evolution = detect_helpfulness_and_tone_evolution(text, language)
                    else:
                        sentiment_analysis = perform_sentiment_analysis(text)
                        helpfulness, tone_evolution = detect_helpfulness_and_tone_evolution(text, language)

                    # Extract entities
                    entities = extract_entities(text, language)

                    # Deduplicate entities
                    for key, value in entities.items():
                        entities[key] = list(set(value))

                    # Compute sentiment for the entire conversation
                    sentiment = perform_sentiment_analysis(text)

                    data.append({
                        'Root Directory': root,
                        'Subfolder': os.path.basename(root),
                        'Sub Subfolder': os.path.basename(os.path.dirname(root)),
                        'Filename': file,
                        **entities,
                        'sentiment': sentiment,
                        'helpfulness': helpfulness,
                        'tone_evolution': tone_evolution
                    })
    return data


# Function to plot entity frequency
def plot_entity_frequency(data, output_dir):
    entity_counts = Counter()
    for entry in data:
        entity_counts[entry['sentiment']] += 1

    plt.bar(entity_counts.keys(), entity_counts.values())
    plt.xlabel('Sentiment')
    plt.ylabel('Frequency')
    plt.title('Sentiment Analysis')
    plt.savefig(os.path.join(output_dir, 'sentiment_analysis.png'))
    plt.close()

# Function to plot sentiment analysis results
def plot_sentiment_analysis(data, output_dir):
    sentiments = [entry['sentiment'] for entry in data]
    sentiment_counts = Counter(sentiments)
    plt.bar(sentiment_counts.keys(), sentiment_counts.values())
    plt.xlabel('Sentiment')
    plt.ylabel('Frequency')
    plt.title('Sentiment Analysis')
    plt.savefig(os.path.join(output_dir, 'sentiment_analysis.png'))
    plt.close()


# Function to save data to CSV
def save_to_csv(data, output_dir):
    output_file = os.path.join(output_dir, 'entity_extraction.csv')
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Root Directory', 'Subfolder', 'Sub Subfolder', 'Filename',
                      'client_name', 'operator_name', 'broker_name', 'contract_number',
                      'offer_number', 'premium_amount', 'branch', 'policy_effect_date',
                      'dossier_type', 'dossier_number', 'sentiment', 'helpfulness',
                      'tone_evolution']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


# Example usage:
root_dir = 'C:/Users/DQ761VX/OneDrive - EY/Documents/Projects/AG_file/Data'  # Change this to the root directory you want to search
output_dir = 'C:/Users/DQ761VX/OneDrive - EY/Documents/Projects/AG_file'

data = process_files(root_dir)
plot_entity_frequency(data, output_dir)
plot_sentiment_analysis(data, output_dir)
save_to_csv(data, output_dir)
