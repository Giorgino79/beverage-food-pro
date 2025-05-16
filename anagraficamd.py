import os
import datetime

def generate_anagrafica_markdown():
    markdown_content = f"""# Implementazione App Anagrafica - Backup Completo
    
## Data generazione: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
    
    # Mappa dei file da includere
    files_map = {
        'anagrafica/models.py': '## 1. Models.py',
        'anagrafica/forms.py': '## 2. Forms.py',
        'anagrafica/views.py': '## 3. Views.py',
        'anagrafica/urls.py': '## 4. URLs.py',
        'anagrafica/admin.py': '## 5. Admin.py',
        'anagrafica/tests.py': '## 6. Tests.py',
        'anagrafica/signals.py': '## 7. Signals.py',
    }
    
    for file_path, header in files_map.items():
        if os.path.exists(file_path):
            markdown_content += f"\n{header}\n\n```python\n"
            with open(file_path, 'r', encoding='utf-8') as f:
                markdown_content += f.read()
            markdown_content += "\n```\n\n"
    
    # Template files
    template_dir = 'anagrafica/templates/anagrafica'
    if os.path.exists(template_dir):
        markdown_content += "\n## 8. Templates\n\n"
        for root, dirs, files in os.walk(template_dir):
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    markdown_content += f"\n### {file}\n\n```html\n"
                    with open(file_path, 'r', encoding='utf-8') as f:
                        markdown_content += f.read()
                    markdown_content += "\n```\n\n"
    
    # Save to file
    with open('ANAGRAFICA_BACKUP_COMPLETO.md', 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print("Backup completo generato in ANAGRAFICA_BACKUP_COMPLETO.md")

if __name__ == "__main__":
    generate_anagrafica_markdown()