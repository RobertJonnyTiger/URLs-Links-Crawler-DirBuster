# URLs Links Crawler + DirBuster
A spider to crawl links from webpages recursivley with a dir busting option.
This tool takes a list of starting URLs, crawls them, finds local links recursively and logs them to Crawled Links.log. Also, it has a DirBusting option.

## Example Usage:
  * `python3 spider.py -u http://localhost/`
  * `python3 spider.py --urls urls_list`

  **If you want to use the dir busting option:**

  * Give the code a directories wordlist to work with like so:
    * `python3 spider.py -u http://localhost/ -b directory-list.txt`

  **Setting recusrsion level (how deep the sipder will crawl links)**

  * By default, recurse level is set to 5 (5 links to crawl from every page) To change that, all you have to do is use the flag `-r` or `--recurse` followed by an `int`.

  * *Example:*
    * `python3 -u http://localhost/ -r 42`

## Requirements:
1. Python3
2. BeautifulSoup

## Credits:
 The skeleton for the class `CrawlerClass` | Frankie @ https://github.com/f-prime
