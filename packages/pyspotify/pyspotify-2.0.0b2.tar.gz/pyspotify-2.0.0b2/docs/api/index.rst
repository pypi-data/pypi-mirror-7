*************
API reference
*************

The pyspotify API follows the `libspotify
<https://developer.spotify.com/technologies/libspotify/>`__ API closely. Thus,
you can refer to the similarly named functions in the libspotify docs for
further details.

.. module:: spotify

.. attribute:: __version__

    pyspotify's version number in the :pep:`386` format.

    ::

        >>> import spotify
        >>> spotify.__version__
        u'2.0.0'

.. autofunction:: get_libspotify_api_version

.. autofunction:: get_libspotify_build_id


**Sections**

.. toctree::
    :maxdepth: 1

    error
    config
    session
    eventloop
    connection
    audio
    link
    track
    album
    artist
    image
    search
    social
    playlist
    user
    toplist
    inbox
    player
    sink
    internal
