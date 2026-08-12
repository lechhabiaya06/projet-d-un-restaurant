from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import config

app = Flask(__name__)
app.secret_key = 'bewok_cle_secrete_2026'
#gestion d'erreur de base de donnee:
   #try/except : Python essaie de se connecter à la base 
   #  si ça échoue (except),
   #  au lieu de faire planter tout le site avec un message technique, 
   # on renvoie simplement None. La route vérifie ensuite if conn is None:
   #  et affiche notre page 500 personnalisée au lieu de l'erreur brute.
def get_db_connection():
    try:
        connection = pymysql.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DB
        )
        return connection
    except Exception as e:
        return None

@app.route('/')
def accueil():
    return render_template('index.html')
#gestion d'erreur de base de donnee
@app.route('/menu')
def menu():
    conn = get_db_connection()
    if conn is None:
        return render_template('500.html'), 500

    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM plats")
    plats = cursor.fetchall()
    conn.close()
    return render_template('menu.html', plats=plats)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    message_confirmation = None
    if request.method == 'POST':
        nom = request.form['nom']
        email = request.form['email']
        message = request.form['message']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (nom, email, message) VALUES (%s, %s, %s)",
            (nom, email, message)
        )
        conn.commit()
        conn.close()

        message_confirmation = "Votre message a bien été envoyé. Nous vous répondrons rapidement !"

    return render_template('contact.html', message_confirmation=message_confirmation)


@app.route('/reservation', methods=['GET', 'POST'])
def reservation():
    message = None
    if request.method == 'POST':
        nom = request.form['nom']
        telephone = request.form['telephone']
        date = request.form['date']
        heure = request.form['heure']
        nb_personnes = request.form['nb_personnes']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reservations (nom, telephone, date, heure, nb_personnes) VALUES (%s, %s, %s, %s, %s)",
            (nom, telephone, date, heure, nb_personnes)
        )
        conn.commit()
        conn.close()

        message = "Votre réservation a bien été enregistrée. Nous vous contacterons pour la confirmer !"

    return render_template('reservation.html', message=message)


@app.route('/commander', methods=['POST'])
def commander():
    ids_plats = request.form.getlist('plat_id')

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    total = 0
    infos_plats = []
    for plat_id in ids_plats:
        cursor.execute("SELECT * FROM plats WHERE id = %s", (plat_id,))
        plat = cursor.fetchone()
        infos_plats.append(plat)
        total = total + float(plat['prix'])

    cursor.execute(
        "INSERT INTO commandes (date, statut, total) VALUES (NOW(), 'en attente', %s)",
        (total,)
    )
    commande_id = cursor.lastrowid

    for plat in infos_plats:
        cursor.execute(
            "INSERT INTO lignes_commande (commande_id, plat_id, quantite, prix_unitaire) VALUES (%s, %s, %s, %s)",
            (commande_id, plat['id'], 1, plat['prix'])
        )

    conn.commit()
    conn.close()

    return f"Commande n°{commande_id} enregistrée avec succès ! Total : {total} Dhs"


@app.route('/login', methods=['GET', 'POST'])
def login():
    erreur = None
    if request.method == 'POST':
        email = request.form['email']
        mot_de_passe = request.form['mot_de_passe']

        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM utilisateurs WHERE email = %s", (email,))
        utilisateur = cursor.fetchone()
        conn.close()

        if utilisateur and check_password_hash(utilisateur['mot_de_passe'], mot_de_passe) and utilisateur['role'] == 'admin':
            session['admin_connecte'] = True
            session['admin_nom'] = utilisateur['nom']
            return redirect(url_for('dashboard'))
        else:
            erreur = "Email ou mot de passe incorrect."

    return render_template('login.html', erreur=erreur)


