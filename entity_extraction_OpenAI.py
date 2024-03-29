import openai
import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

# Initialize OpenAI API
openai.api_key = 'your_openai_api_key_here'


# Function to process text files in directories
def process_files(root_dir):
    data = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.txt') and not file.endswith('_corrected.txt'):
                file_path = os.path.join(root, file)
                # Check if the file is empty
                if os.path.getsize(file_path) == 0:
                    continue
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    # Skip processing if the text is empty
                    if not text.strip():
                        continue

                    # Analyze the conversation using OpenAI's language model
                    result = analyze_conversation(text)

                    data.append({
                        'Root Directory': root,
                        'Subfolder': os.path.basename(root),
                        'Sub Subfolder': os.path.basename(os.path.dirname(root)),
                        'Filename': file,
                        **result
                    })
    return data


# Function to analyze conversation using OpenAI's language model
def analyze_conversation(text):
    # Define the prompt with context and potential entities
    prompt = """
    Imagine you are an agent tasked with analyzing calls between operators and agents in an insurance underwriting context. You need to analyze the calls and extract the calls entities based on the conversation. Here are some typical scenarios encountered in such calls:

    - **Revision of Price:** The caller (agent) wants to negotiate or discuss the pricing of a particular insurance policy. This may involve asking for discounts, adjusting premiums, or exploring alternative pricing options.
    - **Adding New Coverage on a Vehicle:** The caller (agent) is interested in adding additional coverage to an existing insurance policy, specifically related to a vehicle. This could include adding comprehensive coverage, collision coverage, or coverage for specific vehicle accessories.
    - **Follow-up on a Claim:** The caller (agent) is following up on a previously filed insurance claim. This may involve checking the status of the claim, providing additional documentation or information requested by the insurer, or seeking clarification on claim-related matters.
    - **Policy Inquiry:** The caller (agent) has general inquiries about an insurance policy or coverage options. This could include questions about policy terms and conditions, coverage limits, deductibles, or eligibility criteria.
    - **Renewal Process:** The caller (agent) is inquiring about or discussing the renewal process for an existing insurance policy. This may involve reviewing renewal options, updating policy details, or addressing any changes in coverage or premiums.
    - **Cancellation Request:** The caller (agent) wants to cancel an existing insurance policy. This could be due to various reasons such as a change in circumstances, dissatisfaction with the coverage or service, or finding a better deal elsewhere.

    Additionally, there may be other topics or reasons for calls that are not listed above. Your task is to analyze the conversation between the operator and the agent and classify the call reason into one of the provided categories or any other relevant category based on the context and topics discussed. Ensure that your classification is accurate and reflects the primary purpose or objective of the call.

    **Potential Entities:**

    | Entity Group | Entity Name | Entity Description | Format |
    |--------------|-------------|--------------------|--------|
    | Client | Client Name | Client full name or company full name | Text |
    | Operator | Operator Name | Name of the AG operator picking up the call | Text |
    | Broker | Broker Name | Broker or agency name | Text |
    | Contract | Contract Number | Contract or dossier number | 12 characters (alphanumeric) |
    | Contract | Offer Number | Offer number | Text |
    | Contract | Premium Amount | Amount of premium, can be multiple | Numeric |
    | Contract | Branch | Type of insurance (Auto, Fire, Liability) | Text |
    | Contract | Policy Effective Dates | Start date of the policy | Date |
    | Contract | Dossier Type | Contract grouping (Familis, Modulis, Modulis Easy, Fleet) | Text |
    | Contract | Dossier Number | Dossier number | 9 digits |

    Ensure that the extracted entities match the specified formats.

    Conversation:
    """ + text

    # Call OpenAI's language model to analyze the conversation
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None
    )

    # Parse the response and extract relevant information
    result = parse_response(response.choices[0].text)

    return result


# Function to parse the response from OpenAI's language model
def parse_response(response_text):
    # Placeholder implementation - Parse the response to extract entities, sentiment, and tone evolution
    # This needs to be tailored based on the structure of the response from OpenAI's language model
    entities = {
        'client_name': 'Jiri De Joghe',
        'operator_name': 'Clara Rosolen',
        'broker_name': 'AB Insurance',
        'contract_number': '1234567890',
        'offer_number': '0987654321',
        'premium_amount': '260.41€',
        'branch': 'Auto ',
        'policy_effect_date': '01 janvier 2024',
        'dossier_type': 'Familis',
        'dossier_number': '987654321',
    }

    sentiment = 'positive'
    helpfulness = True
    tone_evolution = 'Neutral'

    return {
        'entities': entities,
        'sentiment': sentiment,
        'helpfulness': helpfulness,
        'tone_evolution': tone_evolution
    }


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
    output_file = os.path.join(output_dir, 'data.csv')
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
# Example usage:
root_dir = 'C:/Users/DQ761VX/OneDrive - EY/Documents/Projects/AG_file/Data'  # Change this to the root directory you want to search
output_dir = 'C:/Users/DQ761VX/OneDrive - EY/Documents/Projects/AG_file'

data = process_files(root_dir)
plot_entity_frequency(data, output_dir)
plot_sentiment_analysis(data, output_dir)
save_to_csv(data, output_dir)
