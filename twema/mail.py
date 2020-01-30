#
# © 2020 Mikhail Gusarov <dottedmag@dottedmag.net>
#
# This file is a part of twema and licensed under AGPLv3. See doc/COPYING at the
# root of the repository for the details.
#
import subprocess
from email.utils import parseaddr


def send(config, msg):
    [name, email] = parseaddr(config["mail"]["from"])

    p = subprocess.Popen(
        ["/usr/sbin/sendmail", "-t", "-oi", "-f", email, "-F", name],
        stdin=subprocess.PIPE,
    )
    p.communicate(msg)
    return p.returncode == 0
