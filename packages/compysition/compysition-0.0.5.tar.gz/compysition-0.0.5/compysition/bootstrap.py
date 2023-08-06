#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  bootstrap.py
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

from compysition.router import Default
import pkg_resources
from multiprocessing import Process
from prettytable import PrettyTable
import signal
import daemon
import argparse
import yaml
import sys
import time
import os
import re

class PidHandling():
    def writePids(self, pids, filename):
        with open (filename,'w') as f:
            f.write("\n".join(pids))

    def readPids(self, filename):
        try:
            with open (filename,'r') as f:
                return [str(a.strip()) for a in f.readlines()]
        except Exception as err:
            print "Unable to open pidfile %s.  Reason: %s"%(filename, err)
            sys.exit(0)

    def deletePids(self, filename):
        os.remove(filename)

class ModuleHandling():

    def extractSummary(self, entrypoint):
        try:
            doc=entrypoint.load().__doc__
        except Exception as err:
            return "! -> Unable to load.  Reason: %s"%(err)
        try:
            return re.search('.*?\*\*(.*?)\*\*', doc, re.DOTALL ).group(1)
        except:
            return "No description found."

    def loadModule(self, entrypoint):
        '''Loads a module from an entrypoint string and returns it.'''

        e=entrypoint.split('.')
        name=e[-1]
        del(e[-1])
        group=".".join(e)
        module_instance=None

        for module in pkg_resources.iter_entry_points(group=group, name=name):
            try:
                module_instance=module.load()
            except Exception as err:
                raise Exception ("Problem loading module %s  Reason: %s"%(module, err))

        if module_instance != None:
            return module_instance
        else:
            raise Exception ("Failed to load module %s  Reason: Not found"%(entrypoint))


    def getVersion(self, entrypoint):
        modulename = vars(entrypoint)["module_name"].split('.')[0]

        try:
            return pkg_resources.get_distribution(modulename).version
        except Exception as err:
            return "Unknown"

class Initialize(ModuleHandling):
    def __init__(self, filename):
        self.filename=filename
        self.config=None
        self.router=Default(interval=1, rescue=False, uuid=False)

    def setup(self):
        self.config=self.loadConfig(self.filename)
        self.setupLogging()
        self.setupMetrics()
        self.setupModules()
        self.setupConnections()

    def setupMetrics(self):
        '''Sets up the metrics portion of the Compysition instance.

        If no metrics section is defined in the bootstrap file it connects the
        null module to the metrics starting point to make sure that queue
        isn't filling up. '''

        if "metrics" in self.config:
            for instance in self.config["metrics"]:
                module = self.loadModule(self.config["metrics"][instance]["module"])
                self.router.registerMetricModule(module, instance, **self.config["metrics"][instance].get("arguments",{}))
        else:
            module = self.loadModule("compysition.builtin.output.null")
            self.router.registerMetricModule(module, "metrics_null")

    def setupModules(self):
        '''Registers all bootstrap file defined modules in the router.'''


        for instance in self.config["modules"]:
            module = self.loadModule(self.config["modules"][instance]["module"])
            try:
                self.router.register(module, instance, **self.config["modules"][instance].get("arguments",{}))
            except Exception as err:
                raise Exception ("Failed to initialize module %s.  Reason: %s"%(instance, err))

    def setupConnections(self):
        '''Makes all connections defined in the bootstrap file.'''

        for connection in self.config["routingtable"]:
            try:
                source=connection.split('->')[0].strip()
                destination=connection.split('->')[1].strip()
            except Exception as err:
                sys.stderr.write("There seems to be a routing table format error in this rule: %s\n"%(connection))
                sys.stderr.flush()
                sys.exit(1)
            self.router.connect(source, destination)

    def loadConfig(self, filename):

        '''Loads the bootstrap file from disk and converts it from YAML to
        Python object.'''

        try:
            with open (filename, 'r') as f:
                return yaml.load(f)
        except Exception as err:
            print "Failed to load config file.  Reason: %s"%(err)
            sys.exit(1)

    def start(self):
        '''Starts the Compysition instance bootstrapped from file.'''

        self.router.start()
        self.router.block()

