import collections
import os
from protorpc import protojson
from . import messages


class Stats(object):

  def __init__(self, pod, paths_to_contents=None):
    self.pod = pod
    if paths_to_contents is None:
      paths_to_contents = pod.export()
    self.paths_to_contents = paths_to_contents

  def get_num_files_per_type(self):
    file_counts = collections.defaultdict(int)
    for path in self.paths_to_contents.keys():
      ext = os.path.splitext(path)[-1]
      file_counts[ext] += 1
    ms = []
    for ext, count in file_counts.iteritems():
      ms.append(messages.FileCountMessage(ext=ext, count=count))
    return ms

  def to_message(self):
    message = messages.StatsMessage()

    message.num_collections = len(self.pod.list_collections())
    message.num_files_per_type = self.get_num_files_per_type()

    message.locales = [str(locale) for locale in self.pod.list_locales()]
    message.langs = self.pod.get_translations().list_locales()
    catalog = self.pod.get_translations().get_catalog()
    message.num_messages = len(catalog) if catalog else 0
    return message

  def to_string(self):
    return protojson.encode_message(self.to_message())
