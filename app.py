from flask import Flask, render_template
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
    return render_template('menu.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/reservation')
def reservation():
    return render_template('reservation.html')

if __name__ == '__main__':
    app.run(debug=True)