# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# Thomas Quintana <quintana.thomas@gmail.com>

from freepy.conf.settings import *
from freepy.lib.commands import *
from freepy.lib.core import *
from freepy.lib.esl import *
from freepy.lib.fsm import *
from freepy.lib.services import *
from pykka import ActorRegistry, ThreadingActor
from twisted.internet import reactor

import logging
import re
import sys
import urllib

# Commands used only by the Freepy server.
class AuthCommand(object):
  def __init__(self, password):
    self.__password__ = password

  def __str__(self):
    return 'auth %s\n\n' % (self.__password__)

class EventsCommand(object):
  def __init__ (self, events, format = 'plain'):
    if(not format == 'json' and not format == 'plain' and not format == 'xml'):
      raise ValueError('The FreeSWITCH event socket only supports the \
        following formats: json, plain, xml')
    self.__events__ = events
    self.__format__ = format

  def __str__(self):
    return 'event %s %s\n\n' % (self.__format__, ' '.join(self.__events__))

# Events used only between the Dispatcher and the Dispatcher Proxy.
class InitializeDispatcherEvent(object):
  def __init__(self, apps, client, events):
    self.__apps__ = apps
    self.__client__ = client
    self.__events__ = events

  def get_apps(self):
    return self.__apps__

  def get_client(self):
    return self.__client__

  def get_events(self):
    return self.__events__

class KillDispatcherEvent(object):
  pass

# Commands used between the Switchlets and the Dispatcher.
class RegisterJobObserverCommand(object):
  def __init__(self, observer, uuid):
    self.__observer__ = observer
    self.__job_uuid__ = uuid

  def get_job_uuid(self):
    return self.__job_uuid__

  def get_observer(self):
    return self.__observer__

class UnregisterJobObserverCommand(object):
  def __init__(self, uuid):
    self.__job_uuid__ = uuid

  def get_job_uuid(self):
    return self.__job_uuid__

class UnwatchEventCommand(object):
  def __init__(self, *args, **kwargs):
    self.__name__ = kwargs.get('name', None)
    self.__pattern__ = kwargs.get('pattern', None)
    self.__value__ = kwargs.get('value', None)
    if not self.__name__ or self.__pattern__ and self.__value__:
      raise ValueError('Please specify a name and a pattern or a value but not both.')

  def get_name(self):
    return self.__name__

  def get_pattern(self):
    return self.__pattern__

  def get_value(self):
    return self.__value__

class WatchEventCommand(UnwatchEventCommand):
  def __init__(self, *args, **kwargs):
    super(WatchEventCommand, self).__init__(*args, **kwargs)
    self.__observer__ = args[0]

  def get_observer(self):
    return self.__observer__

# The Core server components.
class ApplicationFactory(object):
  def __init__(self, dispatcher):
    self.__classes__ = dict()
    self.__singletons__ = dict()
    self.__init_event__ = InitializeSwitchletEvent(dispatcher)
    self.__uninit_event__ = UninitializeSwitchletEvent()

  def __contains_name__(self, name):
    return self.__classes__.has_key(name) or self.__singletons__.has_key(name)

  def __get_klass__(self, name):
    module = sys.modules.get(name)
    if not module:
      separator = name.rfind('.')
      path = name[:separator]
      klass = name[separator + 1:]
      module = __import__(path, globals(), locals(), [klass], -1)
      return getattr(module, klass)

  def get_instance(self, name):
    klass = self.__classes__.get(name)
    if klass:
      instance = klass().start()
      instance.tell({'content': self.__init_event__})
      return instance
    else:
      instance = self.__singletons__.get(name)
      return instance

  def register(self, name, type = 'class'):
    if self.__contains_name__(name):
      raise ValueError("Names must be unique across classes and singletons.\n\
      %s already exists please choose a different name and try again.",
      name)
    klass = self.__get_klass__(name)
    if type == 'class':
      self.__classes__.update({name: klass})
    if type == 'singleton':
      singleton = klass.start()
      singleton.tell({'content': self.__init_event__})
      self.__singletons__.update({name: singleton})

  def unregister(self, name):
    klass = self.__classes__.get(name)
    if klass:
      del self.__classes__[name]
    else:
      singleton = self.__singletons__.get(name)
      singleton.tell({'content': self.__uninit_event__})
      if singleton:
        singleton.stop()
        del self.__singletons__[name]

  def shutdown(self):
    # Cleanup the singletons being managed.
    names = self.__singletons__.keys()
    for name in names:
      self.unregister(name) 

