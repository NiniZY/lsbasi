# day10的学习概念
## 符号理解及意思表达
    1. symbol:程序当中的元素，例如变量，变量类型，或者子程序等
    2. symbol中包含的信息有变量名称，变量类别（变量，子程序，或者内置类型），变量类型
## why do we need to track symbols
    增加symbol,可以实现对变量内置数据类型的管理，对新增变量的数据类型进行管理。
    归纳结果就是可以在程序被运行前，对变量的数据类型进行校验。
## What is the difference between defining a symbol and resolving/looking up the symbol?
   定义和解析的区别：定义就是向变量表中新增一个KV<变量名称，变量数据类型>，解析就是根据变量名称获得名称所归纳的数据类型。