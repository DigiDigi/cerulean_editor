import torch
from constants import *

imports = ('torch')  # These are Imports for any functions that exists in the sidebar. Written top level.
modules = dict()
noncalling = set()  # Modules that aren't called. Non-functions.
# WIP: The ones I have here are for testing and should actually be functions.

# TD: Maybe remove the sets here later. Most of module variations are specifically one type.

testcontainers = set()

modules[CONT_CLASS] = None

modules[TORCH_NN_LINEAR] = torch.nn.Linear
noncalling.add(TORCH_NN_LINEAR)


modules[TORCH_NN_CONV2D] = torch.nn.Conv2d
noncalling.add(TORCH_NN_SIGMOID)

modules[TORCH_NN_SIGMOID] = torch.nn.Sigmoid
noncalling.add(TORCH_NN_SIGMOID)

modules[DEBUG_FUNC] = None
modules[DEBUG_NONCALL] = None
noncalling.add(DEBUG_NONCALL)
modules[DEBUG_FUNCB] = None
modules[DEBUG_NONCALLB] = None
noncalling.add(DEBUG_NONCALLB)

modules[DEBUG_TESTCONTAINER] = None
testcontainers.add(DEBUG_TESTCONTAINER)
modules[DEBUG_TESTCONTAINER2] = None
testcontainers.add(DEBUG_TESTCONTAINER2)

# WIP:
# How do we write a function here that returns the data in the text view?
modules[F_PYTHON] = None

modules[TORCH_FLOATTENSOR] = torch.FloatTensor
modules[TORCH_AUTOGRAD_VARIABLE] = torch.autograd.Variable
modules[TORCH_NN_LINEAR] = torch.nn.Linear
modules[TORCH_NN_SIGMOID] = torch.nn.Sigmoid

def func_print(v):
    print (v)
modules[F_PRINT] = func_print

# Not sure what the cleanest way to implement this is.
def func_cuda(v, device_id=None):
    v.cuda(device_id)
    return v
modules[F_CUDA] = func_cuda


def func_cpu(v):
    v.cpu()
    return v
modules[F_CPU] = func_cuda



