from subprocess import Popen

from multi_miner.miners.abstract_miner import AbstractMiner
from multi_miner.misc.benchmark import Benchmark


class CCMiner(AbstractMiner):
    def __init__(self, path_to_exec, algo, url, port, wallet):
        self.path_to_exec = path_to_exec
        self.algo = algo
        self.url = url
        self.port = port
        self.wallet = wallet
        self.password = password
        self.miner_proc = None

    def return_when_miner_is_using_gpu(self):
        assert self.miner_proc and self.miner_proc.poll() == None, "Process is not running"

        cmd = "nvidia-smi pmon | grep %i" % self.miner_proc.pid
        checker = Popen(cmd.split(" "))

        for line in checker.stdout:
            if line != "":
                break

        checker.kill()

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
        kwarg_str = ""
        for k,v in kwargs.items():
            kwarg_str += "%s %s " % (k, v)

        run_args = {
            "exec": path_to_exec,
            "algo": algo,
            "url": url,
            "port": port,
            "wallet": wallet,
            "pass": password,
            "kwargs": kwarg_str,
        }

        return "%(exec)s -a %(algo)s --quiet -i 22 %(kwargs)s-o %(url)s:%(port)i -u %(wallet)s -p %(pass)s" % run_args

    def start_and_return(self):
        cmd = self._get_run_cmd(
            self.path_to_exec,
            self.algo,
            self.url,
            self.port,
            self.wallet,
            self.password
        )
        self.miner_proc = Popen(cmd.split())

    def stop_mining_and_return_when_stopped(self):
        self.miner_proc.terminate()
        self.miner_proc.wait(3)
        self.miner_proc.kill()
        self.miner_proc.wait()
        self.miner_proc = None

    def benchmark(self, num_samples=20):
        cmd = self._get_run_cmd(
            self.path_to_exec,
            self.algo,
            "",
            "",
            "",
            "",
            kwargs={"--benchmark", ""}
        ) + " | grep 'Total:'"
        bench_proc = Popen(cmd.split(" "))
        bench_results = []

        for line in bench_proc.stdout:
            split_line = line.split(" ")
            assert split_line[2] == "Total:"
            bench_results.append(
                Benchmark(
                    float(split_line[3]),
                    BenchmarkUnit.unit_from_str(split_line[4])
                )
            )

            if len(bench_results) == num_samples:
                break

        avg_bench = sum([b.get_rate() for b in bench_results]) / len(bench_results)
        return Benchmark(avg_bench, bench_results[0].get_unit())
