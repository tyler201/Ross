import vlc
from vlc import State
import os
import time

def playtrack(fileid, songname):
    filename = fileid + ".wav"
    print('Now playing: ' + songname)
    music = vlc.MediaPlayer(filename)
    music.play()
    time.sleep(1)
    while music.get_state() == State.Playing or music.get_state() == State.Opening:
        from __main__ import volume
        music.audio_set_volume(int(volume))
        from __main__ import skipped
        if skipped:
            break
        pass
    print("Finished.")
    music.stop()
    os.remove(filename)