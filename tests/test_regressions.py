"""Offline regressions for shortlist safety and failed collection runs."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import fetch_bubble_board as bubble
import fetch_postings as fetch
import filter_postings as shortlist
import sweep_boards as sweep


class RegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_main(self, module, args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(sys, "argv", [module.__name__, *map(str, args)]):
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                module.main()
        return stdout.getvalue(), stderr.getvalue()

    def row(self, suffix="one", location="Worldwide"):
        return ["ashby", "acme", "Backend Engineer", location, f"https://example.com/{suffix}"]

    def filter(self, rows, bodies=None, log=None):
        (self.root / "rows.json").write_text(json.dumps(rows))
        (self.root / "profile.md").write_text(
            "```criteria\ntitles_in: backend\ngeo_in: worldwide\n"
            "stack_in: typescript\nstack_out: ruby on rails\n```\n")
        args = [self.root / "rows.json", "--profile", self.root / "profile.md",
                "--out", self.root / "out.json", "--rejects", self.root / "rejects.json"]
        if bodies is not None:
            (self.root / "bodies.json").write_text(json.dumps(bodies))
            args += ["--bodies", self.root / "bodies.json"]
        if log is not None:
            (self.root / "applied.md").write_text(log)
            args += ["--applied", self.root / "applied.md"]
        self.run_main(shortlist, args)
        return json.loads((self.root / "out.json").read_text())

    def body(self, row, text="Required: TypeScript.", status="verified"):
        return [row[4], row[2], row[3], text, status]

    def test_geo_rejection_does_not_reserve_duplicate_key(self):
        ny, remote = self.row("ny", "New York"), self.row("remote")
        self.assertEqual([r["url"] for r in self.filter([ny, remote])], [remote[4]])

    def test_two_pass_filter_preserves_alternative_until_body_is_checked(self):
        wrong, right = self.row("wrong"), self.row("right")
        first = self.filter([wrong, right])
        self.assertEqual(len(first), 2)
        bodies = [self.body(wrong, "Required: Python."), self.body(right)]
        self.assertEqual([r["url"] for r in self.filter([wrong, right], bodies)], [right[4]])

    def test_verified_duplicates_are_removed(self):
        rows = [self.row("one"), self.row("two")]
        self.assertEqual(len(self.filter(rows, [self.body(r) for r in rows])), 1)

    def test_unverified_alternative_cannot_hide_verified_posting(self):
        unknown, verified = self.row("unknown"), self.row("verified")
        bodies = [self.body(unknown, "Enable JavaScript", "unverified"), self.body(verified)]
        kept = self.filter([unknown, verified], bodies)
        self.assertEqual([r["checked"] for r in kept], ["manual-review", "title+location+body"])

    def test_first_pass_still_removes_repeated_urls(self):
        row = self.row()
        self.assertEqual(len(self.filter([row, row])), 1)

    def test_resume_statuses_and_submission_history(self):
        row = self.row()
        for status, expected in [("blocked: waiting for code", 1), ("not applied: old criteria", 1),
                                 ("sent", 0), ("replied", 0), ("rejected", 0), ("unknown", 0)]:
            with self.subTest(status=status):
                log = ("| # | Company | Role | Geography | URL | Date | Status | Letter |\n"
                       f"| 1 | Acme | Backend Engineer | Worldwide | {row[4]} | 2026-09-17 | {status} | letter.md |\n")
                self.assertEqual(len(self.filter([row], log=log)), expected)

    def test_legacy_log_without_status_remains_conservative(self):
        log = "| 1 | Acme | Backend Engineer | Worldwide | https://example.com/one |\n"
        self.assertEqual(self.filter([self.row()], log=log), [])

    def test_stack_mentions_require_context_review(self):
        row = self.row()
        for text in ["TypeScript required. Ruby on Rails is a bonus, not required.",
                     "TypeScript and Ruby on Rails are required."]:
            with self.subTest(text=text):
                kept = self.filter([row], [self.body(row, text)])
                self.assertEqual(len(kept), 1)
                self.assertIn("Ruby on Rails", kept[0]["note"])
                self.assertEqual(kept[0]["checked"], "manual-review")

    def test_title_stack_exclusion_still_rejects(self):
        row = self.row()
        row[2] = "Backend Ruby on Rails Engineer"
        self.assertEqual(self.filter([row]), [])

    def test_html_shell_is_unverified_and_cannot_reject_on_stack(self):
        row = self.row()
        with patch.object(fetch, "get", return_value="<title>Enable JavaScript</title>"):
            body = fetch.fetch(row[4])
        self.assertEqual(body[4], "unverified")
        kept = self.filter([row], [body])
        self.assertEqual(len(kept), 1)
        self.assertEqual(kept[0]["checked"], "manual-review")

    def test_failed_and_legacy_bodies_require_manual_review(self):
        row = self.row()
        for body in [self.body(row, "", "failed"), self.body(row, "Enable JavaScript")[:4]]:
            with self.subTest(body=body):
                kept = self.filter([row], [body])
                self.assertEqual(len(kept), 1)
                self.assertEqual(kept[0]["checked"], "manual-review")

    def test_ats_description_is_verified_but_empty_description_is_failed(self):
        for text, expected in [("TypeScript role", "verified"), ("  ", "failed")]:
            with self.subTest(text=text), patch.object(fetch, "RESOLVERS", [lambda url: ("Role", "Worldwide", text)]):
                self.assertEqual(fetch.fetch("https://example.com/job")[4], expected)

    def test_fetch_cli_marks_network_failure(self):
        links, out = self.root / "links.txt", self.root / "bodies.json"
        links.write_text("https://example.com/job\n")
        with patch.object(fetch, "get", return_value=None):
            self.run_main(fetch, [links, "--out", out])
        self.assertEqual(json.loads(out.read_text()), [["https://example.com/job", "", "", "", "failed"]])

    def test_total_sweep_failure_preserves_previous_output(self):
        out = self.root / "rows.json"
        out.write_text('["previous run"]')
        for response in [None, "not JSON", '{"error": "unavailable"}']:
            with self.subTest(response=response), patch.object(sweep, "load_tokens", return_value=["acme"]):
                with patch.object(sweep, "get", return_value=response), self.assertRaises(SystemExit):
                    self.run_main(sweep, ["--ats", "ashby", "--out", out])
                self.assertEqual(json.loads(out.read_text()), ["previous run"])

    def test_successful_empty_board_is_valid(self):
        out = self.root / "rows.json"
        with patch.object(sweep, "load_tokens", return_value=["acme"]):
            with patch.object(sweep, "get", return_value='{"jobs": []}'):
                self.run_main(sweep, ["--ats", "ashby", "--out", out])
        self.assertEqual(json.loads(out.read_text()), [])

    def test_sweep_keeps_postings_from_each_supported_ats(self):
        responses = {"ashby": '{"jobs":[{"title":"Backend","jobUrl":"https://example.com/a"}]}',
                     "greenhouse": '{"jobs":[{"title":"Backend","id":123}]}',
                     "lever": '[{"text":"Backend","hostedUrl":"https://example.com/l"}]'}
        for ats, response in responses.items():
            with self.subTest(ats=ats), patch.object(sweep, "get", return_value=response):
                rows, error = sweep.fetch((ats, "acme"))
            self.assertIsNone(error)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][:3], (ats, "acme", "Backend"))

    def test_partial_sweep_failure_is_reported(self):
        out = self.root / "rows.json"
        def response(url):
            return None if url.endswith("bad") else '{"jobs": []}'
        with patch.object(sweep, "load_tokens", return_value=["good", "bad"]):
            with patch.object(sweep, "get", side_effect=response):
                _, stderr = self.run_main(sweep, ["--ats", "ashby", "--out", out])
        self.assertIn("1 failed", stderr)

    def test_one_entire_ats_failing_is_not_hidden_by_another(self):
        def response(url):
            return None if "ashbyhq" in url else '{"jobs": []}'
        with patch.object(sweep, "load_tokens", return_value=["acme"]):
            with patch.object(sweep, "get", side_effect=response), self.assertRaises(SystemExit):
                self.run_main(sweep, ["--ats", "ashby", "greenhouse", "--out", self.root / "rows.json"])
        self.assertFalse((self.root / "rows.json").exists())


    # --- Bubble boards -------------------------------------------------------

    def bubble_board(self, **over):
        board = {"host": "example.com", "org": "Acme", "type": "jobs",
                 "url": "https://example.com/job/{_id}", "title": "Name",
                 "location": None, "body": "Description",
                 "visible_if": {"Visible": True}, "extras": ["Grade"],
                 "salary": {"range": "Salary range", "currency": "Currency", "period": "Period"}}
        board.update(over)
        return board

    def test_bubble_missing_location_stays_empty_not_remote(self):
        """A board with no location field must emit "", which filter_postings keeps.

        Writing "Remote" instead is tested against geo_in, matches nothing, and the row
        is dropped with a reason that reads as if it were correct."""
        rows, bodies = bubble.to_rows(
            [{"_id": "1", "Name": "Backend Engineer", "Visible": True,
              "Description": "We use TypeScript.", "Remote": True}], self.bubble_board())
        self.assertEqual(rows[0][3], "")
        self.assertEqual(bodies[0][2], "")
        # Pass one runs on locations alone, and that is where "Remote" would be fatal.
        self.assertEqual([r["title"] for r in self.filter(rows)], ["Backend Engineer"])
        remoteish = [r[:3] + ["Remote"] + r[4:] for r in rows]
        self.assertEqual(self.filter(remoteish), [])

    def test_bubble_hoists_geography_stated_below_the_filter_window(self):
        """Measured on a real board: the only sentence naming geography sat at char 6394,
        and filter_postings reads the first 3000."""
        buried = "Perks\n" + ("padding. " * 500) + "\n100% remote, worldwide\n"
        rows, bodies = bubble.to_rows(
            [{"_id": "1", "Name": "Backend Engineer", "Visible": True,
              "Description": "We use TypeScript.\n" + buried}], self.bubble_board())
        self.assertGreater(bodies[0][3].find("worldwide", 3000), -1,
                           "the source really does bury it past the filter's window")
        self.assertIn("Location note: 100% remote, worldwide", bodies[0][3][:120])
        self.assertEqual([r["title"] for r in self.filter(rows, bodies=bodies)],
                         ["Backend Engineer"])

    def test_bubble_keeps_the_apply_link_out_of_bbcode(self):
        rows, bodies = bubble.to_rows(
            [{"_id": "1", "Name": "Backend Engineer", "Visible": True,
              "Description": "[h3][b]How to apply[/b][/h3]"
                             "[url=https://ats.example/x]the form[/url] TypeScript"}],
            self.bubble_board())
        self.assertIn("the form (https://ats.example/x)", bodies[0][3])
        self.assertNotIn("[h3]", bodies[0][3])

    def test_bubble_invisible_records_are_dropped_and_salary_is_surfaced(self):
        records = [{"_id": "1", "Name": "Live", "Visible": True, "Grade": "Senior",
                    "Salary range": [0, 10000], "Currency": "USD", "Period": "Month",
                    "Description": "TypeScript"},
                   {"_id": "2", "Name": "Draft", "Visible": False, "Description": "TypeScript"}]
        rows, bodies = bubble.to_rows(records, self.bubble_board())
        self.assertEqual([r[2] for r in rows], ["Live"])
        self.assertIn("Salary: 10000 USD Month", bodies[0][3])

    def test_bubble_probe_reads_type_not_found_as_api_enabled(self):
        missing = json.dumps({"statusCode": 404, "body": {"status": "NOT_FOUND"}})
        with patch.object(bubble, "get", return_value=missing):
            found, note = bubble.probe("example.com", guesses=["jobs"])
        self.assertIsNone(found)
        self.assertIn("Data API is ON", note)
        with patch.object(bubble, "get", return_value='{"response":{"results":[]}}'):
            found, _ = bubble.probe("example.com", guesses=["jobs"])
        self.assertEqual(found, "jobs")

    def test_bubble_refuses_to_read_people(self):
        with patch.object(sys, "argv", ["bubble", "example.com", "--type", "users"]):
            with self.assertRaises(SystemExit) as caught:
                bubble.main()
        self.assertIn("people, not postings", str(caught.exception))



if __name__ == "__main__":
    unittest.main()
