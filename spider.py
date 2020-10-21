#!/usr/bin/python3
"""
== URLs Links Crawler. ==
    Author: Robert Tiger
    Date: Oct', 2020

== Description: ==
    This tool takes a list of starting URLs, crawls in them, finds local links recursively and logs them to Crawled Links.log. Also, it has DirBusting option.

== Usage: ==
        python3 <script name> [OPTIONS]

== Credits: ==
    The skeleton for the class CrawlerClass Frankie @ https://github.com/f-prime
"""
import argparse
import os
import re
from typing import List

import requests
import sys
import datetime
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from core.colors import *

# Defines Parser:
parser = argparse.ArgumentParser(description = 'Crawls given URLs, extracts links to a specific recursion '
                                               'depth and busting directories (DirBuster)')

# Arguments to be parsed:
parser.add_argument('-u', '--url',       help = 'Target URL. Example: http://domain.com/', dest = 'url')
parser.add_argument('--urls',            help = 'List file containing target URLs.',       dest = 'url_file')
parser.add_argument('-r', '--recursion', help = 'Maximum recursion level depth to crawl. (Default: 5)',
                    default = 5,                                                           dest = 'max_links')
parser.add_argument('-b', '--buster',    help = 'Activates the DirBuster class and parsing the wordlist for the '
                                             'DirBuster.', dest = 'buster_wordlist')
parser.add_argument('-o', '--output',    help = 'Path for the output file (No need to type extension. Saving '
                                              'as JSON file. '
                                 'Default: dirs_out.json)', dest = 'output_path', default = 'dirs_out.json')

args = parser.parse_args()
url             = args.url
url_file        = args.url_file
recurse_level   = args.max_links
buster_wordlist = args.buster_wordlist
output_path     = args.output_path


class CrawlerClass(object):
    """Responsible of handling the args: URLs_list and max_links and also provides the crawler with
    the User-Agent. + Removes empty lines from URLs list."""
    def __init__(self, URLs_list, max_links: int):
        self.starting_URLs                               = URLs_list
        for URL in self.starting_URLs:
            if len(URL) <= 0: self.starting_URLs.remove(URL)  # Removes empty lines from URL list.
        self.visited_links                               = set()
        self.user_agent                                  = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
        self.max_links                                   = max_links


    def get_html(self, url: str) -> str:
        """Called from get_links()
    Requests the HTML from <URL> using the self.user_agent
    returns "" if no connection established.
    returns the HTML content."""
        try:
            html  = requests.get(url, headers = {"User-Agent": self.user_agent})
        except Exception as e:
            print(e)
            return ""
        return html.content.decode('latin-1')
    
    
    def get_links(self, URL: str) -> list:
        """Called from crawl()
    Calls the get_html function with a URL, sets the parsed base netloc to a variable.
    returns a list with all the local links within the page from <URL> with the amount of <max_links>"""
        html          = self.get_html(URL)
        parsed        = urlparse(URL)
        local_base    = f"{parsed.scheme}://{parsed.netloc}"
        fetched_links = re.findall('<a\s+(?:[^>]*?\s+)?href="([^"]*)"', html)
        for link in re.findall('<img\s+(?:[^>]*?\s+)?src="([^"]*)"', html):
            fetched_links.append(link)
        links_with_base = []
        local_links     = []
        for link in fetched_links:
            if not urlparse(link).netloc:
                links_with_base.append(local_base + link)
            else:
                links_with_base.append(link)

        for link in links_with_base:
            if urlparse(link).netloc in local_base:
                local_links.append(link)
        maximum_links_to_crawl = local_links[:int(self.max_links)]
        return maximum_links_to_crawl


    def extract_info(self, link: str) -> dict:
        """When called from crawl(), extracts meta information of a link.
    Returns dict with name of meta and the content. {name: 'ZYX', content: 'XYZ'}"""
        html = self.get_html(link)
        meta = re.findall("<meta .*?name=[\"'](.*?)['\"].*?content=[\"'](.*?)['\"].*?>", html)
        return dict(meta)


    def start(self):
        """Starts the process of crawling. Starts from getting the full starting_URLs list.
    Gets URLs from self.starting_URLs. For every URL in the list, call to self.crawl(URL) with the current
    URL in the loop. Also, responsible of creating the Crawled Links.log log file.
    For every starting_URL, Calls to crawl() with the URL in the list."""
        for URL in self.starting_URLs:
            print(f"{run} Now Crawling: {URL}")
            with open('Crawled Links.log', 'a+') as log:
                log.write(f'{separator}' + '[{:%d/%m/%Y, %H:%M:%S}]'.format(
                    datetime.datetime.now()) + f'\nCrawled Starting URL: {URL} \n{separator}')
            self.crawl(URL)
            print(f"{good} Crawled: {URL}\n --> Check output in '{underline}Crawled Links.log{end}'\n")


    def crawl(self, URL: str):
        """Gets a URL from, calls to self.get_links() with the URL provided.
    For every link it got from get_links() passes the ones that were visited.
    Logs links and Meta Description to Crawled Links.log.
    Calls to itself again until self.get_links() list gets exhausted."""
        for link in self.get_links(URL):
            if link in self.visited_links:
                continue
            self.visited_links.add(link)
            info = self.extract_info(link)
            with open('Crawled Links.log', 'a+') as log:
                log.write(
                    f"""{tab}Link: {link}
{tab}Meta Description: {info.get('description')}\n\n""")
            self.crawl(link)


