"""
Music Parser from music information sites.

Author: Yungon Park
"""
import re
import json

import requests
from bs4 import BeautifulSoup


class MusicParser(object):
    """Base parser class for parsing album information from music sites."""

    @staticmethod
    def check_album_cover_pattern(original_url):
        """Check album cover file pattern."""
        naver_pattern = re.compile('http://musicmeta[.]phinf[.]naver[.]net/album/.*[.]jpg[?].*')
        melon_pattern = re.compile('http://cdnimg[.]melon[.]co[.]kr/cm/album/images/.*[.]jpg')
        bugs_pattern = re.compile('https://image[.]bugsm[.]co[.]kr/album/images/.*[.]jpg')
        allmusic_pattern = re.compile('https://cps-static[.]rovicorp[.]com/.*[.]jpg.*')

        result = naver_pattern.search(original_url)
        if result:
            return True

        result = melon_pattern.search(original_url)
        if result:
            return True

        result = bugs_pattern.search(original_url)
        if result:
            return True

        result = allmusic_pattern.search(original_url)
        if result:
            return True

        return False

    @staticmethod
    def get_original_data(album_url):
        """Get original data for an album from web sites."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'
        }
        data = requests.get(album_url, headers=headers)

        return BeautifulSoup(data.text, "html.parser")

    @staticmethod
    def check_input(url_input):
        """Check if input URL is valid and return normalized URL."""
        bugs_pattern = re.compile("bugs[.]co[.]kr/album/[0-9]{1,8}")
        naver_music_pattern = re.compile("music[.]naver[.]com/album/index.nhn[?]albumId=[0-9]{1,8}")
        melon_pattern = re.compile("melon[.]com/album/detail[.]htm[?]albumId=[0-9]{1,8}")
        allmusic_pattern = re.compile("allmusic[.]com/album/.*mw[0-9]{10}")

        match = bugs_pattern.search(url_input)
        if match:
            return "http://music." + match.group(), BugsParser()

        match = naver_music_pattern.search(url_input)
        if match:
            return "http://" + match.group(), NaverMusicParser()

        match = melon_pattern.search(url_input)
        if match:
            return "http://www." + match.group(), MelonParser()

        match = allmusic_pattern.search(url_input)
        if match:
            return "http://www." + match.group(), AllMusicParser()

        return None, None

    def get_parsed_data(self, input_url):
        """Get JSON data from music sites."""
        pass

    def get_artist(self, artist_data):
        """Get artist information"""
        pass

    def get_track(self, track_data, disk_num):
        """Get single track information from tag."""
        pass

    def get_track_list(self, track_row_list):
        """Get track list from 'tr' tags."""
        pass

    def parse_album(self, album_url):
        """Parse album data from music information site."""
        pass


class NaverMusicParser(MusicParser):
    """ Parsing album information from Naver Music. """

    def get_artist(self, artist_data):
        """Get artist information"""
        if artist_data.find('a'):
            artist_list = artist_data.find_all('a')
            if len(artist_list) == 1:
                artist = artist_list[0].text
            else:
                artist = ", ".join(item.text for item in artist_list)
        else:
            artist = artist_data.find('span').text

        return artist

    def get_track(self, track_data, disk_num):
        """Get single track information from tag."""
        track = dict()
        track['disk'] = disk_num
        track['track_num'] = int(track_data.find('td', class_='order').text)
        track['track_title'] = track_data.find('td', class_='name').find('span', class_='ellipsis').text
        track['track_artist'] = track_data.find('td', class_='artist').text.strip()
        return track

    def get_track_list(self, track_row_list):
        """Get track list from 'tr' tags."""
        disk_num = 1    # Set default disk number.

        tracks = []
        for row in track_row_list:
            if row.find('td', class_='cd_divide'):
                disk = row.find('td', class_='cd_divide')
                disk_num = int(disk.text.split(' ')[1])
            else:
                if row.find('td', class_='order').text == "{TRACK_NUM}":
                    continue

                tracks.append(self.get_track(row, disk_num))

        return tracks

    def parse_album(self, album_url):
        """Parse album data from music information site."""
        soup = self.get_original_data(album_url)

        album_data = dict()
        album_data['artist'] = self.get_artist(soup.find('dd', class_='artist'))
        album_data['album_title'] = soup.find('div', class_='info_txt').h2.text
        album_data['album_cover'] = soup.find('div', class_='thumb').img['src']
        album_data['tracks'] = self.get_track_list(soup.find('tbody').find_all('tr'))

        return json.dumps(album_data, ensure_ascii=False)

    def get_parsed_data(self, input_url):
        """Get parsed data and return JSON object."""
        pattern = re.compile("music[.]naver[.]com")

        match = pattern.search(input_url)
        if match:
            return self.parse_album(input_url)
        else:
            return None


class BugsParser(MusicParser):
    """ Parsing album information from Bugs. """

    def get_artist(self, artist_data):
        """Get artist information"""
        if artist_data.find('a'):
            artist_list = artist_data.find('td').find_all('a')
            if len(artist_list) == 1:
                artist = artist_list[0].text
            else:
                artist = ", ".join(item.text for item in artist_list)
        else:
            artist = artist_data.find('td').text.strip()

        return artist

    def get_track(self, track_data, disk_num):
        """Get single track information from tag."""
        track = dict()

        track['disk'] = disk_num
        track['track_num'] = int(track_data.find('p', class_='trackIndex').em.text)
        track_title_data = track_data.find('p', class_='title')

        if track_title_data.find('a'):
            track['track_title'] = track_title_data.a.text
        else:
            track['track_title'] = track_title_data.span.text

        track_artist_tag = track_data.find('p', class_='artist')
        track_artists = track_artist_tag.find('a', class_='more')

        if track_artists:
            onclick_text = track_artists['onclick'].split(",")[1].split("||")
            artist_list = []
            for i in range(len(onclick_text)):
                if i % 2 == 0:
                    continue
                else:
                    artist_list.append(onclick_text[i])

            track['track_artist'] = ", ".join(artist_list)
        else:
            track['track_artist'] = track_artist_tag.a.text

        return track

    def get_track_list(self, track_row_list):
        """Get track list from 'tr' tags."""
        disk_num = 1    # Set default disk number.

        tracks = []

        for row in track_row_list:
            if row.find('th', attrs={'scope': 'colgroup'}):
                # Get disk number
                disk = row.find('th', attrs={'scope': 'colgroup'})
                disk_num = int(disk.text.split(' ')[1])
            else:
                tracks.append(self.get_track(row, disk_num))

        return tracks

    def parse_album(self, album_url):
        """Parse album data from music information site."""
        soup = self.get_original_data(album_url)

        # Get artist information.
        album_data = dict()
        album_data['artist'] = self.get_artist(soup.find('table', class_='info').tr)
        album_data['album_title'] = soup.find('header', class_='pgTitle').h1.text
        album_data['album_cover'] = soup.find('div', class_='photos').img['src']

        # For supporting multiple disks (And try to parse except first row)
        table_row_list = soup.find('table', class_='trackList').find_all('tr')[1:]
        album_data['tracks'] = self.get_track_list(table_row_list)

        return json.dumps(album_data, ensure_ascii=False)

    def get_parsed_data(self, input_url):
        """Get parsed data and return JSON object."""
        pattern = re.compile("bugs[.]co[.]kr")

        match = pattern.search(input_url)
        if match:
            return self.parse_album(input_url)
        else:
            return None


class MelonParser(MusicParser):
    """ Parsing album information from Melon. """

    def get_artist(self, artist_data):
        """Get artist information"""
        if artist_data.find('span'):
            artist_list = artist_data.find_all('span', class_=None)
            if len(artist_list) == 1:
                artist = artist_list[0].text
            else:
                artist = ", ".join(item.text for item in artist_list)
        else:
            artist = artist_data.find('dd').text.strip()

        return artist

    def get_track(self, track_data, disk_num):
        """Get single track information from tag."""
        track = dict()
        track['disk'] = disk_num
        track['track_num'] = int(track_data.find('span', class_='rank').text)
        track_title_data = track_data.find('div', class_='ellipsis')
        check_track_info = track_title_data.find('a')

        if check_track_info:
            # Song you can play.
            track['track_title'] = check_track_info.text
        else:
            # Song you can't play.
            track['track_title'] = track_title_data.find('span', class_='disabled').text

        # Get track artist
        track_artist_list = track_data.find('div', class_='rank02') \
                                      .find('span', class_='checkEllipsis') \
                                      .find_all('a')

        if len(track_artist_list) == 1:
            track['track_artist'] = track_artist_list[0].text
        else:
            # Support multiple artists for one song.
            track['track_artist'] = ", ".join(item.text for item in track_artist_list)

        return track

    def get_track_list(self, track_row_list):
        """Get track list from 'tr' tags."""
        tracks = []
        disk_num = 1

        for disk in track_row_list:
            track_list = disk.find_all('tr')[1:]

            for row in track_list:
                if 'class' in row.attrs:
                    disk_num = int(row.find('strong').text[2:])
                    continue

                tracks.append(self.get_track(row, disk_num))

        return tracks

    def parse_album(self, album_url):
        """Parse album data from music information site."""
        soup = self.get_original_data(album_url)

        album_data = dict()
        album_data['artist'] = self.get_artist(soup.find('div', class_='artist'))
        # Exclude strong and span tag when getting album title.
        album_data['album_title'] = soup.find('div', class_='song_name').find_all(text=True)[-1].strip()
        album_data['album_cover'] = soup.find('div', class_='thumb').find('img')['src']
        album_data['tracks'] = self.get_track_list(soup.find('div', class_='d_song_list').
                                                   find_all('table'))

        return json.dumps(album_data, ensure_ascii=False)

    def get_parsed_data(self, input_url):
        """Get parsed data and return JSON object."""
        pattern = re.compile("melon[.]com")

        match = pattern.search(input_url)
        if match:
            return self.parse_album(input_url)
        else:
            return None


class AllMusicParser(MusicParser):
    """ Parsing album information from AllMusic. """

    def get_artist(self, artist_data):
        """Get artist information"""
        if artist_data.find('a'):
            artist_list = artist_data.find_all('a')
            if len(artist_list) == 1:
                artist = artist_list[0].text.strip()
            else:
                artist = ", ".join(item.text.strip() for item in artist_list)
        else:
            artist = artist_data.find('span').text.strip()

        return artist

    def get_track(self, track_data, disk_num):
        """Get single track information from tag."""
        track = dict()
        track['disk'] = disk_num
        track['track_num'] = track_data.find('td', class_='tracknum').text
        track['track_title'] = track_data.find('div', class_='title').find('a').text
        track_artist_list = track_data.find('td', class_='performer').find_all('a')

        if len(track_artist_list) == 1:
            track['track_artist'] = track_artist_list[0].text
        else:
            track['track_artist'] = ", ".join(item.text for item in track_artist_list)

        return track

    def get_track_list(self, track_row_list):
        """Get track list from 'tr' tags."""
        tracks = []

        for disk in track_row_list:
            if len(track_row_list) == 1:
                disk_num = 1
            else:
                disk_num = int(disk.find('div', class_='headline').h3.text.strip().split(" ")[-1])

            table_row_list = disk.find('tbody').find_all('tr')

            for row in table_row_list:
                tracks.append(self.get_track(row, disk_num))

        return tracks

    def parse_album(self, album_url):
        """Parse album data from music information site."""
        soup = self.get_original_data(album_url)

        album_data = dict()

        sidebar = soup.find('div', class_='sidebar')        # To get album cover.
        content = soup.find('div', class_='content')        # To get artist, album title, track lists.

        album_data['artist'] = self.get_artist(content.find('h2', class_='album-artist'))
        album_data['album_title'] = content.find('h1', class_='album-title').text.strip()
        album_data['album_cover'] = sidebar.find('div', class_='album-contain').find(
            'img', class_='media-gallery-image'
        )['src']
        album_data['tracks'] = self.get_track_list(content.find_all('div', class_='disc'))

        return json.dumps(album_data, ensure_ascii=False)

    def get_parsed_data(self, input_url):
        """Get parsed data and return JSON object."""
        pattern = re.compile("allmusic[.]com")

        match = pattern.search(input_url)
        if match:
            return self.parse_album(input_url)
        else:
            return None
