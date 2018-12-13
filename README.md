#  Cerulean Editor

A Python/PyTorch IDE by way of visual quasi-graph nodes.

# WIP: Not yet working. Still mostly prototyping.

Code is built up by a series of connected nodes. You drag n' drop and
connect functions/variables in a 2D area. It's meant to speed up
visualization and prototyping. Ideally this will enable easy reuse of
neural net models and weights. Might be useful as a general IDE as well.


### Advanced Model
TD: (Image of a large containerized model and special widgets.)

### Basic Graph

![Assignment](examples/ex_12.png?raw=true "Assignment")

>split1, split2 = Split(Concat(Tensor(data1), Tensor(data2)))

>output1 = FC(Concat(split1, split2))

>output2 = FC_B(FC_A(Concat(split1, split2)))



### Overview of nodes:

> A solid arrow to a solid box indicate an inputs to a functions.

> A dotted box indicates an instance/variable.

> ![Function](examples/ex_function.png?raw=true "Function")

> A solid arrow to a dotted box indicates assignment.

> ![Assignment](examples/ex_assignment.png?raw=true "Assignment")



> Dotted lines are 'newlines' or breaks between lines of code.

> ![Code break](examples/ex_newline.png?raw=true "Code break")

> Having state is necessary for nearly any NN. Classes and
> functions are defined within containers.

> TD: ex. of Class Definition
> ex. of Function Definition
