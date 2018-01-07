from subprocess import PIPE, Popen

from speed_miner.misc.logging import LOG

procs = []


def start_proc(cmd, pipe_stdout=False):
    kwargs = {}
    if pipe_stdout:
        kwargs["stdout"] = PIPE

    p = Popen(cmd.split(" "), **kwargs)
    procs.append(p)
    LOG.debug("Started \"%s\" with pid of %i", cmd, p.pid)
    return p


def term_proc(proc, term_wait_time=3):
    if proc.poll() is None:
        LOG.debug(
            "Terminating process %i and waiting up to %i seconds for it to end...",
            proc.pid,
            term_wait_time,
        )
        proc.terminate()
        proc.wait(term_wait_time)

    if proc.poll() is None:
        LOG.warning(
            "Process %i didn't terminate. Killing process and waiting until process exits...",
            proc.pid,
        )
        proc.kill()
        proc.wait()

    LOG.debug("Process %i terminated with %i", proc.pid, proc.poll())


def term_all_procs():
    LOG.debug("Terminating all processes...")
    for p in procs:
        LOG.debug("Reviewing a process with exit status %s..." % p.poll())
        if p.poll() is None:
            term_proc(p, term_wait_time=1)
