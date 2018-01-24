from subprocess import PIPE, Popen, TimeoutExpired

from speed_miner.misc.logging import LOG


procs = []


def start_proc(cmd, pipe_stdout=False, preexec_fn=None):
    global pid_to_procs
    kwargs = {}
    if pipe_stdout:
        kwargs["stdout"] = PIPE
    if preexec_fn:
        kwargs["preexec_fn"] = preexec_fn

    p = Popen(cmd.split(" "), **kwargs)

    procs.append(p)

    LOG.debug("Started \"%s\" with pid of %i", cmd, p.pid)
    return p


def term_proc(proc, term_wait_time=3):
    global pid_to_procs
    if proc.poll() is None:
        LOG.debug(
            "Terminating process %i and waiting up to %i seconds for it to end...",
            proc.pid,
            term_wait_time,
        )
        proc.terminate()
        try:
            proc.wait(term_wait_time)
        except TimeoutExpired:
            pass

    if proc.poll() is None:
        LOG.warning(
            "Process %i didn't terminate. Killing process and waiting until process exits...",
            proc.pid,
        )
        proc.kill()
        proc.wait()

    if proc.stdout:
        proc.stdout.close()

    if proc.stderr:
        proc.stder.close()

    if proc.stdin:
        proc.stdin.close()

    assert proc.poll() is not None, "Proc %i didn't terminate properly" % proc.pid

    LOG.debug("Process %i terminated with %i", proc.pid, proc.poll())


def term_all_procs(term_wait_time=1):
    global procs
    LOG.debug("Terminating all processes...")
    for p in procs:
        if p.poll() is None:
            term_proc(p, term_wait_time=term_wait_time)
