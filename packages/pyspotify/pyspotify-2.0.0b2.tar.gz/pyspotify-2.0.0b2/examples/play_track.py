#!/usr/bin/env python

"""
This is an example of playing music from Spotify using pyspotify.

The example use the :class:`spotify.AlsaSink`, and will thus only work on
systems with an ALSA sound subsystem, which means most Linux systems.

You can either run this file directly without arguments to play a default
track::

    python play_track.py

Or, give the script a Spotify track URI to play::

    python play_track.py spotify:track:3iFjScPoAC21CT5cbAFZ7b
"""

from __future__ import unicode_literals

import sys
import threading

import spotify

if sys.argv[1:]:
    track_uri = sys.argv[1]
else:
    track_uri = 'spotify:track:6xZtSE6xaBxmRozKA0F6TA'

# Assuming a spotify_appkey.key in the current dir
session = spotify.Session()

# Process events in the background
loop = spotify.EventLoop(session)
loop.start()

# Connect an audio sink
audio = spotify.AlsaSink(session)

# Events for coordination
logged_in = threading.Event()
end_of_track = threading.Event()


def on_logged_in(session, error_type):
    assert error_type == spotify.ErrorType.OK, 'Login failed'
    logged_in.set()


def on_end_of_track(self):
    end_of_track.set()


# Register event listeners
session.on(spotify.SessionEvent.LOGGED_IN, on_logged_in)
session.on(spotify.SessionEvent.END_OF_TRACK, on_end_of_track)

# Assuming a previous login with remember_me=True and a proper logout
session.relogin()

logged_in.wait()

# XXX This isn't very elegant
while session.connection_state != spotify.ConnectionState.LOGGED_IN:
    session.process_events()

# Play a track
track = session.get_track(track_uri).load()
session.player.load(track)
session.player.play()

# Wait for playback to complete or Ctrl+C
try:
    while not end_of_track.wait(0.1):
        pass
except KeyboardInterrupt:
    pass
