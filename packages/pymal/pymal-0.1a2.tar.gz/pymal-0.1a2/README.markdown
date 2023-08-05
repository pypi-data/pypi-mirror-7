Table of contents
=================
[TOC]

pymal
==========
Provides programmatic access to MyAnimeList data with python.
Objects in pymal are lazy-loading: they won't go out and fetch MAL info until you first-request it.

Dependencies
===========
* python 3.4.*
    - Wasn't tried on oth pythons, but i believe it will work on all python 3.
    - Because of python 3 new and python 2.7.*.
* BeautifulSoup4
    - html5lib for BeautifulSoup4 to read html pages better.
* requests
    - httpcache for requests to have cache (might be removed because no cache can be created with mal right now).

Installation
============
After cloning the repository, navigate to the directory and run `python setup.py install`.

Testing
=======
To run the tests that come with MAL Client:
1. Install nose2 (A really good package for running tests - `pip install nose2`). For more data look on [nose2](https://github.com/nose-devs/nose2 "nose2").
  If you decided to install nose 2, i recommend on the plugin nose2-cov for code statistics - `pip install nose2-cov`.
2. Navigate to the python-mal directory
3. Create a text file named account_settings.json and put your MAL username and password in dict under 'password' and 'username'.
4. Run `nose2` or `python -m unittest` with a lot of parameters that i don't know.

Make sure you don't spam the tests too quickly! You're likely to be IP-banned if you do this too much in too short a span of time.

    ----------- coverage: platform win32, python 3.4.1-final-0 -----------
    Name                     Stmts   Miss Branch BrMiss     Cover
    -------------------------------------------------------------
    pymal\Account               81     18     10      7    72.53%
    pymal\AccountAnimes        123     10     24      8    87.76%
    pymal\AccountMangas        123     10     24      8    87.76%
    pymal\Anime                232      8     49     14    92.17%
    pymal\Manga                235     11     51     14    91.26%
    pymal\MyAnime              231     21     40     14    87.08%
    pymal\MyManga              233     26     44     17    84.48%
    pymal\Season                39     12      2      1    68.29%
    pymal\Seasons               57     22     10      4    61.19%
    pymal\global_functions      80     11     28      7    83.33%
    -------------------------------------------------------------
    TOTAL                     1434    149    282     94    85.84%

Usage
=====
Most objects data can be required by not authentication mal, but all list manipulations on MAL requires authentication.

Account
------
To connect MAL you need an Account object.

``` python
from pymal.Account import Account
account = Account('mal-username', 'mal-password')
```

Then all your mangas and animes will be like this:

``` python
animelist = account.animes
mangalist = account.mangas
```

Anime
-----
Right now, give him the anime id and it will generate the most of the things.

``` python
from pymal.Anime import Anime
anime = Anime(1887)  # Lucky star's anime id
```

For all data that can be used look in the python.
To add it its need an account object to related on.

``` python
my_anime = anime.add_anime(account)
assert type(my_anime) != type(anime)
assert issubclass(my_anime.__class__, anime.__class__)
```

MyAnime
-------
A subclass of Anime which has more attribute like the account's number of watched episodes and so on.

Manga
-----
Right now, give him the manga id and it will generate the most of the things.

``` python
from pymal.Manga import Manga
manga = Manga(587)  # Lucky star's manga id
```

All the objects under account are subclass of Anime and Manga.
To add it its need an account object to related on.

``` python
my_manga = manga.add_anime(account)
assert type(my_manga) != type(manga)
assert issubclass(my_manga.__class__, manga.__class__)
```

MyManga
-------
A subclass of Manga which has more attribute like the account's number of read chapters and so on.