import subprocess
from utils.log import log


def ping_ok(host):
    log("Pinging {}".format(host))
    try:
        subprocess.check_output("ping -c 1 {}".format(host), shell=True)
    except:
        return False
    return True
