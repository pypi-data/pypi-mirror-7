#!/usr/bin/env python
# coding: utf-8

"""
Default task
============

A default task, that covers file system layout.

"""
# pylint: disable=F0401,E1101,E1103
from gluish import GLUISH_DATA
from gluish.parameter import ClosestDateParameter
from luigi.task import id_to_name_and_params
import datetime
import hashlib
import luigi
import os
import tempfile


def is_closest_date_parameter(task, param_name):
    """ Return the parameter class of param_name on task. """
    for name, obj in task.get_params():
        if name == param_name:
            return hasattr(obj, 'use_closest_date')
    return False


class BaseTask(luigi.Task):
    """
    A base task with a `path` method. BASE should be set to the root
    directory of all tasks. TAG is a shard for a group of related tasks.
    """
    BASE = os.environ.get(GLUISH_DATA, tempfile.gettempdir())
    TAG = 'default'

    def closest(self):
        """ Return the closest date for a given date.
        Defaults to the same date. """
        return self.date

    def path(self, filename=None, ext='tsv', digest=False):
        """
        Return the path for this class with a certain set of parameters.
        `ext` sets the extension of the file.
        If `hash` is true, the filename (w/o extenstion) will be hashed.
        """
        if self.TAG is NotImplemented or self.BASE is NotImplemented:
            raise RuntimeError('TAG and BASE must be set.')
        
        task_name, task_params = id_to_name_and_params(self.task_id)

        if filename is None:
            if 'date' in task_params:
                if is_closest_date_parameter(self, 'date'):
                    task_params['date'] = self.closest()

            parts = ('{k}-{v}'.format(k=k, v=v)
                     for k, v in task_params.iteritems())

            name = '-'.join(sorted(parts))
            if len(name) == 0:
                name = 'output'
            if digest:
                name = hashlib.sha1(name).hexdigest()
            if not ext:
                filename = '{fn}'.format(ext=ext, fn=name)
            else:
                filename = '{fn}.{ext}'.format(ext=ext, fn=name)

        return os.path.join(unicode(self.BASE), unicode(self.TAG), task_name,
                            filename)


class MockTask(BaseTask):
    """ A mock task object. Read fixture from path and that's it. """
    fixture = luigi.Parameter()

    def content(self):
        """ Return the content of the file in path. """
        with open(self.fixture) as handle:
            return handle.read()

    def run(self):
        """ Just copy the fixture, so we have some output. """
        luigi.File(path=self.fixture).copy(self.output().path)

    def output(self):
        """ Mock output. """
        return luigi.LocalTarget(path=self.path(digest=True))