class DispatcherProxy(IEventSocketClientObserver):
  def __init__(self, apps, dispatcher, events):
    self.__apps__ = apps
    self.__dispatcher__ = dispatcher
    self.__events__ = events

  def on_event(self, event):
    self.__dispatcher__.tell({'content': event})

  def on_start(self, client):
    event = InitializeDispatcherEvent(self.__apps__, client, self.__events__)
    self.__dispatcher__.tell({'content': event})

  def on_stop(self):
    event = KillDispatcherEvent()
    self.__dispatcher__.tell({'content': event})

class Dispatcher(FiniteStateMachine, ThreadingActor):
  initial_state = 'not ready'

  transitions = [
    ('not ready', 'authenticating'),
    ('authenticating', 'failed authentication'),
    ('authenticating', 'initializing'),
    ('initializing', 'failed initialization'),
    ('initializing', 'dispatching'),
    ('dispatching', 'dispatching'),
    ('dispatching', 'done')
  ]

  def __init__(self, *args, **kwargs):
    super(Dispatcher, self).__init__(*args, **kwargs)
    self.__logger__ = logging.getLogger('freepy.lib.server.dispatcher')
    self.__observers__ = dict()
    self.__transactions__ = dict()
    self.__watches__ = list()

  @Action(state = 'authenticating')
  def __authenticate__(self, message):
    password = freeswitch_host.get('password')
    auth_command = AuthCommand(password)
    self.__client__.send(auth_command)

  @Action(state = 'done')
  def __cleanup__(self, message):
    self.__apps__.shutdown()
    self.stop()

  @Action(state = 'dispatching')
  def __dispatch__(self, message):
    if message:
      if isinstance(message, BackgroundCommand):
        self.__dispatch_command__(message)
      elif isinstance(message, ServiceRequest):
        self.__dispatch_service_request__(message)
      elif isinstance(message, RegisterJobObserverCommand):
        observer = message.get_observer()
        uuid = message.get_job_uuid()
        if observer and uuid:
          self.__observers__.update({uuid: observer})
      elif isinstance(message, UnregisterJobObserverCommand):
        uuid = message.get_job_uuid()
        if self.__observers__.has_key(uuid):
          del self.__observers__[uuid]
      else:
        headers = message.get_headers()
        content_type = headers.get('Content-Type')
        if content_type == 'command/reply':
          uuid = headers.get('Job-UUID')
          if uuid:
            self.__dispatch_response__(uuid, message)
        elif content_type == 'text/event-plain':
          uuid = headers.get('Job-UUID')
          if uuid:
            self.__dispatch_observer_event__(uuid, message)
          else:
            self.__dispatch_incoming__(message)

  def __dispatch_command__(self, message):
    # Make sure we can route the response to the right actor.
    uuid = message.get_job_uuid()
    sender = message.get_sender()
    self.__transactions__.update({uuid: sender})
    # Send the command.
    self.__client__.send(message)

  def __dispatch_incoming__(self, message):
    if not self.__dispatch_incoming_using_dispatch_rules__(message) and \
       not self.__dispatch_incoming_using_watches__(message):
      self.__logger__.info('No route was defined for the following message.\n \
      %s\n%s', str(message.get_headers()), str(message.get_body()))

  def __dispatch_incoming_using_dispatch_rules__(self, message):
    headers = message.get_headers()
    # Dispatch based on the pre-defined dispatch rules.
    for rule in dispatch_rules:
      target = rule.get('target')
      name = rule.get('header_name')
      header = headers.get(name)
      if not header:
        continue
      header = urllib.unquote_plus(header)
      value = rule.get('header_value')
      if value and header == value:
        self.__apps__.get_instance(target).tell({'content': message})
        return True
      pattern = rule.get('header_pattern')
      if pattern:
        match = re.search(pattern, header)
        if match:
          self.__apps__.get_intance(target).tell({'content': message})
          return True
    return False

  def __dispatch_incoming_using_watches__(self, message):
    headers = message.get_headers()
    # Dispatch based on runtime watches defined by switchlets.
    for watch in self.__watches__:
      name = watch.get_name()
      header = headers.get(name)
      if not header:
        continue
      header = urllib.unquote_plus(header)
      value = watch.get_value()
      if value and header == value:
        watch.get_observer().tell({'content': message})
        return True
      pattern = watch.get_pattern()
      if pattern:
        match = re.search(pattern, header)
        if match:
          watch.get_observer().tell({'content': message})
          return True
    return False

  def __dispatch_observer_event__(self, uuid, message):
    recipient = self.__observers__.get(uuid)
    if recipient:
      recipient.tell({'content': message})

  def __dispatch_response__(self, uuid, message):
    recipient = self.__transactions__.get(uuid)
    if recipient:
      del self.__transactions__[uuid]
      recipient.tell({'content': message})

  def __dispatch_service_request__(self, message):
    name = message.__class__.__name__
    target = self.__events__.get(name)
    if target:
      service = self.__apps__.get_instance(target)
      service.tell({ 'content': messsage })

  @Action(state = 'initializing')
  def __initialize__(self, message):
    if 'BACKGROUND_JOB' not in dispatch_events:
      # The BACKGROUND_JOB events must be added at the front of the
      # list in case the list ends with CUSTOM events.
      dispatch_events.insert(0, 'BACKGROUND_JOB')
    events_command = EventsCommand(dispatch_events)
    self.__client__.send(events_command)

  def __on_auth__(self, message):
    if self.state() == 'not ready':
      self.transition(to = 'authenticating', event = message)

  def __on_command__(self, message):
    if self.state() == 'dispatching':
      self.transition(to = 'dispatching', event = message)

  def __on_command_reply__(self, message):
    reply = message.get_header('Reply-Text')
    if self.state() == 'authenticating':
      if reply == '+OK accepted':
        self.transition(to = 'initializing', event = message)
      elif reply == '-ERR invalid':
        self.transition(to = 'failed authentication', event = message)
    if self.state() == 'initializing':
      if reply == '+OK event listener enabled plain':
        self.transition(to = 'dispatching')
      elif reply == '-ERR no keywords supplied':
        self.transition(to = 'failed initialization', event = message)
    if self.state() == 'dispatching':
      self.transition(to = 'dispatching', event = message)

  def __on_event__(self, message):
    if self.state() == 'dispatching':
      self.transition(to = 'dispatching', event = message)

  def __on_init__(self, message):
    self.__apps__ = message.get_apps()
    self.__client__ = message.get_client()
    self.__events__ = message.get_events()

  def __on_kill__(self, message):
    if self.state() == 'dispatching':
      self.transition(to = 'done', event = message)

  def __on_observer__(self, message):
    if self.state() == 'dispatching':
      self.transition(to = 'dispatching', event = message)

  def __on_service_request__(self, message):
    if self.state() == 'dispatching':
      self.transition(to = 'dispatching', event = message)

  # Watches are not handled as a state change because singleton switchlets
  # may add watches during initialization at which point the dispatcher's
  # FSM is still not ready.
  def __on_watch__(self, message):
    if isinstance(message, WatchEventCommand):
      self.__watches__.append(message)
    elif isinstance(message, UnwatchEventCommand):
      name = message.get_name()
      value = message.get_value()
      if not value:
        value = message.get_pattern()
      match = None
      for watch in self.__watches__:
        if name == watch.get_name() and value == watch.get_value() or \
           value == watch.get_pattern:
          match = watch
      self.__watches__.remove(match)

  def on_failure(self, exception_type, exception_value, traceback):
    self.__logger__.error(exception_value)

  def on_receive(self, message):
    # This is necessary because all Pykka messages
    # must be of type dict.
    message = message.get('content')
    if not message:
      return
    # Handle the message.
    if isinstance(message, Event):
      content_type = message.get_header('Content-Type')
      if content_type == 'auth/request':
        self.__on_auth__(message)
      elif content_type == 'command/reply':
        self.__on_command_reply__(message)
      elif content_type == 'text/event-plain':
        self.__on_event__(message)
    elif isinstance(message, BackgroundCommand):
      self.__on_command__(message)
    elif isinstance(message, ServiceRequest):
      self.__on_service_request__(message)
    elif isinstance(message, RegisterJobObserverCommand):
      self.__on_observer__(message)
    elif isinstance(message, UnregisterJobObserverCommand):
      self.__on_observer__(message)
    elif isinstance(message, InitializeDispatcherEvent):
      self.__on_init__(message)
    elif isinstance(message, KillDispatcherEvent):
      self.__on_kill__(message)
    elif isinstance(message, UnwatchEventCommand):
      self.__on_watch__(message)
    elif isinstance(message, WatchEventCommand):
      self.__on_watch__(message)

