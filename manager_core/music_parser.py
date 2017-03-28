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

    def __init__(self):
        """Constructor for this class."""
        pass

    @staticmethod
    def check_album_cover_pattern(original_url):
        """Check album cover file pattern."""
        # Example pattern.
        # Naver: http://musicmeta.phinf.naver.net/album/000/645/645112.jpg?type=r204Fll&v=20160623150347
        # Melon: http://cdnimg.melon.co.kr/cm/album/images/006/23/653/623653.jpg
        # Bugs: http://image.bugsm.co.kr/album/images/200/5712/571231.jpg
        # AllMusic: http://cps-static.rovicorp.com/3/JPG_500/MI0002/416/MI0002416076.jpg?partner=allrovi.com
        naver_pattern = re.compile('http://musicmeta[.]phinf[.]naver[.]net/album/.*[.]jpg[?].*')
        melon_pattern = re.compile('http://cdnimg[.]melon[.]co[.]kr/cm/album/images/.*[.]jpg')
        bugs_pattern = re.compile('http://image[.]bugsm[.]co[.]kr/album/images/.*[.]jpg')
        allmusic_pattern = re.compile('http://cps-static[.]rovicorp[.]com/.*[.]jpg.*')

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

        return BeautifulSoup(data.text, "html.parser", from_encoding="utf-8")

    @staticmethod
    def check_input(url_input):
        """Check if input URL is valid and return normalized URL."""
        bugs_pattern = re.compile("bugs[.]co[.]kr/album/[0-9]{1,8}")
        naver_music_pattern = re.compile("music[.]naver[.]com/album/index.nhn[?]albumId=[0-9]{1,8}")
        melon_pattern = re.compile("melon[.]com/album/detail[.]htm[?]albumId=[0-9]{1,8}")
        allmusic_pattern = re.compile("allmusic[.]com/album/.*mw[0-9]{10}")

        match = bugs_pattern.search(url_input)

        if match:
            return "http://music." + match.group()

        match = naver_music_pattern.search(url_input)

        if match:
            return "http://" + match.group()

        match = melon_pattern.search(url_input)

        if match:
            return "http://www." + match.group()

        match = allmusic_pattern.search(url_input)

        if match:
            return "http://www." + match.group()

        return None

    def get_naver_music_data(self, album_url):
        """Get album data from Naver Music and return JSON data."""
        soup = self.get_original_data(album_url)

        # Get artist information.
        artist_data = soup.find('dd', class_='artist')
        if artist_data.find('a'):
            artist_list = artist_data.find_all('a')
            if len(artist_list) == 1:
                artist = artist_list[0].text
            else:
                artist = ", ".join(item.text for item in artist_list)
        else:
            artist = artist_data.find('span').text

        album_title = soup.find('div', class_='info_txt').h2.text
        album_cover = soup.find('div', class_='thumb').img['src']

        disk_num = 1

        tracks = []
        track_list = soup.find('tbody')

        table_row_list = track_list.find_all('tr')

        for row in table_row_list:
            if row.find('td', class_='cd_divide'):
                disk = row.find('td', class_='cd_divide')
                disk_num = int(disk.text.split(' ')[1])
            else:
                if row.find('td', class_='order').text == "{TRACK_NUM}":
                    continue

                track_num = row.find('td', class_='order')
                track_title = row.find('td', class_='name')
                track_artist = row.find('td', class_='artist')

                tracks.append({"disk": disk_num, "track_num": int(track_num.text),
                               "track_title": track_title.find('span', class_='ellipsis').text,
                               "track_artist": track_artist.text.strip()})

        return json.dumps({"artist": artist,
                           "album_title": album_title,
                           "album_cover": album_cover,
                           "tracks": tracks},
                          ensure_ascii=False)

    def get_bugs_data(self, album_url):
        """Get album data from Bugs and returns JSON data."""
        soup = self.get_original_data(album_url)

        # Get artist information.
        basic_info = soup.find('table', class_='info').tr

        if basic_info.find('a'):
            artist_list = basic_info.find('td').find_all('a')
            if len(artist_list) == 1:
                artist = artist_list[0].text
            else:
                artist = ", ".join(item.text for item in artist_list)
        else:
            artist = basic_info.find('td').text.strip()

        album_title = soup.find('header', class_='pgTitle').h1.text
        album_cover = soup.find('div', class_='photos').img['src']

        disk_num = 1

        tracks = []

        # For supporting multiple disks
        track_list_table = soup.find('table', class_='trackList')
        track_list_body = track_list_table.find('tbody')
        table_row_list = track_list_body.find_all('tr')

        for row in table_row_list:
            if row.find('th', attrs={'scope': 'col'}):
                # Get disk number
                disk = row.find('th', attrs={'scope': 'col'})
                disk_num = int(disk.text.split(' ')[1])
            else:
                track_num = row.find('p', class_='trackIndex')
                track_title_data = row.find('p', class_='title')

                # Check track_title_data has an link for the title of album.
                if track_title_data.find('a'):
                    track_title = track_title_data.a.text
                else:
                    track_title = track_title_data.span.text

                # Get track artist
                track_artist_tag = row.find('p', class_='artist')

                # Check to have more artists.
                more_artist = track_artist_tag.find('a', class_='more')

                if more_artist:
                    onclick_text = more_artist['onclick'].split(",")[1].split("||")
                    artist_list = []
                    for i in range(len(onclick_text)):
                        if i % 2 == 0:
                            continue
                        else:
                            artist_list.append(onclick_text[i])

                    track_artist = ", ".join(artist_list)
                else:
                    track_artist = track_artist_tag.a.text

                tracks.append({"disk": disk_num, "track_num": int(track_num.em.text),
                               "track_title": track_title,
                               "track_artist": track_artist})

        return json.dumps({"artist": artist,
                           "album_title": album_title,
                           "album_cover": album_cover,
                           "tracks": tracks},
                          ensure_ascii=False)

    def get_melon_data(self, album_url):
        """Get album data from Melon and returns JSON data."""
        soup = self.get_original_data(album_url)

        # Get artist name.
        basic_info = soup.find('dl', class_='song_info clfix')

        if basic_info.find('span'):
            artist_list = basic_info.find_all('span', class_=None)
            if len(artist_list) == 1:
                artist = artist_list[0].text
            else:
                artist = ", ".join(item.text for item in artist_list)
        else:
            artist = basic_info.find('dd').text.strip()

        # Get album title. (Exclude strong and span tag)
        album_title = soup.find('p', class_='albumname').find_all(text=True)[-1].strip()

        album_cover_thumb = soup.find('div', class_='wrap_thumb')
        album_cover = album_cover_thumb.find('img')['src']

        # Get track list
        tracks = []

        # To support multiple disks
        track_list_table = soup.find_all('table', attrs={'border': '1'})

        for disk in track_list_table:
            disk_num = int(disk.find('caption').text.split(" ")[0][2:])

            track_list_body = disk.find('tbody')
            table_row_list = track_list_body.find_all('tr')

            for row in table_row_list:
                track_num = row.find('td', class_='no').div.text
                track_title_data = row.find('div', class_='ellipsis')
                check_track_info = track_title_data.find_all('a')

                if len(check_track_info) == 2:
                    # Song you can play.
                    track_title = check_track_info[-1].text
                else:
                    # Song you can't play.
                    track_title = track_title_data.find_all('span')[-1].text

                # Get track artist
                track_artist_list = row.find('div', id='artistName').find('span', class_="checkEllipsis").find_all('a')

                if len(track_artist_list) == 1:
                    track_artist = track_artist_list[0].text
                else:
                    track_artist = ", ".join(item.text for item in track_artist_list)

                tracks.append({"disk": disk_num, "track_num": int(track_num),
                               "track_title": track_title,
                               "track_artist": track_artist})

        return json.dumps({"artist": artist,
                           "album_title": album_title,
                           "album_cover": album_cover,
                           "tracks": tracks},
                          ensure_ascii=False)

    def get_allmusic_data(self, album_url):
        """Get album data from AllMusic and return JSON data."""
        soup = self.get_original_data(album_url)

        # Get sidebar. (To get album cover)
        sidebar = soup.find('div', class_='sidebar')

        # Get contents. (To get artist, album title, track lists)
        content = soup.find('div', class_='content')

        # Get album artist from content.
        artist_tag = content.find('h2', class_='album-artist')

        if artist_tag.find('a'):
            artist_list = artist_tag.find_all('a')
            if len(artist_list) == 1:
                artist = artist_list[0].text
            else:
                artist = ", ".join(item.text for item in artist_list)
        else:
            artist = artist_tag.find('span').text

        album_title = content.find('h1', class_='album-title').text

        album_cover_thumb = sidebar.find('div', class_='album-contain')
        album_cover = album_cover_thumb.find('img', class_='media-gallery-image')['src']

        # Get track list
        tracks = []

        # For supporting multiple disks
        track_list_table = content.find_all('div', class_='disc')

        for disk in track_list_table:
            # Get disk number.
            if len(track_list_table) == 1:
                disk_num = 1
            else:
                disk_num = int(disk.find('div', class_='headline').h3.text.strip().split(" ")[-1])

            track_list_body = disk.find('tbody')
            table_row_list = track_list_body.find_all('tr')

            for row in table_row_list:
                track_num = row.find('td', class_='tracknum').text
                track_title = row.find('div', class_='title').find('a').text
                track_artist_list = row.find('td', class_='performer').find_all('a')

                if len(track_artist_list) == 1:
                    track_artist = track_artist_list[0].text
                else:
                    track_artist = ", ".join(item.text for item in track_artist_list)

                tracks.append({"disk": disk_num, "track_num": int(track_num),
                               "track_title": track_title,
                               "track_artist": track_artist})

        return json.dumps({"artist": artist,
                           "album_title": album_title,
                           "album_cover": album_cover,
                           "tracks": tracks},
                          ensure_ascii=False)

    def get_parsed_data(self, input_url):
        """Get JSON data from music sites."""
        bugs_pattern = re.compile("bugs[.]co[.]kr")
        naver_music_pattern = re.compile("music[.]naver[.]com")
        melon_pattern = re.compile("melon[.]com")
        allmusic_pattern = re.compile("allmusic[.]com")

        match = bugs_pattern.search(input_url)
        if match:
            return self.get_bugs_data(input_url)

        match = naver_music_pattern.search(input_url)
        if match:
            return self.get_naver_music_data(input_url)

        match = melon_pattern.search(input_url)
        if match:
            return self.get_melon_data(input_url)

        match = allmusic_pattern.search(input_url)
        if match:
            return self.get_allmusic_data(input_url)

        return None
