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
@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/reservation')
def reservation():
    return render_template('reservation.html')


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