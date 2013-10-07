#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generates a CV or resume from JSON data using various templates
(LaTeX, plain-text, or HTML).
"""

import json
import codecs
import jinja2
import os
import re
import sys
from optparse import OptionParser
from time import localtime, strftime

__version__ = '0.3'

def objwalk(obj, path = (), memo = None):
    """From http://code.activestate.com/recipes/577982-recursively-walk-python-objects/"""
    from collections import Mapping, Set, Sequence

    string_types = (str, unicode) if str is bytes else (str, bytes)
    iteritems = lambda mapping: getattr(mapping, 'iteritems', mapping.items)()

    if memo is None:
        memo  = set()
    iterator = None
    if isinstance(obj, Mapping):
        iterator = iteritems
    elif isinstance(obj, (Sequence, Set)) and not isinstance(obj, string_types):
        iterator = enumerate
    if iterator:
        if id(obj) not in memo:
            memo.add(id(obj))
            for path_component, value in iterator(obj):
                for result in objwalk(value, path + (path_component,), memo):
                    yield result
            memo.remove(id(obj))
    else:
        yield path, obj

def transform(obj, patt, repl):
    """From http://stackoverflow.com/questions/11501090/iterate-over-nested-lists-and-dictionaries"""
    regex = re.compile(patt)
    for p, v in objwalk(obj):
        if isinstance(v, basestring):
            if regex.findall(v):
                new_obj = obj
                for s in p[:-1]:
                    new_obj = new_obj[s]
                new_obj[p[-1]] = regex.sub(repl, v)

def load_json(json_file = None):
    return json.load(codecs.open(json_file, 'r', 'utf-8-sig'))

def get_keywords(json_data = None):
    keywords = []
    for k in json_data['overview']['skills']:
        keywords.append(k['area'].replace(',', ';'))
    for k in json_data['overview']['platforms']:
        keywords.append(k['platform'])
    for k in json_data['overview']['languages']:
        keywords.append(k['language'])
    for k in json_data['overview']['tools']:
        for t in k["tools"]:
            keywords.append(t["tool"])
    for k in json_data['overview']['interests']:
        keywords.append(k)
    keywords = ','.join([ k.replace(', ', ',') for k in keywords ]).split(',')
    keywords = list(set(keywords))
    keywords.sort()
    keywords = [ k.replace(';', ',') for k in keywords ]
    return keywords

def render_cv():
    cv_renderer = jinja2.Environment(
        block_start_string = '%(',
        block_end_string = '%)',
        variable_start_string = '%((',
        variable_end_string = '%))',
        loader = jinja2.FileSystemLoader(os.path.abspath('.')))
    return cv_renderer

def parse_opts():
    usage = """
    Generates a CV or resume from JSON data using various templates
    (LaTeX, plain-text, or HTML).

    %s [options]
    """ % sys.argv[0]

    parser = OptionParser(usage=usage,
        version="%s %s" % (sys.argv[0], __version__))
    parser.add_option('-d', '--data', dest='data_file',
        default='cv.json', help='JSON data file')
    parser.add_option('-t', '--template', dest='template_file',
        default='cv.tex.j2', help='Template file (LaTeX|plain-text|HTML)')
    parser.add_option('-o', '--output', dest='output_file',
        default='cv.tex', help='Output file (LaTeX|plain-text|HTML)')
    parser.add_option('-v', '--verbose', action="store_true",
        default=False, help='Be more verbose')

    (opts, args) = parser.parse_args()
    return (opts, args)

def main():
    (opts, args) = parse_opts()

    if not os.path.exists(opts.data_file):
        print "Cannot open data file %s" % opts.data_file
        sys.exit(1)

    if not os.path.exists(opts.template_file):
        print "Cannot open template %s" % opts.template_file
        sys.exit(1)

    if opts.verbose:
        print "Loading JSON from %s" % opts.data_file
    cv_data = load_json(opts.data_file)['cv']
    cv_data[u'keywords'] = get_keywords(cv_data)
    cv_data[u'last_update'] = strftime("%-d %b %Y", localtime())

    link_marker = '\\[([^\\]]+)\\]\\(([^\\)]+)\\)'
    if '.tex.' in opts.template_file:
        if opts.verbose:
            print "Converting LaTeX \href links"
        link_sub = r'\\href{\2}{\1}'
        transform(cv_data, link_marker, link_sub)
    if '.txt.' in opts.template_file:
        if opts.verbose:
            print "Converting to plaintext links"
        link_sub = r'\1 <\2>'
        transform(cv_data, link_marker, link_sub)

    if opts.verbose:
        print "Rendering using %s" % opts.template_file
    cv_template = render_cv().get_template(opts.template_file)
    with open(opts.output_file, 'w') as cv:
        cv.write(cv_template.render(cv_data))
    if opts.verbose:
        print "Output file: %s" % opts.output_file

if __name__ == '__main__':
    main()
