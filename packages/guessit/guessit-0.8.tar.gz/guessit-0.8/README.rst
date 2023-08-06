GuessIt
=======

.. image:: http://img.shields.io/pypi/v/guessit.svg
    :target: https://pypi.python.org/pypi/guessit
    :alt: Latest Version

.. image:: http://img.shields.io/badge/license-LGPLv3-blue.svg
    :target: https://pypi.python.org/pypi/guessit
    :alt: License

.. image:: http://img.shields.io/travis/wackou/guessit.svg
    :target: http://travis-ci.org/wackou/guessit
    :alt: Build Status

.. image:: http://img.shields.io/coveralls/wackou/guessit.svg
    :target: https://coveralls.io/r/wackou/guessit?branch=master
    :alt: Coveralls


GuessIt is a python library that tries to extract as much information as
possible from a video file.

It has a very powerful filename matcher that allows to guess a lot of
metadata from a video using only its filename. This matcher works with
both movies and tv shows episodes.

For example, GuessIt can do the following::

    $ guessit "Treme.1x03.Right.Place,.Wrong.Time.HDTV.XviD-NoTV.avi"
    For: Treme.1x03.Right.Place,.Wrong.Time.HDTV.XviD-NoTV.avi
    GuessIt found: {
        [1.00] "mimetype": "video/x-msvideo",
        [0.80] "episodeNumber": 3,
        [0.80] "videoCodec": "XviD",
        [1.00] "container": "avi",
        [1.00] "format": "HDTV",
        [0.70] "series": "Treme",
        [0.50] "title": "Right Place, Wrong Time",
        [0.80] "releaseGroup": "NoTV",
        [0.80] "season": 1,
        [1.00] "type": "episode"
    }



Features
--------

At the moment, the filename matcher is able to recognize the following
property types::

    [ title,                             # for movies and episodes
      series, season,                    # for episodes only
      episodeNumber, episodeDetails,     # for episodes only
      date, year,                        # 'date' instance of datetime.date
      language, subtitleLanguage,        # instances of babelfish.Language
      country,                           # instances of babelfish.Country
      fileSize, duration,                # when detecting video file metadata
      container, format,
      videoCodec, audioCodec,
      videoProfile, audioProfile,
      audioChannels, screenSize,
      releaseGroup, website,
      cdNumber, cdNumberTotal,
      filmNumber, filmSeries,
      bonusNumber, edition,
      idNumber,                          # tries to identify a hash or a serial number
      other
      ]


GuessIt also allows you to compute a whole lof of hashes from a file,
namely all the ones you can find in the hashlib python module (md5,
sha1, ...), but also the Media Player Classic hash that is used (amongst
others) by OpenSubtitles and SMPlayer, as well as the ed2k hash.

If you have the 'guess-language' python package installed, GuessIt can also
analyze a subtitle file's contents and detect which language it is written in.

If you have the 'enzyme' python package installed, GuessIt can also detect the
properties from the actual video file metadata.


Install
-------

Installing GuessIt is simple with `pip <http://www.pip-installer.org/>`_::

    $ pip install guessit

or, with `easy_install <http://pypi.python.org/pypi/setuptools>`_::

    $ easy_install guessit

But, you really `shouldn't do that <http://www.pip-installer.org/en/latest/other-tools.html#pip-compared-to-easy-install>`_.



Support
-------

The project website for GuessIt is hosted at `ReadTheDocs <http://guessit.readthedocs.org/>`_.
There you will also find the User guide and Developer documentation.

This project is hosted on GitHub: `<https://github.com/wackou/guessit>`_

Please report issues and/or feature requests via the `bug tracker <https://github.com/wackou/guessit/issues>`_.

You can also report issues using the command-line tool::

    $ guessit --bug "filename.that.fails.avi"


Contribute
----------

GuessIt is under active development, and contributions are more than welcome!

#. Check for open issues or open a fresh issue to start a discussion around a feature idea or a bug.
   There is a Contributor Friendly tag for issues that should be ideal for people who are not very
   familiar with the codebase yet.
#. Fork `the repository`_ on Github to start making your changes to the **master**
   branch (or branch off of it).
#. Write a test which shows that the bug was fixed or that the feature works as expected.
#. Send a pull request and bug the maintainer until it gets merged and published. :)

.. _the repository: https://github.com/wackou/guessit

License
-------

GuessIt is licensed under the `LGPLv3 license <http://www.gnu.org/licenses/lgpl.html>`_.
