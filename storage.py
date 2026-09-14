import json
from typing import Dict, Optional
from core import Table


class Database:
    def __init__(self, name: str):
        self.name = name.strip()
        self.tables: Dict[str, Table] = {}

    def create_table(self, table_name: str) -> Table:
        table_name = table_name.strip()
        if not table_name:
            raise ValueError("Назва таблиці не може бути порожньою")
        if table_name in self.tables:
            raise ValueError(f"Таблиця '{table_name}' вже існує у базі даних")

        new_table = Table(name=table_name)
        self.tables[table_name] = new_table
        return new_table

    def drop_table(self, table_name: str):
        if table_name not in self.tables:
            raise KeyError(f"Таблицю '{table_name}' не знайдено")
        del self.tables[table_name]

    def get_table(self, table_name: str) -> Optional[Table]:
        return self.tables.get(table_name)

    def save_to_file(self, filepath: str):
        data = {
            "name": self.name,
            "tables": [table.to_dict() for table in self.tables.values()]
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load_from_file(cls, filepath: str) -> "Database":
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        db = cls(name=data.get("name", "UnnamedDB"))
        for t_data in data.get("tables", []):
            table = Table.from_dict(t_data)
            db.tables[table.name] = table
        return db