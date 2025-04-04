import unittest
from utils.response_calculator import ResponseTimeCalculator

class TestResponseTimeCalculator(unittest.TestCase):
    def setUp(self):
        self.calculator = ResponseTimeCalculator()

    def test_calculate_score_perfect_times(self):
        # Test with perfect response times (500ms)
        response_times = [500, 500, 500]
        result = self.calculator.calculate_score(response_times)
        
        self.assertEqual(result['score'], 100)
        self.assertEqual(result['average_time'], 500)
        self.assertEqual(result['individual_scores'], [100, 100, 100])

    def test_calculate_score_slow_times(self):
        # Test with slower response times
        response_times = [800, 900, 1000]
        result = self.calculator.calculate_score(response_times)
        
        # Expected scores with new algorithm:
        # 800ms: 100 - (800-500)/50 = 94
        # 900ms: 100 - (900-500)/50 = 92
        # 1000ms: 100 - (1000-500)/50 = 90
        self.assertAlmostEqual(result['score'], 92.0, places=1)
        self.assertEqual(result['average_time'], 900)
        self.assertEqual(result['individual_scores'], [94.0, 92.0, 90.0])

    def test_calculate_score_very_slow_times(self):
        # Test with very slow response times
        response_times = [2000, 2500, 3000]
        result = self.calculator.calculate_score(response_times)
        
        # Expected scores with new algorithm:
        # 2000ms: 100 - (2000-500)/50 = 70
        # 2500ms: 100 - (2500-500)/50 = 60
        # 3000ms: 100 - (3000-500)/50 = 50
        self.assertAlmostEqual(result['score'], 60.0, places=1)
        self.assertEqual(result['average_time'], 2500)
        self.assertEqual(result['individual_scores'], [70.0, 60.0, 50.0])

    def test_calculate_score_extremely_slow_times(self):
        # Test with extremely slow response times (should get 0)
        response_times = [5500, 6000, 6500]
        result = self.calculator.calculate_score(response_times)
        
        self.assertEqual(result['score'], 0)
        self.assertEqual(result['average_time'], 6000)
        self.assertEqual(result['individual_scores'], [0, 0, 0])

    def test_invalid_number_of_attempts(self):
        # Test with wrong number of attempts
        with self.assertRaises(ValueError):
            self.calculator.calculate_score([500, 500])  # Only 2 attempts

    def test_attempt_tracking(self):
        # Test attempt tracking
        self.calculator.start_attempt()
        time1 = self.calculator.end_attempt()
        
        self.calculator.start_attempt()
        time2 = self.calculator.end_attempt()
        
        self.calculator.start_attempt()
        time3 = self.calculator.end_attempt()
        
        attempts = self.calculator.get_attempts()
        self.assertEqual(len(attempts), 3)
        self.assertEqual(attempts[0]['response_time'], time1)
        self.assertEqual(attempts[1]['response_time'], time2)
        self.assertEqual(attempts[2]['response_time'], time3)

if __name__ == '__main__':
    unittest.main() 