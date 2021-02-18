from spi import (
    Lexer,
    Parser,
    NodeVisitor,
    BuiltinTypeSymbol,
    VarSymbol,
    ProcedureSymbol,
    ScopedSymbolTable,
    ProgramSymbol
)


class SemanticAnalyzer(NodeVisitor):
    def __init__(self):
        self.current_scope = None
        init_scope = ScopedSymbolTable(
            scope_name='builtin',
            scope_level=0,
            enclosing_scope=self.current_scope
        )
        init_scope._init_builtins()
        self.current_scope = init_scope
        self.output = None


    def visit_Block(self, node):
        results = []
        for declaration in node.declarations:
            result = self.visit(declaration)
            results.append(result)
        results.append('\nbegin')
        result = self.visit(node.compound_statement)
        result = '      ' + result
        results.append(result)
        results.append('end')
        return '\n'.join(results)  # 将添加到文本都进行\n换行的操作

    def visit_Program(self, node):
        program_name = node.name
        result_str = 'program %s0;\n' % program_name

        global_scope = ScopedSymbolTable(
            scope_name='global',
            scope_level=self.current_scope.scope_level+1,
            enclosing_scope=self.current_scope  # self.current_scope 当前是内置scope
        )
        program_symbol = ProgramSymbol(node.name)
        self.current_scope.insert(program_symbol)

        self.current_scope = global_scope

        # visit subtree
        result_str += self.visit(node.block)
        result_str += '.'
        result_str += ' {END OF %s}' % program_name
        self.output = result_str
        self.current_scope = self.current_scope.enclosing_scope  # 当前范围的值实际发生了变更。此次的范围识别为内置级别

    def visit_Compound(self, node):
        results = []
        for child in node.children:
            result = self.visit(child)
            if result is None:
                continue
            results.append(result)
        return '\n'.join(results)

    def visit_NoOp(self, node):
        pass

    def visit_BinOp(self, node):
        t1 = self.visit(node.left)
        t2 = self.visit(node.right)
        return '%s %s %s' % (t1, node.op.value, t2)

    def visit_ProcedureDecl(self, node):
        proc_name = node.proc_name
        proc_symbol = ProcedureSymbol(proc_name)
        self.current_scope.insert(proc_symbol)
        result_str = 'procedure %s%s' % (
            proc_name, self.current_scope.scope_level
        )

        # Scope for parameters and local variables
        procedure_scope = ScopedSymbolTable(
            scope_name=proc_name,
            scope_level=self.current_scope.scope_level + 1,
            enclosing_scope=self.current_scope
        )
        self.current_scope = procedure_scope

        if node.params:
            result_str += '('

        formal_params = []
        # Insert parameters into the procedure scope
        for param in node.params:
            param_type = self.current_scope.lookup(param.type_node.value)
            param_name = param.var_node.value
            var_symbol = VarSymbol(param_name, param_type)
            self.current_scope.insert(var_symbol)
            proc_symbol.params.append(var_symbol)
            scope_level = str(self.current_scope.scope_level)
            formal_params.append(
                '%s : %s' % (param_name + scope_level, param_type.name)
            )

        result_str += ';'.join(formal_params)
        if node.params:
            result_str += ')'

        result_str += ';'
        result_str += '\n'
        result_str += self.visit(node.block_node)
        result_str += '; {END OF %s}' % proc_name

        # indent procedure text
        result_str = '\n'.join('   ' + line for line in result_str.splitlines())

        self.current_scope = self.current_scope.enclosing_scope

        return result_str

    def visit_VarDecl(self, node):
        type_name = node.type_node.value
        type_symbol = self.current_scope.lookup(type_name)

        # We have all the information we need to create a variable symbol.
        # Create the symbol and insert it into the symbol table.
        var_name = node.var_node.value
        var_symbol = VarSymbol(var_name, type_symbol)

        # Signal an error if the table alrady has a symbol
        # with the same name
        if self.current_scope.lookup(var_name, current_scope_only=True):
            raise Exception(
                "Error: Duplicate identifier '%s' found" % var_name
            )

        self.current_scope.insert(var_symbol)
        scope_level = str(self.current_scope.scope_level)
        return '   var %s : %s;' % (var_name + scope_level, type_name)

    def visit_Assign(self, node):
        # right-hand side
        t2 = self.visit(node.right)
        # left-hand side
        t1 = self.visit(node.left)
        return '%s %s %s;' % (t1, ':=', t2)

    def visit_Var(self, node):
        var_name = node.value
        var_symbol = self.current_scope.lookup(var_name)
        if var_symbol is None:
            raise Exception(
                "Error: Symbol(identifier) not found '%s'" % var_name
            )
        scope_level = str(var_symbol.scope.scope_level)
        return '<%s:%s>' % (var_name + scope_level, var_symbol.type.name)


if __name__ == '__main__':
    import sys

    text = "program Main;                         " \
           "   var x, y : real;                   " \
           "   procedure AlphaA(a : integer);     " \
           "      var y : integer;                " \
           "   begin { AlphaA }                   " \
           "                                      " \
           "   end;  { AlphaA }                   " \
           "                                      " \
           "   procedure AlphaB(a : integer);     " \
           "      var b : integer;                 " \
           "   begin { AlphaB }                    " \
           "                                       " \
           "   end;  { AlphaB }                    " \
           "                                       " \
           "begin { Main }                         " \
           "                                       " \
           "end.  { Main }                         "

    lexer = Lexer(text)
    parser = Parser(lexer)
    tree = parser.parse()

    source_compiler = SemanticAnalyzer()
    source_compiler.visit(tree)
    print(source_compiler.output)
