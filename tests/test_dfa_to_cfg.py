import unittest
from backend.dfa_to_cfg import convert_dfa_to_cfg

class TestDfaToCfg(unittest.TestCase):
    def test_sample_conversion(self):
        dfa = {
            "states": ["q0", "q1", "q2"],
            "alphabet": ["a", "b"],
            "transitions": {
                ("q0", "a"): "q1",
                ("q0", "b"): "q2",
                ("q1", "a"): "q0",
                ("q1", "b"): "q2",
                ("q2", "a"): "q2",
                ("q2", "b"): "q2",
            },
            "start_state": "q0",
            "accept_states": ["q1"],
        }

        cfg = convert_dfa_to_cfg(dfa)

        self.assertEqual(cfg["start_variable"], "q0")
        self.assertEqual(cfg["terminals"], ["a", "b"])
        self.assertIn("ε", cfg["productions"]["q1"])
        self.assertIn("a q1", cfg["productions"]["q0"])
        self.assertIn("b q2", cfg["productions"]["q0"])

    def test_missing_key_raises(self):
        with self.assertRaises(ValueError):
            convert_dfa_to_cfg({"states": ["q0"]})

if _name_ == "_main_":
    unittest.main()
