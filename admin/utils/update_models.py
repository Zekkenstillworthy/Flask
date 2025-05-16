# Script to update all model files to use the main app's db
import os
import re

# Directory of admin models
models_dir = os.path.join(os.path.dirname(__file__), 'admin', 'models')

# List all python files in the models directory
model_files = [f for f in os.listdir(models_dir) if f.endswith('.py') and f != '__init__.py']

# Process each model file
for filename in model_files:
    filepath = os.path.join(models_dir, filename)
    print(f"Processing {filepath}")
    
    # Read the file content
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Check if import is from admin
    if 'from admin import db' in content:
        # Replace the import
        content = content.replace('from admin import db', 'from __init__ import db')
        
        # Add __table_args__ to all models if not already present
        # This is a simple pattern match and might need adjustment
        model_pattern = r'class\s+(\w+)\s*\(\s*db\.Model\s*\)\s*:\s*\n\s*__tablename__\s*=\s*[\'"]([\w_]+)[\'"]'
        replacement = r'class \1(db.Model):\n    __tablename__ = "\2"\n    __table_args__ = {"extend_existing": True}'
        
        # Apply the replacement
        content = re.sub(model_pattern, replacement, content)
        
        # Write the updated content back to the file
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)
        
        print(f"Updated {filename}")
    else:
        print(f"No changes needed for {filename}")

print("All model files processed")
