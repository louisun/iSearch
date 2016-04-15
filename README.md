# iSearch


`iSearch`是一款命令行单词查询/管理工具，主要是为了方便自己考研和学习时候查找和管理单词。

内容来自[网易有道词典](http://dict.youdao.com/)。

通过 API 得到的内容比较简略，只能派临时之用。因此采用网页解析，整理出尚能看的内容。

内容包括【柯林斯词典】、【词组】、【同近义词】、【词语辨析】、【其他例句】，每个单词不一定都有以上各项内容。

其他功能有：

- 在本地 sqlite 数据库中添加单词、删除单词
- 对数据库中的单词设置`优先级`
- 按照`首字母`、`优先级范围`、`添加时间`列出单词
- 从文本文件中批量添加单词到数据库
- 颜色高亮（也可关闭，方便导出到文本文件）
- 可以是词组和中文
- 从数据库查询时，可以只输入单词的首部。
- 查看每个字母、优先级的单词数目。

**注：**

普通的查询，先会在本地数据库查找，若没有找到才从网上查找。


---

# 环境

第三方库：
`requests`、`bs4`、`termcolor`

# 设置

初次使用， 请先试查一个单词，以创建配置目录和数据库。

默认配置文件和数据库在`~/.iSearch`目录下。

可以在`utils.py`中设置自己存放数据库和配置文件的目录。

为了方便使用，最好`alias`一下，比如将`python /目录/isearch.py`命名为更为简短的命令。

最好备份数据库文件，以防意外丢失。

# 使用方法


参数说明：
>无额外参数           直接查词
>
>-f     --file       从文本文件添加单词列表到数据库
>
>-a     --add        添加单词
>
>-d     --delete     删除单词
>
>-p     --priority   根据优先级列出单词
>
>-t     --time     列出最近加入的n个单词
>
>-l     --catalog    列出A-Z开头的单词目录
>
>-s     --set        设置单词的优先级
>
>-v     --verbose    查看详细信息
>
>-o      -output     输出模式


---




## 直接查询
```
isearch sun

sun 不在数据库中，从有道词典查询
sun /sʌn/

N-SING The sun is the ball of fire in the sky that the Earth goes around, and that gives us heat and light. 太阳 

例： The sun was now high in the southern sky. 太阳当时正高挂在南面天空上。 

例： The sun came out, briefly. 太阳出来了，时间很短。 

2. N-UNCOUNT You refer to the light and heat that reach us from the sun as the sun . 阳光 

例： Dena took them into the courtyard to sit in the sun. 德娜把他们带到院子里坐在阳光下。

【词组】

in the sun 在阳光下，无忧无虑

under the sun 天下；究竟

with the sun 朝着太阳转动的方向，顺时针方向

sun yat-sen n. 孙逸仙

see the sun 活着；出生；发现太阳的耀眼

setting sun 落日；斜阳

morning sun 朝阳

...

【同近义词】

n. [天]太阳

sonne

vi. [天]晒太阳

bask
```
## 从文本文件添加单词到数据库
```
isearch -f [文件绝对路径]


下面输入default默认为配置目录下的word_list.txt文件

isearch -f default 

```

## 逐个添加单词到数据库 （默认优先级为 1）
```
isearch -a sun

sun has been inserted into database

```

## 从数据库中删除

```
isearch -d [单词]

sun has been deleted from database
```

## 设置优先级 （1 到 5）

```
isearch -s 3 sun

the priority of sun has been reset to 3

```

## 根据优先级（1 到 5）列出单词


```
//非verbose模式, 只输出优先级和单词
//-v --verbose 模式, 输出详细意思 

//非output模式, 命令行多色
//-o --output 模式, 非多色输出, 可以重定向到文件

//列出优先级为1的单词
isearch -p 1

//列出优先级大于2的单词
isearch -p 2+

//列出优先级为2-3的单词
isearch -p 2-3
```

## 列出最近添加的N个单词

```
//非verbose模式, 只输出优先级和单词
//-v --verbose 模式, 输出详细意思

//非output模式, 命令行多色
//-o --output 模式, 非多色输出, 可以重定向到文件

isearch -t 10
```

## 列出以A-Z开头的所有单词

```
//非verbose模式, 只输出优先级和单词
//-v --verbose 模式, 输出详细意思

//非output模式, 命令行多色
//-o --output 模式, 非多色输出, 可以重定向到文件

isearch -l a
```

## 计数

```
// 列出以 a 字母开头的单词数目
isearch -c a

// 列出优先级为 3 的单词数目
isearch -c 3

// 列出优先级大于 3 的单词数目
isearch -c 3+

// 列出优先级为 2-3 的单词数目
isearch -c 2-3

// 列出全部单词数目
isearch -c all
