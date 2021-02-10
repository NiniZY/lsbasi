# 编译器学习总结
## 概念自我理解
编译器整体是一个往回循环的语言处理机制，需要使用语法明确指定每一条规则的使用。  
以及规则之间的嵌套。
## 概念逻辑框图
下文是需要编译的原始文件。其中可以看到程序的整体开始是以BEGIN开始，END.结束。
内部会有逻辑嵌套，以begin开始，end;结束。逻辑表述中，以`;`分隔开，最后一句话可以不用`;`
```
BEGIN

    BEGIN
        number := 2;
        a := number;
        b := 10 * a + 10 * number / 4;
        c := a - - b
    END;

    x := 11;
END.
```
 ```
    program : compound_statement DOT

    compound_statement : BEGIN statement_list END

    statement_list : statement
                   | statement SEMI statement_list

    statement : compound_statement
              | assignment_statement
              | empty

    assignment_statement : variable ASSIGN expr

    empty :

    expr: term ((PLUS | MINUS) term)*

    term: factor ((MUL | DIV) factor)*

    factor : PLUS factor
           | MINUS factor
           | INTEGER
           | LPAREN expr RPAREN
           | variable

    variable: ID
```