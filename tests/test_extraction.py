import tempfile
import unittest
from pathlib import Path

from app import (
    clean_text,
    listening_front_matter,
    split_render_chunks,
    split_sections,
    structured_pdf_text,
)


STRUCTURED_XML = """<?xml version="1.0" encoding="UTF-8"?>
<pdf2xml>
  <page number="1" width="900" height="1200">
    <fontspec id="0" size="13" family="ExampleRegular" color="#000000"/>
    <fontspec id="1" size="15" family="ExampleBold" color="#000000"/>
    <text top="100" left="60" width="18" height="15" font="1">2.1</text>
    <text top="100" left="90" width="250" height="15" font="1">Path Dependence of AI Emotional Support</text>
    <text top="125" left="60" width="340" height="15" font="0">The left column begins with ordinary prose.</text>
    <text top="100" left="490" width="310" height="15" font="0">The right column must not join the heading.</text>
  </page>
</pdf2xml>
"""


class ExtractionTests(unittest.TestCase):
    def test_spoken_front_matter_excludes_contact_information(self) -> None:
        raw = (
            "A Study of Careful Listening\n"
            "Alice Smith and Bob Jones alice@example.org\n"
            "Example University\n"
            "Published 2026\n\n"
            "Abstract\nThe article begins here."
        )

        spoken = listening_front_matter(raw, 130)

        self.assertIn("A Study of Careful Listening.", spoken)
        self.assertIn("By Alice Smith and Bob Jones.", spoken)
        self.assertIn("Published in 2026.", spoken)
        self.assertNotIn("@", spoken)
        self.assertNotIn("University", spoken)

    def test_numeric_pdf_citations_are_removed_from_listening_text(self) -> None:
        cleaned = clean_text(
            "Companies repair what their AI confidently broke [ 8 ]. "
            "Other failures followed [80, 99]. Similar evidence appears elsewhere [ 101–103 ]."
        )

        self.assertEqual(
            cleaned,
            "Companies repair what their AI confidently broke. "
            "Other failures followed. Similar evidence appears elsewhere.",
        )

    def test_bold_numbered_pdf_heading_becomes_a_section(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            xml_path = Path(temp_dir) / "paper.xml"
            xml_path.write_text(STRUCTURED_XML, encoding="utf-8")
            cleaned = clean_text(structured_pdf_text(xml_path))
            sections = split_sections(cleaned)

        self.assertEqual(sections[0].title, "Path Dependence of AI Emotional Support")
        self.assertIn("ordinary prose", sections[0].text)
        self.assertIn("right column", sections[0].text)

    def test_render_chunks_stay_within_the_word_limit(self) -> None:
        text = "\n\n".join(" ".join([f"word{index}"] * 80) for index in range(5))
        chunks = split_render_chunks(text, max_words=160)

        self.assertEqual(len(chunks), 3)
        self.assertTrue(all(len(chunk.split()) <= 160 for chunk in chunks))


if __name__ == "__main__":
    unittest.main()
