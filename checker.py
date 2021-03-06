# gone/checker.py
'''
*** Do not start this project until you have fully completed Exercise 3. ***

In this project you need to perform semantic checks on your program.
This problem is multifaceted and complicated.  To make it somewhat
less brain exploding, you need to take it slow and in parts.

First, you will need to define a symbol table that keeps track of
previously declared identifiers.  The symbol table will be consulted
whenever the compiler needs to lookup information about variable and
constant declarations.  

Next, you will need to define objects that represent the different
builtin datatypes and record information about their capabilities.
See the file gone/typesys.py.

Finally, you'll need to write code that walks the AST and enforces
a set of semantic rules. Here is a list of the minimal set of things
that need to be checked:

1.  Names and symbols:

    All identifiers must be defined before they are used.  This
    includes variables, constants, and typenames.  For example, this
    kind of code generates an error:

       a = 3;              // Error. 'a' not defined.
       var a int;

    Note: typenames such as "int", "float", and "string" are built-in
    names that should already be defined at the start of checking.

2.  Types of literals and constants

    All literal symbols are implicitly typed and must be assigned a
    type of "int", "float", or "string".  This type is used to set
    the type of constants.  For example:

       const a = 42;         // Type "int"
       const b = 4.2;        // Type "float"
       const c = "forty";    // Type "string"


3.  Binary operator type checking

    Binary operators only operate on operands of the same type and produce a
    result of the same type.  Otherwise, you get a type error.  For example:

        var a int = 2;
        var b float = 3.14;

        var c int = a + 3;    // OK
        var d int = a + b;    // Error.  int + float
        var e int = b + 4.5;  // Error.  int = float

4.  Unary operator type checking.

    Unary operators always return a result that's the same type as the operand.

5.  Supported operators

    Here are the operators that need to be supported by each type:

    int:      binary { +, -, *, /}, unary { +, -}
    float:    binary { +, -, *, /}, unary { +, -}
    string:   binary { + }, unary { }

    Attempts to use unsupported operators should result in an error. 
    For example:

        var string a = "Hello" + "World";     // OK
        var string b = "Hello" * "World";     // Error (unsupported op *)

    Bonus: Support mixed-type operators in certain cases

        var string a = "Hello" * 4;          // OK. String replication
        var string b = 4 * "Hello";          // OK. String replication

6.  Assignment.

    The left and right hand sides of an assignment operation must be
    declared as the same type.

        var a int;
        a = 4 + 5;     // OK
        a = 4.5;       // Error. int = float

    Values can only be assigned to variable declarations, not
    to constants.

        var a int;
        const b = 42;

        a = 37;        // OK
        b = 37;        // Error. b is const

Implementation Strategy:
------------------------
You're going to use the NodeVisitor class defined in gone/ast.py to
walk the parse tree.   You will be defining various methods for
different AST node types.  For example, if you have a node BinaryOp,
you'll write a method like this:

      def visit_BinaryOp(self, node):
          ...

To start, make each method simply print out a message:

      def visit_BinaryOp(self, node):
          print('visit_BinaryOp:', node)
          ...

This will at least tell you that the method is firing.  Try some
simple code examples and make sure that all of your methods
are actually running when you walk the parse tree.

After you're satisfied that your methods are running, add support
for a symbol name and focus on the problem of managing names. 
Declarations such as:

      var a int;
      const b = 42;

put names into the symbol table.  The symbol table could be as
simple as a dict:
     
      { 'a': ...,  'b': .... }

Use of a name elsewhere such as in an expression "37 + b" look things
up in the symbol table. Write some test inputs that involve undefined
names and make sure it's working.   Note:  There is some extra complexity
in your symbol table in that you also need to check more than just types.
For example, if "b" is a constant, you can't assign to it.  You'll
need to have some way to check for that.

After names are working, move on to type propagation. Start with
literals.  Work your way through more complex operations such
as binary operators and unary operators.  You're going to be
checking and propagating types.  For example, your visit_BinaryOp() 
method might look roughly like this:

     def visit_BinaryOp(self, node):
         self.visit(node.left)
         self.visit(node.right)
         if node.left.type != node.right.type:
             # Type Error!
         else:
            node.type = node.left.type    # Propagate the type

After you're propagating types, shift your focus to the capabilities
of each type. For example, the '-' operator works with int and float
types, but not with strings.   You'll need to figure out some
way to check for this.

Wrap up by focusing on variable assignment and other details.
Make sure that the left and right sides have the same type.

General thoughts and tips
-------------------------
The main thing you need to be thinking about with checking is program
correctness.  Does this statement or operation that you're looking at
in the parse tree make sense?  If not, some kind of error needs to be
generated.  Use your own experiences as a programmer as a guide (think
about what would cause an error in your favorite programming
language).

One challenge is going to be the management of many fiddly details. 
You've got to track symbols, types, and different sorts of capabilities.
It's not always clear how to best organize all of that.  So, expect to
fumble around a bit at first.
'''

