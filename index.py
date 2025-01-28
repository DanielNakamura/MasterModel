from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def create_tables():
    conn = sqlite3.connect('jde.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS F4101 (
            ITEMNMBR TEXT PRIMARY KEY,
            ITEMDESC TEXT,
            ITEMTYPE TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS F4102 (
            ITEMNMBR TEXT,
            BRANCHPLANT TEXT,
            QUANTITY INTEGER,
            PRIMARY KEY (ITEMNMBR, BRANCHPLANT)
        )
    ''')
    conn.commit()
    conn.close()

def insert_fake_records():
    conn = sqlite3.connect('jde.db')
    cursor = conn.cursor()

    # Inserindo registros na F4101
    cursor.execute("INSERT OR IGNORE INTO F4101 (ITEMNMBR, ITEMDESC, ITEMTYPE) VALUES ('1001', 'Item 1001', 'Type A')")
    cursor.execute("INSERT OR IGNORE INTO F4101 (ITEMNMBR, ITEMDESC, ITEMTYPE) VALUES ('1002', 'Item 1002', 'Type B')")
    cursor.execute("INSERT OR IGNORE INTO F4101 (ITEMNMBR, ITEMDESC, ITEMTYPE) VALUES ('1003', 'Item 1003', 'Type C')")

    # Inserindo registros na F4102
    cursor.execute("INSERT OR IGNORE INTO F4102 (ITEMNMBR, BRANCHPLANT, QUANTITY) VALUES ('1001', 'Branch 1', 50)")
    cursor.execute("INSERT OR IGNORE INTO F4102 (ITEMNMBR, BRANCHPLANT, QUANTITY) VALUES ('1002', 'Branch 2', 30)")

    conn.commit()
    conn.close()

def fetch_dropdown_data():
    conn = sqlite3.connect('jde.db')
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT BRANCHPLANT FROM F4102")
    branch_plants = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT ITEMNMBR FROM F4101")
    items = [row[0] for row in cursor.fetchall()]

    conn.close()
    return branch_plants, items

@app.route('/')
def index():
    branch_plants, items = fetch_dropdown_data()
    return render_template('index.html', branch_plants=branch_plants, items=items)

@app.route('/submit', methods=['POST'])
def submit():
    model_item = request.form['model_item']
    new_item = request.form['new_item']
    
    conn = sqlite3.connect('jde.db')
    cursor = conn.cursor()

    differences = []

    # Verificar se o model_item existe na tabela F4102
    model_result = cursor.execute(
        "SELECT BRANCHPLANT, QUANTITY FROM F4102 WHERE ITEMNMBR = ?", (model_item,)
    ).fetchone()

    if model_result:
        # Verificar se o new_item já existe em F4102
        f4102_exists = cursor.execute(
            "SELECT * FROM F4102 WHERE ITEMNMBR = ?", (new_item,)
        ).fetchone()

        if not f4102_exists:
            # Gerar comando de INSERT para o new_item baseado no model_item
            branch_plant, quantity = model_result
            insert_command_f4102 = f"INSERT INTO F4102 (ITEMNMBR, BRANCHPLANT, QUANTITY) VALUES ('{new_item}', '{branch_plant}', {quantity});"
            differences.append(f"New item {new_item} does not exist in F4102.")
            differences.append(f"SQL Command: {insert_command_f4102}")
        else:
            differences.append(f"New item {new_item} already exists in F4102. No action needed.")
    else:
        differences.append(f"Model item {model_item} does not exist in F4102. Cannot generate SQL for F4102.")

    conn.close()

    # Renderizar o template com os resultados
    return render_template('results.html', model_item=model_item, new_item=new_item, differences=differences)

if __name__ == '__main__':
    create_tables()
    insert_fake_records()
    app.run(debug=True)