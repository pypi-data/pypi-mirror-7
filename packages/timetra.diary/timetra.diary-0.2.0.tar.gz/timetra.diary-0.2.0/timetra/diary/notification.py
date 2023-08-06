# -*- coding: utf-8 -*-
#
#    Timetra is a time tracking application and library.
#    Copyright © 2010-2014  Andrey Mikhaylenko
#
#    This file is part of Timetra.
#
#    Timetra is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Timetra is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with Timer.  If not, see <http://gnu.org/licenses/>.
#
import os
import subprocess
from warnings import warn

# Audible notifications
#try:
#    sys.path.insert(0, '/home/andy/src')
##    import beeper   # custom script, see http://paste.pocoo.org/show/316/
##    import beeper_alsa
#    subprocess.Popen(['beep', '-l', '0'])
#except OSError:
#    warn('Simple audible alerts are disabled')
#    beep_enabled = False
#else:
#    beep_enabled = True


__all__ = ['beep', 'say', 'show']


def beep(*pairs):
    """Emits beeps using the "beep" program."""
    beeps = []
    for frequency, duration in pairs:
        beeps.extend(['-f', str(frequency), '-l', str(duration), '-n'])
    beeps.pop()   # remove the last "-n" separator to prevent extra beep
    subprocess.Popen(['beep'] + beeps) #, '-f', str(frequency), '-l', str(duration)])
    #'beep -f 100 -n -f 150 -n -f 50 -n -f 300 -n -f 200 -n -f 400'.split())
#    try:
#        beeper.beep(frequency, duration)
#    except IOError:
#        beeper_alsa.beep(frequency, duration)


def say(text):
    """Uses Festival TTS to actually say the message."""
    # see http://ubuntuforums.org/showthread.php?t=751169
    sound_wrapper = 'padsp'  # or 'aoss' or 'esddsp' or none
    command = 'echo \'(SayText "{text}")\' | {sound_wrapper} festival &'
    text = text.replace('"','').replace("'",'')
    os.system(command.format(sound_wrapper=sound_wrapper, text=text))


def show(text, critical=False):
    # Visible notifications
    try:
        import notify2 as notify_lib
    except ImportError:
        try:
            import pynotify as notify_lib
        except ImportError:
            notify_lib = None
    if notify_lib:
        notify_lib.init('timetra')
    else:
        warn('Visible alerts are disabled')

    if not notify_lib:
        return False

    note = notify_lib.Notification(summary='Time Tracker', message=text)
    if critical:
        note.set_urgency(notify_lib.URGENCY_CRITICAL)
    note.show()
    return True
