# Separate module for the treestore so that main isn't clogged up.

from constants import *

def additems(treestore, treeview):

    piter = treestore.append(None, ['Containers', 0])
    treestore.append(piter, ['Class', CONT_CLASS])
    treestore.append(piter, ['If', DEBUG_NONCALL])
    treestore.append(piter, ['For', DEBUG_NONCALL])
    treestore.append(piter, ['While', DEBUG_NONCALL])

    piter = treestore.append(None, ['Nodes', 0])
    treestore.append(piter, ['Function', DEBUG_FUNC])
    treestore.append(piter, ['Instance', DEBUG_NONCALL])
    treestore.append(piter, ['Comment', DEBUG_NONCALL])
    treestore.append(piter, ['Return', DEBUG_NONCALL])
    treestore.append(piter, ['Yield', DEBUG_NONCALL])

    piter = treestore.append(None, ['Special', 0])
    treestore.append(piter, ['Raw Pycode', DEBUG_NONCALL])
    treestore.append(piter, ['Updater', DEBUG_NONCALL])
    treestore.append(piter, ['Pixel Out', DEBUG_NONCALL])
    treestore.append(piter, ['Text Out', DEBUG_NONCALL])

    piter = treestore.append(None, ['', 0])

    piter = treestore.append(None, ['debug', 0])
    treestore.append(piter, ['GTK', DEBUG_GTK])
    treestore.append(piter, ['Test Container', DEBUG_TESTCONTAINER])
    treestore.append(piter, ['Test Container 2', DEBUG_TESTCONTAINER2])

    piter = treestore.append(None, ['', 0])

    piter = treestore.append(None, ['torch.nn', 0])
    treestore.append(piter, ['Linear', TORCH_NN_LINEAR])
    treestore.append(piter, ['Sigmoid', TORCH_NN_SIGMOID])

    piter = treestore.append(None, ['torch', 0])
    treestore.append(piter, ['FloatTensor', TORCH_FLOATTENSOR])

    piter = treestore.append(None, ['Instances', 0])
    treestore.append(piter, ['a', TORCH_NN_LINEAR])
    treestore.append(piter, ['b', TORCH_NN_LINEAR])
    treestore.append(piter, ['c', TORCH_NN_LINEAR])
    treestore.append(piter, ['d', TORCH_NN_LINEAR])

    piter = treestore.append(None, ['', 0])
