from speed_miner.miners.ccminer import CCMiner


def get_supported_algos():
    return CCMiner.get_supported_algos()


def get_miner_for_algo(algo, url, port, wallet, password):
    assert algo in get_supported_algos(), "%s is not a supported algo" % algo

    algo_to_custom_ccminer = {
        "x17": "/usr/local/bin/alexis-ccminer",
        "blakecoin": "/usr/local/bin/alexis-ccminer",
        "lbry": "/usr/local/bin/alexis-ccminer",
        "skein": "/usr/local/bin/alexis-ccminer",
    }
    default_ccminer = "/usr/local/bin/tpruvot-ccminer"
    path_to_exec = algo_to_custom_ccminer.get(algo) or default_ccminer

    return CCMiner(path_to_exec, algo, url, port, wallet, password)
