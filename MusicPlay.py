from pygame import mixer


class MusicPlay:
    def __init__(self, music):
        self.music = music
        self.isPlaying = True
        mixer.music.set_volume(0.618)
        mixer.music.play(-1)

    def pause(self, pos):
        if pos[0] > (41 * 25 + 8) and pos[0] < (41 * 25 + 94) and pos[1] > (27 * 25 + 4) and pos[1] < (27 * 25 + 68):
            mixer.music.pause() if self.isPlaying is True else mixer.music.unpause()
            self.isPlaying = not self.isPlaying
            return True
        return False
