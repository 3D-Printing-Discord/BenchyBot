import json
import os

# LOAD CONFIG 
print("Loading config... ", end =" ")
with open('config.json') as f:
  config_data = json.load(f)
print("done!")

# CHECK IF DATABASE EXISTS
if os.path.isfile(config_data['database']):
    print("Databse already exists!")
    exit()

print("Running all init files:")

for module in config_data['modules']:

    if os.path.exists(f"modules/{module}/init_database.py"):

        print(f"-- {module}... ", end =" ")

        os.system(f"python3 modules/{module}/init_database.py {config_data['database']}")
        
        print("done!")

print("Complete.\nDatabase is now ready for use.")