from sentence_transformers import SentenceTransformer
import json

# Load the model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


def embed_text(text):
    return model.encode(text).tolist()


input_file_path = 'summary_dataset.json'
output_file_path = 'embeddings_dataset.json'

# Load your data
with open(input_file_path, 'r') as file:
    data = json.load(file)

# Initialize a counter to track progress
counter = 0
total = len(data)
print(f"Total entries to process: {total}")

# Process the data
processed_data = []
for entry in data:
    # Update and display the counter
    counter += 1
    print(f"Processing entry {counter} of {total}...")

    entry['embedding'] = embed_text(entry['summary'])
    del entry['summary']  # Remove the summary field
    processed_data.append(entry)

# Write the modified data to the output json file
with open(output_file_path, 'w') as file:
    json.dump(processed_data, file)

print(f"Processing complete. Output saved to {output_file_path}.")
