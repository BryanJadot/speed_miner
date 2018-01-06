from subprocess import Popen

from speed_miner.misc.logging import LOG

procs = []

def start_proc(cmd, **kwargs):
    p = Popen(cmd.split(" "), **kwargs)
    procs.append(p)
    LOG.debug("Started \"%s\" with pid of %i", cmd, p.pid)
    return p

def term_proc(proc, term_wait_time=3):
    if proc.poll() is None:
        LOG.debug("Terminating process %i and waiting up to %i seconds for it to end...", proc.pid, term_wait_time)
        proc.terminate()
        proc.wait(term_wait_time)

    if proc.poll() is None:
        LOG.warning("Process %i didn't terminate. Killing process and waiting until process exits...", proc.pid)
        proc.kill()
        proc.wait()

    LOG.debug("Process %i terminated with %i", proc.pid, proc.poll())

def term_all_procs():
    for p in procs:
        if p.poll() is not None:
            term_proc(p, term_wait_time=1)
