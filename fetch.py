#!/usr/local/bin/python3

from notion.client import NotionClient
from notion.block import SubheaderBlock, BulletedListBlock
from dotenv import load_dotenv
from jinja2 import Template
from datetime import datetime

import sh
import hashlib
import mistune
import mimetypes

load_dotenv()

import os, re, json

client = NotionClient(
    token_v2=os.getenv("NOTION_TOKEN")
)

doomsday = client.get_block(
    "https://www.notion.so/Doomsday-Tracker-18652816d3dc4ed3a643365b4e274b91"
)
last_edited_time = doomsday.get('last_edited_time')
ts = datetime.fromtimestamp(last_edited_time / 1000)
arr = []

curr_about = ''

for block in doomsday.children:

    try:
        dict_to_push = {}

        if (isinstance(block, SubheaderBlock)):
            curr_about = block.title

        if (isinstance(block, BulletedListBlock)):
            _text = block.title
            
            year = re.search('^\[(.*?)\]', _text)
            link = re.search('\[Link\]\((.*?)\)', _text)
            headline = re.search('^\[.*?\](.*?)\(.*\)', _text)

            mime = mimetypes.guess_type(link.group(1))[0] or ''

            if ('image' in mime or 'pdf' in mime):
                _hash = hashlib.md5(link.group(1).encode()).hexdigest()

                ext = link.group(1).split('.')[-1]
                sh.wget("-O", "assets/sources/%s.%s" % (_hash, ext), link.group(1))
                
                dict_to_push['link'] = "assets/sources/%s.%s" % (_hash, ext)
            else:
                dict_to_push['link'] = link.group(1)

            dict_to_push['year'] = year.group(1)
            dict_to_push['headline'] = mistune.html(headline.group(1)).replace("<p>", "").replace("</p>", "")
            dict_to_push['about_year'] = curr_about
            dict_to_push['status'] = 'Failed'

            for _block in block.children:
                groups = re.search('^(.*?)\:(.*?)(\|(.*))?$', _block.title).groups()

                if (groups[0] == "Category"):
                    dict_to_push['category'] = groups[1].strip()

                if (groups[0] == "Status"):
                    dict_to_push['status'] = groups[1].strip()

                    if groups[2]:
                        dict_to_push['status_comment'] = groups[3].strip()
            
            arr.append(dict_to_push)
    except:
        print(block)
        raise("fuck you")

with open("root.html", "r") as f:
    html = f.read()
    tmpl = Template(html)

with open("index.html", "w") as f:
    f.write(tmpl.render(items=arr, last_modified=ts.strftime("%b %d, %Y")))


sh.jq(sh.purgecss([
    "--css",
    "assets/tailwind.css",
    "--content",
    "index.html"
]), "-r", ".[].css", _out="assets/build.css")

    


