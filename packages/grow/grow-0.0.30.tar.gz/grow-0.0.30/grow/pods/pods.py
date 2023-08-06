"""A pod encapsulates all files used to build a web site.

Pods are the main interface to everything in a web site. Specifically, pods are
used to do the following sorts of tasks:

  - manage content (collections, blueprints, and documents)
  - manage pod files (any of the files contained in the pod)
  - list routes
  - building and deployment
  - listing and running tests

Pods are accessed using their root directory.

  pod = pods.Pod('/home/growler/my-site/')

You can get a content collection from the pod.

  collection = pod.get_collection('/content/pages/')

You can get a content document from the pod.

  document = pod.get_doc('/content/pages/index.md')

You can get a static file from the pod.

  file = pod.get_file('/podspec.yaml')
"""

import copy
import jinja2
import logging
import os
import re
from grow.common import utils
from grow.deployments import deployments
from grow.pods import files
from grow.pods import locales
from grow.pods import messages
from grow.pods import podspec
from grow.pods import routes
from grow.pods import storage
from grow.pods import tests
from grow.pods import translations
from grow.pods.collectionz import collectionz
from grow.pods.controllers import tags
from grow.pods.preprocessors import preprocessors


class Error(Exception):
  pass


class BuildError(Error):
  pass


# TODO(jeremydw): A handful of the properties of "pod" should be moved to the
# "podspec" class.

