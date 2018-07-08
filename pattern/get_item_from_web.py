#!/usr/bin/python
# -*- coding: UTF-8 -*-

import urllib2
import requests
from bs4 import BeautifulSoup
import os
import sys
import shutil


import time

web_link = 'https://images.garnstudio.com'
pattern_prefix = 'https://www.garnstudio.com/includes'

def change_to_string(string):
    if isinstance(string, unicode):
        return string.encode('utf8')
    return string


def change_to_unicode(uni_string):
    if isinstance(uni_string, str):
        return uni_string.decode('utf8')
    return uni_string


def download_file(file_name, download_url, mytype = 'pdf'):
    response = urllib2.urlopen(download_url)
    file = open(file_name + "." + mytype, 'wb')
    file.write(response.read())
    file.close()

def get_url_from_page(page_url):
    page = requests.get(page_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    contents = soup.prettify()
    lines = [line.strip() for line in contents.split(u'\n')]
    links = [line for line in lines if line.startswith(u'<a href="/pattern')]
    urls = [link.split(' ')[1] for link in links]

    purls = []
    for url in urls:
        url = change_to_string(url)[6:-1]
        tmp = url.split('.')
        purl = tmp[0] + '-print.' + tmp[1]
        purl = purl.replace('amp;', '')
        purl = pattern_prefix + purl
        purls.append(purl)

    return purls


def get_pattern_url(link_path):
    with open(link_path,'rb') as the_file:
        page_urls = the_file.readlines()
    urls = []
    for page_url in page_urls:
        urls += get_url_from_page(page_url)
    return urls

def get_pattern_code(url):
    start = url.index('=') + 1
    end = url.index('&')
    return url[start:end]

def get_item_from_url(url):
    # url = "https://www.garnstudio.com/includes/pattern-print.php?id=7729&cid=8"
    # url = 'https://www.garnstudio.com/includes/pattern-print.php?id=1998&cid=19'
    # url = 'https://www.garnstudio.com/includes/pattern-print.php?id=8347&cid=19'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    # Save text
    text = soup.find_all('p')
    pattern_code = get_pattern_code(url)
    file_name = pattern_code + '.txt'
    with open(file_name, 'wb') as the_file:
        for t in text:
            the_file.write(change_to_string(t.get_text()))
    the_file.close()

    # Save images
    contents = soup.prettify()
    lines = [line.strip() for line in contents.split(u'\n')]
    links = [line for line in lines if line.startswith(u'<img') and u'mag' in line]
    img_links = [link.split(u'src=')[1].split(u'"')[1] for link in links]

    for i, link in enumerate(img_links):
        url = web_link + str(link)
        file_name = pattern_code + '-' + str(i)
        download_file(file_name, url, mytype='jpg')

#####################################################
# Get pattern links and save to links to a txt file ##########
# Run this only one time and then it should be commented out #
##############################################################
def get_and_write_pattern_url():
    # knit_child.txt is the file with web urls
    link_path = 'links/knit_child.txt'
    urls = get_pattern_url(link_path)
    with open('links/kc_pattern_links.txt','wb') as the_file:
        for url in urls:
            the_file.write('%s\n' % change_to_string(url))
    print('Completed getting all pattern urls')
#############################################################
def get_item_from_web():
    with open('links/kc_pattern_links.txt','rb') as the_file:
        lines = the_file.readlines()
        urls = [line.strip() for line in lines]
    for i,url in enumerate(urls):
        if i%50 == 0:
            print(i)
        get_item_from_url(url)
        # time.sleep(2)

#############################################################
# Filter pattern
def is_sweater(text_file):
    with open(text_file, 'rb') as the_file:
        mytext = the_file.read()
    not_sweater_words = ['HAT', 'MITTENS', 'SCARF', 'JUMPER', 'SOCK', 'SLIPPER', 'HEAD BAND', 'LEG', 'TIGHTS', 'COWL',
                         'THUMB', 'PONCHO', 'BLANKET', 'MITTEN', 'BERET', 'HEAD BAND', 'NECK WARMER', 'PANTS',
                         'LEG WARMER', 'TROUSERS', 'bootie']
    for word in not_sweater_words:
        if word in mytext:
            return 0
    return 1

def get_filenames(extension='txt'):
    path = os.path.dirname(os.path.realpath('__file__'))
    files = os.listdir(path)
    file_names = [i for i in files if i.endswith(extension)]
    return file_names


def get_sweater_pattern_names():
    files_txt = get_filenames()
    sweater_pattern_names = []

    for file_txt in files_txt:
        if is_sweater(file_txt):
            sweater_pattern_names.append(file_txt.split('.')[0])
    return sweater_pattern_names

def find_files_with_name(name):
    path = os.path.dirname(os.path.realpath('__file__'))
    files = os.listdir(path)
    file_names = []
    for file in files:
        file_name = file.split('.')[0]
        code = file_name.split('-')[0]
        if code == name:
            file_names.append(file)
    return file_names

def move_sweater_patterns_to_folder():
    sweater_pattern_names = get_sweater_pattern_names()
    for name in sweater_pattern_names:
        files = find_files_with_name(name)
        target = 'sweater/'
        for file in files:
            try:
                shutil.move(file, target)
            except IOError as e:
                print("Unable to copy file. %s" % e)
            except:
                print("Unexpected error:", sys.exc_info())

##############################################################

