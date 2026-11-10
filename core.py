from enum import Enum
import re
from datetime import time
from typing import List, Any, Optional
import uuid


class DataType(str, Enum):
    INTEGER = "integer"
    REAL = "real"
    CHAR = "char"
    STRING = "string"
    TIME = "time"
    TIME_INVL = "timeInvl"


class Validator:
    TIME_REGEX = re.compile(r"^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$")

    @classmethod
    def _parse_time(cls, time_str: str) -> Optional[time]:
        match = cls.TIME_REGEX.match(time_str.strip())
        if not match:
            return None
        h, m, s = map(int, match.groups())
        return time(hour=h, minute=m, second=s)

    @classmethod
    def validate(cls, data_type: DataType, value: Any) -> bool:
        if value is None:
            return False

        if data_type == DataType.CHAR:
            return isinstance(value, str) and len(value) == 1

        if data_type == DataType.STRING:
            return isinstance(value, str)

        str_val = str(value).strip()

        if data_type == DataType.INTEGER:
            try:
                int(str_val)
                return True
            except ValueError:
                return False

        elif data_type == DataType.REAL:
            try:
                float(str_val)
                return True
            except ValueError:
                return False

        elif data_type == DataType.TIME:
            return cls._parse_time(str_val) is not None

        elif data_type == DataType.TIME_INVL:
            parts = str_val.split("-")
            if len(parts) != 2:
                return False
            start = cls._parse_time(parts[0].strip())
            end = cls._parse_time(parts[1].strip())
            return (start is not None) and (end is not None) and (start <= end)

        return False


class Column:
    def __init__(self, name: str, data_type: DataType):
        self.name = name.strip()
        self.data_type = data_type

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.data_type.value
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Column":
        return cls(name=data["name"], data_type=DataType(data["type"]))


class Row:
    def __init__(self, values: List[Any], row_id: Optional[str] = None):
        self.id = row_id or str(uuid.uuid4())[:8]
        self.values = values

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "values": self.values
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Row":
        return cls(values=data["values"], row_id=data.get("id"))


class Table:
    DEFAULT_TYPE_VALUES = {
        DataType.INTEGER: 0,
        DataType.REAL: 0.0,
        DataType.CHAR: " ",
        DataType.STRING: "",
        DataType.TIME: "00:00:00",
        DataType.TIME_INVL: "00:00:00-00:00:00",
    }

    def __init__(self, name: str, columns: Optional[List[Column]] = None):
        self.name = name.strip()
        self.columns: List[Column] = columns or []
        self.rows: List[Row] = []

    def add_column(self, name: str, data_type: DataType, default_value: Any = None):
        name = name.strip()
        if not name:
            raise ValueError("Назва колонки не може бути порожньою")
        if any(col.name == name for col in self.columns):
            raise ValueError(f"Колонка з назвою '{name}' вже існує в таблиці")

        if default_value is None:
            default_value = self.DEFAULT_TYPE_VALUES[data_type]

        if not Validator.validate(data_type, default_value):
            raise ValueError(f"Дефолтне значення '{default_value}' не відповідає типу {data_type.value}")

        new_col = Column(name, data_type)
        self.columns.append(new_col)

        for row in self.rows:
            row.values.append(default_value)

    def delete_column(self, col_index: int):
        if not (0 <= col_index < len(self.columns)):
            raise IndexError("Некоректний індекс колонки")

        self.columns.pop(col_index)

        for row in self.rows:
            row.values.pop(col_index)

        if not self.columns:
            self.rows.clear()

    def add_row(self, raw_values: List[Any]) -> Row:
        if len(raw_values) != len(self.columns):
            raise ValueError(
                f"Кількість переданих значень ({len(raw_values)}) "
                f"не відповідає схемі колонок ({len(self.columns)})"
            )

        for col, val in zip(self.columns, raw_values):
            if not Validator.validate(col.data_type, val):
                raise ValueError(
                    f"Значення '{val}' у колонці '{col.name}' не відповідає типу {col.data_type.value}"
                )

        row = Row(values=list(raw_values))
        self.rows.append(row)
        return row

    def update_row_values(self, row_id: str, new_values: List[Any]):
        row = next((r for r in self.rows if r.id == row_id), None)
        if not row:
            raise KeyError(f"Рядок з id '{row_id}' не знайдено")

        if len(new_values) != len(self.columns):
            raise ValueError(
                f"Кількість переданих значень ({len(new_values)}) "
                f"не відповідає схемі колонок ({len(self.columns)})"
            )

        for col, val in zip(self.columns, new_values):
            if not Validator.validate(col.data_type, val):
                raise ValueError(
                    f"Значення '{val}' у колонці '{col.name}' не відповідає типу {col.data_type.value}"
                )

        row.values = list(new_values)

    def edit_row(self, row_id: str, col_index: int, new_value: Any):
        row = next((r for r in self.rows if r.id == row_id), None)
        if not row:
            raise KeyError(f"Рядок з id '{row_id}' не знайдено")

        if not (0 <= col_index < len(self.columns)):
            raise IndexError("Некоректний індекс колонки")

        target_col = self.columns[col_index]
        if not Validator.validate(target_col.data_type, new_value):
            raise ValueError(
                f"Значення '{new_value}' не відповідає типу {target_col.data_type.value}"
            )

        row.values[col_index] = new_value

    def delete_row(self, row_id: str):
        self.rows = [r for r in self.rows if r.id != row_id]

    def rename_column(self, col_index: int, new_name: str):
        if not (0 <= col_index < len(self.columns)):
            raise IndexError("Некоректний індекс колонки")

        new_name = new_name.strip()
        if not new_name:
            raise ValueError("Назва колонки не може бути порожньою")

        if any(idx != col_index and c.name == new_name for idx, c in enumerate(self.columns)):
            raise ValueError(f"Колонка з ім'ям '{new_name}' вже існує")

        self.columns[col_index].name = new_name

    def swap_columns(self, index_a: int, index_b: int):
        total_cols = len(self.columns)
        if not (0 <= index_a < total_cols and 0 <= index_b < total_cols):
            raise IndexError("Індекси колонок виходять за межі допустимого діапазону")

        if index_a == index_b:
            return

        self.columns[index_a], self.columns[index_b] = (
            self.columns[index_b],
            self.columns[index_a],
        )

        for row in self.rows:
            row.values[index_a], row.values[index_b] = (
                row.values[index_b],
                row.values[index_a],
            )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "columns": [col.to_dict() for col in self.columns],
            "rows": [row.to_dict() for row in self.rows]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Table":
        table = cls(name=data["name"])
        table.columns = [Column.from_dict(c) for c in data.get("columns", [])]

        for r_data in data.get("rows", []):
            row = Row.from_dict(r_data)
            if len(row.values) != len(table.columns):
                raise ValueError(f"Пошкоджений запис у таблиці '{table.name}': невідповідність кількості значень")
            for col, val in zip(table.columns, row.values):
                if not Validator.validate(col.data_type, val):
                    raise ValueError(
                        f"Пошкоджені дані у завантаженому файлі: значення '{val}' не відповідає типу {col.data_type.value}"
                    )
            table.rows.append(row)

        return table