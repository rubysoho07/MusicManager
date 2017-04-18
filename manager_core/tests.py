# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.test import TestCase
from .music_parser import MusicParser, MelonParser, BugsParser, AllMusicParser, NaverMusicParser


# Create your tests here.
class MusicParserTestCase(TestCase):
    """
    Test for Music Parser.
    
    Example 1, 2 are for Korean music sites. (Bugs, Melon, Naver)
    Example 1: Crying Nut/No Brain - 96
    Example 2: Various Artists - Club Heavy 20th
    
    Example 3, 4 are for AllMusic.
    Example 3: The Smashing Pumpkins - Mellon Collie and the Infinite Sadness
    Example 4: Various Artists - Judgment Night OST
    """
    bugs_example_1 = "http://music.bugs.co.kr/album/450734"
    bugs_example_2 = "http://music.bugs.co.kr/album/20032982"
    melon_example_1 = "http://www.melon.com/album/detail.htm?albumId=2281828"
    melon_example_2 = "http://www.melon.com/album/detail.htm?albumId=2681984"
    naver_music_example_1 = "http://music.naver.com/album/index.nhn?albumId=451880"
    naver_music_example_2 = "http://music.naver.com/album/index.nhn?albumId=634351"
    all_music_example_3 = "http://www.allmusic.com/album/mellon-collie-and-the-infinite-sadness-mw0000645152"
    all_music_example_4 = "http://www.allmusic.com/album/judgment-night-mw0000101514"

    bugs_parser = None
    naver_music_parser = None
    melon_parser = None
    all_music_parser = None

    def setUp(self):
        """Configuration before tests."""
        self.bugs_parser = BugsParser()
        self.naver_music_parser = NaverMusicParser()
        self.melon_parser = MelonParser()
        self.all_music_parser = AllMusicParser()

    def test_check_input(self):
        """Check input URL is valid and return correct URL and parser object to parse."""
        bugs_result, self.bugs_parser = MusicParser.check_input(self.bugs_example_1)
        self.assertEqual(bugs_result, self.bugs_example_1)
        self.assertNotEqual(self.bugs_parser, None)

        melon_result, self.melon_parser = MusicParser.check_input(self.melon_example_1)
        self.assertEqual(melon_result, self.melon_example_1)
        self.assertNotEqual(self.melon_parser, None)

        naver_music_result, self.naver_music_parser = MusicParser.check_input(self.naver_music_example_1)
        self.assertEqual(naver_music_result, self.naver_music_example_1)
        self.assertNotEqual(self.naver_music_parser, None)

        all_music_result, self.all_music_parser = MusicParser.check_input(self.all_music_example_3)
        self.assertEqual(all_music_result, self.all_music_example_3)
        self.assertNotEqual(self.all_music_parser, None)

    def test_check_album_cover_pattern(self):
        """Check album cover patterns from music information sites."""
        naver_pattern = "http://musicmeta.phinf.naver.net/album/000/645/645112.jpg?type=r204Fll&v=20160623150347"
        melon_pattern = "http://cdnimg.melon.co.kr/cm/album/images/006/23/653/623653.jpg"
        bugs_pattern = "http://image.bugsm.co.kr/album/images/200/5712/571231.jpg"
        all_music_pattern = "http://cps-static.rovicorp.com/3/JPG_500/MI0002/416/MI0002416076.jpg?partner=allrovi.com"

        naver_result = MusicParser.check_album_cover_pattern(naver_pattern)
        self.assertEqual(naver_result, True)

        melon_result = MusicParser.check_album_cover_pattern(melon_pattern)
        self.assertEqual(melon_result, True)

        bugs_result = MusicParser.check_album_cover_pattern(bugs_pattern)
        self.assertEqual(bugs_result, True)

        all_music_result = MusicParser.check_album_cover_pattern(all_music_pattern)
        self.assertEqual(all_music_result, True)

        error_result = MusicParser.check_album_cover_pattern("http://music.bugs.co.kr/album/450734")
        self.assertEqual(error_result, False)

    def test_check_naver_music(self):
        """Check parsing from Naver Music."""
        result1 = self.naver_music_parser.parse_album(self.naver_music_example_1)
        result1_json = json.loads(result1)
        self.assertEqual(result1_json['artist'], "크라잉 넛, 노브레인")
        self.assertEqual(result1_json['album_title'], "96")

        result2 = self.naver_music_parser.parse_album(self.naver_music_example_2)
        result2_json = json.loads(result2)
        self.assertEqual(result2_json['artist'], "Various Artists")
        self.assertIn("CLUB HEAVY 20th", result2_json['album_title'])

    def test_check_melon(self):
        """Check parsing from Melon."""
        result1 = self.melon_parser.parse_album(self.melon_example_1)
        result1_json = json.loads(result1)
        self.assertEqual(result1_json['artist'], "크라잉 넛, 노브레인")
        self.assertEqual(result1_json['album_title'], "96")

        result2 = self.melon_parser.parse_album(self.melon_example_2)
        result2_json = json.loads(result2)
        self.assertEqual(result2_json['artist'], "Various Artists")
        self.assertIn("Club Heavy 20th", result2_json['album_title'])

    def test_check_bugs(self):
        """Check parsing from Naver Music."""
        result1 = self.bugs_parser.parse_album(self.bugs_example_1)
        result1_json = json.loads(result1)
        self.assertEqual(result1_json['artist'], "크라잉넛(Crying Nut), 노브레인(No Brain)")
        self.assertEqual(result1_json['album_title'], "96")

        result2 = self.bugs_parser.parse_album(self.bugs_example_2)
        result2_json = json.loads(result2)
        self.assertEqual(result2_json['artist'], "Various Artists")
        self.assertIn("Club Heavy 20th", result2_json['album_title'])

    def test_check_allmusic(self):
        """Check parsing from AllMusic."""
        result3 = self.all_music_parser.parse_album(self.all_music_example_3)
        result3_json = json.loads(result3)
        self.assertEqual(result3_json['artist'], "The Smashing Pumpkins")
        self.assertEqual(result3_json['album_title'], "Mellon Collie and the Infinite Sadness")

        result4 = self.all_music_parser.parse_album(self.all_music_example_4)
        result4_json = json.loads(result4)
        self.assertEqual(result4_json['artist'], "Original Soundtrack")
        self.assertEqual(result4_json['album_title'], "Judgment Night")

    def test_get_parsed_data(self):
        """Check all procedures to parse information from music sites."""
        result1 = self.naver_music_parser.get_parsed_data(self.naver_music_example_1)
        self.assertNotEqual(result1, None)

        result2 = self.melon_parser.get_parsed_data(self.melon_example_1)
        self.assertNotEqual(result2, None)

        result3 = self.bugs_parser.get_parsed_data(self.bugs_example_1)
        self.assertNotEqual(result3, None)

        result4 = self.all_music_parser.get_parsed_data(self.all_music_example_3)
        self.assertNotEqual(result4, None)
