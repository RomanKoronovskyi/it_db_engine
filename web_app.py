import os
from flask import Flask, render_template, request, jsonify
from core import DataType, Table
from storage import Database

app = Flask(__name__)

DB_FILE = "test_db.json"

def get_db() -> Database:
    if os.path.exists(DB_FILE):
        try:
            return Database.load_from_file(DB_FILE)
        except Exception:
            pass
    return Database("WebEnterpriseDB")

db = get_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/state", methods=["GET"])
def get_state():
    return jsonify({
        "db_name": db.name,
        "tables": list(db.tables.keys())
    })

@app.route("/api/tables", methods=["POST"])
def create_table():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Назва таблиці не може бути порожньою"}), 400
    try:
        db.create_table(name)
        db.save_to_file(DB_FILE)
        return jsonify({"status": "ok", "name": name})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/tables/<table_name>", methods=["DELETE"])
def drop_table(table_name: str):
    try:
        db.drop_table(table_name)
        db.save_to_file(DB_FILE)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/tables/<table_name>", methods=["GET"])
def get_table_data(table_name: str):
    table = db.get_table(table_name)
    if not table:
        return jsonify({"error": "Таблицю не знайдено"}), 404
    return jsonify({
        "name": table.name,
        "columns": [c.to_dict() for c in table.columns],
        "rows": [r.to_dict() for r in table.rows]
    })

@app.route("/api/tables/<table_name>/columns", methods=["POST"])
def add_column(table_name: str):
    table = db.get_table(table_name)
    if not table:
        return jsonify({"error": "Таблицю не знайдено"}), 404
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    col_type = data.get("data_type", "")
    try:
        table.add_column(name, DataType(col_type))
        db.save_to_file(DB_FILE)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/tables/<table_name>/columns/rename", methods=["POST"])
def rename_column(table_name: str):
    table = db.get_table(table_name)
    if not table:
        return jsonify({"error": "Таблицю не знайдено"}), 404
    data = request.get_json() or {}
    col_index = data.get("col_index")
    new_name = data.get("new_name", "").strip()
    try:
        table.rename_column(int(col_index), new_name)
        db.save_to_file(DB_FILE)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/tables/<table_name>/columns/swap", methods=["POST"])
def swap_columns(table_name: str):
    table = db.get_table(table_name)
    if not table:
        return jsonify({"error": "Таблицю не знайдено"}), 404
    data = request.get_json() or {}
    idx_a = data.get("index_a")
    idx_b = data.get("index_b")
    try:
        table.swap_columns(int(idx_a), int(idx_b))
        db.save_to_file(DB_FILE)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/tables/<table_name>/rows", methods=["POST"])
def add_row(table_name: str):
    table = db.get_table(table_name)
    if not table:
        return jsonify({"error": "Таблицю не знайдено"}), 404
    data = request.get_json() or {}
    raw_values = data.get("values", [])
    try:
        row = table.add_row(raw_values)
        db.save_to_file(DB_FILE)
        return jsonify({"status": "ok", "row_id": row.id})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/tables/<table_name>/rows/<row_id>", methods=["PUT"])
def update_row(table_name: str, row_id: str):
    table = db.get_table(table_name)
    if not table:
        return jsonify({"error": "Таблицю не знайдено"}), 404
    data = request.get_json() or {}
    new_values = data.get("values", [])
    try:
        table.update_row_values(row_id, new_values)
        db.save_to_file(DB_FILE)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/tables/<table_name>/rows/<row_id>", methods=["DELETE"])
def delete_row(table_name: str, row_id: str):
    table = db.get_table(table_name)
    if not table:
        return jsonify({"error": "Таблицю не знайдено"}), 404
    table.delete_row(row_id)
    db.save_to_file(DB_FILE)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)