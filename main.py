from flask import Flask, render_template, request, jsonify
from utils.db import create_connection

app = Flask(__name__)

# Endpoint / 
@app.route('/')
def homepage():
    return render_template('index.html')

### API ###

# Endpoint API /api/docenti
@app.route('/api/docenti', methods=['GET'])
def get_docenti():
    connection = create_connection()

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT ID, Nome, Cognome, Email FROM Docente;")    
    docenti = cursor.fetchall()
    cursor.close()
    
    return jsonify(docenti), 200

# Endpoint API /api/aule
@app.route('/api/aule', methods=['GET'])
def get_aule():
    connection = create_connection()

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT ID FROM Aula;")    
    aule = cursor.fetchall()
    cursor.close()
    return jsonify(aule), 200

# Endpoint API /api/seminari
@app.route('/api/seminari', methods=['GET'])
def api_seminari():
    connection = create_connection()

    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.ID, s.Titolo, s.Orario, a.Capacita, d.Nome, d.Cognome 
        FROM Seminario s 
        JOIN Aula a ON s.AulaID = a.ID 
        JOIN Docente d ON s.DocenteID = d.ID 
        ORDER BY STR_TO_DATE(s.Orario, '%d/%m/%Y %h:%m:%s') ASC;
    """)
    seminari = cursor.fetchall()
    cursor.close()
    return jsonify(seminari), 200

# Endpoint API /api/prenotazioni
@app.route('/api/prenotazioni')
def api_prenotazioni():
    connection = create_connection()

    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.ID, p.NumeroStudenti, s.Titolo, s.Orario 
        FROM Prenotazioni p 
        JOIN Seminario s ON p.SeminarioID = s.ID;
    """)
    prenotazioni = cursor.fetchall()
    cursor.close()
    return jsonify(prenotazioni), 200

# Endpoint API /api/signup
@app.route('/api/signup', methods=['POST'])
def signup():
    connection = create_connection()

    data = request.json
    nome = data['Nome']
    cognome = data['Cognome']
    email = data['Email']
    password = data['Password']

    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO Docente (Nome, Cognome, Email, Password) 
        VALUES (%s, %s, %s, %s);
    """, (nome, cognome, email, password))
    connection.commit()
    cursor.close()
    return jsonify({'message': 'Docente registrato con successo!'})

# Endpoint API /api/insert/seminario
@app.route('/api/insert/seminario', methods=['POST'])
def insert_seminario():
    connection = create_connection()

    data = request.json
    titolo = data['Titolo']
    orario = data['Orario']
    aula_id = data['AulaID']
    docente_id = data['DocenteID']

    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO Seminario (Titolo, Orario, AulaID, DocenteID) 
        VALUES (%s, %s, %s, %s);
    """, (titolo, orario, aula_id, docente_id))
    connection.commit()
    cursor.close()
    return jsonify({'message': 'Seminario inserito con successo!'})

# Endpoint API /api/book
@app.route('/api/book', methods=['POST'])
def book_seminario():
    connection = create_connection()

    data = request.json
    seminario_id = data['SeminarioID']
    numero_studenti = int(data['NumeroStudenti'])

    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.Capacita, COALESCE(SUM(p.NumeroStudenti), 0) AS TotalePrenotati 
        FROM Seminario s 
        JOIN Aula a ON s.AulaID = a.ID 
        LEFT JOIN Prenotazioni p ON s.ID = p.SeminarioID 
        WHERE s.ID = %s 
        GROUP BY a.Capacita;
    """, (seminario_id,))
    result = cursor.fetchone()
    if not result or result['TotalePrenotati'] + numero_studenti > result['Capacita']:
        return jsonify({'error': 'Capacità aula superata!'}), 400

    cursor.execute("""
        INSERT INTO Prenotazioni (SeminarioID, NumeroStudenti) 
        VALUES (%s, %s);
    """, (seminario_id, numero_studenti))
    connection.commit()
    cursor.close()
    return jsonify({'message': 'Prenotazione effettuata con successo!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3452, debug=True)