def URLs_list_maker(URLs_list_path: str) -> list:
    """Provided a file with URLs to crawl.
Prints the URLs list to CLI.
Returns a list of starting_urls to crawl from a file."""
    Starting_URLs_list = []
    with open(URLs_list_path, 'r+') as file:
        for line in file.readlines():
            Starting_URLs_list.append(line.strip())
    print(f"{run} {bold}{underline}URLs in queue:{end}")
    for URL in Starting_URLs_list:
        if len(URL) <= 1: Starting_URLs_list.remove(URL)
    Starting_URLs_list = [x for x in Starting_URLs_list if not x.startswith('#')]
    for i, URL in enumerate(Starting_URLs_list):
        print(f'{tab}{bold}{i+1}.{end} {URL}')
    print('')
    return Starting_URLs_list
def buster_list_maker(wordlist: str) -> list:
    """Creates a list of dirs_list from dirs_list"""
    dirs_list = []
    with open(wordlist, 'r+') as file:
        for line in file.readlines():
            dirs_list.append(line.strip())
        dirs_list = [x for x in dirs_list if not x.startswith('#')]
        return dirs_list


class DirBuster(object):
    def __init__(self, starting_urls: list, dirs: list):
        """From starting_urls list defines starting_URLs dirs list for the class"""
        self.starting_URLs = starting_urls
        self.dirs = dirs


    def start_buster(self) -> dict:
        """Builds the final_results dict. Sets every url as key in the dictionary and gets the value from
        final method. Returns final_results dict (Will be used in output method)"""
        final_results = {}
        global url
        if url:
            print(f"\n{run} {underline}Dir Busting{end}: {url}")
            final_results[url] = []
            try:
                final_results[url] = self.final(url)
                if final_results[url]:
                    print(f"\n%s Directories for: %s{url}%s:" % (run, bold, end))
                    for result in final_results[url]:
                        print(tab + info + ' ' + green + result + end)
                else:
                    print(f"{tab}%s Couldn't find any hidden directories." % bad)
            except ConnectionError as e:
                exit(f'%s%s Target encountered connection error:%s\n{e}' % (bad, red, end))
        elif url_file:
            for url in self.starting_URLs:
                print(f"\n{run} {underline}Dir Busting{end}: {url}")
                final_results[url] = []
                try:
                    final_results[url] = self.final(url)
                    if final_results[url]:
                        print(f"\n%s Directories for: %s{url}%s:" % (run, bold, end))
                        for result in final_results[url]:
                            print(tab + info + ' ' + green + result + end)
                    else:
                        print(f"{tab}%s Couldn't find any directories." % bad)
                except ConnectionError as e:
                    exit(f'%s%s Target encountered connection error:%s\n{e}' % (bad, red, end))
                    print(f'%s Passing on: {url}...' % info)
                    pass
        return final_results
        
    @staticmethod
    def final(URL) -> list:
        """Tries to get an ok response from the url with each of the dirs from the list.
        When succeeded, prints dir and saves result to list.
        Finally, returns list of found dirs."""
        found_dirs = []
        for word in dirs:
            r = requests.get(f'{URL}{word}')
            status = r.status_code
            if status < 310:
                print(f"{tab}{good} Found directory: {green}{bold}{word}{end}")
                found_dirs.append(URL + word)
        return found_dirs

    def output(self):
        """Finally, dumps final_results dict to JSON file."""
        global output_path
        final_results = self.start_buster()
        print(f'\n{run} Finished! Dumping results to JSON file...')
        if ".json" in output_path:
            with open(str(output_path), 'w', encoding = "utf8") as json_output:
                json.dump(final_results, json_output, sort_keys = True, indent = 4)
            print(f'%s Final results saved to JSON file at: %s{output_path}%s' % (good, bold, end))
        else:
            output_path = output_path + '.json'
            self.output()
    

if __name__ == "__main__":
    if not url and not url_file:
        exit('%s%s%s Please specify URL (-u) or URLs list file (--urls).%s' % (bad, red, bold, end))
    if os.path.exists('Crawled Links.log'):
        answer = input("%s Detected %s'Crawled Links.log'%s in this directory.\n"
                       "Would you like to remove this file and start over? [Yes/No]\n"
                       "%sAnswering no will append this scan result to the existing one: %s" % (info,
                                                                                             underline,
                                                                                                end, bold,
                                                                                                end))
        if answer.lower() == "yes" or "y" in answer.lower()[0]: os.remove('Crawled Links.log')
        else: pass
    if url_file:
        print(f"{run} {bold}Started: {underline}Crawler{end}...")
        print(f"%s Recursion level set to: %s{recurse_level}%s (Change with -r, --recursion. Default: 5)\n" %
              (info, bold, end))
        Starting_URLs = URLs_list_maker(url_file)  # Returns a list of starting_urls to crawl from a
        # file.
        crawler = CrawlerClass(Starting_URLs, recurse_level)  # Defines class with starting_urls and max_links to
        crawler.start()
    if url:
        print(f"{run} {bold}Started: {underline}Crawler{end}...")
        print(f"%s Recursion level set to: %s{recurse_level}%s\n%s(Change with -r, --recursion. (Default: "
              f"5)\n" %
              (info, bold, end, tab))
        Starting_URL = list()
        Starting_URL.append(url)
        crawler = CrawlerClass(Starting_URL, recurse_level)
        crawler.start()
    if buster_wordlist:
        print(f"{run} {bold}Started: {underline}DirBuster{end}...")
        dirs = buster_list_maker(buster_wordlist)
        if url_file:
            Starting_URLs = URLs_list_maker(url_file)
            buster = DirBuster(Starting_URLs, dirs)
        if url:
            Starting_URL = list()
            Starting_URL.append(url)
            buster = DirBuster(Starting_URL, dirs)
        # noinspection PyUnboundLocalVariable
        buster.output()
