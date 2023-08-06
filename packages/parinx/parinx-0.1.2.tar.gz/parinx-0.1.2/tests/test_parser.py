#!/usr/bin/env python

import unittest2

from parinx import parser
from parinx.errors import MethodParsingException


class TestParser(unittest2.TestCase):

    def test_get_docsring(self):
        class A(object):
            def foo(self):
                """docstring"""

            def bar(self):
                pass

        class B(A):
            def foo(self):
                pass

            def bar(self):
                pass

        self.assertEqual(parser.get_method_docstring(B, 'foo'), 'docstring')
        self.assertEqual(parser.get_method_docstring(B, 'bar'), None)

    def test_parse_docstring(self):
        docstring = """
        Return a Zone instance.
        Second line docsting.

        :type zone_id: ``str``
        :param zone_id: Required zone id (required)

        :keyword    auth:   Initial authentication information for the node
                            (optional)
        :type       auth: :class:`NodeAuthSSHKey` or `NodeAuthPassword`

        :return:    instance
        :rtype: :class:`Zone` or `Node`
        """
        result = parser.parse_docstring(docstring)
        description = result['description']
        args = result['arguments']
        return_type = result['return']['type_name']
        return_description = result['return']['description']
        self.assertTrue(description.startswith('Return'))
        self.assertTrue('Second line' in description)
        self.assertEqual(args['zone_id']['type_name'], '``str``')
        self.assertEqual(args['zone_id']['required'], True)
        self.assertItemsEqual(args['auth']['type_name'],
                              'class:`NodeAuthSSHKey` or `NodeAuthPassword`')
        self.assertEqual(args['auth']['required'], False)
        self.assertEqual(return_type, 'class:`Zone` or `Node`')
        self.assertEqual(return_description, 'instance')

    def test_parse_docstring_fails(self):
        docstring = """
        Return a Zone instance.
        Second line docsting.

        :type zone_id: ``str``
        :param zone_id: Required zone id (required)

        :return: :class:`Zone` or `Node` instance.
        """
        self.assertRaises(MethodParsingException,
                          parser.parse_docstring, docstring)
        docstring = """
        Return a Zone instance.
        Second line docsting.

        :type zone_id:  ``str``
        :param zone_id: Required zone id (required)

        :return: instance.
        """
        self.assertRaises(MethodParsingException,
                          parser.parse_docstring, docstring)

    def test_parse_args(self):
        class A(object):
            def update_zone(self, zone, domain, type='master',
                            ttl=None, extra=None):
                pass

        result = parser.parse_args(A.update_zone)
        self.assertEqual(result.keys(),
                         ['zone', 'domain', 'type', 'ttl', 'extra'])
        self.assertEqual(result['zone']['required'], True)
        self.assertEqual(result['type']['required'], False)
        self.assertFalse('default' in result['zone'])
        self.assertTrue('default' in result['ttl'])


class InheritParseDocstringTests(unittest2.TestCase):
    class Foo(object):
        def create_node(self, **kwargs):
            """
            Create a new node instance.

            :keyword    name:   String with a name for this new node (required)
            :type       name:   ``str``

            :keyword    size:   The size of resources allocated to this node.
                                (required)
            :type       size:   ``dict``

            :return: The newly created node.
            :rtype: :class:`Node`
            """

        def deploy_node(self, **kwargs):
            """
            Deploy a new node, and start deployment.

            Depends on a Provider Driver supporting either using a specific
            password or returning a generated password.

            @inherits: :class:`Foo.create_node`

            :keyword    deploy: Deployment to run once machine is online and
                                availble to SSH.
            :type       deploy: :class:`NodeAuthSSHKey`
            """

    class Bar(Foo):
        def create_node(self, **kwargs):
            """
            Create a new bar node

            @inherits: :class:`Foo.create_node`

            :keyword    ex_fqdn:   Fully Qualified domain of the node
            :type       ex_fqdn:   ``str``

            :return: New bar node
            """

        def deploy_node(self, **kwargs):
            """
            Deploy bar node

            @inherits: :class:`Foo.deploy_node`
            """

    def test_foo_create_node(self):
        docstring = parser.get_method_docstring(self.Foo, 'create_node')
        result = parser.parse_docstring(docstring, self.Foo)
        description = result['description']
        args = result['arguments']
        return_type = result['return']['type_name']
        return_description = result['return']['description']
        self.assertTrue(description.startswith('Create a new node '))
        self.assertEqual(len(args), 2)
        self.assertEqual('``str``', args['name']['type_name'])
        self.assertEqual('``dict``', args['size']['type_name'])
        self.assertEqual(return_type, 'class:`Node`')
        self.assertEqual(return_description, 'The newly created node.')

    def test_foo_deploy_node(self):
        docstring = parser.get_method_docstring(self.Foo, 'deploy_node')
        result = parser.parse_docstring(docstring, self.Foo)
        description = result['description']
        args = result['arguments']
        return_type = result['return']['type_name']
        return_description = result['return']['description']
        self.assertTrue(description.startswith('Deploy a new node'))
        self.assertEqual(len(args), 3)
        self.assertEqual('class:`NodeAuthSSHKey`', args['deploy']['type_name'])
        self.assertEqual('``str``', args['name']['type_name'])
        self.assertEqual('``dict``', args['size']['type_name'])
        self.assertEqual(return_type, 'class:`Node`')
        self.assertEqual(return_description, 'The newly created node.')

    def test_bar_create_node(self):
        docstring = parser.get_method_docstring(self.Bar, 'create_node')
        result = parser.parse_docstring(docstring, self.Bar)
        description = result['description']
        args = result['arguments']
        return_type = result['return']['type_name']
        return_description = result['return']['description']
        self.assertTrue(description.startswith('Create a new bar node'))
        self.assertEqual(len(args), 3)
        self.assertEqual('``str``', args['name']['type_name'])
        self.assertEqual('``dict``', args['size']['type_name'])
        self.assertEqual('``str``', args['ex_fqdn']['type_name'])
        self.assertEqual(return_type, 'class:`Node`')
        self.assertEqual(return_description, 'New bar node')

    def test_bar_deploy_node(self):
        docstring = parser.get_method_docstring(self.Bar, 'deploy_node')
        result = parser.parse_docstring(docstring, self.Bar)
        description = result['description']
        args = result['arguments']
        return_type = result['return']['type_name']
        return_description = result['return']['description']
        self.assertTrue(description.startswith('Deploy bar node'))
        self.assertEqual(len(args), 3)
        self.assertEqual('class:`NodeAuthSSHKey`', args['deploy']['type_name'])
        self.assertEqual('``str``', args['name']['type_name'])
        self.assertEqual('``dict``', args['size']['type_name'])
        self.assertEqual(return_type, 'class:`Node`')
        self.assertEqual(return_description, 'The newly created node.')
