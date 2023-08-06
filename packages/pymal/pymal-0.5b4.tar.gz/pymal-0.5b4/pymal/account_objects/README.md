[TOC]

Usage
=====
All accounts connected object are placed here.

Objects
-------

### AccountAnimes
It should lazy load accounts' list of animes.
It can held future global data about accounts' animes.
It shouldn't be used out side of context of account

In the package it only a package for list(MyAnime).

### AccountMangas
It should lazy load accounts' list of mangas.
It can held future global data about accounts' mangas.
It shouldn't be used out side of context of account.

In the package it only a package for list(MyManga).

### Accountfriends
It should lazy load accounts' list of friends.
It can held future global data about accounts' friends.
It shouldn't be used out side of context of account.

In the package it only a package for list(Account).

### MyAnime
This object and `MyManga` should have a very close interface (except for volumes-chapters vs episodes).
A basic object to obtain account specific data about an anime.
Can manipulate the anime data in the account's list.

### MyManga
This object and `MyAnime` should have a very close interface (except for volumes-chapters vs episodes).
A basic object to obtain account specific data about a manga.
Can manipulate the manga data in the account's list.
