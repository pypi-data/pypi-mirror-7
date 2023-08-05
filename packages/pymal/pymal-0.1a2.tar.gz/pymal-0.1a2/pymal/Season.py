__authors__ = ""
__copyright__ = "(c) 2014, pymal"
__license__ = "BSD License"
__contact__ = "Name Of Current Guardian of this file <email@address>"

import hashlib

from pymal.decorators import load, SingletonFactory
from pymal.Anime import Anime

__all__ = ['Season']


class Season(object, metaclass=SingletonFactory):
    """
    Lazy load of season data.
    
    Attributes:
        animes - a set of animes.
        year - the season year.
        season_name - The season name.
          Can be 'Winter', 'Spring', 'Summer' or 'Fall'.
    """
    __all__ = ['animes', 'reload']

    def __init__(self, season_name: str, year: int or str, animes_ids: set):
        """
        """
        self.season_name = season_name
        self.year = int(year)
        self.__animes_ids = animes_ids
        self._is_loaded = False
        self.__animes = set()

    @property
    @load
    def animes(self):
        return self.__animes

    def reload(self):
        self.__animes = set(map(Anime, self.__animes_ids))
        self._is_loaded = True
        assert len(self.__animes) == len(self.__animes_ids)

    def __iter__(self):
        class SeasonIterator(object):

            def __init__(self, values):
                self. values = list(values)
                self.location = 0

            def __iter__(self):
                self.location = 0
                return self

            def __next__(self):
                if self.location >= len(self.values):
                    raise StopIteration
                value = self.values[self.location]
                self.location += 1
                return value
        return SeasonIterator(self.animes)

    def __len__(self):
        return len(self.animes)

    def __hash__(self):
        hash_md5 = hashlib.md5()
        hash_md5.update(str(self.year).encode())
        hash_md5.update(self.season_name.encode())
        return int(hash_md5.hexdigest(), 16)

    def __repr__(self):
        return "<{0:s} {1:s} {2:d}>".format(self.__class__.__name__,
                                            self.season_name, self.year)
