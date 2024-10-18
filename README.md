This project attempts to recreate the Branch and Bound method of linear programming, but only with models that have only binary variables in their compositions.

How do I run the code?
    When running the code (with python branchbound.py), the user will be asked for the name of the file that contains the input data. Right after this answer, the code flow will happen normally and you will have the solution at the end

This input file must be in the following form:

  ° First line -> number_of_variables number_of_restrictions (Separated with a space)
  ° Second line -> Objective function coefficients
  ° Other lines -> Constraint coefficients
  ° In addition, all constraints must be written as less than the last coefficient

How the code works:

  ° The code works by generating a binary tree with models associated with each child, solving the model of the root and saving the results in the node. 
  ° It then enters an infinite loop, stopping only when all possible nodes have been generated. The code executes all the threads created to solve the nodes of the current height. Afterwards, it tests each node to determine if it generated an infeasible solution, a solution with integer variables, a solution with non-integer variables worse than the integer solution found, or none of these cases.
  ° If none of the cases is found, it branches the node, removing the possibility of the first non-integer variable having a non-integer value again without removing any integer solutions. 
  ° In the end, the code displays the value of the integer solution found, how the variables generated that value, and a visual representation of the tree with all the nodes.

  All the code is commented in Portuguese (Brazil)
