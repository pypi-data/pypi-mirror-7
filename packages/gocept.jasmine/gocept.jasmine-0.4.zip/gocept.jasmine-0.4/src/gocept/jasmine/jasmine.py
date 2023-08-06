# -*- coding: utf-8 -*-
# Copyright (c) 2013 gocept gmbh & co. kg
# See also LICENSE.txt

import fanstatic
import gocept.httpserverlayer.wsgi
import gocept.jasmine.resource
import gocept.selenium.webdriver
import pdb
import plone.testing
import unittest


class TestApp(object):

    def need_resources(self):
        # Need your fanstatic resources here.
        pass

    @property
    def body(self):
        # Return HTML you need for your tests here.
        return ''

    def __call__(self, environ, start_response):
        start_response('200 OK', [])
        self.need_resources()
        gocept.jasmine.resource.jasmine.need()
        return [
            '<html><head>Jasmine Tests</head><body>{}</body></html>'.format(
                self.body)]


class Layer(plone.testing.Layer):
    "Layer for the jasmine tests."

    def __init__(self, bases=None, name=None, module=None, application=None):
        super(Layer, self).__init__(bases, name, module)
        if application is None:
            raise ValueError('Layer needs a WSGI app to run.')
        self.application = application

    def setUp(self):
        super(Layer, self).setUp()
        self['application'] = self.application
        self['wsgi_app'] = fanstatic.Fanstatic(self['application'])

    def tearDown(self):
        super(Layer, self).tearDown()
        del self['wsgi_app']
        del self['application']


def get_layer(application):
    # in case an KeyError 'selenium' is thrown, check that the class names
    # of your test applications are unique
    prefix = application.__class__.__name__
    wsgi_layer = Layer(application=application, name='{}Layer'.format(prefix))
    server_layer = gocept.httpserverlayer.wsgi.Layer(
        name='{}HTTPServerLayer'.format(prefix), bases=(wsgi_layer,))
    webdriver_layer = gocept.selenium.webdriver.Layer(
        name='{}WebdriverLayer'.format(prefix), bases=(server_layer,))
    layer = gocept.selenium.webdriver.WebdriverSeleneseLayer(
        name='{}JasmineLayer'.format(prefix), bases=(webdriver_layer,))
    return layer


class TestCase(unittest.TestCase,
               gocept.selenium.webdriver.WebdriverSeleneseTestCase):

    layer = NotImplemented
    debug = False

    def run_jasmine(self, url=None):
        if url is None:
            url = '/'
        sel = self.selenium
        sel.open(url)
        if self.debug:
            pdb.set_trace()
        sel.waitForPageToLoad()
        sel.waitForTextPresent('gocept.jasmine.tests.finished')
        summary = sel.getText('css=.bar')
        if 'Failing' in summary:
            message = '\n\n'.join(f.text for f in sel.selenium.
                                  find_elements_by_class_name('messages'))
            self.fail('{}\n##############################\n\n{}'.format(
                summary, message))
