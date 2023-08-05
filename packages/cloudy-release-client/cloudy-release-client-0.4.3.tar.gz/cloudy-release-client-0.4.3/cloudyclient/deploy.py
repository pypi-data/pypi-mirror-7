import os
import tempfile
import logging

from cloudyclient.api import run, cd


ENTRY_POINT_SCRIPT_TEMPLATE = '''
from {module} import {func}

{func}()
'''
logger = logging.getLogger(__name__)


class DeploymentScript(object):
    '''
    Sets up environment and executes a deployment script in a sub process.
    '''

    def __init__(self, script_type, script):
        self.script_type = script_type
        # Replace DOS line endings, as bash does not like them
        self.script = script.strip().replace('\r\n', '\n')

    def run(self, base_dir):
        if not self.script:
            return
        with tempfile.NamedTemporaryFile(prefix='cloudy-release-script-') as fp:
            run_func_name = 'run_%s' % self.script_type
            try:
                run_func = getattr(self, run_func_name)
            except AttributeError:
                raise ValueError('unsupported sript type "%s"' % self.script_type)
            with cd(base_dir):
                run_func(fp)

    def run_bash(self, fp):
        '''
        Run a bash script.
        '''
        logger.info('running bash deployment script')
        self.write_script(self.script, fp)
        run('/bin/bash', fp.name)

    def run_python_script(self, fp):
        '''
        Run a Python script.
        '''
        logger.info('running python deployment script')
        self.write_script(self.script, fp)
        run('/usr/bin/env', 'python', fp.name)

    def run_python_entry_point(self, fp):
        '''
        Run a Python entry point.
        '''
        logger.info('running python entry point %s' % self.script)
        if ':' in self.script:
            module, _, func = self.script.partition(':')
            script = ENTRY_POINT_SCRIPT_TEMPLATE.format(module=module, func=func)
            self.write_script(script, fp)
            run('/usr/bin/env', 'python', fp.name)
        else:
            run('/usr/bin/env', 'python', '-m', self.script)

    def run_python_file(self, fp):
        '''
        Run path to a Python script.
        '''
        run('/usr/bin/env', 'python', self.script)

    def write_script(self, script, fp):
        '''
        Write *script* to file object *fp* and make sure the contents are on
        disc.
        '''
        fp.write(self.script)
        fp.flush()
        os.fsync(fp)