@app.route('/logout')
def logout():
    session.pop('admin_connecte', None)
    session.pop('admin_nom', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not session.get('admin_connecte'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT COUNT(*) AS total FROM plats")
    nb_plats = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM commandes")
    nb_commandes = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM reservations")
    nb_reservations = cursor.fetchone()['total']

    cursor.execute("SELECT * FROM commandes ORDER BY id DESC LIMIT 5")
    dernieres_commandes = cursor.fetchall()

    cursor.execute("SELECT * FROM reservations ORDER BY id DESC LIMIT 5")
    dernieres_reservations = cursor.fetchall()

    conn.close()

    return render_template('dashboard.html',
        nb_plats=nb_plats,
        nb_commandes=nb_commandes,
        nb_reservations=nb_reservations,
        dernieres_commandes=dernieres_commandes,
        dernieres_reservations=dernieres_reservations
    )

@app.route('/admin/plats')
def admin_plats():
    if not session.get('admin_connecte'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT plats.*, categories.nom AS categorie_nom FROM plats JOIN categories ON plats.categorie_id = categories.id")
    plats = cursor.fetchall()
    conn.close()

    return render_template('admin_plats.html', plats=plats)
@app.route('/admin/plats/ajouter', methods=['GET', 'POST'])
def admin_plats_ajouter():
    if not session.get('admin_connecte'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()

    if request.method == 'POST':
        nom = request.form['nom']
        description = request.form['description']
        prix = request.form['prix']
        image = request.form['image']
        categorie_id = request.form['categorie_id']

        cursor.execute(
            "INSERT INTO plats (nom, description, prix, image, categorie_id) VALUES (%s, %s, %s, %s, %s)",
            (nom, description, prix, image, categorie_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('admin_plats'))

    conn.close()
    return render_template('admin_plat_form.html', categories=categories, plat=None)
@app.route('/admin/plats/modifier/<int:id>', methods=['GET', 'POST'])
def admin_plats_modifier(id):
    if not session.get('admin_connecte'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()

    if request.method == 'POST':
        nom = request.form['nom']
        description = request.form['description']
        prix = request.form['prix']
        image = request.form['image']
        categorie_id = request.form['categorie_id']

        cursor.execute(
            "UPDATE plats SET nom=%s, description=%s, prix=%s, image=%s, categorie_id=%s WHERE id=%s",
            (nom, description, prix, image, categorie_id, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('admin_plats'))

    cursor.execute("SELECT * FROM plats WHERE id = %s", (id,))
    plat = cursor.fetchone()
    conn.close()

    return render_template('admin_plat_form.html', categories=categories, plat=plat)
@app.route('/admin/plats/supprimer/<int:id>')
def admin_plats_supprimer(id):
    if not session.get('admin_connecte'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM plats WHERE id = %s", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_plats'))


@app.route('/admin/categories/ajouter', methods=['GET', 'POST'])
def admin_categories_ajouter():
    if not session.get('admin_connecte'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        nom = request.form['nom']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categories (nom) VALUES (%s)", (nom,))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_categories'))

    return render_template('admin_categorie_form.html', categorie=None)
@app.route('/admin/categories')
def admin_categories():
    if not session.get('admin_connecte'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    conn.close()

    return render_template('admin_categories.html', categories=categories)


@app.route('/admin/categories/modifier/<int:id>', methods=['GET', 'POST'])
def admin_categories_modifier(id):
    if not session.get('admin_connecte'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        nom = request.form['nom']
        cursor.execute("UPDATE categories SET nom=%s WHERE id=%s", (nom, id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_categories'))

    cursor.execute("SELECT * FROM categories WHERE id = %s", (id,))
    categorie = cursor.fetchone()
    conn.close()

    return render_template('admin_categorie_form.html', categorie=categorie)


@app.route('/admin/categories/supprimer/<int:id>')
def admin_categories_supprimer(id):
    if not session.get('admin_connecte'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categories WHERE id = %s", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_categories'))

@app.route('/admin/commandes')
def admin_commandes():
    if not session.get('admin_connecte'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM commandes ORDER BY id DESC")
    commandes = cursor.fetchall()
    conn.close()

    return render_template('admin_commandes.html', commandes=commandes)


@app.route('/admin/commandes/statut/<int:id>', methods=['POST'])
def admin_commandes_statut(id):
    if not session.get('admin_connecte'):
        return redirect(url_for('login'))

    nouveau_statut = request.form['statut']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE commandes SET statut=%s WHERE id=%s", (nouveau_statut, id))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_commandes'))
@app.route('/admin/reservations')
def admin_reservations():
    if not session.get('admin_connecte'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM reservations ORDER BY id DESC")
    reservations = cursor.fetchall()
    conn.close()

    return render_template('admin_reservations.html', reservations=reservations)


@app.route('/admin/reservations/annuler/<int:id>')
def admin_reservations_annuler(id):
    if not session.get('admin_connecte'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reservations WHERE id = %s", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_reservations'))

@app.errorhandler(404)
def page_non_trouvee(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def erreur_serveur(e):
    return render_template('500.html'), 500
if __name__ == '__main__':
    app.run(debug=True)
