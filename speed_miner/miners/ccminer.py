import sys

from threading import Condition

from speed_miner.miners.abstract_miner import AbstractMiner
from speed_miner.misc.benchmark import Benchmark, Benchmarker, BenchmarkUnit
from speed_miner.misc.logging import LOG
from speed_miner.misc.miner_store import MinerStore
from speed_miner.misc.process_util import start_proc, term_proc
from speed_miner.misc.thread_util import CrashThread


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
        self.logger_thread = None
        self.share_cond = Condition()

    @classmethod
    def get_supported_algos(cls):
        if cls._cached_ccminer_algos:
           return cls._cached_ccminer_algos

        proc = start_proc("ccminer -h", pipe_stdout=True)
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

        term_proc(proc)

        cls._cached_ccminer_algos = supported_algos
        return supported_algos

    def return_when_miner_is_using_gpu(self):
        assert self.miner_proc and self.miner_proc.poll() == None, "Process is not running"

        checker = start_proc("nvidia-smi pmon", pipe_stdout=True)

        for line in checker.stdout:
            if str(self.miner_proc.pid).encode('utf-8') in line:
                break

        term_proc(checker)

    def return_when_share_is_done(self):
        self.share_cond.acquire()
        self.share_cond.wait()
        self.share_cond.release()

    def _get_intensity_override(self, algo):
        # Hack to set intensity for a specific algo.
        # nist5
        # skein? 27 may be better than 20
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
            # Let's keep the order of the kwargs always consistent.
            for k,v in iter(sorted(list(kwargs.items()))):
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
            cmd = "%s -o %s" % (cmd, url)

        if port:
            cmd = "%s:%s" % (cmd, port)

        if wallet:
            cmd = "%s -u %s" % (cmd, wallet)

        if password:
            cmd = "%s -p %s" % (cmd, password)

        return cmd.strip()

    def get_mining_cmd(self):
        return self._get_run_cmd(
            self.path_to_exec,
            self.algo,
            self.url,
            self.port,
            self.wallet,
            self.password
        )

    def start_and_return(self):
        cmd = self.get_mining_cmd()
        self.miner_proc = start_proc(cmd, pipe_stdout=True)
        self.logger_thread = self._start_and_return_logging_thread(self.miner_proc.stdout)

    @staticmethod
    def stdout_printer(stdout, name, share_cond, algo):
        for line in stdout:
            line = line.decode("UTF-8").strip()
            if "booooo" in line or "yes!" in line:
                share_cond.acquire()
                share_cond.notify_all()
                share_cond.release()
                speed = line.split(",")[-1].rpartition(" ")[0].strip()

                LOG.share(algo, "yes!" in line, speed)

            LOG.debug(line)

    def _start_and_return_logging_thread(self, proc_stdout):
        t = CrashThread(
            target=CCMiner.stdout_printer,
            args=(proc_stdout, str(self), self.share_cond, self.algo),
            name="%s (%s)" % (str(self), "stdout"),
        )
        t.start()
        return t

    def stop_mining_and_return_when_stopped(self):
        LOG.debug("Terminating ccminer (%s)...", self.algo)
        term_proc(self.miner_proc)

        LOG.debug("Terminating logging thread for ccminer (%s)...", self.algo)
        self.logger_thread.join()
        self.miner_proc = None
        self.logger_thread = None

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
        LOG.debug("Benchmarking \033[92m%s\033[0m...", self.algo)
        cache_key = "BENCH%s" % (cmd)
        cached_benchmark = MinerStore.get(cache_key)
        if cached_benchmark:
            b = Benchmark(float(cached_benchmark["rate"]), BenchmarkUnit[cached_benchmark["unit"]])
            LOG.debug("Benchmark found in cache: %s!", b)
            return b

        LOG.info("Benchmark not found for \033[92m%s\033[0m. Benchmarking...", self.algo)

        bench_proc = start_proc(cmd, pipe_stdout=True)
        bm = Benchmarker()

        for line in bench_proc.stdout:
            line = line.strip().decode("UTF-8")

            if "Total:" in line:
                split_line = line.split(" ")
                bm.add_rate(
                    float(split_line[3]), BenchmarkUnit.unit_from_str(split_line[4]))


                final_bench = bm.get_benchmark()
                if final_bench:
                    break

        term_proc(bench_proc)

        MinerStore.set(cache_key, {"unit": final_bench.get_unit().name, "rate": final_bench.get_rate()})
        LOG.info("Benchmark found: %s!", final_bench)

        return final_bench

    def wait(self, timeout=None):
        self.miner_proc.wait(timeout=timeout)

    def is_mining(self):
        return self.miner_proc.poll() is None

    def __str__(self):
        return "CCMiner - %s" % self.algo

    def __eq__(self, other):
        return self.get_mining_cmd() == (other and other.get_mining_cmd())
