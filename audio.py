from pygame import mixer_music as mm
from settings import *
from support import load_audio
import json, os

class Audio:
    def __init__(self, main):
        self.main = main
        self.fx_volume = 1
        self.music_volume = 0.5
        self.volume_step = 0.1
        self.music_volumes = {
            "level":0.5,
            "menu": 0.8,
        }
        self.cur_music = None
        self.fx = {
            "impact": load_audio("impact", 0.5),
            "explosion": load_audio("explosion", 0.128),
            "coin-collect": load_audio("coin-collect", 0.6),
            "transition": load_audio("transition", 1),
            "bubbles-short": load_audio("bubbles-short",0.7),
            "wave": load_audio("wave",1),
            "ambience": load_audio("ambience",1),
            "powerup": load_audio("powerup", 1, "wav"),
            "coin-bonus": load_audio("coin-bonus", 0.6, "wav"),
        }
        self.load_data()

    def load_data(self):
        if not os.path.exists("data/audio.save"): self.save_data()
        with open("data/audio.save","rb") as file:
            encoded_data = file.read()
            string_data = self.main.fernet.decrypt(encoded_data)
            data = json.loads(string_data)
            self.change_music_volume(data["music-volume"])
            self.change_fx_volume(data["sound-volume"])

    def save_data(self):
        with open("data/audio.save","wb") as file:
            data = {
                "music-volume":self.music_volume,
                "sound-volume":self.fx_volume,
            }
            string_data = json.dumps(data)
            encoded_data = self.main.fernet.encrypt(string_data.encode())
            file.write(encoded_data)

    def update_music_volume(self, amount):
        self.change_music_volume(self.music_volume+amount)

    def step_music_volume(self, sign):
        self.update_music_volume(self.volume_step*sign)

    def change_music_volume(self, volume):
        self.music_volume = volume
        self.music_volume = pygame.math.clamp(self.music_volume,0.0,1.0)
        self.refresh_volumes()

    def update_fx_volume(self, amount):
        self.change_fx_volume(self.fx_volume+amount)

    def step_fx_volume(self, sign):
        self.update_fx_volume(self.volume_step*sign)

    def change_fx_volume(self, volume):
        self.fx_volume = volume
        self.fx_volume = pygame.math.clamp(self.fx_volume,0.0,1.0)
        self.refresh_volumes()

    def refresh_volumes(self):
        if self.cur_music: mm.set_volume(self.music_volume * self.music_volumes[self.cur_music])
        for fx in self.fx.values(): fx["sound"].set_volume(self.fx_volume*fx["volume"])

    def play_music(self, name, ext="mp3", fade_ms = 100):
        mm.stop(); mm.unload()
        mm.load(f"assets/audio/music/{name}.{ext}")
        self.cur_music = name
        self.refresh_volumes()
        mm.play(-1, fade_ms=fade_ms)
    
    def stop_music(self): mm.stop()
    def pause_music(self): mm.pause()
    def resume_music(self): mm.unpause()
         
    def play_fx(self, name, loops=0): self.fx[name]["sound"].play(loops)
    def stop_fx(self, name): self.fx[name]["sound"].stop()
    def play_fx_single(self, name, loops=0):
        self.fx[name]["sound"].stop()
        self.fx[name]["sound"].play(loops)
