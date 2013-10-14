from django.test import TestCase

from .models import User


class ChangesMixinBeforeAndCurrentTestCase(TestCase):
    def test_empty(self):
        user = User()

        self.assertDictContainsSubset({'id': None, 'name': ''}, user.old_state())
        self.assertDictContainsSubset({'id': None, 'name': ''}, user.previous_state())
        self.assertDictContainsSubset({'id': None, 'name': ''}, user.current_state())
        self.assertEqual({}, user.old_changes())
        self.assertEqual({}, user.changes())

    def test_new(self):
        user = User(name='Foo Bar')

        self.assertDictContainsSubset({'id': None, 'name': 'Foo Bar'}, user.old_state())
        self.assertDictContainsSubset({'id': None, 'name': 'Foo Bar'}, user.previous_state())
        self.assertDictContainsSubset({'id': None, 'name': 'Foo Bar'}, user.current_state())
        self.assertEqual({}, user.old_changes())
        self.assertEqual({}, user.changes())

    def test_change_from_new(self):
        user = User()
        user.name = 'Foo Bar'

        self.assertDictContainsSubset({'id': None, 'name': ''}, user.old_state())
        self.assertDictContainsSubset({'id': None, 'name': ''}, user.previous_state())
        self.assertDictContainsSubset({'id': None, 'name': 'Foo Bar'}, user.current_state())
        self.assertEqual({'name': ('', 'Foo Bar')}, user.old_changes())
        self.assertEqual({'name': ('', 'Foo Bar')}, user.changes())

    def test_change_from_db(self):
        user = User(name='Foo Bar')
        user.save()

        self.assertDictContainsSubset({'id': None, 'name': 'Foo Bar'}, user.old_state())
        self.assertDictContainsSubset({'id': 1, 'name': 'Foo Bar'}, user.previous_state())
        self.assertDictContainsSubset({'id': 1, 'name': 'Foo Bar'}, user.current_state())

        user = User.objects.filter(pk=user.pk)[0]
        user.name = 'My Real Name'

        self.assertDictContainsSubset({'id': 1, 'name': 'Foo Bar'}, user.old_state())
        self.assertDictContainsSubset({'id': 1, 'name': 'Foo Bar'}, user.previous_state())
        self.assertDictContainsSubset({'id': 1, 'name': 'My Real Name'}, user.current_state())
        self.assertEqual({'name': ('Foo Bar', 'My Real Name')}, user.old_changes())

    def test_save(self):
        user = User()
        user.name = 'Foo Bar'
        user.save()

        user.name = 'My Real Name'

        pk = user.pk

        self.assertDictContainsSubset({'id': None, 'name': ''}, user.old_state())
        self.assertDictContainsSubset({'id': pk, 'name': 'Foo Bar'}, user.previous_state())
        self.assertDictContainsSubset({'id': pk, 'name': 'My Real Name'}, user.current_state())
        self.assertDictEqual({'id': (None, pk), 'name': ('', 'My Real Name')}, user.old_changes())
        self.assertFalse(user.was_persisted())
        self.assertTrue(user.is_persisted())

        user.save()

        self.assertDictContainsSubset({'id': pk, 'name': 'Foo Bar'}, user.old_state())
        self.assertDictContainsSubset({'id': pk, 'name': 'My Real Name'}, user.previous_state())
        self.assertDictContainsSubset({'id': pk, 'name': 'My Real Name'}, user.current_state())
        self.assertEqual({'name': ('Foo Bar', 'My Real Name')}, user.old_changes())
        self.assertTrue(user.was_persisted())
        self.assertTrue(user.is_persisted())


        user.name = 'I Changed My Mind'
        user.save()

        self.assertDictContainsSubset({'id': pk, 'name': 'My Real Name'}, user.old_state())
        self.assertDictContainsSubset({'id': pk, 'name': 'I Changed My Mind'}, user.current_state())
        self.assertEqual({'name': ('My Real Name', 'I Changed My Mind')}, user.old_changes())
        self.assertTrue(user.was_persisted())
        self.assertTrue(user.is_persisted())


    def test_new_is_was_persisted(self):
        user = User()
        self.assertFalse(user.was_persisted())
        self.assertFalse(user.is_persisted())

        user.save()
        self.assertFalse(user.was_persisted())
        self.assertTrue(user.is_persisted())

        user.delete()
        self.assertTrue(user.was_persisted())
        self.assertFalse(user.is_persisted())

        user.save()
        self.assertFalse(user.was_persisted())
        self.assertTrue(user.is_persisted())

        user.delete()
        self.assertTrue(user.was_persisted())
        self.assertFalse(user.is_persisted())