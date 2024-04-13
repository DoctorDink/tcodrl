from __future__ import annotations

from typing import List

import soundfile  # pip install soundfile
import tcod.sdl.audio

import game.color
import game.entity
import game.exceptions
import game.game_map
import game.input_handlers
import game.message_log
import game.render_functions


class Audio:
    def __init__(self):
        self.mixer = tcod.sdl.audio.BasicMixer(tcod.sdl.audio.open())
        self.sfxChannel = None
        self.musicChannel = None
        self.sample_rate = None
        self.newSound = None
        self.newMusic = None
        self.music = []
        self.sound = []

    def load_sounds(self) -> None:
        self.newSound, self.sample_rate = soundfile.read("data/death.wav")
        self.newSound = self.mixer.device.convert(self.newSound, self.sample_rate)
        self.sound.append(self.newSound)

        self.music, self.sample_rate = soundfile.read("data/scratch.wav")
        self.music = self.mixer.device.convert(self.music, self.sample_rate)
        self.sound.append(self.music)

        self.newSound, self.sample_rate = soundfile.read("data/orc.wav")
        self.newSound = self.mixer.device.convert(self.newSound, self.sample_rate)
        self.sound.append(self.newSound)

        self.newSound, self.sample_rate = soundfile.read("data/sword_slash.wav")
        self.newSound = self.mixer.device.convert(self.newSound, self.sample_rate)
        self.sound.append(self.newSound)


    def play_sfx(self, soundName: str) -> None:
        if(soundName == "orc_die"):
            self.sfxChannel = self.mixer.play(self.sound[2])
        elif(soundName == "sword_slash"):
            self.sfxChannel = self.mixer.play(self.sound[3])
        else:
            self.sfxChannel = self.mixer.play(self.sound[0])

    def play_music(self, musicName: str) -> None:
        self.musicChannel = self.mixer.play(self.sound[1], volume=0.2, loops=-1)
        pass