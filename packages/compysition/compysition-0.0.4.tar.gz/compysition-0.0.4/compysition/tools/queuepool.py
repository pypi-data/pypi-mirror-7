#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  queuepool.py
#
#  Copyright 2013 Jelle Smet <development@smetj.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

class QueuePool():

    def __init__(self):
        pass

    def shutdown(self):
        '''Closes all queues in preparation of actor shutdown.'''

        for q in self.__dict__.keys():
            self.__dict__[q].lock()

    def listQueues(self):
        '''return the list of queue names from the queuepool.'''

        return self.__dict__.keys()

    def getQueueInstances(self):
        '''Return a dict of queue instances from the queuepool.'''

        #return {name:self.__dict__[name] for name in self.__dict__.keys()}
        return dict((name, self.__dict__[name]) for name in self.__dict__.keys())

    def getErrorQueueInstances(self):
        '''Return a dict of error queue instances from the queuepool.'''
        return self.__get_queue_instances(type="ERROR")

    def getEventQueueInstances(self):
        '''Return a dict of event queue instances from the queuepool.'''
        return self.__get_queue_instances(type="EVENT")

    def __get_queue_instances(self, type="EVENT"):
        #return {name:self.__dict__[name] for name in self.__dict__.keys()}
        all_queues = dict((name, self.__dict__[name]) for name in self.__dict__.keys())
        filtered_queues = {}

        for key in all_queues:
            if all_queues[key].type == type:
                filtered_queues[key] = all_queues[key]

        return filtered_queues

    def messagesLeft(self):
        '''Checks each queue whether there are any messages left.'''
        qs=[]
        for q in self.__dict__.keys():
            if not self.__dict__[q].empty():
                qs.append(q)
        if len(qs) == 0:
            return []
        else:
            return qs

    def dump(self, name):
        '''Convenience function to self.<name>.dump'''
        return self.__dict__[name].dump()