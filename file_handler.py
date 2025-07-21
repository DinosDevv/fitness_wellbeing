import json

#JSON FILE UTILS

def overwrite_json_file(file_path, data):
  try:
    with open(file_path, 'w') as file:
      json.dump(data, file, indent=4)
  except IOError as e:
      print(f"Error writing to file {file_path}: {e}")
    
def read_json_file(file_path):
  try:
      with open(file_path, 'r') as file:
          return json.load(file)
  except FileNotFoundError:
      return []
  except json.JSONDecodeError:
      return []
def append_to_json_file(file_path, data):
  try:
      existing_data = read_json_file(file_path)
  except FileNotFoundError:
      existing_data = []

  existing_data.append(data)
  
  overwrite_json_file(file_path, existing_data)
