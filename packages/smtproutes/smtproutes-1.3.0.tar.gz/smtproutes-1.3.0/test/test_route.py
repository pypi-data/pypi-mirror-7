import unittest
from smtproutes import Route, RoutingException
from smtproutes.sender_auth import DKIMAuth, GmailSPFAuth, SenderAuthException
from smtproutes.decorators import route

class TestRoute(unittest.TestCase):

    def setUp(self):
        self.valid_dkim_eml = file('test/fixtures/valid_dkim.eml').read()
        self.invalid_dkim_eml = file('test/fixtures/invalid_dkim.eml').read()

    def test_route_regexes_extracted_from_methods_on_class_inheriting_from_Route(self):

        class RouteImpl(Route):

            def route1(self, route=r'ben@example.com'):
                pass

            def route2(self, route=r'ben2@example.com'):
                pass

        route = RouteImpl()
        route._initialize()
        self.assertTrue('ben@example.com' in route._routes)
        self.assertTrue('ben2@example.com' in route._routes)

    def test_calling_route_with_a_matching_regex_results_in_the_appropriate_route_being_invoked(self):

        class RouteImpl(Route):

            def route1(self, route=r'ben@example.com'):
                self.bar = 'bar'

            def route2(self, route=r'ben2@example.com'):
                self.bar = 'foo'

        message =  'To: Benjamin <ben@example.com>, eric@foo.com, Eric <eric2@example.com>\nFrom: Ben Coe <bencoe@example.com>'

        route = RouteImpl()
        route._initialize()
        route._route(
            message_data=message
        )
        self.assertEqual('bar', route.bar)

    def test_route_decorator_can_be_used_to_define_endpoint_rather_than_kwarg(self):

        class RouteImpl(Route):

            @route('ben@example.com')
            def route1(self):
                self.bar = 'bar'

            @route('ben2@example.com')
            def route2(self):
                self.bar = 'foo'

        message =  'To: Benjamin <ben@example.com>, eric@foo.com, Eric <eric2@example.com>\nFrom: Ben Coe <bencoe@example.com>'

        r = RouteImpl()
        r._initialize()
        r._route(
            message_data=message
        )
        self.assertEqual('bar', r.bar)

    def test_a_cc_field_that_matches_a_route_causes_the_route_to_be_triggered(self):

        class RouteImpl(Route):
            @route(r'ben@example.com')
            def route1(self):
                self.bar = 'bar'

            @route(r'ben2@example.com')
            def route2(self):
                self.bar = 'foo'

        message =  'To: Benjamin <foo@example.com>, eric@foo.com, Eric <eric2@example.com>\nCC: ben@example.com\nFrom: Ben Coe <bencoe@example.com>'

        r = RouteImpl()
        r._initialize()
        r._route(
            message_data=message
        )
        self.assertEqual('bar', r.bar)

    def test_a_bcc_field_that_matches_a_route_causes_the_route_to_be_triggered(self):

        class RouteImpl(Route):
            @route(r'ben@example.com')
            def route1(self):
                self.bar = 'bar'

            @route(r'ben2@example.com')
            def route2(self):
                self.bar = 'foo'

        message =  'BCC: chuck@example.com, ben@example.com\nTo: Benjamin <foo@example.com>, eric@foo.com, Eric <eric2@example.com>\nCC: bar@example.com\nFrom: Ben Coe <bencoe@example.com>'

        r = RouteImpl()
        r._initialize()
        r._route(
            message_data=message
        )
        self.assertEqual('bar', r.bar)

    def test_x_forwarded_to_address_is_treated_as_to_address(self):

        class RouteImpl(Route):
            @route(r'ben@example.com')
            def route1(self):
                self.bar = 'bar'

        message =  'X-Forwarded-To: chuck@example.com, ben@example.com\nTo: Benjamin <foo@example.com>, eric@foo.com, Eric <eric2@example.com>\nCC: bar@example.com\nFrom: Ben Coe <bencoe@example.com>'

        r = RouteImpl()
        r._initialize()
        r._route(message)
        self.assertEqual(r.tos[3].email, 'chuck@example.com')

    def test_a_routing_exception_should_be_raised_if_the_route_is_not_found(self):
        class RouteImpl(Route):
            pass

        message =  'To: Benjamin <ben@example.com>, eric@foo.com, Eric <eric2@example.com>\nFrom: Ben Coe <bencoe@example.com>'
        route = RouteImpl()
        route._initialize()
        try:
            route._route(
                message_data=message
            )
            self.assertTrue(False)
        except RoutingException, re:
            self.assertTrue('ben@example.com' in str(re))
            self.assertTrue(True)

    def test_named_groups_stored_as_instance_variables_on_route(self):
        class RouteImpl(Route):

            def route(self, route=r'(?P<user>[^-]*)-(?P<folder>.*)@.*'):
                self.called = True

        message =  'To: Benjamin <bencoe-awesome-folder@example.com>\nFrom: bencoe@example.com'
        route = RouteImpl()
        route._initialize()
        route._route(message_data=message)
        self.assertEqual(route.user, 'bencoe')
        self.assertEqual(route.folder, 'awesome-folder')
        self.assertEqual(route.called, True)

    def test_instance_variables_populated_based_on_email_message(self):
        class RouteImpl(Route):

            def route(self, route=r'a@example.com'):
                self.called = True

        message =  'To: a <a@example.com>, b@example.com\nFrom: c@example.com\nCC: d <d@example.com>, e@example.com\nBCC: f@example.com'
        route = RouteImpl()
        route._initialize()
        route._route(message_data=message)
        self.assertTrue(route.message)
        self.assertEqual(route.tos[0].email, 'a@example.com')
        self.assertEqual(route.tos[1].email, 'b@example.com')
        self.assertEqual(route.mailfrom.email, 'c@example.com')
        self.assertEqual(route.ccs[0].email, 'd@example.com')
        self.assertEqual(route.ccs[1].email, 'e@example.com')
        self.assertEqual(route.bccs[0].email, 'f@example.com')

    def test_exception_raised_when_sender_auth_fails_on_route(self):
        class RouteImpl(Route):
            def route(self, route=r'bcoe@.*', sender_auth=DKIMAuth):
                self.called = True

        route = RouteImpl()
        route._initialize()
        route.called = False
        try:
            route._route(
                message_data=self.invalid_dkim_eml
            )
            self.assertTrue(False)
        except SenderAuthException:
            self.assertTrue(True)
        self.assertFalse(route.called)

    def test_no_exception_raised_when_sender_auth_succeeds_on_route(self):
        class RouteImpl(Route):
            def route(self, route=r'ben@.*', sender_auth=GmailSPFAuth):
                self.called = True

        route = RouteImpl()
        route._initialize(peer_ip='209.85.213.46')
        route._route(
            message_data=self.valid_dkim_eml
        )
        self.assertTrue(route.called)

    def test_route_decorator_can_be_used_rather_than_kwarg_to_specify_sender_auth(self):
        class RouteImpl(Route):
            @route('bcoe@.*', sender_auth=GmailSPFAuth)
            def route(self):
                self.called = True

        route = RouteImpl()
        route._initialize(peer_ip='209.85.213.46')
        route._route(
            message_data=self.invalid_dkim_eml
        )
        self.assertTrue(route.called)

    def test_if_list_of_sender_authentication_approaches_is_provided_route_called_if_any_pass(self):
        class RouteImpl(Route):
            def route(self, route=r'bcoe@.*', sender_auth=[DKIMAuth, GmailSPFAuth]):
                self.called = True

        route = RouteImpl()
        route._initialize(peer_ip='209.85.213.46')
        route._route(
            message_data=self.invalid_dkim_eml
        )
        self.assertTrue(route.called)

    def test_if_list_of_sender_authentication_approaches_is_provided_exception_raised_if_all_fail(self):
        class RouteImpl(Route):
            def route(self, route=r'bcoe@.*', sender_auth=[DKIMAuth, GmailSPFAuth]):
                self.called = True

        route = RouteImpl()
        route._initialize()
        route.called = False

        try:
            route._route(
                message_data=self.invalid_dkim_eml
            )
            self.assertTrue(False)
        except SenderAuthException:
            self.assertTrue(True)
        self.assertFalse(route.called)
