from grow.pods import pods
from grow.pods import storage
import unittest


class DocumentsTestCase(unittest.TestCase):

  def setUp(self):
    self.pod = pods.Pod('grow/pods/testdata/pod/', storage=storage.FileStorage)

  def test_doc_storage(self):
    doc = self.pod.get_doc('/content/pages/intro.md')
    self.assertEqual('About page.', doc.body)
    self.assertEqual('<p>About page.</p>', doc.html)
    keys = ['$title', '$order', '$titles']
    self.assertItemsEqual(keys, doc.fields.keys())

    doc = self.pod.get_doc('/content/pages/home.yaml')
    keys = ['$title', '$view', '$path', '$order', 'foo']
    self.assertItemsEqual(keys, doc.fields.keys())
    self.assertIsNone(doc.body)
    self.assertIsNone(doc.html)


if __name__ == '__main__':
  unittest.main()
