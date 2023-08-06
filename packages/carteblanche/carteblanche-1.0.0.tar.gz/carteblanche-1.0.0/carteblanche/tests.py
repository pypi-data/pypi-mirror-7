import random
import unittest
import base as cb

class ProjectViewVerb(cb.Verb):
    condition_name = 'can_view'
    def get_url(self):
        return "projects/"

class ProjectMemberVerb(cb.Verb):
    condition_name = "is_member"
    def is_available(self, user):
        return self.noun.is_member(user)

class ProjectUploadVerb(ProjectMemberVerb):
    display_name = "Upload Media"

    def get_url(self):
        return "projects/upload"

class ProjectPostVerb(ProjectMemberVerb):
    display_name = "Post"

    def get_url(self):
        return "/projects/post"

class Project(cb.Noun):
    verb_classes = [ProjectUploadVerb, ProjectPostVerb, ProjectViewVerb]

    def __init__(self):
        super(Project, self).__init__()
        self.run_count = 0

    def is_member(self, user):
        self.run_count += 1
        return True

class ProjectDupe(cb.Noun):
    def __init__(self):
        super(ProjectDupe, self).__init__()
        self.run_count = 0

    def is_member(self, user):
        self.run_count += 1
        return True

    def get_verbs(self):
        verbs = [
            ProjectUploadVerb(noun=self),
            ProjectPostVerb(noun=self),
            ProjectViewVerb(noun=self)
        ]
        return verbs


class TestNounFunctions(unittest.TestCase):
    verbs = []
    nouns = []

    def setUp(self):
        self.nouns.append(Project())
        self.nouns.append(ProjectDupe())

        def register_verbs(noun):
            self.verbs.append(ProjectUploadVerb(noun))
            self.verbs.append(ProjectPostVerb(noun))
            self.verbs.append(ProjectViewVerb(noun))

        register_verbs(self.nouns[0])
        register_verbs(self.nouns[1])

    def test_cache(self):
        # make sure the is_member method was run once only
        self.nouns[0].get_available_verbs(None)
        self.assertTrue(self.nouns[0].run_count == 1)
        #reset it
        self.nouns[0].run_count = 0

    def test_visible(self):
        self.assertEqual(self.nouns[0].get_available_verbs('no need for a user object')[0]['visible'], True)

    def test_no_cache(self):
        verbs = self.nouns[0].get_available_verbs(None)
        self.assertTrue(self.verbs[2].get_serialized() in verbs)

    def test_get_verbs_override(self):
        self.assertTrue(self.nouns[0].get_available_verbs(None) == self.nouns[1].get_available_verbs(None))
        


if __name__ == '__main__':
    unittest.main()
