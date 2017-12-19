from subprocess import PIPE, Popen

from multi_miner.miners.abstract_miner import AbstractMiner
from multi_miner.misc.benchmark import Benchmark, Benchmarker, BenchmarkUnit
from multi_miner.misc.logger import pr
from multi_miner.misc.miner_store import MinerStore


class CCMiner(AbstractMiner):
    _cached_ccminer_algos = None

    def __init__(self, path_to_exec, algo, url, port, wallet, password):
        self.path_to_exec = path_to_exec
        self.algo = algo
        self.url = url
        self.port = port
        self.wallet = wallet
        self.password = password
        self.miner_proc = None

    @classmethod
    def get_supported_algos(cls):
        if cls._cached_ccminer_algos:
           return cls._cached_ccminer_algos

        proc = Popen("ccminer -h".split(" "), stdout=PIPE)
        reading_algos = False
        supported_algos = set()

        for line in proc.stdout:
            line = line.strip()

            if line.split(b" ")[0] == b"-d,":
                break

            if reading_algos:
                supported_algos.add(line.split(b" ")[0].decode("UTF-8"))

            if line.split(b" ")[0] == b"-a,":
                reading_algos = True

        cls._cached_ccminer_algos = supported_algos
        return supported_algos

    def return_when_miner_is_using_gpu(self):
        assert self.miner_proc and self.miner_proc.poll() == None, "Process is not running"

        cmd = "nvidia-smi pmon"
        checker = Popen(cmd.split(" "), stdout=PIPE)

        for line in checker.stdout:
            if str(self.miner_proc.pid).encode('utf-8') in line:
                break

        checker.kill()

    def _get_intensity_override(self, algo):
        # Hack to set intensity for a specific algo.
        # nist5
        return None

    def _get_run_cmd(
            self,
            path_to_exec,
            algo,
            url,
            port,
            wallet,
            password,
            kwargs=None
    ):
        assert path_to_exec and algo

        kwarg_str = ""
        if kwargs:
            for k,v in kwargs.items():
                kwarg_str += " %s" % k
                if v:
                    kwarg_str += " %s" %v

        run_args = {
            "exec": path_to_exec,
            "algo": algo,
            "kwargs": kwarg_str,
        }
        cmd = "%(exec)s -a %(algo)s --quiet%(kwargs)s" % run_args

        intensity = self._get_intensity_override(algo)

        if intensity:
            cmd = "%s -i %s" % (cmd, intensity)

        if url:
            cmd = "%s -o stratum+tcp://%s" % (cmd, url)

        if port:
            cmd = "%s:%s" % (cmd, port)

        if wallet:
            cmd = "%s -u %s" % (cmd, wallet)

        if password:
            cmd = "%s -p %s" % (cmd, password)

        return cmd.strip()

        #cmd = "%(exec)s -a %(algo)s --quiet -i 22 %(kwargs)s-o %(url)s:%(port)s -u %(wallet)s -p %(pass)s" % run_args

    def start_and_return(self):
        cmd = self._get_run_cmd(
            self.path_to_exec,
            self.algo,
            self.url,
            self.port,
            self.wallet,
            self.password
        )
        pr("Executing \"%s\"\n" % cmd, prefix="CCMiner")
        self.miner_proc = Popen(cmd.split(" "), stdout=PIPE)

    def stop_mining_and_return_when_stopped(self):
        self.miner_proc.terminate()
        self.miner_proc.wait(3)
        self.miner_proc.kill()
        self.miner_proc.wait()
        self.miner_proc = None

    def benchmark(self):
        cmd = self._get_run_cmd(
            self.path_to_exec,
            self.algo,
            "",
            "",
            "",
            "",
            kwargs={"--benchmark": "", "--no-color": ""}
        )
        #pr("Benchmarking \033[92m%s\033[0m...\n" % self.algo, prefix="Benchmarker")
        cache_key = "BENCH%s" % (cmd)
        cached_benchmark = MinerStore.get(cache_key)
        if cached_benchmark:
            b = Benchmark(float(cached_benchmark["rate"]), BenchmarkUnit[cached_benchmark["unit"]])
            #pr("Benchmark found in cache: %s!\n\n" % b, prefix="Benchmarker")
            return b

        pr("Benchmark not found for \033[92m%s\033[0m. Benchmarking...\n" % self.algo, prefix="Benchmarker")

        bench_proc = Popen(cmd.split(" "), stdout=PIPE)
        bench_results = []
        bm = Benchmarker()

        for line in bench_proc.stdout:
            line = line.strip()
            split_line = line.split(b" ")

            if len(split_line) > 4 and split_line[2] == b"Total:":
                bm.add_rate(
                    float(split_line[3]), BenchmarkUnit.unit_from_str(split_line[4].decode("UTF-8")))


                final_bench = bm.get_benchmark()
                if final_bench:
                    break

        bench_proc.kill()
        bench_proc.wait()

        MinerStore.set(cache_key, {"unit": final_bench.get_unit().name, "rate": final_bench.get_rate()})
        pr("Benchmark found: %s!\n" % final_bench, prefix="Benchmarker")

        return final_bench

    def wait(self, timeout=None):
        self.miner_proc.wait(timeout=timeout)

    def __str__(self):
        return "CCMiner (%s)" % self.algo
