from flask import Flask, render_template

# Création de l'application Flask
# On lui indique que nos fichiers HTML sont dans le dossier 'frontend'
app = Flask(__name__, template_folder='frontend', static_folder='frontend')

@app.route('/')
def home():
    # Quand l'utilisateur va sur l'adresse principale (/), on affiche index.html
    return render_template('index.html')

if __name__ == '__main__':
    # Lancement du serveur local sur le port 5000
    app.run(debug=True, port=5000)
