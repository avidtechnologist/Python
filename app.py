#!/bin/env python

import argparse
import inspect
import os
import urllib2
import ConfigParser
from datetime import datetime

########## utility function
def parse_interval(interval):
    if isinstance(interval, int):
        return interval

    unit = 1
    if interval.endswith('s'):
        pass
    elif interval.endswith('m'):
        unit *= 60
    elif interval.endswith('h'):
        unit *= 60 * 60
    elif interval.endswith('d'):
        unit *= 60 * 60 * 24
    else:
        pass

    val = int(interval.rstrip('smhd')) * unit
    return val
####################

def get_conf_file():
    """Get app config file.

    Returns:
        App config file path.
    """
    file_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    default_conf_path = os.path.join(file_dir, 'app.conf')

    parser = argparse.ArgumentParser(description='SocialMention program')
    parser.add_argument('--conf', default=default_conf_path, help="program config file")
    args = parser.parse_args()
    conf_path = args.conf
    return conf_path

def parse_conf_file(file_path):
    """Parse config file based on ``file_path``.

    Arguments:
    - `file_path`:

    Returns:
        A dict contains all the config values.
    """
    config = ConfigParser.ConfigParser()
    config.read(file_path)

    config_dict = {}
    from_ts_str = config.get('GENERAL', 'from_ts')
    config_dict['from_ts'] = parse_interval(from_ts_str)
    config_dict['output_file_dir'] = config.get('GENERAL', 'output_file_dir')

    query = config.get('SEARCH ARGS', 'q', '')
    query_list = []
    for e in query.split(','):
        query_list.append(e.strip())
    config_dict['query_list'] = query_list
    config_dict['type'] = config.get('SEARCH ARGS', 't', '')
    config_dict['format'] = config.get('SEARCH ARGS', 'f', 'csv')
    config_dict['lang'] = config.get('SEARCH ARGS', 'lang', 'en')
    config_dict['key'] = config.get('SEARCH ARGS', 'key', '')

    return config_dict

def build_search_url(conf_dict, url_base):
    """Build a search url base on the config value.

    Arguments:
    - `url_base`: Socialmention search api url base, *Must* ends with '?'.
    - `conf_dict`:

    Returns:
        A search url.
    """
    query_list = conf_dict['query_list']
    if query_list:
        if len(query_list) > 1:
            url_base += 'q=%s' % query_list[0]
            for e in query_list[1:]:
                url_base += '&q=%s' % e
        elif len(query_list) == 1:
            url_base += 'q=%s' % query_list[0]
        else:
            pass

    type = conf_dict['type']
    if type:
        url_base += '&t=%s' % type

    format = conf_dict['format']
    if format:
        url_base += '&f=%s' % format

    lang = conf_dict['lang']
    if lang:
        url_base += '&lang=%s' % lang

    key = conf_dict['key']
    if key:
        url_base += '&key=%s' % key

    from_ts = conf_dict['from_ts']
    if from_ts > 0:
        url_base += '&from_ts=%d' % from_ts

    return url_base

def do_search_and_save_to_file(search_url, output_file):
    """Send search request and save result to ``output_file``.

    Arguments:
    - `search_url`:
    - `output_file`:
    """
    req = urllib2.Request(search_url)
    res = urllib2.urlopen(req)
    the_page = res.read()
    with open(output_file, "a") as f:
        f.write(the_page)
        print "Save search result to file: %s" % output_file

def main():
    """Main logic of the program.
    """
    conf_path = get_conf_file()
    conf_dict = parse_conf_file(conf_path)
    url_base = 'http://api2.socialmention.com/search?'
    search_url = build_search_url(conf_dict, url_base)

    format = conf_dict['format']
    output_file_dir = conf_dict['output_file_dir']
    query_list = conf_dict['query_list']
    for q in query_list:
        now = datetime.now()
        file_name = '%s_%s_%s.%s' % (q, now.strftime("%Y%m%d"),
                                     now.strftime("%H%M%S"), format)
        output_file = os.path.join(output_file_dir, file_name)
        do_search_and_save_to_file(search_url, output_file)

if __name__ == "__main__":
    main()
