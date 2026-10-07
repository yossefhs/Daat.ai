"""Regression checks for false missing-seif reports caused by source typography."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("veilleur", Path(__file__).parents[1] / "scripts/veilleur.py")
veilleur = importlib.util.module_from_spec(spec)
spec.loader.exec_module(veilleur)


class SourceCoverageTests(unittest.TestCase):
    def test_present_source_with_tags_nikud_and_hebrew_quotes(self):
        source = 'עכו"ם שמילא מים לבהמתו מבור שהוא רשות היחיד לרשות הרבים'
        pages = {'niveau-1-base': '<blockquote class="text-source">עכו״ם שֶׁמילא <small>מים</small> לבהמתו מבור שהוא רשות היחיד לרשות הרבים</blockquote>'}
        self.assertEqual(veilleur.detect_seifim_orphelins(325, pages, [source]), [])

    def test_optional_edition_heading(self):
        source = 'דין הקידוש בבהכ"נ. ובו סעיף אחד:נוהגין לקדש בבהכ"נ ואין למקדש לטעום מיין הקידוש'
        pages = {'niveau-1-base': '<blockquote class="text-source">נוהגין לקדש בבהכ״נ ואין למקדש לטעום מיין הקידוש</blockquote>'}
        self.assertEqual(veilleur.detect_seifim_orphelins(269, pages, [source]), [])

    def test_absent_source_still_reported(self):
        source = 'עכו"ם שמילא מים לבהמתו מבור שהוא רשות היחיד לרשות הרבים'
        findings = veilleur.detect_seifim_orphelins(325, {'niveau-1-base': '<p>Un autre sujet.</p>'}, [source])
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]['seif'], 1)


if __name__ == '__main__':
    unittest.main()
