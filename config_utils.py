import json
config_path = '/root/DBEDA/config.json'

# Load config
print("Loading config from")
with open(config_path, 'r') as json_file:
    config = json.load(json_file)
print("Loading config successful!")
    