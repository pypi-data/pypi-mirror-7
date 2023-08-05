# UPS 是一个又拍云服务的简化版服务器端

一个又拍云服务的模拟器，提供与又拍云相同的接口，
开发人员可部署在测试环境中，以与正式环境的又拍云服务隔离。

可使用笔者的另一个项目UPC[http://upyun.gitcafe.com/likang/upc-for-UPYUN] 
进行管理测试。


## 安装

```
pip install ups
```

## 使用

保存如下示例的文件到个人目录的 .upcrc 文件中 （支持多个 bucket ）

```
[server]
host=127.0.0.1
port=8080

[your-bucket-name]
username=foo
password=bar
path=/nfs/images

```

然后直接运行
```
$ ups
```


## 其他
时间仓促，难免有考虑不周的地方，欢迎扔 issue :D

[github](https://github.com/likang/ups)

[gitcafe](https://gitcafe.com/likang/ups)
