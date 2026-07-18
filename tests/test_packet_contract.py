import os
import tempfile
import unittest
import zipfile
from pathlib import Path

from app import build_packet, create_packet_archive, infer_citation_name
from web_app import safe_filename


SAMPLE_PAPER = """# Listening With Tired Eyes

Genevieve Prentice and Bruce Stephenson

2026

## Abstract

This original sample describes a local listening workflow for dense scholarly documents. It contains enough text to exercise packet creation without invoking speech rendering during the test.

## Introduction

Readers sometimes need to rest their eyes while continuing to follow an argument. A listening packet preserves the source while providing section text prepared for speech.
"""


class PacketContractTests(unittest.TestCase):
    def test_citation_name_uses_two_authors_year_and_short_title(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "paper.md"
            source.write_text(SAMPLE_PAPER, encoding="utf-8")
            self.assertEqual(
                infer_citation_name(source),
                "PrenticeStephenson2026_ListeningWithTiredEyes",
            )

    def test_skip_audio_packet_preserves_source_sections_and_readme(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "paper.md"
            output = root / "packet"
            source.write_text(SAMPLE_PAPER, encoding="utf-8")

            build_packet(source, output, "Evan (Enhanced)", 130, skip_audio=True)

            citation = "PrenticeStephenson2026_ListeningWithTiredEyes"
            self.assertTrue((output / f"{citation}.md").is_file())
            self.assertTrue((output / "01_Abstract.txt").is_file())
            self.assertTrue((output / "02_Introduction.txt").is_file())
            self.assertTrue((output / "README_listening_packet.md").is_file())
            self.assertFalse((output / "README.md").exists())

    def test_packet_archive_has_one_citation_named_folder(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir)
            citation = "Prentice2026_ListeningWithTiredEyes"
            source = output / f"{citation}.pdf"
            audiobook = output / f"{citation}.m4b"
            readme = output / "README_listening_packet.md"
            source.write_bytes(os.urandom(2048))
            audiobook.write_bytes(os.urandom(4096))
            readme.write_text("# Listening packet\n", encoding="utf-8")

            archive = create_packet_archive(output, citation, [source, audiobook, readme])

            with zipfile.ZipFile(archive) as packet:
                self.assertEqual(
                    set(packet.namelist()),
                    {
                        f"{citation}/{source.name}",
                        f"{citation}/{audiobook.name}",
                        f"{citation}/{readme.name}",
                    },
                )

    def test_safe_filename_removes_paths_and_unsafe_characters(self) -> None:
        self.assertEqual(safe_filename("../../My Paper (final).pdf"), "My_Paper_final_.pdf")
        self.assertEqual(safe_filename("..."), "document.txt")


if __name__ == "__main__":
    unittest.main()
