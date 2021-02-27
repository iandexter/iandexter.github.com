#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generates a CV or resume from JSON data using various templates
(LaTeX, plain-text, or HTML).
"""

import os
import re
import sys
import subprocess
import json
import codecs
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from time import localtime, strftime
from collections.abc import Mapping, Set, Sequence
from jinja2 import Environment, FileSystemLoader
import minify_html

__version__ = '0.5'

def objwalk(obj, path = (), memo = None):
    """
    http://code.activestate.com/recipes/577982-recursively-walk-python-objects/
    """

    iteritems = lambda mapping: getattr(mapping, 'iteritems', mapping.items)()

    if memo is None:
        memo  = set()
    iterator = None
    if isinstance(obj, Mapping):
        iterator = iteritems
    elif isinstance(obj, (Sequence, Set)) and not isinstance(obj, str):
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
    """
    http://stackoverflow.com/questions/11501090/iterate-over-nested-lists-and-dictionaries
    """
    regex = re.compile(patt)
    for path, val in objwalk(obj):
        if isinstance(val, str):
            if regex.findall(val):
                new_obj = obj
                for step in path[:-1]:
                    new_obj = new_obj[step]
                new_obj[path[-1]] = regex.sub(repl, val)

def load_json(json_file = None):
    """
    Load the data file.
    """
    try:
        return json.load(codecs.open(json_file, 'r', 'utf-8-sig'))
    except json.decoder.JSONDecodeError:
        print("Error: Invalid JSON")
        sys.exit(1)

def get_keywords(json_data = None):
    """
    Collect and transform the keywords.
    """
    keywords = []
    for keyword in json_data['overview']['skills']:
        keywords.append(keyword['area'].replace(',', ';'))
    for keyword in json_data['overview']['platforms']:
        keywords.append(keyword['platform'])
    for keyword in json_data['overview']['languages']:
        keywords.append(keyword['language'])
    for keyword in json_data['overview']['tools']:
        for tool in keyword["tools"]:
            keywords.append(tool["tool"])
    for keyword in json_data['overview']['interests']:
        keywords.append(keyword)
    keywords = ','.join([ keyword.replace(', ', ',') for keyword in keywords ]).split(',')
    keywords = list(set(keywords))
    keywords.sort()
    keywords = [ keyword.replace(';', ',') for keyword in keywords ]
    return keywords

def render_cv():
    """
    Render the data using the Jinja template.
    """
    cv_renderer = Environment(
        block_start_string='%(',
        block_end_string='%)',
        variable_start_string='%((',
        variable_end_string='%))',
        loader=FileSystemLoader(os.path.abspath('.')))
    return cv_renderer

def parse_args():
    """
    Parse command-line arguments.
    """
    description = (
        "Generates a CV or resume from JSON data using various templates "
        "(LaTeX, plain-text, or HTML)."
    )

    parser = ArgumentParser(description=description,
            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--data', dest='data_file',
            default='cv.json', help='specify JSON data')
    parser.add_argument('-t', '--template', dest='template_file',
        default='cv.tex.j2', help='specify Jinja template')
    parser.add_argument('-o', '--output', dest='output_file',
        default='cv.tex', help='specify output (LaTeX|plain-text|HTML)')
    parser.add_argument('-m', '--minify', action='store_true',
            default=False, help='minify HTML')
    parser.add_argument('-c', '--convert', action='store_true',
            default=False, help='convert TeX to PDF')
    parser.add_argument('-v', '--verbose', action='store_true',
            default=False, help='be more verbose')
    parser.add_argument('-V', '--version', action='version',
            version=f"%(prog)s {__version__}")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    return args

def search_replace(json_data = None, template_file = None):
    """
    Search and replace special characters.
    """
    transform_list = {
        'tex': [
            { '_regex': '\\[([^\\]]+)\\]\\(([^\\)]+)\\)',
              '_sub': r'\\href{\2}{\1}'
            },
            { '_regex': r'\&ntilde;', '_sub': r'{\\~n}' },
            { '_regex': r'\&eacute;', '_sub': r"{\\'e}" },
            { '_regex': r'\&amp;', '_sub': r"{\\&}" },
            { '_regex': r'([\d+])%', '_sub': r'\1\\%' }
        ],
        'txt': [
            { '_regex': '\\[([^\\]]+)\\]\\(([^\\)]+)\\)',
              '_sub': r'\1 <\2>'
            },
            { '_regex': r'\&ntilde;', '_sub': r'n' },
            { '_regex': r'\&eacute;', '_sub': r'e' },
            { '_regex': r'\&amp;', '_sub': r'&' },
        ],
        'html': [
            { '_regex': '\\[([^\\]]+)\\]\\(([^\\)]+)\\)',
              '_sub': r'<a href="\2">\1</a>'
            }
        ]
    }

    for key, val in transform_list.items():
        if key in template_file:
            for text in val:
                transform(json_data, text['_regex'], text['_sub'])

def minify(html_file):
    """
    Minify the HTML file.
    """
    with open(html_file, 'r+') as raw_file:
        html = raw_file.read()
        try:
            minified = minify_html.minify(html, minify_js=True, minify_css=True)
        except SyntaxError as err:
            print(err)
        raw_file.seek(0)
        raw_file.write(minified)
        raw_file.truncate()

def tex2pdf(tex_file):
    """
    Convert TeX to PDF.
    """
    cmd = ['pdflatex', tex_file]
    return subprocess.call(cmd, stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)

def main():
    """
    All the work goes here.
    """
    args = parse_args()

    if not os.path.exists(args.data_file):
        print(f"Cannot open data file {args.data_file}")
        sys.exit(1)

    if not os.path.exists(args.template_file):
        print(f"Cannot open template {args.template_file}")
        sys.exit(1)

    if args.verbose:
        print(f"Loading JSON from {args.data_file}")
    cv_data = load_json(args.data_file)['cv']
    cv_data[u'keywords'] = get_keywords(cv_data)
    cv_data[u'last_update'] = strftime("%-d %B %Y", localtime())

    if args.verbose:
        print("Converting special characters")
    search_replace(cv_data, args.template_file)

    if args.verbose:
        print(f"Rendering using {args.template_file}")
    cv_template = render_cv().get_template(args.template_file)
    with open(args.output_file, 'w') as cv_file:
        cv_file.write(cv_template.render(cv_data))
        if args.verbose:
            print(f"Output file: {args.output_file}")

    if 'html' in args.output_file and args.minify:
        minify(args.output_file)
        if args.verbose:
            print(f"Minified {args.output_file}")
    if 'tex' in args.output_file and args.convert:
        pdf_file = f"{os.path.splitext(args.output_file)[0]}.pdf"
        if not tex2pdf(args.output_file):
            if args.verbose:
                print(f"Converted {args.output_file} to {pdf_file}")
        else:
            print(f"Failed to convert {args.output_file} to {pdf_file}")

if __name__ == '__main__':
    main()
