import unittest
import os
from core import Table, DataType, Validator
from storage import Database

class TestDatabaseEngine(unittest.TestCase):

    def setUp(self):
        self.table = Table("Employees")
        self.table.add_column("id", DataType.INTEGER)
        self.table.add_column("name", DataType.STRING)
        self.table.add_column("shift", DataType.TIME_INVL)

    def test_basic_types_validation(self):
        self.assertTrue(Validator.validate(DataType.INTEGER, 42))
        self.assertTrue(Validator.validate(DataType.INTEGER, "-15"))
        self.assertFalse(Validator.validate(DataType.INTEGER, "12.34"))
        self.assertFalse(Validator.validate(DataType.INTEGER, "abc"))

        self.assertTrue(Validator.validate(DataType.REAL, 3.14))
        self.assertTrue(Validator.validate(DataType.REAL, "-0.05"))
        self.assertFalse(Validator.validate(DataType.REAL, "not_a_number"))

        self.assertTrue(Validator.validate(DataType.CHAR, "A"))
        self.assertFalse(Validator.validate(DataType.CHAR, "AB"))
        self.assertFalse(Validator.validate(DataType.CHAR, ""))

        self.assertTrue(Validator.validate(DataType.STRING, "text 123"))

    def test_time_and_time_invl_validation(self):
        self.assertTrue(Validator.validate(DataType.TIME, "09:30:00"))
        self.assertTrue(Validator.validate(DataType.TIME, "23:59:59"))
        self.assertFalse(Validator.validate(DataType.TIME, "25:00:00"))
        self.assertFalse(Validator.validate(DataType.TIME, "12:61:00"))

        self.assertTrue(Validator.validate(DataType.TIME_INVL, "08:00:00 - 17:00:00"))
        self.assertTrue(Validator.validate(DataType.TIME_INVL, "10:00:00-10:00:00"))

        self.assertFalse(Validator.validate(DataType.TIME_INVL, "18:00:00 - 09:00:00"))
        self.assertFalse(Validator.validate(DataType.TIME_INVL, "invalid-interval"))
        self.assertFalse(Validator.validate(DataType.TIME_INVL, "09:00:00"))

    def test_variant_operations_swap_and_rename_columns(self):
        row1 = self.table.add_row([1, "Bob", "09:00:00 - 18:00:00"])
        row2 = self.table.add_row([2, "Alice", "08:00:00 - 16:30:00"])

        self.table.rename_column(0, "emp_id")
        self.assertEqual(self.table.columns[0].name, "emp_id")
        with self.assertRaises(ValueError):
            self.table.rename_column(0, "name")

        self.table.swap_columns(0, 2)

        self.assertEqual(self.table.columns[0].name, "shift")
        self.assertEqual(self.table.columns[0].data_type, DataType.TIME_INVL)
        self.assertEqual(self.table.columns[2].name, "emp_id")
        self.assertEqual(self.table.columns[2].data_type, DataType.INTEGER)

        self.assertEqual(row1.values, ["09:00:00 - 18:00:00", "Bob", 1])
        self.assertEqual(row2.values, ["08:00:00 - 16:30:00", "Alice", 2])

        with self.assertRaises(IndexError):
            self.table.swap_columns(0, 99)

    def test_database_persistence(self):
        db = Database("TestStore")
        t = db.create_table("Items")
        t.add_column("code", DataType.CHAR)
        t.add_row(["X"])

        test_file = "temp_test_db.json"
        try:
            db.save_to_file(test_file)
            loaded_db = Database.load_from_file(test_file)
            self.assertIn("Items", loaded_db.tables)
            loaded_table = loaded_db.get_table("Items")
            self.assertEqual(len(loaded_table.rows), 1)
            self.assertEqual(loaded_table.rows[0].values, ["X"])
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

if __name__ == "__main__":
    unittest.main()