from .errors import error
from .ast import *
from .typesys import check_binop, check_unaryop, error_type, builtin_types, _supported_binops, _supported_unaryops


class SymbolTable(object):
    '''
    Class representing a symbol table.   To start, it should provide
    functionality for adding and looking up objects associated with
    identifiers.   Think Python dictionaries.  You might want to add
    extra functionality later so it's probably better to make it
    a separate class as opposed to using a dict directly.
    '''
    pass


class CheckProgramVisitor(NodeVisitor):
    '''
    Program checking class.   This class uses the visitor pattern as described
    in ast.py.   You need to define methods of the form visit_NodeName()
    for each kind of AST node that you want to process.  You may need to
    adjust the method names here if you've picked different AST node names.
    '''

    def __init__(self):
        # Initialize the symbol table
        self._symbol_table = {}

        # Add built-in type names to the symbol table
        self._symbol_table.update({t: t for t in builtin_types})

    def visit_Unaryop(self, node):
        # 1. Make sure that the operation is supported by the type
        # 2. Set the result type 
        #
        # Hint: Use the check_unaryop() function in typesys.py
        self.visit(node.expr)
        op = (node.op, node.expr.type)
        node.type = _supported_unaryops.get(op, error_type)

    def visit_BinOp(self, node):
        # 1. Make sure left and right operands have the same type
        # 2. Make sure the operation is supported
        # 3. Assign the result type
        #
        # Hint: Use the check_binop() function in typesys.py
        # print('visit_Binop:', node)

        self.visit(node.left)
        self.visit(node.right)
        if node.left.type != node.right.type:
            error(node.lineno, 'Type Error: Left and right operands do not have the same type')
            node.type = error_type

        # check if operation is supported
        op = (node.left.type, node.op, node.right.type)
        node.type = _supported_binops.get(op, error_type)

    def visit_AssignmentStatement(self, node):
        # 1. Make sure the location of the assignment is defined
        # 2. Visit the expression on the right hand side
        # 3. Check that the types match
        self.visit(node.store_location)
        if node.expr:
            self.visit(node.expr)

    def visit_ConstDeclaration(self, node):
        # 1. Check that the constant name is not already defined
        # 2. Add an entry to the symbol table
        # print('visit_ConstDeclaration', node)
        sym = self._symbol_table.get(node.name, None)
        if not sym:
            self.visit(node.expr)
            node.type = node.expr.type
            self._symbol_table[node.name] = node
        else:
            error(node.lineno, 'Const Re-Declaration of %s' % (node.name))

    def visit_VarDeclaration(self, node):
        # 1. Check that the variable name is not already defined
        # 2. Add an entry to the symbol table
        # 3. Check that the type of the expression (if any) is the same
        self.visit(node.typename)
        node.type = node.typename.type
        if node.expr:
            self.visit(node.expr)
            if (node.expr.type != node.type and
                        node.expr.type != error_type):
                error(node.lineno, 'Type error %s = %s' % (node.type, node.expr.type))
        self._symbol_table[node.name] = node

    def visit_Typename(self, node):
        # 1. Make sure the typename is valid and that it's actually a type

        sym = self._symbol_table.get(node.name, None)
        if sym:
            if sym in builtin_types:
                node.type = sym
            else:
                error(node.lineno, '%s is not a type' % node.name)
                node.type = error_type
        else:
            error(node.lineno, '%s is not defined' % node.name)
            node.type = error_type

    def visit_LoadVariable(self, node):
        # 1. Make sure the location is a valid variable or constant value
        # 2. Assign the type of the variable to the node

        sym = self._symbol_table.get(node.name, None)
        if sym:
            if isinstance(sym, (ConstDeclaration, VarDeclaration, ParmDeclaration)):
                node.type = sym.type
            else:
                error(node.lineno, '%s not a valid location' % node.name)
                node.type = error_type
        else:
            error(node.lineno, '%s undefined' % node.name)
            node.type = error_type
        # Attach the symbol to the node
        node.sym = sym

    def visit_StoreVariable(self, node):
        # 1. Make sure the location can be assigned
        # 2. Assign the appropriate type
        sym = self._symbol_table.get(node.name)
        if sym:
            if isinstance(sym, (VarDeclaration, ParmDeclaration)):
                node.type = sym.type
            elif isinstance(sym, ConstDeclaration):
                error(node.lineno, 'Type error. %s is constant' % node.name)
                node.type = sym.type
            else:
                error(node.lineno, '%s not a valid location' % node.name)
                node.type = error_type
        else:
            error(node.lineno, '%s undefined' % node.name)
            node.type = error_type

    def visit_Literal(self, node):
        # 1. Attach an appropriate type to the literal
        # print('visit_Literal', node)
        node.type = self._symbol_table[node.typename]
        # You will need to add more methods here in Projects 5-8.


    def visit_ParmDeclaration(self, node):
        # 1. Visit the typename and propagate types
        self.visit(node.typename)
        node.type = node.typename.type


    def visit_FunctionPrototype(self, node):
        # 1. Make sure the function name is not already defined
        # 2. Visit the parameters to make sure they contain valid types
        # 3. Make sure the function return type is a valid type
        # 4. Place the function prototype in the symbol table
        for parm in node.parameters:
            self.visit(parm)
        self.visit(node.typename)
        node.type = node.typename.type
        self._symbol_table[node.name] = node


    def visit_FunctionCall(self, node):
        symnode = self._symbol_table.get(node.name, None)
        if symnode:
            if not isinstance(symnode, FunctionPrototype):
                error(node.lineno, '%s not a function' % node.name)
                node.type = error_type
            else:
                # A valid function prototype.  Check arguments and types
                if len(node.arglist) != len(symnode.parameters):
                    error(node.lineno,
                          '%s expected %d arguments. Got %d.' % (node.name, len(symnode.parameters), len(node.arglist)))
                for n, (arg, parm) in enumerate(zip(node.arglist, symnode.parameters), start=1):
                    self.visit(arg)
                    if arg.type != parm.type:
                        error(arg.lineno, 'Type error. Argument %d must be %s' % (n, parm.type))
                node.type = symnode.type
        else:
            error(node.lineno, 'Undefined name %s' % node.name)
            node.type = error_type

    # Function declaration
    def visit_FunctionDeclaration(self, node):
        # 1. Check to make sure not nested function
        # 2. Visit prototype to check for duplication/typenames
        # 3. Set up a new local scope
        # 4. Process function parameters and add symbols to symbol table
        # 5. Visit the body
        # 6. Pop the local scope
        import ipdb
        ipdb.set_trace()
        if self.current_function:
            error(node.lineno, 'Nested functions not supported.')
        else:
            self.visit(node.prototype)
            self._local_symtab = {}
            self.current_function = node

            # Process the function parameters
            for parm in node.prototype.parameters:
                self._symbol_table[parm.name] = parm

            self.visit(node.statements)
            self._local_symtab = None
            self.current_function = None




# ----------------------------------------------------------------------
#                       DO NOT MODIFY ANYTHING BELOW       
# ----------------------------------------------------------------------

def check_program(ast):
    '''
    Check the supplied program (in the form of an AST)
    '''
    checker = CheckProgramVisitor()
    checker.visit(ast)


def main():
    '''
    Main program. Used for testing
    '''
    import sys
    from .parser import parse

    if len(sys.argv) != 2:
        sys.stderr.write('Usage: python3 -m gone.checker filename\n')
        raise SystemExit(1)

    ast = parse(open(sys.argv[1]).read())
    check_program(ast)


if __name__ == '__main__':
    main()
