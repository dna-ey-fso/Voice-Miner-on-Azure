import os
import csv
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

def detect_language(text):
    try:
        return detect(text)
    except LangDetectException:
        return "Unknown"

def process_folders(root_dir, output_file):
    i=0
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['Directory', 'Operator','Subdirectory','File', 'Language']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.endswith('.txt') and not filename.endswith('_corrected.txt'):
                    file_path = os.path.join(dirpath, filename)
                    subdirectory = os.path.relpath(dirpath, root_dir)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        text = file.read()
                        language = detect_language(text)
                        i+=1
                        print("We are at file ", i)
                        print( "Directory is ", root_dir)
                        print("File is ", filename)
                        print("language is ", language)
                        writer.writerow({'Directory': root_dir,'Operator' : os.path.basename(os.path.dirname(subdirectory)), 'Subdirectory': os.path.relpath(dirpath, root_dir), 'File': filename, 'Language': language})

if __name__ == "__main__":
    root_directory = 'C:/Users/DQ761VX/OneDrive - EY/Documents/Projects/AG_file/Data'  # Change this to the root directory you want to search
    output_csv_file = 'language_detection_results.csv'  # Change this to the desired output CSV file name
    process_folders(root_directory, output_csv_file)
