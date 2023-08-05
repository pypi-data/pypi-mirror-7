#!/usr/bin/env python
# -*- coding: utf-8  -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2012 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

"""
``rattail.filemon`` -- File Monitor
"""

import os
import os.path
import sys
import Queue
import logging

from ..util import load_object

if sys.platform == 'win32':
    import win32api
    from rattail.win32 import file_is_free


log = logging.getLogger(__name__)


class MonitorProfile(object):
    """
    This is a simple profile class, used to represent configuration of the file
    monitor service.
    """

    def __init__(self, config, key):
        self.config = config
        self.key = key

        self.dirs = config.require('rattail.filemon', '{0}.dirs'.format(key))
        self.dirs = eval(self.dirs)

        actions = config.require('rattail.filemon', '{0}.actions'.format(key))
        actions = eval(actions)

        self.actions = []
        for action in actions:
            if isinstance(action, tuple):
                spec = action[0]
                args = list(action[1:])
            else:
                spec = action
                args = []
            func = load_object(spec)
            self.actions.append((spec, func, args))

        self.locks = config.getboolean(
            'rattail.filemon', '{0}.locks'.format(key), default=False)

        self.process_existing = config.getboolean(
            'rattail.filemon', '{0}.process_existing'.format(key), default=True)

        self.stop_on_error = config.getboolean(
            'rattail.filemon', '{0}.stop_on_error'.format(key), default=False)


def get_monitor_profiles(config):
    """
    Convenience function to load monitor profiles from config.
    """

    monitored = {}

    # Read monitor profile(s) from config.
    keys = config.require('rattail.filemon', 'monitored')
    keys = keys.split(',')
    for key in keys:
        key = key.strip()
        log.debug("get_monitor_profiles: loading profile: {0}".format(key))
        profile = MonitorProfile(config, key)
        monitored[key] = profile
        for path in profile.dirs[:]:

            # Ensure the monitored path exists.
            if not os.path.exists(path):
                log.warning("get_monitor_profiles: profile '{0}' has nonexistent "
                            "path, which will be pruned: {1}".format(key, path))
                profile.dirs.remove(path)

            # Ensure the monitored path is a folder.
            elif not os.path.isdir(path):
                log.warning("get_monitor_profiles: profile '{0}' has non-folder "
                            "path, which will be pruned: {1}".format(key, path))
                profile.dirs.remove(path)

    for key in monitored.keys():
        profile = monitored[key]

        # Prune any profiles with no valid folders to monitor.
        if not profile.dirs:
            log.warning("get_monitor_profiles: profile has no folders to "
                        "monitor, and will be pruned: {0}".format(key))
            del monitored[key]

        # Prune any profiles with no valid actions to perform.
        elif not profile.actions:
            log.warning("get_monitor_profiles: profile has no actions to "
                        "perform, and will be pruned: {0}".format(key))
            del monitored[key]

    return monitored


def queue_existing(profile, path):
    """
    Adds files found in a watched folder to a processing queue.  This is called
    when the monitor first starts, to handle the case of files which exist
    prior to startup.

    If files are found, they are first sorted by modification timestamp, using
    a lexical sort on the filename as a tie-breaker, and then added to the
    queue in that order.

    :param profile: Monitor profile for which the folder is to be watched.  The
    profile is expected to already have a queue attached; any existing files
    will be added to this queue.
    :type profile: :class:`rattail.filemon.MonitorProfile` instance

    :param path: Folder path which is to be checked for files.
    :type path: string

    :returns: ``None``
    """

    def sorter(x, y):
        mtime_x = os.path.getmtime(x)
        mtime_y = os.path.getmtime(y)
        if mtime_x < mtime_y:
            return -1
        if mtime_x > mtime_y:
            return 1
        return cmp(x, y)

    paths = [os.path.join(path, x) for x in os.listdir(path)]
    for path in sorted(paths, cmp=sorter):

        # Only process normal files.
        if not os.path.isfile(path):
            continue

        # If using locks, don't process "in transit" files.
        if profile.locks and path.endswith('.lock'):
            continue

        log.debug("queue_existing: queuing existing file for "
                  "profile '{0}': {1}".format(profile.key, path))
        profile.queue.put(path)


def perform_actions(profile):
    """
    Callable target for action threads.
    """

    keep_going = True
    while keep_going:

        try:
            path = profile.queue.get_nowait()
        except Queue.Empty:
            pass
        else:

            # In some cases, processing one file may cause other related files
            # to also be processed.  When this happens, a path on the queue may
            # point to a file which no longer exists.
            if not os.path.exists(path):
                log.info("perform_actions: path does not exist: {0}".format(path))
                continue

            log.debug("perform_actions: processing file: {0}".format(path))

            if sys.platform == 'win32':
                while not file_is_free(path):
                    win32api.Sleep(0)

            for spec, func, args in profile.actions:

                log.info("perform_actions: calling function '{0}' on file: {1}".format(
                        spec, path))

                try:
                    func(path, *args)

                except:
                    log.exception(u"error processing file: %s", path)

                    # Don't process any more files if the profile is so
                    # configured.
                    if profile.stop_on_error:
                        keep_going = False

                    # Either way this particular file probably shouldn't be
                    # processed any further.
                    log.warning("perform_actions: no further processing will "
                                "be done for file: {0}".format(path))
                    break

    log.warning("perform_actions: error encountered, and configuration "
                "dictates that no more actions will be processed for "
                "profile: {0}".format(profile.key))
