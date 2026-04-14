import pygame
import os
import glob


class MusicPlayer:
    def __init__(self, music_dir):
        pygame.mixer.init()
        self.tracks = self._load_tracks(music_dir)
        self.idx = 0
        self.playing = False
        self.pos_start = 0

    def _load_tracks(self, directory):
        exts = ("*.mp3", "*.wav", "*.ogg")
        files = []
        for ext in exts:
            files += glob.glob(os.path.join(directory, ext))
        files.sort()
        return files

    def _name(self, path):
        return os.path.splitext(os.path.basename(path))[0]

    def current_name(self):
        if not self.tracks:
            return "No tracks found"
        return self._name(self.tracks[self.idx])

    def track_count(self):
        return len(self.tracks)

    def current_idx(self):
        return self.idx

    def is_playing(self):
        return self.playing and pygame.mixer.music.get_busy()

    def play(self):
        if not self.tracks:
            return
        pygame.mixer.music.load(self.tracks[self.idx])
        pygame.mixer.music.play()
        self.pos_start = pygame.time.get_ticks()
        self.playing = True

    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False

    def next(self):
        if not self.tracks:
            return
        self.stop()
        self.idx = (self.idx + 1) % len(self.tracks)
        self.play()

    def prev(self):
        if not self.tracks:
            return
        self.stop()
        self.idx = (self.idx - 1) % len(self.tracks)
        self.play()

    def elapsed_str(self):
        if not self.playing:
            return "0:00"
        secs = (pygame.time.get_ticks() - self.pos_start) // 1000
        return f"{secs // 60}:{secs % 60:02d}"
