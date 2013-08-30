#!/usr/bin/env python26
# -*- coding: utf-8 -*-

"""
Filename:         buildr.py
Author:           im4
HeadURL:          $HeadURL: https://svn.asiandevbank.org/ccau-unix/sysadmin/im4/bin/python.inc $
Last revised by:  $Author: im4 $
Last commit:      $Revision: 4481 $
Last commit date: $Date: 2013-02-28 15:08:58 +0800 (Thu, 28 Feb 2013) $
Description:      Generates resume from JSON data using Jinja2 templates.
"""

import json
import codecs
import jinja2
import os

__version__ = '0.1'

def load_json(json_file = None):
    return json.load(codecs.open(json_file, 'r', 'utf-8-sig'))

def get_keywords(json_data = None):
    keywords = []
    for k in json_data['overview']['skills']:
        keywords.append(k['area'])
    for k in json_data['overview']['platforms']:
        keywords.append(k['platform'])
    for k in json_data['overview']['languages']:
        keywords.append(k['language'])
    return keywords

def render_resume():
    resume_renderer = jinja2.Environment(
        block_start_string = '%(',
        block_end_string = '%)',
        variable_start_string = '%((',
        variable_end_string = '%))',
        loader = jinja2.FileSystemLoader(os.path.abspath('.')))
    return resume_renderer

if __name__ == '__main__':
    JSON_FILE = 'resume-iandexter.json'
    EXT = 'tex'
    TEMPLATE = "resume.%s.j2" % EXT
    OUTPUT = 'resume-iandexter.%s' % EXT

    resume_data = load_json(JSON_FILE)['resume']
    resume_data[u'keywords'] = get_keywords(resume_data)

    resume_template = render_resume().get_template(TEMPLATE)
    with open(OUTPUT, 'w') as resume:
        resume.write(resume_template.render(resume_data))
