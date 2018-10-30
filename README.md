# SteamDataMining
云计算实践作业

## Data Collection
主要爬取的是 [SteamDB](https://steamdb.info/) 和 [SteamSpy](https://steamspy.com/api.php) 网站的数据，以及 [steampowered](https://store.steampowered.com/api/appdetails/?filters=basic&appids=570&l=en) api接口  
在爬取 SteamDB 和 SteamSpy 时，这两个网站都设置了防爬机制，需要使用 `Selenium` 和 `PhantomJS` 模拟真实用户使用浏览器，从而获取到加载完成的网页内容，再通过 `Beautiful Soup`抓取相关信息  

- 抓取 SteamSpy 网站的 Steam Top100 游戏的appid  
- 根据 appid 查询 steampowered api，获取游戏的基本信息，包括语言(有些游戏的基本信息 api 存在问题，需记录下这些 appid ，并手动爬取)  
- 根据 appid 抓取 SteamDB 中的user_tags，获取用户标签(steampowered api 中提供了官方的tag，但是不够全面)  
- 根据 appid 和 SteamDB 界面中的 cucurrency ，抓取每个游戏共40个地区的近10个月售价数据  
- 所有的原始数据存入 `MongoDB`


## Streaming
使用了 PySpark Streaming 的 api ，一共两个进程  
- 第一个进程`MongoInputStreaming`: 流数据模拟 负责读取 `MongoDB` 中存储的原始数据，每次读取5条，间隔2s读一次。每次读完后，将数据中的 tags 信息写入到某个被监听的文件夹中  
- 第二个进程`ListenerStreaming`: 流数据处理 每4s查询被监听的文件夹下有没有新文件写入 有的话就进行tag计数处理；计数处理完成后，将当前batch的处理结果写入文件；并统计目前已经处理过的所有batch的tags 将统计结果推送给 echarts 展示  


## Dynamic Representation
使用了 `Flask`+ `Jinja2` 作为 Web端框架  
使用了 `Flask SSE` 作为服务端推送组件，该组件需要依赖 `Redis`  
使用了 `Echarts` 作为图表展示工具  
> gunicorn StreamingDR:app --worker-class gevent --bind 127.0.0.1:8000

------

*动态展示流处理过程*
![](https://upload-images.jianshu.io/upload_images/6164211-3a9c15fd923f8475.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

![](https://upload-images.jianshu.io/upload_images/6164211-3a1eeff15bf7e87b.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
