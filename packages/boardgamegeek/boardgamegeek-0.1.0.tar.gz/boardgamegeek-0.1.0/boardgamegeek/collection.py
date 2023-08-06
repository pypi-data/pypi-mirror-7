from __future__ import unicode_literals
from copy import copy
from collections import Iterator

from .games import CollectionBoardGame
from .utils import DictObject


class Collection(DictObject):

    def __init__(self, data):
        kw = copy(data)
        if "items" not in kw:
            kw["items"] = []
        self.__game_ids = set()
        super(Collection, self).__init__(kw)

    def _format(self, log):
        log.info("owner    : {}".format(self.owner))
        log.info("size     : {} items".format(len(self)))

        log.info("items")

        for i in self:
            i._format(log)
            log.info("---------------------")

    def _add_game(self, game):
        # Collections can have duplicate elements (different collection ids), so don't add the same thing multiple times
        if game["id"] not in self.__game_ids:
            self._data["items"].append(game)
            self.__game_ids.add(game["id"])

    def __str__(self):
        return "{}'s collection, {} items".format(self.owner, len(self))

    def __repr__(self):
        return "Collection: (owner: {}, items: {})".format(self.owner, len(self))

    def __len__(self):
        return len(self._data["items"])

    @property
    def owner(self):
        return self._data.get("owner")

    @property
    def items(self):
        # TODO: create this list when _add_game instead of doing it on each items() call.
        return [CollectionBoardGame(x) for x in self._data["items"]]

    def __iter__(self):
        for item in self._data["items"]:
            yield CollectionBoardGame(item)
