from django.test import TestCase
from django.test.client import RequestFactory

from organizations.forms import OrganizationForm, OrganizationUserForm
from organizations.models import Organization
from organizations.tests.utils import request_factory_login


class OrgFormTests(TestCase):

    fixtures = ['users.json', 'orgs.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.org = Organization.objects.get(name="Nirvana")
        self.admin = self.org.organization_users.get(user__username="krist")
        self.owner = self.org.organization_users.get(user__username="kurt")

    def test_admin_edits_form(self):
        user = self.admin.user
        request = request_factory_login(self.factory, user)
        form = OrganizationForm(request, instance=self.org,
                data={'name': self.org.name, 'owner': self.owner.id})
        self.assertTrue(form.is_valid())
        form = OrganizationForm(request, instance=self.org,
                data={'name': self.org.name, 'owner': self.admin.id})
        self.assertFalse(form.is_valid())

    def test_owner_edits_form(self):
        user = self.owner.user
        request = request_factory_login(self.factory, user)
        form = OrganizationForm(request, instance=self.org,
                data={'name': self.org.name, 'owner': self.owner.id})
        self.assertTrue(form.is_valid())

    def test_edit_owner_user(self):
        form = OrganizationUserForm(instance=self.owner,
                data={'is_admin': True})
        self.assertTrue(form.is_valid())
        form = OrganizationUserForm(instance=self.owner,
                data={'is_admin': False})
        self.assertFalse(form.is_valid())