class Start(Initialize):

    def setupLogging(self):
        '''Sets up logging in case we're running in start mode.

        If the bootstrap file has no log section logs are written to syslog.
        '''

        if "logs" in self.config:
            for instance in self.config["logs"]:
                module = self.loadModule(self.config["logs"][instance]["module"])
                self.router.registerLogModule(module, instance, **self.config["logs"][instance].get("arguments",{}))
        else:
            loglevelfilter=self.loadModule("compysition.builtin.logging.loglevelfilter")
            self.router.registerLogModule(loglevelfilter, "loglevelfilter")

            syslog=self.loadModule("compysition.builtin.output.syslog")
            self.router.register(syslog, "syslog")

            self.router.connect("loglevelfilter.outbox", "syslog.inbox")

class Debug(Initialize):

    def setupLogging(self):
        '''Sets up logging in case we're running in debug mode.

        If the bootstrap file has no log section logs are written to stdout.
        '''

        if "logs" in self.config:
            for instance in self.config["logs"]:
                module = self.loadModule(self.config["logs"][instance]["module"])
                self.router.registerLogModule(module, instance, **self.config["logs"][instance].get("arguments",{}))
        else:
            loglevelfilter=self.loadModule("compysition.builtin.logging.loglevelfilter")
            self.router.registerLogModule(loglevelfilter, "loglevelfilter")

            humanlogformatter=self.loadModule("compysition.builtin.logging.humanlogformatter")
            self.router.register(humanlogformatter, "humanlogformatter")

            stdout=self.loadModule("compysition.builtin.output.stdout")
            self.router.register(stdout, "stdout_logs")

            self.router.connect("loglevelfilter.outbox", "humanlogformatter.inbox")
            self.router.connect("humanlogformatter.outbox", "stdout_logs.inbox")

class Stop(PidHandling):

    def __init__(self, pid):
        self.pid=pid

    def do(self):
        '''Initiates the stopping process.'''

        pids=self.readPids(self.pid)
        for pid in pids:
            os.kill(int(pid), signal.SIGINT)
        sys.stdout.write("Stopping instances .")
        for pid in pids:
            while True:
                sys.stdout.write(".")
                sys.stdout.flush()
                try:
                    os.kill(int(pid), 0)
                    time.sleep(1)
                except:
                    break
        self.deletePids(self.pid)
        print("")

class Kill(PidHandling):

    def __init__(self, pid):
        self.pid=pid

    def do(self):
        '''Kills all processes.'''

        print ("Killing all processes")
        pids=self.readPids(self.pid)
        for pid in pids:
            os.kill(int(pid), signal.SIGKILL)
        self.deletePids(self.pid)

class List(ModuleHandling):

    def __init__(self, group ):
        self.group=group
        self.current_version=pkg_resources.get_distribution('compysition').version

    def do(self):
        '''Produces an overview of all available Compysition modules.'''

        groups=[ "compysition.builtin.logging", "compysition.builtin.metrics", "compysition.builtin.flow",
        "compysition.builtin.function", "compysition.builtin.input","compysition.builtin.output",
        "compysition.input","compysition.output","compysition.function"]

        print ("Available Compysition modules:")
        table = PrettyTable(["Group","Module","Version","Description"])
        table.align["Group"]='l'
        table.align["Module"]='l'
        table.align["Version"]='l'
        table.align["Description"]='l'

        if self.group != None:
            groups = [self.group]

        for group in groups:
            g=group
            for module in pkg_resources.iter_entry_points(group=group, name=None):
                if g.startswith("compysition.builtin"):
                    table.add_row([group, str(module).split()[0], self.current_version, self.extractSummary(module)])
                else:
                    table.add_row([group, str(module).split()[0], self.getVersion(module), self.extractSummary(module)])
                group=""
            table.add_row(["","","",""])

        print table

