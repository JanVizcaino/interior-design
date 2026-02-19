import os
import json

models_dir = "public/models"

files = [f for f in os.listdir(models_dir) if f.endswith('.glb')]
files.sort()

output_path = os.path.join(models_dir, "index.json")
with open(output_path, 'w') as f:
    json.dump(files, f, indent=2)

print(f"index.json generado con {len(files)} modelos:")
for f in files:
    print(f"  - {f}")