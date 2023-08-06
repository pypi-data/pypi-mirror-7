# -*- coding: utf-8 -*-
"""Django page CMS selemium test module"""
import django

from django.conf import settings
from pages.models import Page, Content
from pages.tests.testcase import TestCase
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase

from selenium import webdriver
from selenium.webdriver import PhantomJS

class SeleniumTestCase(TestCase, LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.PhantomJS()
        client = self.get_admin_client()

        admin_url = '%s%s' % (self.live_server_url, reverse('admin:index'))
        response = client.get(admin_url)
        session_id = response.client.cookies[settings.SESSION_COOKIE_NAME].value

        self.browser.get(admin_url)
        self.browser.implicitly_wait(1)
        self.browser.add_cookie({'name': settings.SESSION_COOKIE_NAME, 
            'value': session_id})

        super(SeleniumTestCase, self).setUp()

    def select_option(self, select, option_id):
        for option in select.find_elements_by_tag_name('option'):
            if option.get_attribute('value') == str(option_id):
                option.click()

    def tearDown(self):
        self.browser.quit()
        super(SeleniumTestCase, self).tearDown()

    def url_change(self, id):
        return '%s%s' % (self.live_server_url,
            reverse('admin:pages_page_change',  args=[id]))

    def test_admin_select(self):
        page = self.new_page()
        self.browser.get(self.url_change(page.id))
        status = self.browser.find_element_by_id('id_status')
        self.assertEqual(status.get_attribute('value'), str(page.status))

        self.select_option(status, str(Page.DRAFT))
        self.assertEqual(status.get_attribute('value'), str(Page.DRAFT))

        src = self.browser.find_element_by_css_selector('.status'
            ).find_element_by_tag_name('img'
            ).get_attribute('src')

        self.assertTrue(src.endswith('draft.gif'))
