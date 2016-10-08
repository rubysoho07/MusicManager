# Music Parser (by Yungon Park)
# 2016.07.09
# 2016.10.05 Add Melon parser.

import requests
import re
import os
import json
from bs4 import BeautifulSoup

test_url_naver = "http://music.naver.com/album/index.nhn?albumId=645112"
test_url_bugs = "http://music.bugs.co.kr/album/571231"
test_url_naver_2disk = "http://music.naver.com/album/index.nhn?albumId=210850"
test_url_bugs_2disk = "http://music.bugs.co.kr/album/311371"
test_url_melon = "http://www.melon.com/album/detail.htm?albumId=99237"
test_url_melon_2disk = "http://www.melon.com/album/detail.htm?albumId=2681984"

"""
Test URL patterns.
------------------
http://music.bugs.co.kr/album/179142?wl_ref=list_tr_11
http://music.naver.com/album/index.nhn?albumId=36231
http://m.music.naver.com/album/index.nhn?albumId=503711&type=
http://m.bugs.co.kr/album/553073
http://music.bugs.co.kr/album/1
http://music.bugs.co.kr/album/10
http://music.naver.com/album/index.nhn?albumId=10
http://music.naver.com/album/index.nhn?albumId=1
http://music.bugs.co.kr/album/20032982?wl_ref=list_tr_11
http://music.naver.com/album/index.nhn?albumId=634351
http://www.melon.com/album/detail.htm?albumId=99237
http://m.app.melon.com/album/music.htm?albumId=99237
http://www.melon.com/album/detail.htm?albumId=2681984
"""


# Save album cover image (with requests library)
def save_image(source, target):
    # If target file exists, return
    if os.path.exists(target):
        return

    # Else, save album cover image
    with open(target, 'wb') as handle:
        response = requests.get(source, stream=True)

        if not response.ok:
            # print "Getting image error"
            return

        for block in response.iter_content(1024):
            handle.write(block)


# Get album data from Naver Music (JSON data)
def get_naver_music_data(album_url):
    # Get original data
    data = requests.get(album_url)
    soup = BeautifulSoup(data.text, "html.parser")

    # If encoding is None, you'll get UnicodeError (-_-)
    soup.prettify(encoding="utf-8")

    # Get and print artist information.
    artist_data = soup.find('dd', class_='artist')
    if artist_data.find('a'):
        artist = artist_data.find('a').text
    else:
        artist = artist_data.find('span').text

    # Get and print album title.
    album_title = soup.find('div', class_='info_txt').h2.text

    # Get and print album cover image.
    album_cover = soup.find('div', class_='thumb').img['src']

    # Save album cover image.
    # ex) http://musicmeta.phinf.naver.net/album/000/645/645112.jpg?type=r204Fll&v=20160623150347
    if not os.path.exists("manager_core/static/manager_core/images"):
        os.mkdir("manager_core/static/manager_core/images")

    save_image(album_cover, "manager_core/static/manager_core/images/naver_" + album_cover.split("/")[-1].split("?")[0])

    # Default number of disk = 1
    disk_num = 1

    # Initialize tracks
    tracks = []

    # Get track list

    # For supporting multiple disks
    track_list_body = soup.find('tbody')

    table_row_list = track_list_body.find_all('tr')

    for row in table_row_list:
        if row.find('td', class_='cd_divide'):
            # Disk number
            disk = row.find('td', class_='cd_divide')
            # print disk.text
            disk_num = int(disk.text.split(' ')[1])
        else:
            if row.find('td', class_='order').text == "{TRACK_NUM}":
                continue

            # Get track number
            track_num = row.find('td', class_='order')

            # Get track title
            track_title = row.find('td', class_='name')
            # Get only song title (exclude '19' sign and 'title' mark)

            # Get track artist
            track_artist = row.find('td', class_='artist')
            # Song artist name needs to be striped.

            # Add to track list
            tracks.append({"disk": disk_num, "track_num": int(track_num.text),
                           "track_title": track_title.find('span', class_='ellipsis').text,
                           "track_artist": track_artist.text.strip()})

    # Make JSON data and return it.
    return json.dumps({"artist": artist,
                       "album_title": album_title,
                       "album_cover": "naver_" + album_cover.split("/")[-1].split("?")[0],
                       "tracks": tracks},
                      ensure_ascii=False)


