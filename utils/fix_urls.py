import os
import glob

replacements = {
    "url_for('login')": "url_for('auth.login')",
    "url_for('register')": "url_for('auth.register')",
    "url_for('logout')": "url_for('auth.logout')",
    "url_for('dashboard')": "url_for('dashboard.index')",
    "url_for('contacts')": "url_for('contacts.index')",
    "url_for('analytics')": "url_for('dashboard.analytics')",
    "url_for('export_messages')": "url_for('dashboard.export_messages')",
    "url_for('agenda')": "url_for('agenda.index')",
    "url_for('instructions')": "url_for('settings.instructions')",
    "url_for('settings_page')": "url_for('settings.index')",
    "url_for('security')": "url_for('settings.security')",
    "url_for('add_contact')": "url_for('contacts.add_contact')",
    "url_for('delete_contact'": "url_for('contacts.delete_contact'",
    "url_for('clear_space')": "url_for('settings.clear_space')"
}

frontend_path = "C:/Users/HP/OneDrive/Desktop/Projet/FAQ_Chat-bot/frontend"
html_files = glob.glob(os.path.join(frontend_path, "*.html"))

for file_path in html_files:
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        
    for old, new in replacements.items():
        content = content.replace(old, new)
        
    # Extra fix for request.endpoint inside base.html
    content = content.replace("request.endpoint == 'dashboard'", "request.endpoint == 'dashboard.index'")
    content = content.replace("request.endpoint == 'agenda'", "request.endpoint == 'agenda.index'")
    content = content.replace("request.endpoint == 'instructions'", "request.endpoint == 'settings.instructions'")
    content = content.replace("request.endpoint == 'contacts'", "request.endpoint == 'contacts.index'")
    content = content.replace("request.endpoint == 'analytics'", "request.endpoint == 'dashboard.analytics'")
    content = content.replace("request.endpoint == 'security'", "request.endpoint == 'settings.security'")
    content = content.replace("request.endpoint == 'settings_page'", "request.endpoint == 'settings.index'")

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

print("URL replacements completed.")
