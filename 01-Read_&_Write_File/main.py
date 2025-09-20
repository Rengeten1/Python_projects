import json
import os

# Get all JSON files in the "01-Read_&_Write_File" directory
json_files = [f for f in os.listdir("01-Read_&_Write_File") if f.startswith("jack") or f.startswith("troy")]

# Dictionary to store team data
team_data = {}

# Read all JSON files and add them to the dictionary
for idx, filename in enumerate(json_files, start=1):
    with open(os.path.join("01-Read_&_Write_File", filename), "r", encoding="utf-8") as f:
        team_data[f"Member {idx}"] = json.load(f)


output_filename = "01-Read_&_Write_File/combined.json"

# Write combined JSON to the output file
with open(output_filename, "w", encoding="utf-8") as f_out:
    json.dump(team_data, f_out, ensure_ascii=False, indent=4)

# Print to the screen
print(json.dumps(team_data, indent=4, ensure_ascii=False))

