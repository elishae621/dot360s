# from django.test import TestCase, RequestFactory
# from user.admin import UserAdminConfig, UserInline
# from user.models import User
# import unittest
# from unittest.mock import patch


# class TestUserAdminConfig(TestCase):

#     def setUp(self):
#         self.request = RequestFactory().get(f'/admin/user/user/{self.user.pk}/change/')

#     @patch('user.admin.UserAdmin.get_inline_instances')
#     def test_get_inline_instances_returns_for_obj(self, get_inline_instances):
#         get_inline_instances.return_value = (UserInline,)
        
#         self.assertTrue(UserAdminConfig.get_inline_instances(
#             UserAdminConfig, request=self.request, obj=self.user))

#     def test_get_inline_instances_returns_none_for_no_obj(self):
#         self.assertFalse(UserAdminConfig.get_inline_instances(UserAdminConfig, request=self.request))
