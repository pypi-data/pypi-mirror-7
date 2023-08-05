from datetime import datetime
import logging
import threading
from time import time
import sys

from pyage.core import inject

from pyage.core.workplace import Workplace


logger = logging.getLogger(__name__)

if __name__ == '__main__':
    start_time = time()
    logging.basicConfig(filename='pyage-' + datetime.now().strftime("%Y%m%d_%H%M%S") + '.log', level=logging.INFO)
    inject.config = sys.argv[1]
    logging.debug("config: %s", inject.config)
    workspace = Workplace()
    workspace.publish()
    workspace.publish_agents()
    logger.debug(workspace.address)
    if hasattr(workspace, "daemon"):
        thread = threading.Thread(target=workspace.daemon.requestLoop)
        thread.setDaemon(True)
        thread.start()
        import Pyro4
        Pyro4.config.COMMTIMEOUT = 1
    while not workspace.stopped:
        workspace.step()
    time = time() - start_time
    logger.debug("elapsed time: %s seconds", time)
    if hasattr(workspace, "daemon"):
        workspace.daemon.close()
    workspace.unregister_agents()
    workspace.unregister()