# Get album data from Bugs. (JSON data)
def get_bugs_data(album_url):
    # Get original data
    data = requests.get(album_url)
    soup = BeautifulSoup(data.text, "html.parser")

    # If encoding is None, you'll get UnicodeError (-_-)
    soup.prettify(encoding="utf-8")

    # Get and print artist information.
    basic_info = soup.find('table', class_='info').tr

    if basic_info.find('a'):
        artist = basic_info.find('a').text
    else:
        artist = basic_info.find('td').text.strip()

    # Get and print album title.
    album_title = soup.find('header', class_='pgTitle').h1.text

    # Get and print album cover image.
    album_cover = soup.find('div', class_='photos').img['src']

    # Save album cover image.
    # ex) http://image.bugsm.co.kr/album/images/200/5712/571231.jpg
    if not os.path.exists("manager_core/static/manager_core/images"):
        os.mkdir("manager_core/static/manager_core/images")

    save_image(album_cover, "manager_core/static/manager_core/images/bugs_" + album_cover.split("/")[-1])

    # Default number of disk = 1
    disk_num = 1

    # Get track list
    # Initialize track lists
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
            # Get track number
            track_num = row.find('p', class_='trackIndex')

            # Get track title
            track_title_data = row.find('p', class_='title')
            if track_title_data.find('a'):
                track_title = track_title_data.a.text
            else:
                track_title = track_title_data.span.text

            # Get track artist
            track_artist = row.find('p', class_='artist')

            # Add to track list
            tracks.append({"disk": disk_num, "track_num": int(track_num.em.text),
                           "track_title": track_title,
                           "track_artist": track_artist.a.text})

    # Make JSON data and return it.
    return json.dumps({"artist": artist,
                       "album_title": album_title,
                       "album_cover": "bugs_" + album_cover.split("/")[-1],
                       "tracks": tracks},
                      ensure_ascii=False)


# Get album data from Melon. (JSON data)
def get_melon_data(album_url):
    # Get original data
    data = requests.get(album_url)
    soup = BeautifulSoup(data.text, "html.parser")

    # If encoding is None, you'll get UnicodeError (-_-)
    soup.prettify(encoding="utf-8")

    # Get and print artist information. (Finished)
    basic_info = soup.find('dl', class_='song_info clfix')

    if basic_info.find('span'):
        artist = basic_info.find('span').text
    else:
        artist = basic_info.find('dd').text.strip()

    # Get and print album title. (Finished)
    # About using find_all() method, see BeautifulSoup documentation.
    # When you use text=True on find_all(), find_all() finds all texts from tags, 
    # and it return them as a list.
    # I just wanted to exclude text from "span" and "strong" tags.
    album_title = soup.find('p', class_='albumname').find_all(text=True)[-1].strip()

    # Get and print album cover image. (Finished)
    album_cover_thumb = soup.find('div', class_='wrap_thumb')
    album_cover = album_cover_thumb.find('img')['src']

    # Save album cover image. (Finished)
    # ex) http://cdnimg.melon.co.kr/cm/album/images/006/23/653/623653.jpg
    if not os.path.exists("manager_core/static/manager_core/images"):
        os.mkdir("manager_core/static/manager_core/images")

    save_image(album_cover, "manager_core/static/manager_core/images/melon_" + album_cover.split("/")[-7])

    # Get track list
    # Initialize track lists
    tracks = []

    # For supporting multiple disks
    track_list_table = soup.find_all('table', attrs={'border': '1'})

    for disk in track_list_table:
        # Get disk number.
        disk_num = int(disk.find('caption').text.split(" ")[0][2:])

        track_list_body = disk.find('tbody')

        table_row_list = track_list_body.find_all('tr')

        for row in table_row_list:

            # Get track number
            track_num = row.find('td', class_='no').div.text

            # Get track title
            track_title_data = row.find('div', class_='ellipsis')

            check_track_info = track_title_data.find_all('a')

            if len(check_track_info) == 2:
                # Song you can play.
                track_title = check_track_info[-1].text
            else:
                # Song you can't play.
                track_title = track_title_data.find_all('span')[-1].text

            # Get track artist
            track_artist = row.find('div', id='artistName')

            # Add to track list
            tracks.append({"disk": disk_num, "track_num": int(track_num),
                           "track_title": track_title,
                           "track_artist": track_artist.a.text})

    # Make JSON data and return it.
    return json.dumps({"artist": artist,
                       "album_title": album_title,
                       "album_cover": "melon_" + album_cover.split("/")[-7],
                       "tracks": tracks},
                      ensure_ascii=False)

