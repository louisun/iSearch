#仅修改主文件，不需要重新安装，执行下述命令即可
```
cp iSearch/*.py /home/fufenghai/.local/lib/python2.7/site-packages/iSearch/

```

# ubuntu 18.04 安装pip
sudo apt install python-pip

# 预计开发
1. MVC模式
   a. 通过函数指针形式传输显示函数，
   b. 显示函数接口定义(参见下方 接口定义 1)
4. 能够支持数据库合并，能够将别人的数据库导入自己的，并且能够简单地添加删除。
那么在表名上，可能需要做特殊处理了。
5. 类封装，整理代码逻辑。


# 已完成修改

2. 使用JSON格式进行存放
    - 字典 ：类型名 + 数组
    - 中文 + 英文 作为一个数组单元
    - 中文 和 英文 间通过\n进行分割
3. 将数据库中存放单元更加细化



# 接口定义

1. 显示函数接口定义
   - 显示方式 0 标准输出 1 写入文件
   - 数据
      a. 基本含义
      b. 相关词
      c. 例句
   - 提示字段颜色
   - 主要内容颜色

# 数据库定义
```
CREATE TABLE IF NOT EXISTS Word
(
name     TEXT PRIMARY KEY NOT NULL,
synonyms TEXT,
discriminate TEXT,
word_group TEXT,
collins TEXT,
bilingual TEXT,
fanyiToggle TEXT,
pr       INT DEFAULT 1,
aset     CHAR[1],
addtime  TIMESTAMP NOT NULL DEFAULT (DATETIME('NOW', 'LOCALTIME'))
)
```

