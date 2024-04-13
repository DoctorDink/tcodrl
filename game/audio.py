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
        self.channel = None
        self.sample_rate = None
        self.currSound = None
        self.music = None
        self.sound = []

    def load_sounds(self) -> None:
        self.currSound, self.sample_rate = soundfile.read("data/death.wav")
        self.currSound = self.mixer.device.convert(self.currSound, self.sample_rate)
        self.sound.append(self.currSound)

        self.music, self.sample_rate = soundfile.read("data/scratch.wav")
        self.music = self.mixer.device.convert(self.music, self.sample_rate)
        self.sound.append(self.music)

        self.currSound, self.sample_rate = soundfile.read("data/orc.wav")
        self.currSound = self.mixer.device.convert(self.currSound, self.sample_rate)
        self.sound.append(self.currSound)

        self.currSound, self.sample_rate = soundfile.read("data/sword_slash.wav")
        self.currSound = self.mixer.device.convert(self.currSound, self.sample_rate)
        self.sound.append(self.currSound)


    def play_sfx(self, soundName: str) -> None:
        if(soundName == "orc_die"):
            self.channel = self.mixer.play(self.sound[2])
        elif(soundName == "sword_slash"):
            self.channel = self.mixer.play(self.sound[3])
        else:
            self.channel = self.mixer.play(self.sound[0])

    def play_music(self) -> None:
        self.channel = self.mixer.play(self.sound[1], volume=0.2, loops=-1)
        pass