# Get album data from AllMusic. (JSON data)
def get_allmusic_data(album_url):
    # Get original data
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'
    }
    data = requests.get(album_url, headers=headers)
    soup = BeautifulSoup(data.text, "html.parser")

    # If encoding is None, you'll get UnicodeError (-_-)
    soup.prettify(encoding="utf-8")

    # Get sidebar. (To get album cover)
    sidebar = soup.find('div', class_='sidebar')

    # Get contents. (To get artist, album title, track lists)
    content = soup.find('div', class_='content')
    
    # Get artist from content. 
    artist = content.find('h2').find('a').text

    # get album title from content.
    album_title = content.find('h1', class_='album-title').text

    # Get and print album cover image. 
    album_cover_thumb = sidebar.find('div', class_='album-contain')
    album_cover = album_cover_thumb.find('img', class_='media-gallery-image')['src']

    # Save album cover image. 
    # ex) http://cps-static.rovicorp.com/3/JPG_500/MI0002/416/MI0002416076.jpg?partner=allrovi.com
    if not os.path.exists("manager_core/static/manager_core/images"):
        os.mkdir("manager_core/static/manager_core/images")

    save_image(album_cover, "manager_core/static/manager_core/images/allmusic_" + album_cover.split("/")[-1].split("?")[0])

    # Get track list
    # Initialize track lists
    tracks = []

    # For supporting multiple disks
    track_list_table = content.find_all('div', class_='disc')

    for disk in track_list_table:
        # Get disk number.
        if len(track_list_table) == 1:
            disk_num = 1
        else:
            disk_num = int(disk.find('div', class_='headline').h3.text.split(" ")[-1])

        track_list_body = disk.find('tbody')

        table_row_list = track_list_body.find_all('tr')

        for row in table_row_list:

            # Get track number
            track_num = row.find('td', class_='tracknum').text

            # Get track title
            track_title = row.find('div', class_='title').find('a').text

            # Get track artist
            track_artist = row.find('td', class_='performer').find('a').text

            # Add to track list
            tracks.append({"disk": disk_num, "track_num": int(track_num),
                           "track_title": track_title,
                           "track_artist": track_artist})

    # Make JSON data and return it.
    return json.dumps({"artist": artist,
                       "album_title": album_title,
                       "album_cover": "allmusic_" + album_cover.split("/")[-1].split("?")[0],
                       "tracks": tracks},
                      ensure_ascii=False)


# Check if input URL is valid.
def check_input(url_input):
    # Bugs URL pattern: bugs[.]co[.]kr\/album\/[0-9]{1,6}
    # Naver music URL pattern: music[.]naver[.]com\/album\/index.nhn[?]albumId=[0-9]{1,6}
    # Melon URL pattern: melon[.]com\/album\/detail[.]htm[?]albumId=[0-9]{1,8}
    # AllMusic URL pattern: allmusic[.]com\/album\/.*mw[0-9]{10}

    bugs_pattern = re.compile("bugs[.]co[.]kr\/album\/[0-9]{1,8}")
    naver_music_pattern = re.compile("music[.]naver[.]com\/album\/index.nhn[?]albumId=[0-9]{1,8}")
    melon_pattern = re.compile("melon[.]com\/album\/detail[.]htm[?]albumId=[0-9]{1,8}")
    allmusic_pattern = re.compile("allmusic[.]com\/album\/.*mw[0-9]{10}")

    # Check bugs pattern
    m = bugs_pattern.search(url_input)

    if m:
        return "http://music." + m.group()

    # Check naver_music_pattern
    m = naver_music_pattern.search(url_input)

    if m:
        return "http://" + m.group()

    # Check melon pattern.
    m = melon_pattern.search(url_input)

    if m:
        return "http://www." + m.group()

    # Check AllMusic pattern.
    m = allmusic_pattern.search(url_input)

    if m:
        return "http://www." + m.group()

    return ""


# For Testing.
if __name__ == "__main__":
    input_val = raw_input("Write album URL (supporting Bugs/Naver Music/Melon): ")

    new_input = check_input(input_val)

    if new_input == "":
        print "ERROR: Invalid input"
    else:
        bugs_pattern = re.compile("bugs[.]co[.]kr")
        naver_music_pattern = re.compile("music[.]naver[.]com")
        melon_pattern = re.compile("melon[.]com")
        allmusic_pattern = re.compile("allmusic[.]com")

        # if Bugs URL, run get_bugs_data()
        m = bugs_pattern.search(new_input)

        if m:
            print get_bugs_data(new_input)

        # if Naver Music URL, run get_naver_music_data()
        m = naver_music_pattern.search(new_input)

        if m:
            print get_naver_music_data(new_input)

        # if Melon URL, run get_melon_data()
        m = melon_pattern.search(new_input)

        if m:
            print get_melon_data(new_input)

        # if AllMusic URL, run get_allmusic_data()
        m = allmusic_pattern.search(new_input)

        if m:
            print get_allmusic_data(new_input)
