import main
import unittest

class TestCheckLineCompletion(unittest.TestCase):
        
    def setUp(self) -> None:
        main.score = 0
        return super().setUp()

    def test_multiple_line_completion(self):
        
        self.grid = [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
        ]
        main.check_line_completion(self.grid)
        expected_grid = [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0] 
        ]
        self.assertEqual(main.score, 30)
        self.assertEqual(self.grid, expected_grid)

    def test_multiple_line_completion_non_contious(self):
        self.grid = [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [1, 1, 1, 1],
            [1, 1, 0, 1],
            [1, 1, 1, 1],
        ]
        main.check_line_completion(self.grid)
        expected_grid = [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [1, 1, 0, 1],
        ]
        self.assertEqual(main.score, 20)
        self.assertEqual(self.grid, expected_grid)
        

if __name__ == '__main__':
    unittest.main()
