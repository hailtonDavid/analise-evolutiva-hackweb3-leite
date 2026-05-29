import unittest

from core import create_sample, verify_integrity, analyze_milk, simulate_spectral_reading


class TestAnaliseEvolutivaMVP(unittest.TestCase):
    def test_create_sample_has_hash_and_chain(self):
        sample = create_sample(seed=42, adulterated=False)
        self.assertIn("evidence_hash", sample)
        self.assertEqual(len(sample["chain"]), 5)
        self.assertEqual(sample["blockchain"]["status_onchain"], "REGISTRADO")

    def test_integrity_is_valid_for_untouched_sample(self):
        sample = create_sample(seed=7, adulterated=False)
        result = verify_integrity(sample)
        self.assertTrue(result["integro"])

    def test_adulterated_sample_has_higher_risk_than_conform_sample(self):
        conform = analyze_milk(simulate_spectral_reading(seed=10, adulterated=False))
        suspect = analyze_milk(simulate_spectral_reading(seed=10, adulterated=True))
        self.assertGreaterEqual(suspect.score_adulteracao, conform.score_adulteracao)


if __name__ == "__main__":
    unittest.main()
