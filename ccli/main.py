import os

from tinydb import TinyDB

from cement.utils import fs
from cement import App, TestApp, init_defaults
from cement.core.exc import CaughtSignal
from .core.exc import ccliError
from .controllers.base import Base
from .controllers.aws import AWS, EC2, Templates


# configuration defaults
CONFIG = init_defaults('ccli')
CONFIG['ccli']['db_file'] = 'db.json'


def extend_tinydb(app):
    app.log.info('saving data with tinydb')
    db_file = app.config.get('ccli', 'db_file')

    # ensure that we expand the full path
    db_file = fs.abspath(db_file)
    app.log.info(f'tinydb database file is: {db_file}')

    # ensure our parent directory exists
    db_dir = os.path.dirname(db_file)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    app.extend('db', TinyDB(db_file))


class Ccli(App):
    """ccli primary application."""

    class Meta:
        label = 'ccli'

        # configuration defaults
        config_defaults = CONFIG

        # call sys.exit() on close
        close_on_exit = True

        # load additional framework extensions
        extensions = [
            'yaml',
            'colorlog',
            'jinja2',
            'print',
        ]

        # configuration handler
        config_handler = 'yaml'

        # configuration file suffix
        config_file_suffix = '.yml'

        # set the log handler
        log_handler = 'colorlog'

        # set the output handler
        output_handler = 'jinja2'

        # register handlers
        handlers = [
            Base,
            AWS,
            EC2,
            Templates,
        ]

        hooks = [
            ('post_setup', extend_tinydb),
        ]


class CcliTest(TestApp, Ccli):
    """A sub-class of ccli that is better suited for testing."""

    class Meta:
        label = 'ccli'


def main():
    with Ccli() as app:
        try:
            app.run()

        except AssertionError as e:
            print('AssertionError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except ccliError as e:
            print('ccliError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print('\n%s' % e)
            app.exit_code = 0


if __name__ == '__main__':
    main()
