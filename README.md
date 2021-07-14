# NEWSCrawler

使用requests也可以抓任意自己想抓的数据，但是唯一不同的是，这样，你将会成为这个行业的"孤儿"。且不说不使用框架有什么好处，但是坏处首先的就是，很多
开源项目的贡献者一起总结出的具体问题的解决模式，你将不会收益。也许，足够的灵活看起来很"酷"，但是，你会变得脱离大部队。使用框架有使用框架的好处，
首先就是，几乎可以不用写什么代码就可以很快将业务流程跑通，方便，快捷，简单，时尚。

笔者总结出一些学习新技术的方法：比如说出现一个新的框架，然后你马上去学下官方文档，做做实验，然后再思考几个在此框架上的应用场景，看能不能实现，然后
试着去实现一番，最后就会得出一种结论。笔者非常不建议去深入的了解某一种框架，这种行为，我觉得如果是官方文档上没说的，或者通过自己简单探求而不能得到
结果，这种行为显得比较蠢，浪费大量的光阴在此，还不如用这点时间去学习和了解新的框架，当你把新的框架了解完毕之后，又回得出一种新的结论。仅此而已。

在学习和了解某些框架的时候，一定要结合特定的应用去考虑，否则就会学了和没学一样。还有一种就是，一定要将自己的某些代码归档保存，并将自己在某些方向的
探求上思索后得出的方法和结论传播到网络上。虽然没什么价值，但是至少能给别人作出参考，间接的也能帮助其它人，也是很不错的意义。

开发环境已经装好了下列依赖：
1. python3
2. pycharm

## 0x1、预备知识:

brew用法:
```shell
brew search  ** #查找某个软件包
brew list   #列出已经安装的软件的包
brew install  **  #安装某个软件包,默认安装的是稳定版本
brew uninstall  **  #卸载某个软件的包
brew upgrade  **  #更新某个软件包
brew info  **  #查看指定软件包的说明
brew cache clean  #清理缓存

brew services run ** #启动m某个服务
brew services start ** #启动 某个 服务，并注册开机自启
brew services stop ** #停止 某个 服务，并取消开机自启
brew services restart ** #重启 某个 服务，并注册开机自启
brew services cleanup #清除已卸载应用的无用配置
```

## 0x2、环境搭建

搭建mac下开发环境。

redis安装，启动:
```shell
brew install redis
brew services run redis
```
设置redis密码登陆:
```shell
vim /usr/local/etc/redis.conf
requirepass 123456
```

命令行密码登陆:
```shell
redis-cli
127.0.0.1:6379> auth 123456
OK
```

python3安装依赖:
```shell
pip install scrapy scrapy-redis scrapy-selenium
```

安装firefox浏览器和驱动geckodriver:
```shell
brew cask install geckodriver
```

安装chrome浏览器和chromedriver:
```shell
brew cask install chromedriver
```

克隆项目到本地：
```shell
git clone https://github.com/cs246810/NEWSCrawler
```
创建虚拟环境并安装依赖包:
```shell
cd NEWSCrawler
venv venv
source venv/bin/active
pip install - r requirements.txt
```

修改项目配置文件(`NEWSCrawler/NEWSCrawler/settings.py`):
```shell
REDIS_URL = 'redis://:密码@主机名:端口'
```

启动百度百家号爬虫:
```shell
scrapy crawl author_baidu
```

启动前程无忧职位搜索爬虫:
```shell
scrapy crawl w1job_search
```

运行之后处于浏览器隐身模式，不会出现窗口，需要django后台推送任务，爬虫才能开始工作。

## 0x3、部署运行

安装scrapyd:
```shell
pip install scrapyd
```

安装scrapy-client:
```shell
pip install scrapyd-client
```

Note: scrapy-client已经没人维护了，提交的14个RP都没人合，可能正在走向死亡，这个项目。
具体解决办法：[issues/78](https://github.com/scrapy/scrapyd-client/issues/78).

启动scrapyd:
```shell
scrapyd
```

部署项目:
```shell
scrapyd-deploy
```
注意要在项目根目录下。

运行爬虫:
```shell
curl http://localhost:6800/schedule.json -d project=NEWSCrawler -d spider=w1job_search
curl http://localhost:6800/schedule.json -d project=NEWSCrawler -d spider=author_baidu
```
相关截图：
![](https://github.com/cs246810/NEWScrawler/blob/master/scrapyd_success.gif)

停止爬虫:
```shell
curl http://localhost:6800/cancel.json -d project=NEWSCrawler -d job={job}
```

删除scrapy项目(要先停止):
```shell
curl http://localhost:6800/delproject.json -d project=NEWSCrawler
```
`
获取状态:
```shell
curl http://127.0.0.1:6800/daemonstatus.json
```
获取项目列表:
```shell
curl http://127.0.0.1:6800/listprojects.json
```

获取项目下已发布的爬虫列表:
```shell
curl http://127.0.0.1:6800/listspiders.json?project=NEWSCrawler
```
获取项目下已发布的爬虫版本列表:
```shell
curl http://127.0.0.1:6800/listversions.json?project=NEWSCrawler
```

获取爬虫运行状态:
```shell
curl http://127.0.0.1:6800/listjobs.json?project=NEWSCrawler
```