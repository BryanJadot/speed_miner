import os
import json


class MinerStore(object):
    PATH_TO_STORE = "/usr/local/etc/miner_store.json"

    @staticmethod
    def set(key, value):
        assert isinstance(key, str)

        store = MinerStore._load()
        store[key] = value

        MinerStore._save(store)

    @staticmethod
    def get(key):
        assert isinstance(key, str)
        store = MinerStore._load()

        return store.get(key)

    @staticmethod
    def _create_if_not_exists():
        if not os.path.isfile(MinerStore.PATH_TO_STORE):
            with open(MinerStore.PATH_TO_STORE, "w+") as f:
                f.write("{}")

    @staticmethod
    def _save(new_dict):
        MinerStore._create_if_not_exists()
        with open(MinerStore.PATH_TO_STORE, "w") as f:
            f.write(json.dumps(new_dict))

    @staticmethod
    def _load():
        MinerStore._create_if_not_exists()
        with open(MinerStore.PATH_TO_STORE, "r") as f:
            return json.loads(f.read())
