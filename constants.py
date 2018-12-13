class Constants(object):
    def __init__(self):
        self.c_int = 0  # 0 will be undefined.

    def new(self):
        self.c_int += 1
        return self.c_int
c = Constants()

TORCH_FLOATTENSOR = c.new()
TORCH_AUTOGRAD_VARIABLE = c.new()
TORCH_NN_CONV2D = c.new()
TORCH_NN_LINEAR = c.new()
TORCH_NN_SIGMOID = c.new()
F_PYTHON = c.new()
F_PRINT = c.new()
F_CUDA = c.new()
F_CPU = c.new()

DEBUG_FUNC = c.new()
DEBUG_NONCALL = c.new()
DEBUG_FUNCB = c.new()
DEBUG_NONCALLB = c.new()
DEBUG_TESTCONTAINER = c.new()
DEBUG_TESTCONTAINER2 = c.new()

DEBUG_GTK = c.new()

CONT_CLASS = c.new()
