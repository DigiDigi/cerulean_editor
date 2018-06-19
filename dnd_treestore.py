# Separate module for the treestore so that main isn't clogged up.

from constants import *

def additems(treestore, treeview):

    #path = treestore.get_path(piter)
    #treeview.scroll_to_cell(path)

    piter = treestore.append(None, ['Containers', 0])
    treestore.append(piter, ['Function', DEBUG_NONCALL])
    treestore.append(piter, ['Class', CONT_CLASS])
    treestore.append(piter, ['If Else', DEBUG_NONCALL])
    treestore.append(piter, ['For', DEBUG_NONCALL])
    treestore.append(piter, ['While', DEBUG_NONCALL])

    piter = treestore.append(None, ['Nodes', 0])
    treestore.append(piter, ['Function', DEBUG_FUNC])
    treestore.append(piter, ['Instance', DEBUG_NONCALL])
    treestore.append(piter, ['Comment', DEBUG_NONCALL])
    treestore.append(piter, ['Return', DEBUG_NONCALL])
    treestore.append(piter, ['Yield', DEBUG_NONCALL])
    treestore.append(piter, ['Print', DEBUG_NONCALL])

    piter = treestore.append(None, ['Special', 0])
    treestore.append(piter, ['Pixel Out', DEBUG_NONCALL])
    treestore.append(piter, ['Text Out', DEBUG_NONCALL])
    treestore.append(piter, ['Code Line', DEBUG_NONCALL])


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

    piter = treestore.append(None, ['debug', 0])
    treestore.append(piter, ['Test Container', DEBUG_TESTCONTAINER])
    treestore.append(piter, ['Test Container 2', DEBUG_TESTCONTAINER2])

    piter = treestore.append(None, ['', 0])




    """
    piter = treestore.append(None, ['Model', 0])
    # treestore.append(piter, ['Container'])
    # treestore.append(piter, ['Parameters'])
    # treestore.append(piter, ['Config'])
    piter = treestore.append(None, ['Input', 0])
    # treestore.append(piter, ['FromFolder'])
    # treestore.append(piter, ['FromCapture'])
    # treestore.append(piter, ['DataLoader'])
    piter = treestore.append(None, ['Layers', 0])
    treestore.append(piter, ['Linear', TORCH_NN_LINEAR])
    treestore.append(piter, ['Conv2d', TORCH_NN_CONV2D])
    piter = treestore.append(None, ['Activations', 0])
    treestore.append(piter, ['Sigmoid', TORCH_NN_SIGMOID])
    treestore.append(piter, ['ReLU', 0])
    treestore.append(piter, ['Softmax', 0])
    piter = treestore.append(None, ['Code', 0])
    treestore.append(piter, ['Python', F_PYTHON])
    piter = treestore.append(None, ['Math', 0])
    treestore.append(piter, ['Add', 0])
    treestore.append(piter, ['Mul', 0])
    treestore.append(piter, ['Sqrt', 0])
    piter = treestore.append(None, ['Output', 0])
    # treestore.append(piter, ['Display'])
    treestore.append(piter, ['Print', 0])
    # treestore.append(piter, ['Terminal'])
    # treestore.append(piter, ['Graph'])
    # treestore.append(piter, ['File'])
    piter = treestore.append(None, ['----', 0])
    piter = treestore.append(None, ['Misc', 0])
    treestore.append(piter, ['Comment', 0])
    """

