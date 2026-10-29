"""Protect source identity, unknown dates and generated output from regressions."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

import build_episodes as build
import site_check
from video_metadata import load_video_metadata, valid_timestamp


class VideoMetadataTests(unittest.TestCase):
    def setUp(self):
        self.records = load_video_metadata(build.ROOT)
        self.catalog = build.parse_episodes((build.ROOT / "index.html").read_text(encoding="utf-8"))
        for ep in self.catalog:
            ep["video_metadata"] = self.records[ep["youtube"].rsplit("/", 1)[-1]]

    def test_generated_dates_and_identity_match_evidence(self):
        for ep in self.catalog:
            with self.subTest(episode=ep["n"]):
                graph = json.loads(build.json_ld(ep, self.catalog))["@graph"]
                video = next(n for n in graph if n["@type"] == "VideoObject")
                record = ep["video_metadata"]
                self.assertEqual(video["url"], ep["youtube"])
                self.assertEqual(video["thumbnailUrl"], record["thumbnailUrl"])
                if record["status"] == "verified":
                    self.assertEqual(video["uploadDate"], record["uploadDate"])
                else:
                    self.assertNotIn("uploadDate", video)
                episode = next(n for n in graph if n["@type"] == "TVEpisode")
                self.assertNotIn("datePublished", episode)  # no invented TV air date

    def test_invalid_dates_are_rejected(self):
        for value in (None, "2026-10-29", "2021-02-30T00:00:00Z", "2021-07-02T09:24:37", "2999-01-01T00:00:00Z"):
            with self.subTest(value=value):
                self.assertFalse(valid_timestamp(value))
        self.assertTrue(valid_timestamp("2021-07-02T09:24:37-07:00"))

    def reject_manifest(self, change):
        data = {"schemaVersion": 1, "videos": copy.deepcopy(self.records)}
        change(data["videos"])
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / ".github/data/video-metadata.json"
            p.parent.mkdir(parents=True)
            p.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_video_metadata(d)

    def test_wrong_video_source_is_rejected(self):
        self.reject_manifest(lambda r: r["Kv2HmDKY9Jk"].update(sourceUrl="https://www.youtube.com/watch?v=MqkBidv5LRU"))

    def test_substituted_date_is_rejected(self):
        self.reject_manifest(lambda r: r["Kv2HmDKY9Jk"].update(uploadDate="2026-10-28T00:00:00Z"))

    def test_unknown_date_is_never_emitted(self):
        ep = copy.deepcopy(self.catalog[0])
        ep["video_metadata"] = {"status": "unverified", "thumbnailUrl": ep["video_metadata"]["thumbnailUrl"]}
        graph = json.loads(build.json_ld(ep, self.catalog))["@graph"]
        self.assertNotIn("uploadDate", next(n for n in graph if n["@type"] == "VideoObject"))

    def test_strict_check_reports_every_unresolved_episode(self):
        _, errors, _ = site_check.check(build.ROOT, build.HOST, 1024, require_video_dates=True)
        unknown = [r for r in self.records.values() if r["status"] == "unverified"]
        self.assertEqual(len(errors), len(unknown), errors)
        for record in unknown:
            self.assertTrue(any(f"episode-{record['episode']}/index.html: missing uploadDate" in e for e in errors))

    def test_generator_is_reproducible(self):
        files = build.expected_files((build.ROOT / "index.html").read_text(encoding="utf-8"),
                                     (build.ROOT / "site.css").read_text(encoding="utf-8"))
        for path, expected in files.items():
            with self.subTest(path=path):
                self.assertEqual(expected, (build.ROOT / path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
