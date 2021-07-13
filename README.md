# NEWSCrawler

这是我为自己搭建的资讯平台管理中心项目的爬虫，基于scrapy, scrapy-redis和 scrapy-selenium这3个库
来做爬虫的快速开发。业务流程是，我在django后台推送爬虫任务到redis然后scrapy-redis从队列中获取任务，
并解析出url和相关的关系数据，scrapy相关再进行爬取数据，然后再推送到存储item的队列中，最后我再使用脚本
将item队列中的数据取出来，然后再通过django的RESTfull API将数据post到数据库中。

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