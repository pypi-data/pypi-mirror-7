from error import MissingKeyError, RemoveFolderError, FileNotWritableError
import os
from shutil import rmtree
import distutils.core


class Deploy:
    def __init__(self, config):
        self._cwd = os.getcwd()
        self._config = config

    def deploy_project(self, testname):
        if 'deployment_path' not in self._config:
            raise MissingKeyError('Could not find deployment path in config file.')

        if self._config['test']:
            if testname is None:
                print 'No tests to build.'
                return

            dest = os.path.join(self._config['deployment_path'], self._config['name'] + '_' + testname)
            source = os.path.join(self._cwd, 'build', self._config['name'] + '_' + testname)
        elif self._config['build']:
            dest = os.path.join(self._config['deployment_path'], self._config['name'])
            source = os.path.join(self._cwd, 'build', self._config['name'])
        else:
            raise MissingKeyError('It seems you are trying to deploy a project but neither build nor test were specified. I am sorry but I do not know what to do now.')

        self._deploy(source, dest)

    def _deploy(self, source, dest):
        if os.path.exists(dest):
            try:
                rmtree(dest)
            except:
                raise RemoveFolderError('Could not remove the existing deployment path.')

        try:
            distutils.dir_util.copy_tree(source, dest)
        except:
            raise FileNotWritableError('Could not copy the build directory to the deployment path.')
