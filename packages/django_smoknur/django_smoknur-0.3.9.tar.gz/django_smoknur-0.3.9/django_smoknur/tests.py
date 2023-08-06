# coding: utf-8

"""
модуль базового теста
"""

import json
import os
import sys

import django
from django.conf import settings
from django.core.management import call_command
from django.db.models import get_apps
from django.test import TransactionTestCase

ERROR_TEXT = u'line={0}, file={1}, url={2}, post_params={3}'

if django.VERSION[:3] > (1, 6, 0) and getattr(settings, 'SMOKNUR_NEW_DJANGO_TESTCASE', True):
    NEW_DJANGO_TESTCASE = True
else:
    NEW_DJANGO_TESTCASE = False

def _fixture_setup(self):
    """
    начиная с джанги 1.6, в данном методе отсутсвует вызов метода call_command('flush')
    поэтому выполняем данный загрузчик фикстур
    """
    for db_name in self._databases_names(include_mirrors=False):
        # Reset sequences
        if self.reset_sequences:
            self._reset_sequences(db_name)

        call_command('flush', verbosity=0, interactive=False, database=db_name)

        if hasattr(self, 'fixtures'):
            # We have to use this slightly awkward syntax due to the fact
            # that we're using *args and **kwargs together.

            call_command('loaddata', *self.fixtures,
                         **{'verbosity': 0, 'database': db_name,
                            'skip_validation': True})

def test_runner(self):
    """smoke test"""

    # авторизуем пользователя
    if (hasattr(settings, 'SMOKNUR_USERNAME') 
        and hasattr(settings, 'SMOKNUR_PASSWORD')):
        self.assertTrue(
            self.client.login(
                username=settings.SMOKNUR_USERNAME,
                password=settings.SMOKNUR_PASSWORD))

    # отправляем пост запросы
    for f in sorted(os.listdir(self.smoknur_path)):
        if f.endswith('.dbg'):
            with open(os.path.join(self.smoknur_path, f)) as f_dbg:
                for index, line in enumerate(f_dbg, 1):
                    if not line.startswith('#'):
                        req = json.loads(line)

                        if getattr(settings, 'SMOKNUR_PRINT_REQUESTS', False):
                            sys.stdout.write(
                                ERROR_TEXT.format(
                                    index,
                                    f,
                                    req['url'],
                                    req['params']).encode('utf-8'))

                        try:
                            resp = self.client.post(
                                req['url'],
                                req['params']
                            )
                        except:
                            sys.stdout.write(
                                ERROR_TEXT.format(
                                    index,
                                    f,
                                    req['url'],
                                    req['params']).encode('utf-8'))
                            raise
                        else:
                            if getattr(settings, 'SMOKNUR_PRINT_RESPONSE', False):
                                size = getattr(settings, 'SMOKNUR_PRINT_RESPONSE_SIZE', 0)
                                sys.stdout.write(
                                    u'{0}, {1}\n'.format(
                                        resp.status_code,
                                        resp.content[:size]).encode('utf-8'))

                        self.assertTrue(
                            resp.status_code in (200, 302),
                            ERROR_TEXT.format(
                                index,
                                f,
                                req['url'],
                                req['params']).encode('utf-8'))

exclude_apps = getattr(settings, 'SMOKNUR_EXCLUDE_APPS', ())

# добавляем в глобал тесткейсы
for app in get_apps():

    if app.__package__ in exclude_apps:
        continue

    path = os.path.join(
        os.path.dirname(app.__file__),
        'smoknur')


    if os.path.exists(path):

        smok_dirs = [
            os.path.join(path, f)
            for f in os.listdir(path)
            if os.path.isdir(os.path.join(path, f))]

        smok_dirs.append(path)

        for smok_dir in smok_dirs:

            test_name = u'{0}_{1}'.format(
                app.__package__.replace('.', '_'),
                os.path.basename(smok_dir)
            ).upper().encode('utf-8')
            
            attrs = {
                'fixtures': [],
                'smoknur_path': smok_dir,
                'test': test_runner
            }

            if NEW_DJANGO_TESTCASE:
                attrs['_fixture_setup'] = _fixture_setup

            for file_ in sorted(os.listdir(smok_dir)):
                if file_.endswith('.json'):
                    attrs['fixtures'].append(os.path.join(smok_dir, file_))

            globals()[test_name] = type(
                test_name, 
                (TransactionTestCase, ), 
                attrs)    
