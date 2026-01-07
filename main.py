import concurrent.futures
import traceback

from Common.config import *
from Common.LoggingSetup import *
from NodeRun.Node import Node


def run_thread(nodesInSys):
    nodesInSys.run()


if __name__ == "__main__":
    nodesList = []
    for i in range(nodeCount):
        n1 = Node()
        nodesList.append(n1)
        n1.listOfNodes.append(n1)

    setNodeId("0")
    nodesList[0].createGenesisBlock()

    print("********After Creating Genesis Block Initial State of the Nodes*********")
    logger.info(
        "********After Creating Genesis Block Initial State of the Nodes*********"
    )
    nodesList[0].printUTXO()
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=nodeCount) as executor:
        for n in nodesList:
            ctx = contextvars.copy_context()
            ctx.run(nodeId.set, n.nodeId)
            fut = executor.submit(ctx.run, run_thread, n)
            futures.append(fut)

    for fut in futures:
        try:
            fut.result()
        except:
            traceback.print_exc()