class Show(ModuleHandling):

    def __init__(self, module):
        self.module=module

    def do(self):
        module = self.loadModule(self.module)
        print module.__doc__

class Dispatch(PidHandling):

    def __init__(self):
        self.procs=[]

    def createDebugInstance(self, config):
        instance=Debug(config)
        instance.setup()
        instance.start()

    def createStartInstance(self, config):
        instance=Start(config)
        instance.setup()
        instance.start()

    def daemonize(self, config, instances, pid):
        if instances == 1:
            self.writePids([str(os.getpid())], pid)
            self.createStartInstance(config)
        else:
            procs = []
            for wb in range(instances):
                procs.append(Process(target=self.createStartInstance, args=(config,)))
                procs[-1].daemon=True
                procs[-1].start()
            try:
                self.writePids([str(a.pid) for a in procs]+[str(os.getpid())], pid)
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                for proc in procs:
                    proc.join()

    def debug(self, command, config, instances):
        if instances == 1:
            self.createDebugInstance(config)
        else:
            procs = []
            for wb in range(instances):
                procs.append(Process(target=self.createDebugInstance, args=(config,)))
                procs[-1].daemon=True
                procs[-1].start()

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                for proc in procs:
                    proc.join()

    def start(self, command, config, instances, pid):

        print "Starting %s compysition instances in background.  Logs are written to syslog. Pidfile is %s"%(instances, pid)
        with daemon.DaemonContext(stdout = sys.stdout, stderr = sys.stderr, working_directory=os.getcwd()):
            self.daemonize(config, instances, pid)

    def stop(self, command, pid):
        stop=Stop(pid)
        stop.do()

    def kill(self, command, pid):
        kill=Kill(pid)
        kill.do()

    def list(self, command, group):
        lst=List(group)
        lst.do()

    def show(self, command, module):
        show=Show(module)
        show.do()

class BootStrap():

    def __init__(self, description="Compysition bootstrap server."):
        parser = argparse.ArgumentParser(description=description)
        subparsers = parser.add_subparsers(dest='command')

        start = subparsers.add_parser('start', description="Starts a Compysition instance and detaches to the background.  Logs are written to syslog.")
        start.add_argument('--config', type=str, dest='config', default='compysition.cfg', help='The Compysition bootstrap file to load.')
        start.add_argument('--instances', type=int, dest='instances', default=1, help='The number of parallel Compysition instances to bootstrap.')
        start.add_argument('--pid', type=str, dest='pid', default='compysition.pid', help='The pidfile to use.')

        debug = subparsers.add_parser('debug', description="Starts a Compysition instance in foreground and writes logs to STDOUT.")
        debug.add_argument('--config', type=str, dest='config', default='compysition.cfg', help='The Compysition bootstrap file to load.')
        debug.add_argument('--instances', type=int, dest='instances', default=1, help='The number of parallel Compysition instances to bootstrap.')

        stop = subparsers.add_parser('stop', description="Tries to gracefully stop the Compysition instance.")
        stop.add_argument('--pid', type=str, dest='pid', default='compysition.pid', help='The pidfile to use.')

        kill = subparsers.add_parser('kill', description="Kills the Compysition processes immediately.")
        kill.add_argument('--pid', type=str, dest='pid', default='compysition.pid', help='The pidfile to use.')

        llist = subparsers.add_parser('list', description="Lists the available Compysition modules.")
        llist.add_argument('--group', type=str, dest='group', default=None, help='List the modules of this group type.')

        show = subparsers.add_parser('show', description="Shows the details of a module.")
        show.add_argument('module', type=str, help='Shows the documentation of the module. ')

        arguments=vars(parser.parse_args())

        dispatch=Dispatch()
        getattr(dispatch, arguments["command"])(**arguments)

def main():

    try:
        BootStrap()
    except Exception as err:
        sys.stderr.write("Failed to bootstrap instance.  Reason: %s\n"%(err))
        sys.stderr.flush()
        sys.exit(1)

if __name__ == '__main__':
    main()