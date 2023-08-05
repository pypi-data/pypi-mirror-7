# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Intuition analysis module
  -------------------------

  Provides high level building blocks to extract insights from various datasets

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

import os
import shutil
import rpy2.robjects as robjects
import dna.logging

log = dna.logging.logger(__name__)


class Stocks(object):
    ''' Produce R report of stocks opportunities '''
    knitr_report = '~/.intuition/assets/report.rnw'

    def __init__(self, report_template=None):
        log.info('loading R context')
        self.r = robjects.r
        self.report_template = report_template \
            or os.path.expanduser(self.knitr_report)
        self.r('require("knitr")')

    def clean(self, everything=False):
        log.debug('cleaning garbage')
        unwanted = ['aux', 'log', 'out', 'tex']
        if everything:
            unwanted.append('pdf')
        unwanted = map(lambda x: 'report.{}'.format(x), unwanted)
        for filename in unwanted:
            if os.path.exists(filename):
                log.debug('deleting {}'.format(filename))
                os.remove(filename)

        if os.path.exists('figure'):
            shutil.rmtree('figure')

    def process(self):
        log.info('processing report')
        self.r('knit2pdf("{}")'.format(self.report_template))
