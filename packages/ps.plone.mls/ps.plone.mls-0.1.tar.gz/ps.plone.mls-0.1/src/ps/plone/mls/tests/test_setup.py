# -*- coding: utf-8 -*-
"""Test Setup of ps.plone.mls."""

# python imports
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# zope imports
from plone import api
from plone.browserlayer.utils import registered_layers

# local imports
from ps.plone.mls.config import PROJECTNAME
from ps.plone.mls.testing import INTEGRATION_TESTING


class TestSetup(unittest.TestCase):
    """Validate setup process for ps.plone.mls."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        """Additional test setup."""
        self.portal = self.layer['portal']

    def test_product_is_installed(self):
        """Validate that our product is installed."""
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled(PROJECTNAME))

    def test_addon_layer(self):
        """Validate that the browserlayer for our product is installed."""
        layers = [l.getName() for l in registered_layers()]
        self.assertIn('IPloneMLSLayer', layers)

    def test_collective_z3cform_widgets_installed(self):
        """Validate that collective.z3cform.widgets is installed."""
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled('collective.z3cform.widgets'))

    def test_plone_app_dexterity_installed(self):
        """Validate that plone.app.dexterity is installed."""
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled('plone.app.dexterity'))

    def test_plone_mls_listing_installed(self):
        """Validate that plone.mls.listing is installed."""
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled('plone.mls.listing'))


class UninstallTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        """Additional test setup."""
        self.portal = self.layer['portal']

        qi = self.portal.portal_quickinstaller
        with api.env.adopt_roles(['Manager']):
            qi.uninstallProducts(products=[PROJECTNAME])

    def test_product_is_uninstalled(self):
        """Validate that our product is uninstalled."""
        qi = self.portal.portal_quickinstaller
        self.assertFalse(qi.isProductInstalled(PROJECTNAME))

    def test_addon_layer_removed(self):
        """Validate that the browserlayer is removed."""
        layers = [l.getName() for l in registered_layers()]
        self.assertNotIn('IPloneMLSLayer', layers)
