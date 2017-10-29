import youtube_dl
import os

class InvalidURL(Exception):
    pass

class SongExists(Exception):
    pass

class InBlacklist(Exception):
    pass

def download(url):
    blacklistfile = open("config/blacklist.txt", "r")
    blacklist = blacklistfile.readlines()
    for links in blacklist:
        blacklist.remove(links)
        blacklist.append(links.strip())
    blacklistfile.close()
    try:
        options = {
            'format': 'bestaudio/best',
            'quiet': True,
            'extractaudio': True,  # only keep the audio
            'audioformat': "wav",  # convert to wav
            'outtmpl': '%(id)s.wav',  # name the file the ID of the video
            'noplaylist': True,  # only download single song, not playlist
        }
        with youtube_dl.YoutubeDL(options) as ydl:
            r = ydl.extract_info(url ,download=False)
            if os.path.isfile(str(r["id"])+".wav"):
                raise SongExists('This song has already been requested.')
            if url in blacklist:
                raise InBlacklist("This song has been blacklisted.")
            print("Downloading", r["title"])
            print(str(url))
            ydl.download([url])
            print("Downloaded", r["title"])
            print("ID:",r["id"])
            return r["title"], r["id"]

    except youtube_dl.utils.DownloadError:
        options = {
            'format': 'bestaudio/best',
            'quiet': True,
            'extractaudio': True,  # only keep the audio
            'audioformat': "wav",  # convert to wav
            'outtmpl': '%(id)s.wav',  # name the file the ID of the video
            'noplaylist': True,  # only download single song, not playlist
        }
        with youtube_dl.YoutubeDL(options) as ydl:
            r = ydl.extract_info("ytsearch:" + url ,download=False)
            if os.path.isfile(str(r["entries"][0]["id"])+".wav"):
                raise SongExists('This song has already been requested.')
            if r["entries"][0]["webpage_url"] in blacklist:
                raise InBlacklist("This song has been blacklisted.")
            print("Downloading", r["entries"][0]["title"])
            ydl.download([r["entries"][0]["webpage_url"]])
            print("Downloaded", r["entries"][0]["title"])
            print("ID:", r["entries"][0]["id"])
            return r["entries"][0]["title"], r["entries"][0]["id"]


def get_url(id):
    options = {
        'format': 'bestaudio/best',
        'quiet': True,
        'extractaudio': True,  # only keep the audio
        'audioformat': "wav",  # convert to wav
        'outtmpl': '%(id)s.wav',  # name the file the ID of the video
        'noplaylist': True,  # only download single song, not playlist
    }
    with youtube_dl.YoutubeDL(options) as ydl:
        r = ydl.extract_info("ytsearch:" + id, download=False)
        return r["entries"][0]["webpage_url"]

if __name__ == "__main__":
    download("MagnusTheMagnus area")
