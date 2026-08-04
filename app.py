from flask import Flask, render_template,request
import pymysql
import config

app = Flask(__name__)

def get_db_connection():
    connection = pymysql.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DB
    )
    return connection

@app.route('/')
def accueil():
    return render_template('index.html')

@app.route('/menu')
def menu():
    conn = get_db_connection()
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
if __name__ == '__main__':
    app.run(debug=True)