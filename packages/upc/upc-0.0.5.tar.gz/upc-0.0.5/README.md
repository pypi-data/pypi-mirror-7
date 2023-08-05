# UPC 又拍云的命令行管理器

UPC 意思是 upyun client，它提供了一个命令行环境，供开发者管理又拍云端文件，如果你
对 GNU 系列工具有基本的了解，那么你甚至可以直接上手，无需查看任何帮助。

## 特色功能如下：

1. 几乎完整的命令补全
2. 批量操作（如上传、删除）
3. 兼容 OSX / Linux or Unix(?)
4. 兼容 Python 2.6+ / Python 3.+
5. 仅依赖 upyun 官方 SDK

## 安装

```
pip install upc
```

## 使用

首先保存如下示例的文件到个人目录的 .upcrc 文件中 （支持多个 bucket ）

```
[your-bucket-name]
username=foo
password=bar
timeout=
chunksize=
endpoint=


```

执行命令

```
upc your-bucket-name
```

## 文档说明

### 命令补全
```
>>> cd a<Tab><tab>
about/ again/
```

### 命令帮助
```
>>> help ls
List directory contents

usage [-hsStTnN]

    -h  Show human-readable output
    -s  Sort by file size
    -S  Sort by file size desc
    -t  Sort by created time
    -T  Sort by created time desc
    -n  Sort by file name
    -N  Sort by file name described
```

### 查看空间使用情况
```
>>> usage
24345 bytes
>>> usage -h
24.34 M
```

### 列出目录文件
```
>>> ls
d	2014-06-01 19:47	101101 bytes	home_dir
-	2014-05-30 18:20	-	love.png
```


### 上传文件
```
>>> put foo.py *.png
foo.py  OK
foo.png OK
bar.png OK
>>> put -r some_dir
some_dir/foo.py OK
som_dir/sub/bar.py OK
```

### 创建目录
```
>>> mkdir foo
>>> mkdir -p foo/bar
```

### 删除文件/目录
```
>>> rm foo.png
>>> rm -r some_dir
>>> rmdir -r some_dir
```

### 切换目录
```
>>> cd foo/bar
>>> cd ../../
```

### 显示当前目录
```
>>> pwd
/foo/bar
```

### 查看文件/目录信息
```
>>> file foo.png
f	2013-01-04 12:00 1.1kb love.png
```

### 列出本地目录文件
```
>>> lls
d	2014-06-01 19:47	101101 bytes	home_dir
-	2014-05-30 18:20	-	love.png
```

### 打印本地当前目录
```
>>> lpwd
/Users/likang
```

### 切换本地目录
```
>>> lcd foo/bar
```

### 切换又拍空间
```
>>> use another-bucket-name
```

### 退出
```
>>> quit
>>> exit
>>> Ctrl-D
```


## 其他
时间仓促，难免有考虑不周的地方，欢迎扔 issue :D

[github](https://github.com/likang/upc)

[gitcafe](https://gitcafe.com/likang/upc)