class Pod(object):

  def __init__(self, root, changeset=None, storage=storage.auto):
    self.storage = storage
    self.root = root if self.storage.is_cloud_storage else os.path.abspath(root)
    self.changeset = changeset

    self.routes = routes.Routes(pod=self)
    self.locales = locales.Locales(pod=self)
    self.translations = translations.Translations(pod=self)
    self.tests = tests.Tests(pod=self)

  def __repr__(self):
    if self.changeset is not None:
      return '<Pod: {}@{}>'.format(self.root, self.changeset)
    return '<Pod: {}>'.format(self.root)

  def exists(self):
    return self.file_exists('/podspec.yaml')

  @property
  @utils.memoize
  def yaml(self):
    try:
      return utils.parse_yaml(self.read_file('/podspec.yaml'))[0]
    except IOError:
      raise Error('Pod does not exist or malformed podspec.yaml.')

  @property
  @utils.memoize
  def podspec(self):
    return podspec.Podspec(pod=self)

  @property
  def error_routes(self):
    return self.yaml.get('error_routes')

  @property
  def flags(self):
    return self.yaml.get('flags', {})

  @property
  def title(self):
    return self.yaml.get('title')

  def get_routes(self):
    return self.routes

  def get_translations(self):
    return self.translations

  def abs_path(self, pod_path):
    path = os.path.join(self.root, pod_path.lstrip('/'))
    return os.path.join(self.root, path)

  def list_dir(self, pod_path='/'):
    path = os.path.join(self.root, pod_path.lstrip('/'))
    return self.storage.listdir(path)

  def open_file(self, pod_path, mode=None):
    path = os.path.join(self.root, pod_path.lstrip('/'))
    return self.storage.open(path, mode=mode)

  def read_file(self, pod_path):
    path = os.path.join(self.root, pod_path.lstrip('/'))
    return self.storage.read(path)

  def write_file(self, pod_path, content):
    path = os.path.join(self.root, pod_path.lstrip('/'))
    self.storage.write(path, content)

  def file_exists(self, pod_path):
    path = os.path.join(self.root, pod_path.lstrip('/'))
    return self.storage.exists(path)

  def delete_file(self, pod_path):
    path = os.path.join(self.root, pod_path.lstrip('/'))
    return self.storage.delete(path)

  def move_file_to(self, source_pod_path, destination_pod_path):
    source_path = os.path.join(self.root, source_pod_path.lstrip('/'))
    destination_path = os.path.join(self.root, destination_pod_path.lstrip('/'))
    return self.storage.move_to(source_path, destination_path)

  def list_collections(self):
    return collectionz.Collection.list(self)

  def get_file(self, pod_path):
    return files.File.get(pod_path, self)

  def create_file(self, pod_path, content):
    """Creates a file inside the pod."""
    return files.File.create(pod_path, content, self)

  def get_doc(self, pod_path, locale=None):
    """Returns a document, given the document's pod path."""
    collection_path, _ = os.path.split(pod_path)
    collection = self.get_collection(collection_path)
    return collection.get_doc(pod_path, locale=locale)

  def get_collection(self, collection_path):
    """Returns a collection.

    Args:
      collection_path: The collection's path relative to the /content/ directory.
    Returns:
      Collection.
    """
    pod_path = os.path.join('/content', collection_path)
    return collectionz.Collection.get(pod_path, _pod=self)

  def get_translation_catalog(self, locale):
    return self.translations.get_translation(locale)

  def duplicate_to(self, other, exclude=None):
    """Duplicates this pod to another pod."""
    if not isinstance(other, self.__class__):
      raise ValueError('{} is not a pod.'.format(other))
    source_paths = self.list_dir('/')
    for path in source_paths:
      if exclude:
        patterns = '|'.join(['({})'.format(pattern) for pattern in exclude])
        if re.match(patterns, path) or 'theme/' in path:
          continue
      content = self.read_file(path)
      other.write_file(path, content)
    # TODO: Handle same-storage copying more elegantly.

  def export(self):
    """Builds the pod, returning a mapping of paths to content."""
    output = {}
    routes = self.get_routes()
    for path in routes.list_concrete_paths():
      controller = routes.match(path)
      output[path] = controller.render()

    error_controller = routes.match_error('/404.html')
    if error_controller:
      output['/404.html'] = error_controller.render()

    return output

  def dump(self, suffix='index.html'):
    output = self.export()
    clean_output = {}
    if suffix:
      for path, content in output.iteritems():
        if suffix and path.endswith('/') or '.' not in os.path.basename(path):
          path = path.rstrip('/') + '/' + suffix
        clean_output[path] = content
    else:
      clean_output = output
    return clean_output

  def to_message(self):
    message = messages.PodMessage()
    message.collections = [collection.to_message() for collection in self.list_collections()]
    message.changeset = self.changeset
    message.routes = self.routes.to_message()
    return message

  def delete(self):
    """Deletes the pod by deleting all of its files."""
    pod_paths = self.list_dir('/')
    for path in pod_paths:
      self.delete_file(path)
    return pod_paths

  def list_deployments(self):
    destination_configs = self.yaml['deployments']
    results = []
    for name in destination_configs.keys():
      results.append(self.get_deployment(name))
    return results

  def get_deployment(self, nickname):
    """Returns a pod-specific deployment."""
    if 'deployments' not in self.yaml:
      raise ValueError('No pod-specific deployments configured.')
    destination_configs = self.yaml['deployments']
    if nickname not in destination_configs:
      text = 'No deployment named {}. Valid deployments: {}.'
      raise ValueError(text.format(nickname, ', '.join(destination_configs.keys())))
    deployment_params = destination_configs[nickname]
    kind = deployment_params.pop('destination')
    try:
      config = destination_configs[nickname]
      deployment = deployments.make_deployment(kind, config)
    except TypeError:
      logging.exception('Invalid deployment parameters.')
      raise
    return deployment

  def list_locales(self):
    codes = self.yaml.get('localization', {}).get('locales', [])
    return locales.Locale.parse_codes(codes)

  def list_preprocessors(self):
    results = []
    preprocessor_config = copy.deepcopy(self.yaml.get('preprocessors', []))
    for params in preprocessor_config:
      kind = params.pop('kind')
      preprocessor = preprocessors.Preprocessor.get(kind, pod=self)
      preprocessor.set_params(**params)
      results.append(preprocessor)
    return results

  def preprocess(self):
    # Preprocess translations.
    translations_obj = self.get_translations()
    translations_obj.recompile_mo_files()
    for preprocessor in self.list_preprocessors():
      preprocessor.run()

  def get_podspec(self):
    return self.podspec

  def get_template_env(self):
    _template_loader = self.storage.JinjaLoader(self.root)
    env = jinja2.Environment(
        loader=_template_loader, autoescape=True, trim_blocks=True,
        extensions=['jinja2.ext.i18n'])
    env.filters['markdown'] = tags.markdown_filter
    env.filters['render'] = tags.render_filter
    return env

  def get_root_path(self, locale=None):
    path_format = self.yaml.get('flags', {}).get('root_path', None)
    if locale is None:
      locale = self.yaml.get('localization', {}).get('default_locale', '')
    if not path_format:
      return '/'
    return path_format.format(**{'locale': locale})
