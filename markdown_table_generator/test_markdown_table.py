import unittest
from markdown_table_generator.markdown_table import MarkdownTableGenerator

class TestMarkdownTableGenerator(unittest.TestCase):

    def test_from_csv_string(self):
        csv_data = "Product,Price,Quantity\nApple,1.2,100\nBanana,0.5,150"
        gen = MarkdownTableGenerator.from_csv_string(csv_data)
        self.assertEqual(gen.headers, ["Product", "Price", "Quantity"])
        self.assertEqual(len(gen.rows), 2)
        self.assertEqual(gen.rows[0], ["Apple", "1.2", "100"])

    def test_from_json_string(self):
        json_data = '[{"id": 1, "name": "Item A"}, {"id": 2, "name": "Item B"}]'
        gen = MarkdownTableGenerator.from_json_string(json_data)
        self.assertEqual(gen.headers, ["id", "name"])
        self.assertEqual(len(gen.rows), 2)
        self.assertEqual(gen.rows[1], ["2", "Item B"])

    def test_sort_rows_numeric(self):
        csv_data = "Name,Score\nAlice,85\nBob,92\nCharlie,78"
        gen = MarkdownTableGenerator.from_csv_string(csv_data)
        gen.sort_rows("Score", reverse=True, numeric=True)
        self.assertEqual(gen.rows[0][0], "Bob")
        self.assertEqual(gen.rows[2][0], "Charlie")

    def test_filter_rows(self):
        csv_data = "City,Country\nParis,France\nBerlin,Germany\nNice,France"
        gen = MarkdownTableGenerator.from_csv_string(csv_data)
        gen.filter_rows("Country", "France")
        self.assertEqual(len(gen.rows), 2)
        self.assertEqual(gen.rows[0][0], "Paris")
        self.assertEqual(gen.rows[1][0], "Nice")

    def test_to_markdown_formatting(self):
        csv_data = "Name,Age\nAlice,30"
        gen = MarkdownTableGenerator.from_csv_string(csv_data)
        md = gen.to_markdown(align={"Age": "right"})
        self.assertIn("| Name  | Age |", md)
        self.assertIn("| Alice |  30 |", md)

if __name__ == "__main__":
    unittest.main()
