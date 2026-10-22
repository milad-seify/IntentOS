from pathlib import Path
import unittest


class ReviewSkillTests(unittest.TestCase):
    def test_review_skill_is_portable_read_only_and_evidence_based(self) -> None:
        content = (
            Path(__file__).resolve().parents[1]
            / "skills"
            / "intentos-review"
            / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertTrue(content.startswith("---\nname: intentos-review\n"))
        self.assertIn("This skill is read-only", content)
        self.assertIn("No concrete case means no finding", content)
        self.assertIn("Must fix", content)
        self.assertIn("Should fix", content)
        self.assertIn("smallest reasonable fix", content)
        self.assertIn("reuse existing project code", content)
        self.assertIn("standard-library or platform capabilities", content)
        self.assertIn("do not optimize for code golf", content)
        self.assertIn("Do not invent findings", content)


if __name__ == "__main__":
    unittest.main()
