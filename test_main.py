import unittest
from main import YearProgressCloner
import datetime
import os

class TestYearProgress(unittest.TestCase):
    def setUp(self):
        self.cloner = YearProgressCloner(year=2024) # うるう年でテスト

    def test_calculate_start_of_year(self):
        """元旦に進捗0%になるか"""
        self.cloner.now = datetime.datetime(2024, 1, 1, 0, 0, 0)
        self.assertEqual(self.cloner.calculate_progress(), 0)

    def test_calculate_mid_year(self):
        """7月初旬におよそ50%になるか"""
        self.cloner.now = datetime.datetime(2024, 7, 2, 0, 0, 0)
        self.assertIn(self.cloner.calculate_progress(), [49, 50, 51])

    def test_calculate_end_of_year(self):
        """大晦日の終盤に99%以上になるか"""
        self.cloner.now = datetime.datetime(2024, 12, 31, 23, 59, 59)
        self.assertEqual(self.cloner.calculate_progress(), 99)

    def test_image_generation(self):
        """画像が正常に生成されるか"""
        path = self.cloner.generate_image(18.5)
        image_path = os.path.join(self.cloner.image_dir, path)
        self.assertTrue(os.path.exists(image_path))
        if os.path.exists(image_path):
            os.remove(image_path)

if __name__ == "__main__":
    unittest.main()