Table of contents
=================
[TOC]

pymal
=====
If you read this that mean that you want to do something with the code (copy, read or add).
This README will try to explain how everything is organized and how it should look like.

Usage
=====
Never put tests in here!
That's why we have a folder for them :)

Globals files
-------------
 * `global_function.py` - Here you should find and place all the globals functions.
    Any function that most of other code will use and its not better any where. Some people will call it 'junk file'.
 * `consts.py` - Here you should find and place all the constants of the project.
    More constants out here means better sharing and finding even for the test!
 * `decorators.py` - Here you should find and place all the global decorators.
    I don't recommend to make a lot of them, only if necessary or looks better.

Object files
------------
 * Each object should be placed in his own file.
 * If some classes should look the same, try to make the same interface in functions' names and their arguments.
 * Inherited is good if you can pass code.
 * Remember that we are reading from anther server (myanimelist.net).
    Make everything as lazy as possible and use all the information from each data you receive.

Objects
-------
### Account
It should held all the data about the account.
Also it's the only one who has the password and authenticated connection. All other object should use him.

#### AccountAnimes
It should lazy load accounts' list of animes.
It can held future global data about accounts' animes.
It should't be used out side of context of account

In the package it only a package for list(MyAnime).

#### AccountMangas
It should lazy load accounts' list of mangas.
It can held future global data about accounts' mangas.
It should't be used out side of context of account.

In the package it only a package for list(MyManga).

### Anime
This object and `Manga` should have a very close interface (except for volumes-chapters vs episodes).
A very basic object to obtain generic data about an anime.

### Manga
This object and `Anime` should have a very close interface (except for volumes-chapters vs episodes).
A very basic object to obtain generic data about a manga.

### MyAnime
This object and `MyManga` should have a very close interface (except for volumes-chapters vs episodes).
A basic object to obtain account specific data about an anime.
Can manipulate the anime data in the account's list.

### MyManga
This object and `MyAnime` should have a very close interface (except for volumes-chapters vs episodes).
A basic object to obtain account specific data about a manga.
Can manipulate the manga data in the account's list.

### Seasons
This object is loaded from a different db.

#### Season
An inner object of Seasons. Don't use it.