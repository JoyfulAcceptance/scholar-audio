import unittest

from app import (
    Section,
    pace_paragraphs,
    prepare_spoken_section,
    scaled_pause,
    slow_acronyms,
    slow_numbers_and_versions,
    verbalize_decimals,
)


class PacingTests(unittest.TestCase):
    def test_acronym_and_surrounding_spaces_slow_to_seventy_five_percent(self) -> None:
        spoken = slow_acronyms("Mean BMRI increased.", 145)

        self.assertEqual(spoken, "Mean[[rate 109]] B M R I [[rate 145]]increased.")

    def test_acronym_restores_an_already_slowed_sentence_rate(self) -> None:
        spoken = slow_acronyms("The BMRI result.", 145, 123)

        self.assertEqual(spoken, "The[[rate 109]] B M R I [[rate 123]]result.")

    def test_decimals_are_written_for_speech_digit_by_digit(self) -> None:
        spoken = verbalize_decimals(
            "BMRI rose from 0.18 to 0.67. GPT-5.6 read 12.4S. Version 1.2.3 stayed intact."
        )

        self.assertEqual(
            spoken,
            "BMRI rose from zero point one eight to zero point six seven. "
            "GPT five point six read twelve point four S. Version 1.2.3 stayed intact.",
        )

    def test_quantitative_decimals_receive_one_continuous_slowed_span(self) -> None:
        spoken = pace_paragraphs("Values changed from 0.20 to 0.24.", 145)

        self.assertEqual(
            spoken,
            "Values changed from[[rate 109]] zero point two [[rate 145]]"
            "to[[rate 109]] zero point two four[[rate 145]].",
        )

    def test_complete_version_label_receives_one_slowed_span(self) -> None:
        spoken = slow_numbers_and_versions("Codex and GPT-5.6 helped.", 145)

        self.assertEqual(
            spoken,
            "Codex and[[rate 109]] G P T five point six [[rate 145]]helped.",
        )

    def test_pause_scaling_uses_130_wpm_baseline(self) -> None:
        self.assertEqual(scaled_pause(700, 130), 700)
        self.assertEqual(scaled_pause(700, 140), 675)
        self.assertEqual(scaled_pause(700, 153), 645)

    def test_new_term_slows_to_ninety_percent_then_restores(self) -> None:
        text = "Calibration refers to the relationship between confidence and correctness."
        paced = pace_paragraphs(text, 153)
        self.assertIn("[[rate 138]]", paced)
        self.assertIn("[[rate 153]]", paced)
        self.assertIn("[[slnc 415]]", paced)

    def test_dense_sentence_slows_to_eighty_five_percent(self) -> None:
        text = (
            "This deliberately dense sentence contains many connected qualifications, several competing "
            "conditions, multiple dependent clauses, four separate examples, and enough additional language "
            "to exceed the conservative threshold without marking ordinary prose as unusually difficult for "
            "a listener to process in one pass."
        )
        paced = pace_paragraphs(text, 140)
        self.assertIn("[[rate 119]]", paced)
        self.assertIn("[[rate 140]]", paced)
        self.assertIn("[[slnc 482]]", paced)

    def test_very_dense_sentence_slows_to_seventy_seven_percent(self) -> None:
        text = " ".join(["concept"] * 50) + "."
        paced = pace_paragraphs(text, 130)
        self.assertIn("[[rate 100]]", paced)
        self.assertIn("[[rate 130]]", paced)
        self.assertIn("[[slnc 550]]", paced)

    def test_ordinary_sentence_remains_at_baseline(self) -> None:
        paced = pace_paragraphs("This is ordinary prose.", 130)
        self.assertEqual(paced, "This is ordinary prose.")

    def test_every_section_begins_with_boundary_silence(self) -> None:
        prepared = prepare_spoken_section(Section("Introduction", "Ordinary prose."), 130)
        self.assertTrue(prepared.startswith("[[slnc 700]]\n\nIntroduction."))

    def test_results_cluster_pauses_between_findings(self) -> None:
        text = "First finding. Second finding. Third finding."
        paced = pace_paragraphs(text, 130, "Results")
        self.assertEqual(paced.count("[[slnc 300]]"), 2)
        self.assertTrue(paced.endswith("[[slnc 450]]"))

    def test_result_cluster_rule_does_not_affect_other_sections(self) -> None:
        text = "First statement. Second statement. Third statement."
        self.assertNotIn("[[slnc", pace_paragraphs(text, 130, "Discussion"))


if __name__ == "__main__":
    unittest.main()
