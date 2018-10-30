# SteamDataMining
云计算实践作业

## DataCollection
主要爬取的是 [SteamDB](https://steamdb.info/) 和 [SteamSpy](https://steamspy.com/api.php) 网站的数据，以及 [steampowered](https://store.steampowered.com/api/appdetails/?filters=basic&appids=570&l=en) api接口  
在爬取 SteamDB 和 SteamSpy 时，这两个网站都设置了防爬机制，需要使用 `Selenium` 和 `PhantomJS` 模拟真实用户使用浏览器，从而获取到加载完成的网页内容，再通过 `Beautiful Soup`抓取相关信息  




## Streaming

## Dynamic Representation