class FreepyServer(object):
  def __generate_event_lookup_table__(self):
    lookup_table = dict()
    for service in dispatcher_services:
      events = service.get('events')
      for event in events:
        lookup_table.update({ event: service.get('target') })
    return lookup_table

  def __init__(self, *args, **kwargs):
    self.__logger__ = logging.getLogger('freepy.lib.server.freepyserver')

  def __load_apps_factory__(self, dispatcher):
    factory = ApplicationFactory(dispatcher)
    for rule in dispatch_rules:
      target = rule.get('target')
      persistent = rule.get('persistent')
      if not persistent:
        factory.register(target, type = 'class')
      else:
        factory.register(target, type = 'singleton')
    return factory

  def __load_services__(self, factory):
    for service in dispatcher_services:
      factory.register(service.get('target'), type = 'singleton')

  def __validate_rule__(self, rule):
    name = rule.get('header_name')
    value = rule.get('header_value')
    pattern = rule.get('header_pattern')
    target = rule.get('target')
    if not name or not target or not value and not pattern \
      or value and pattern:
      return False
    else:
      return True

  def start(self):
    # Initialize application wide logging.
    logging.basicConfig(filename = logging_filename, format = logging_format,
      level = logging_level)
    # Validate the list of rules.
    for rule in dispatch_rules:
      if not self.__validate_rule__(rule):
        self.__logger__.critical('The rule %s is invalid.', str(rule))
        return
    # Create a dispatcher thread.
    dispatcher = Dispatcher().start()
    # Load all the apps.
    apps = self.__load_apps_factory__(dispatcher)
    # Load the dispatcher services.
    self.__load_services__(apps)
    # Generate an event lookup table.
    events = self.__generate_event_lookup_table__()
    # Create the proxy between the event socket client and the dispatcher.
    dispatcher_proxy = DispatcherProxy(apps, dispatcher, events)
    # Create an event socket client factory and start the reactor.
    address = freeswitch_host.get('address')
    port = freeswitch_host.get('port')
    factory = EventSocketClientFactory(dispatcher_proxy)
    reactor.connectTCP(address, port, factory)
    reactor.run()

  def stop(self):
    ActorRegistry.stop_all()
  