import numpy as np
import re
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Bidirectional
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.sequence import pad_sequences
from googletrans import Translator                                 
import pickle

                        
def load_shlokas_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.readlines()

def clean_shloka(text):
    text = re.sub(r'॥\s*\d+\s*\d*॥', '', text)
    text = re.sub(r'\|\|', '', text)                     
    return text.strip()

def extract_lines_from_shlokas(shlokas):
    lines = []
    for shloka in shlokas:
        parts = shloka.strip().split('।')
        for line in parts:
            cleaned = clean_shloka(line)
            if cleaned:
                lines.append(cleaned)
    return lines

def extract_full_shlokas(shlokas):
    full_shlokas = []
    buffer = []
    for line in extract_lines_from_shlokas(shlokas):
        buffer.append(line)
        if len(buffer) == 2:
            full_shlokas.append(tuple(buffer))
            buffer = []
    return full_shlokas

                       
raw_shlokas = load_shlokas_from_file('geetamain1.txt')
shloka_pairs = extract_full_shlokas(raw_shlokas)

                                             
full_lines = [f"{line1} {line2}" for line1, line2 in shloka_pairs]

              
tokenizer = Tokenizer()
tokenizer.fit_on_texts(full_lines)
total_words = len(tokenizer.word_index) + 1

                      
input_sequences = []
for line in full_lines:
    token_list = tokenizer.texts_to_sequences([line])[0]
    for i in range(1, len(token_list)):
        n_gram_sequence = token_list[:i+1]
        input_sequences.append(n_gram_sequence)

                   
sequence_length = max([len(seq) for seq in input_sequences])
input_sequences = pad_sequences(input_sequences, maxlen=sequence_length, padding='pre')

X = input_sequences[:, :-1]
y = to_categorical(input_sequences[:, -1], num_classes=total_words)

                 
model = Sequential()
model.add(Embedding(input_dim=total_words, output_dim=100, input_length=sequence_length - 1))
model.add(Bidirectional(LSTM(150)))
model.add(Dense(total_words, activation='softmax'))

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model.build(input_shape=(None, sequence_length - 1))
model.summary()

                 
model.fit(X, y, epochs=40, batch_size=32, verbose=1)

                                             
def generate_all_shlokas_from_seed(seed_text, shloka_pairs):
    seed_text = seed_text.strip()
    visited = set()                                                         

    def find_matching_shlokas(seed, pairs):
        matching_shlokas = []
        for line1, line2 in pairs:
            full_shloka = f"{line1} ।\n{line2}"                                    
            if full_shloka not in visited and (seed in line1 or seed in line2):
                matching_shlokas.append(full_shloka)                                 
                visited.add(full_shloka)                               
        return matching_shlokas

    matching_shlokas = find_matching_shlokas(seed_text, shloka_pairs)
    return matching_shlokas

                                       
def extract_chapter_and_verse(shloka):
    match = re.search(r'॥\s*(\d+)-(\d+)\s*॥', shloka)
    if match:
        chapter = match.group(1)                                              
        verse = match.group(2)                                               
        return f"This Shlok Belongs to Chapter {chapter}, Verse {verse}."
    else:
        return "Chapter and verse information not found."

                                 
def translate_shloka(shloka, target_language="en"):
    translator = Translator()
    try:
        translation = translator.translate(shloka, dest=target_language)
        return translation.text
    except Exception as e:
        return f"Error during translation: {e}"


                
model.save("shloka_model.h5")

with open("tokenizer.pkl", "wb") as f:
    pickle.dump(tokenizer, f)
