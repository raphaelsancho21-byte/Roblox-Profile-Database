import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import robloxdb_v2 as db
import robloxdb_v2_tui
from robloxdb_visual import render
from robloxdb_presence import check_presence

PROFILE = {
    "profile": {"id": 1234, "name": "SamplePlayer", "displayName": "Sample",
                "created": "2021-01-01T00:00:00Z", "description": "Example"},
    "social_counts": {"friends": 10, "followers": 20, "following": 30},
    "favorite_games": [], "created_games": [], "currently_wearing_asset_ids": [],
    "username_history": [], "collected_at_utc": "2026-11-22T00:00:00Z"
}

class CoreTests(unittest.TestCase):
    def test_favorites_and_cases(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(db, "FAV_FILE", Path(temp)/"favorites.json"), patch.object(db, "CASES", Path(temp)/"cases"):
                db.favorite("user", 1234, "SamplePlayer")
                self.assertEqual(db.favorites()[0]["id"], "1234")
                self.assertEqual(db.remove_favorite("user", 1234), 1)
                case=db.create_case("SamplePlayer", "Brookhaven", "Teste local")
                self.assertEqual(db.close_case(case["id"])["status"],"fechada")
    def test_history(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(db, "HISTORY_FILE", Path(temp)/"history.json"):
                db.add_history("profile", "1234", "SamplePlayer")
                self.assertEqual(db.history()[0]["id"], "1234")
    def test_comparison(self):
        x=db.compare_profiles(PROFILE, PROFILE)
        self.assertTrue(any(row[0]=="Seguidores" for row in x))
    def test_game_id_input_rejects_names(self):
        with self.assertRaises(ValueError):
            db.game_from_input("Brookhaven")
    def test_html_renders_without_network(self):
        with patch("robloxdb_visual.thumbnails", return_value={}):
            doc=render(PROFILE)
            self.assertIn("SamplePlayer",doc)
            self.assertIn("PROFILE EXPLORER",doc)
    def test_presence_online(self):
        from unittest.mock import MagicMock
        response = MagicMock()
        response.__enter__.return_value = response
        response.read.return_value = b'{"userPresences":[{"userId":1234,"userPresenceType":2}]}'
        with patch("robloxdb_presence.urllib.request.urlopen", return_value=response):
            value = check_presence(1234)
            self.assertEqual(value["status"], "Jogando")

    def test_presence_unavailable_not_offline(self):
        from urllib.error import HTTPError
        with patch("robloxdb_presence.urllib.request.urlopen", side_effect=HTTPError("url",403,"Forbidden",{},None)):
            value = check_presence(1234)
            self.assertEqual(value["status"], "Indisponível")

    def test_tui_is_importable(self):
        self.assertTrue(callable(robloxdb_v2_tui.run))

if __name__=="__main__":
    unittest.main()
