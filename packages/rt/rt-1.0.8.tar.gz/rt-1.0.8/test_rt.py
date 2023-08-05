"""Tests for Rt - Python interface to Request Tracker :term:`API`"""

__license__ = """ Copyright (C) 2013 CZ.NIC, z.s.p.o.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
__docformat__ = "reStructuredText en"
__authors__ = [
  '"Jiri Machalek" <jiri.machalek@nic.cz>'
]

import unittest
import random
import string

from six import iteritems
from six.moves import range

import rt

class RtTestCase(unittest.TestCase):

    RT_VALID_CREDENTIALS = {
        'RT3.8 stable': {
            'url': 'http://rt.easter-eggs.org/demos/3.8/REST/1.0',
            'admin': {
                'default_login': 'admin',
                'default_password': 'admin',
            },
            'john.foo': {
                'default_login': 'john.foo',
                'default_password': 'john.foo',
            }
        },
        'RT4.0 stable': {
            'url': 'http://rt.easter-eggs.org/demos/4.0/REST/1.0',
            'admin': {
                'default_login': 'admin',
                'default_password': 'admin',
            },
            'john.foo': {
                'default_login': 'john.foo',
                'default_password': 'john.foo',
            }
        },
    }

    RT_INVALID_CREDENTIALS = {
        'RT3.8 stable (bad credentials)': {
            'url': 'http://rt.easter-eggs.org/demos/3.8/REST/1.0',
            'default_login': 'idontexist',
            'default_password': 'idonthavepassword',
        },
    }

    RT_MISSING_CREDENTIALS = {
        'RT4.0 stable (missing credentials)': {
            'url': 'http://rt.easter-eggs.org/demos/4.0/REST/1.0',
        },
    }

    RT_BAD_URL = {
        'RT (bad url)': {
            'url': 'http://httpbin.org/status/404',
            'default_login': 'idontexist',
            'default_password': 'idonthavepassword',
        },
    }

    def test_login_and_logout(self):
        for name in self.RT_VALID_CREDENTIALS:
            tracker = rt.Rt(self.RT_VALID_CREDENTIALS[name]['url'], **self.RT_VALID_CREDENTIALS[name]['john.foo'])
            self.assertTrue(tracker.login(), 'Invalid login to RT demo site ' + name)
            self.assertTrue(tracker.logout(), 'Invalid logout from RT demo site ' + name)
        for name, params in iteritems(self.RT_INVALID_CREDENTIALS):
            tracker = rt.Rt(**params)
            self.assertFalse(tracker.login(), 'Login to RT demo site ' + name + ' should fail but did not')
            self.assertRaises(rt.AuthorizationError, lambda: tracker.search())
        for name, params in iteritems(self.RT_MISSING_CREDENTIALS):
            tracker = rt.Rt(**params)
            self.assertRaises(rt.AuthorizationError, lambda: tracker.login())
        for name, params in iteritems(self.RT_BAD_URL):
            tracker = rt.Rt(**params)
            self.assertRaises(rt.UnexpectedResponse, lambda: tracker.login())

    def check_or_create_queue(self, name):
        tracker = rt.Rt(self.RT_VALID_CREDENTIALS[name]['url'], **self.RT_VALID_CREDENTIALS[name]['admin'])
        tracker.login()
        queue = tracker.get_queue('General')
        if 'Name' not in queue:
            queue_id = tracker.create_queue('General')
        tracker.logout()

    def test_ticket_operations(self):
        ticket_subject = 'Testing issue ' + "".join([random.choice(string.ascii_letters) for i in range(15)])
        ticket_text = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
        for name in ('RT4.0 stable', 'RT3.8 stable'):
            self.check_or_create_queue(name)

            url = self.RT_VALID_CREDENTIALS[name]['url']
            default_login = self.RT_VALID_CREDENTIALS[name]['john.foo']['default_login']
            default_password = self.RT_VALID_CREDENTIALS[name]['john.foo']['default_password']
            tracker = rt.Rt(url, default_login=default_login, default_password=default_password)
            self.assertTrue(tracker.login(), 'Invalid login to RT demo site ' + name)
            # empty search result
            search_result = tracker.search(Subject=ticket_subject)
            self.assertEqual(search_result, [], 'Search for ticket with random subject returned non empty list.')
            # create
            ticket_id = tracker.create_ticket(Subject=ticket_subject, Text=ticket_text)
            self.assertTrue(ticket_id > -1, 'Creating ticket failed.')
            # search
            search_result = tracker.search(Subject=ticket_subject)
            self.assertEqual(len(search_result), 1, 'Created ticket is not found by the subject.')
            self.assertEqual(search_result[0]['id'], 'ticket/' + str(ticket_id), 'Bad id in search result of just created ticket.')
            self.assertEqual(search_result[0]['Status'], 'new', 'Bad status in search result of just created ticket.')
            # search all queues
            search_result = tracker.search(Queue=rt.ALL_QUEUES, Subject=ticket_subject)
            self.assertEqual(search_result[0]['id'], 'ticket/' + str(ticket_id), 'Bad id in search result of just created ticket.')
            # raw search
            search_result = tracker.search(raw_query='Subject="%s"' % ticket_subject)
            self.assertEqual(len(search_result), 1, 'Created ticket is not found by the subject.')
            self.assertEqual(search_result[0]['id'], 'ticket/' + str(ticket_id), 'Bad id in search result of just created ticket.')
            self.assertEqual(search_result[0]['Status'], 'new', 'Bad status in search result of just created ticket.')
            # raw search all queues
            search_result = tracker.search(Queue=rt.ALL_QUEUES, raw_query='Subject="%s"' % ticket_subject)
            self.assertEqual(search_result[0]['id'], 'ticket/' + str(ticket_id), 'Bad id in search result of just created ticket.')
            # get ticket
            ticket = tracker.get_ticket(ticket_id)
            self.assertEqual(ticket, search_result[0], 'Ticket get directly by its id is not equal to previous search result.')
            # edit ticket
            requestors = ['tester1@example.com', 'tester2@example.com']
            tracker.edit_ticket(ticket_id, Status='open', Requestors=requestors)
            # get ticket (edited)
            ticket = tracker.get_ticket(ticket_id)
            self.assertEqual(ticket['Status'], 'open', 'Ticket status was not changed to open.')
            self.assertEqual(ticket['Requestors'], requestors, 'Ticket requestors were not added properly.')
            # get history
            hist = tracker.get_history(ticket_id)
            self.assertTrue(len(hist) > 0, 'Empty ticket history.')
            self.assertEqual(hist[0]['Content'], ticket_text, 'Ticket text was not receives is it was submited.')
            # get_short_history
            short_hist = tracker.get_short_history(ticket_id)
            self.assertTrue(len(short_hist) > 0, 'Empty ticket short history.')
            self.assertEqual(short_hist[0][1], 'Ticket created by john.foo')
            # create 2nd ticket
            ticket2_subject = 'Testing issue ' + "".join([random.choice(string.ascii_letters) for i in range(15)])
            ticket2_id = tracker.create_ticket(Subject=ticket2_subject)
            self.assertTrue(ticket2_id > -1, 'Creating 2nd ticket failed.')
            # edit link
            self.assertTrue(tracker.edit_link(ticket_id, 'DependsOn', ticket2_id))
            # get links
            links1 = tracker.get_links(ticket_id)
            self.assertTrue('DependsOn' in links1, 'Missing just created link DependsOn.')
            self.assertTrue(links1['DependsOn'][0].endswith('ticket/' + str(ticket2_id)), 'Unexpected value of link DependsOn.')
            links2 = tracker.get_links(ticket2_id)
            self.assertTrue('DependedOnBy' in links2, 'Missing just created link DependedOnBy.')
            self.assertTrue(links2['DependedOnBy'][0].endswith('ticket/' + str(ticket_id)), 'Unexpected value of link DependedOnBy.')
            # reply with attachment
            attachment_content = b'Content of attachment.'
            attachment_name = 'attachment-name.txt'
            reply_text = 'Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.'
            # should provide a content type as RT 4.0 type guessing is broken (missing use statement for guess_media_type in REST.pm)
            self.assertTrue(tracker.reply(ticket_id, text=reply_text, files=[(attachment_name, attachment_content, 'text/plain')]), 'Reply to ticket returned False indicating error.')
            at_ids = tracker.get_attachments_ids(ticket_id)
            self.assertTrue(at_ids, 'Emply list with attachment ids, something went wrong.')
            at_content = tracker.get_attachment_content(ticket_id, at_ids[-1])
            self.assertEqual(at_content, attachment_content, 'Recorded attachment is not equal to the original file.')
            # attachments list
            at_list = tracker.get_attachments(ticket_id)
            at_names = [at[1] for at in at_list]
            self.assertTrue(attachment_name in at_names, 'Attachment name is not in the list of attachments.')
            # merge tickets
            self.assertTrue(tracker.merge_ticket(ticket2_id, ticket_id), 'Merging tickets failed.')
            # delete ticket
            self.assertTrue(tracker.edit_ticket(ticket_id, Status='deleted'), 'Ticket delete failed.')
            # get user
            self.assertEqual(tracker.get_user(default_login)['EmailAddress'], default_login + '@no.mail', 'Bad user email received.')

if __name__ == '__main__':
    unittest.main()

