# import flowp.testing
#
#
# class TestCaseIntegrationTest(flowp.testing.TestCase):
#     class Something:
#         def __init__(self):
#             self.a = 1
#             self.b = "abc"
#
#         def c(self):
#             return "def"
#
#     def test_subject_declaration_add_should_object(self):
#         subject = self.subject("abc")
#         self.assertIsInstance(subject.should, flowp.testing.Should)
#
#     def test_subject_declaration_add_should_object_to_every_element_in_object_dictionary(self):
#         subject = self.Something()
#         subject = self.subject(subject)
#         self.assertIsInstance(subject.a.should, flowp.testing.Should)
#         self.assertIsInstance(subject.b.should, flowp.testing.Should)
#         self.assertIsInstance(subject.c().should, flowp.testing.Should)
#
#     def test_subject_declaration_add_should_object_to_builtin_methods(self):
#         """
#         TODO: this test fails, need to change self.subject decorating algorithm
#         (problems with endless recursion at builtin types)
#         """
#         s = self.subject("abac")
#         self.assertTrue(hasattr(s.count('a'), 'should'))
#         s.count('a').should == 2
#
#     def test_subject_declaration_add_should_object_to_descriptor_objects_values(self):
#         class Something:
#             @property
#             def x(self):
#                 return 1
#
#         subject = self.subject(Something())
#         subject.x.should == 1
#
#     def test_should_asserts_with_subject_declaration(self):
#         sub = self.Something()
#         sub = self.subject(sub)
#         sub.should.be_instanceof(self.Something)
#         sub.a.should.be_instanceof(int)
#         sub.a.should == 1
#         sub.c().should.be_instanceof(str)
#         sub.c().should == "def"
#
#     def test_subject_declaration_add_should_object_to_bool_object(self):
#         """
#         TODO: This test fails, bool objects (True, False) are not extendable types,
#         so they are kind a problematic at this point. Needed different solution.
#         """
#         true_sub = self.subject(True)
#         false_sub = self.subject(False)
#         true_sub.should.be_true
#         false_sub.should.be_false