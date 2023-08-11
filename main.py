import atexit
import json
from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger
from pytube import Playlist, YouTube
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

src_file: Path = Path("src_file.json")
src_data: dict = {}

if src_file.exists():
    with src_file.open('r') as file:
        src_data = json.load(file)


@dataclass
class PlaylistContainer(object):
    playlist_url: str
    playlist_items: list[str] = field(default_factory=lambda: [])


data: dict[PlaylistContainer] = {
    playlist_url: PlaylistContainer(playlist_url, playlist_items) for playlist_url, playlist_items in src_data.items()
}

logger.debug(f"Loaded: {data}")


def save() -> None:
    with src_file.open('w') as save_file:
        json.dump(data, save_file)

    logger.debug("Saved.")


atexit.register(save)


class YouTubeWatcher(object):
    def __init__(self, youtube_url: str):
        self._youtube_url: str = youtube_url
        self._playlist: Playlist = self._load_playlist()

    def _load_playlist(self):
        return Playlist(self._youtube_url)

    def get_playlist_content_urls(self) -> list[str]:
        return self._playlist.video_urls

    def get_videos(self) -> list[YouTube]:
        yt_items: list[YouTube] = []
        for url in self.get_playlist_content_urls():
            try:
                yt_object: YouTube = YouTube(url)
            except Exception as error:
                logger.error(error)
            else:
                logger.debug(f"Loaded {url}")
                yt_items.append(yt_object)
        return yt_items


class SpotifyManager(object):
    def __init__(self, client_id: str, client_secret: str):
        self._client_id: str = client_id
        self._client_secret: str = client_secret

        os.environ["SPOTIPY_CLIENT_ID"] = self._client_id
        os.environ["SPOTIPY_CLIENT_SECRET"] = self._client_secret
        os.environ["SPOTIPY_REDIRECT_URI"] = "http://127.0.0.1:9090/callback"

        self._scope: str = "playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public"
        self._spotify: spotipy.Spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=self._scope))

    def find_similar(self, items: list[YouTube]) -> None:
        query: str
        counter = 0
        for item in items:
            query = f"track:{item.title} artist:{item.author}"
            logger.debug(f"Query: {query}")
            try:
                search_results: dict = self._spotify.search(q=query, type="track", limit=1)
                print(search_results)
                i = search_results.get("tracks", {}).get("items", [])
                print(i)
                if len(i) != 0:
                    counter += 1
            except Exception as error:
                logger.error(error)
        logger.info(f"Found a total of {counter} perfect matches.")


sport_ytw: YouTubeWatcher = YouTubeWatcher("https://youtube.com/playlist?list=PLo9MEokKqo24pzLjVkZtThzDyhV3UBAu7")

# 0FDtEa7zPHSMDYLjq9IAse

sp_manager: SpotifyManager = SpotifyManager("aa38b256fe354682ae3c2eb8a56b8334", "625778d759de477e824506fb4f7f578c")
sp_manager.find_similar(sport_ytw.get_videos())
