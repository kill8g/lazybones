# lazybones
Command Quick Lookup Tool

# Explain
这是一个懒汉shell命令速查工具, 收集了一些常用的命令的使用示例
当你不知道一个命令应该使用什么参数, 或者不知道应该使用什么命令, 又懒得Google或者查看man page, 
也许这个工具能够帮助到你

# Usage
`python lazybones.py -t "Search content"`

例如:
`python lazybones.py -t 如何遍历文件夹内的所有文件`

lazybones会根据你的输入内容告诉你一些常用的命令示例
```shell
# 遍历文件
for file in $(ls path);
do
 echo $file;
done

# 递归遍历所有文件并每个文件执行echo命令
find folder -type f -exec echo {} \;
```

或者可以使用交互模式
`python lazybones.py -i`
```shell
> 如何遍历文件夹内的所有文件

# 遍历文件
for file in $(ls path);
do
 echo $file;
done

# 递归遍历所有文件并每个文件执行echo命令
find folder -type f -exec echo {} \;
```
然后, 你可以直接在工具内输入你要使用的命令, 使用感叹号修饰你的命令即可
```shell
> !find folder -type f -exec echo {} \;
...
```
