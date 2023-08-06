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
Objects which connected to Account are placed under `account_object` folder.

You can find there:

 * AccountAnimes
 * AccountMangas
 * AccountFriends
 * MyAnime
 * MyManga

### Anime
This object and `Manga` should have a very close interface (except for volumes-chapters vs episodes).
A very basic object to obtain generic data about an anime.

### Manga
This object and `Anime` should have a very close interface (except for volumes-chapters vs episodes).
A very basic object to obtain generic data about a manga.

### Seasons
This object is loaded from a different db.
