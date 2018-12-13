import torch
from constants import *

imports = ('torch')  # These are Imports for any functions that exists in the sidebar. Written top level.
functions = dict()
noncalling = set()  # Non-functions.
# WIP: The ones I have here are for testing and should actually be functions.

functions[CONT_CLASS] = None

functions[TORCH_NN_LINEAR] = torch.nn.Linear
noncalling.add(TORCH_NN_LINEAR)

functions[TORCH_NN_CONV2D] = torch.nn.Conv2d
noncalling.add(TORCH_NN_SIGMOID)

functions[TORCH_NN_SIGMOID] = torch.nn.Sigmoid
noncalling.add(TORCH_NN_SIGMOID)

functions[DEBUG_FUNC] = None
functions[DEBUG_NONCALL] = None
noncalling.add(DEBUG_NONCALL)
functions[DEBUG_FUNCB] = None
functions[DEBUG_NONCALLB] = None
noncalling.add(DEBUG_NONCALLB)

functions[DEBUG_TESTCONTAINER] = None
functions[DEBUG_TESTCONTAINER2] = None

# WIP:
# How do we write a function here that returns the data in the text view?
functions[F_PYTHON] = None

functions[TORCH_FLOATTENSOR] = torch.FloatTensor
functions[TORCH_AUTOGRAD_VARIABLE] = torch.autograd.Variable
functions[TORCH_NN_LINEAR] = torch.nn.Linear
functions[TORCH_NN_SIGMOID] = torch.nn.Sigmoid

def func_print(v):
    print (v)
functions[F_PRINT] = func_print

# Not sure what the cleanest way to implement this is.
def func_cuda(v, device_id=None):
    v.cuda(device_id)
    return v
functions[F_CUDA] = func_cuda


def func_cpu(v):
    v.cpu()
    return v
functions[F_CPU] = func_cuda



