# -*- coding: utf-8 -*-
#
# AWL simulator - PLC core server
#
# Copyright 2013 Michael Buesch <m@bues.ch>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

from __future__ import division, absolute_import, print_function, unicode_literals
from awlsim.core.compat import *

from awlsim.core.main import *
from awlsim.core.parser import *
from awlsim.core.cpuspecs import *

from awlsim.coreserver.messages import *

import sys
import os
import distutils.spawn
import subprocess
import select
import signal
import socket
import errno
import time


class AwlSimServer(object):
	DEFAULT_HOST	= "localhost"
	DEFAULT_PORT	= 4151

	ENV_MAGIC	= "AWLSIM_CORESERVER_MAGIC"

	EnumGen.start
	STATE_INIT	= EnumGen.item
	STATE_RUN	= EnumGen.item
	STATE_EXIT	= EnumGen.item
	EnumGen.end

	class Client(object):
		"""Client information."""

		def __init__(self, sock, host, port):
			# Socket
			self.socket = sock
			self.host = host
			self.port = port
			self.transceiver = AwlSimMessageTransceiver(sock)

			# CPU-dump
			self.dumpInterval = 0
			self.nextDump = 0

			# Memory read requests
			self.memReadRequestMsg = None
			self.repetitionFactor = 0
			self.repetitionCount = 0

	@classmethod
	def start(cls, listenHost, listenPort, forkInterpreter=None):
		"""Start a new server.
		If 'forkInterpreter' is not None, spawn a subprocess.
		If 'forkInterpreter' is None, run the server in this process."""

		environment = {
			AwlSimServer.ENV_MAGIC		: AwlSimServer.ENV_MAGIC,
			"AWLSIM_CORESERVER_HOST"	: str(listenHost),
			"AWLSIM_CORESERVER_PORT"	: str(listenPort),
			"AWLSIM_CORESERVER_LOGLEVEL"	: str(Logging.getLoglevel()),
		}

		if forkInterpreter is None:
			return cls._execute(environment)
		else:
			interp = distutils.spawn.find_executable(forkInterpreter)
			if not interp:
				raise AwlSimError("Failed to find interpreter "
						  "executable '%s'" % forkInterpreter)
			serverProcess = subprocess.Popen([interp, "-m", "awlsim.coreserver.server"],
							 env = environment,
							 shell = False)
			return serverProcess

	@classmethod
	def _execute(cls, env=None):
		"""Execute the server process.
		Returns the exit() return value."""

		server, retval = None, 0
		try:
			server = AwlSimServer()
			for sig in (signal.SIGTERM, signal.SIGINT):
				signal.signal(sig, server.signalHandler)
			server.runFromEnvironment(env)
		except AwlSimError as e:
			print(e.getReport())
			retval = 1
		except KeyboardInterrupt:
			print("Interrupted.")
		finally:
			if server:
				server.close()
		return retval

	def __init__(self):
		self.__setRunState(self.STATE_INIT)
		self.sim = None
		self.socket = None
		self.clients = []

	def runFromEnvironment(self, env=None):
		"""Run the server.
		Configuration is passed via environment variables in 'env'.
		If 'env' is not passed, os.environ is used."""

		if not env:
			env = dict(os.environ)

		try:
			loglevel = int(env.get("AWLSIM_CORESERVER_LOGLEVEL"))
		except (TypeError, ValueError) as e:
			raise AwlSimError("AwlSimServer: No loglevel specified")
		Logging.setLoglevel(loglevel)

		if self.socket:
			raise AwlSimError("AwlSimServer: Already running")

		if env.get(self.ENV_MAGIC) != self.ENV_MAGIC:
			raise AwlSimError("AwlSimServer: Missing magic value")

		host = env.get("AWLSIM_CORESERVER_HOST")
		if not host:
			raise AwlSimError("AwlSimServer: No listen host specified")
		try:
			port = int(env.get("AWLSIM_CORESERVER_PORT"))
		except (TypeError, ValueError) as e:
			raise AwlSimError("AwlSimServer: No listen port specified")

		self.run(host, port)

	def __setRunState(self, runstate):
		self.state = runstate
		# Make a shortcut variable for RUN
		self.__running = bool(runstate == self.STATE_RUN)

	def __rebuildSelectReadList(self):
		rlist = [ self.socket ]
		rlist.extend(client.transceiver.sock for client in self.clients)
		self.__selectRlist = rlist

	def __cpuBlockExitCallback(self, userData):
		now = self.sim.cpu.now
		if any(c.dumpInterval and now >= c.nextDump for c in self.clients):
			msg = AwlSimMessage_CPUDUMP(str(self.sim.cpu))
			for client in self.clients:
				if client.dumpInterval and now >= client.nextDump:
					client.nextDump = now + client.dumpInterval / 1000.0
					client.transceiver.send(msg)

	def __updateCpuBlockExitCallback(self):
		if any(c.dumpInterval for c in self.clients):
			self.sim.cpu.setBlockExitCallback(self.__cpuBlockExitCallback, None)
		else:
			self.sim.cpu.setBlockExitCallback(None)

	def __rx_PING(self, client, msg):
		client.transceiver.send(AwlSimMessage_PONG())

	def __rx_PONG(self, client, msg):
		printInfo("AwlSimServer: Received PONG")

	def __rx_RESET(self, client, msg):
		status = AwlSimMessage_REPLY.STAT_OK
		self.__setRunState(self.STATE_INIT)
		self.sim.reset()
		client.transceiver.send(AwlSimMessage_REPLY.make(msg, status))

	def __rx_RUNSTATE(self, client, msg):
		status = AwlSimMessage_REPLY.STAT_OK
		if msg.runState == msg.STATE_STOP:
			self.__setRunState(self.STATE_INIT)
		elif msg.runState == msg.STATE_RUN:
			self.sim.startup()
			self.__setRunState(self.STATE_RUN)
		else:
			status = AwlSimMessage_REPLY.STAT_FAIL
		client.transceiver.send(AwlSimMessage_REPLY.make(msg, status))

	def __rx_LOAD_CODE(self, client, msg):
		status = AwlSimMessage_REPLY.STAT_OK
		parser = AwlParser()
		parser.parseData(msg.code)
		self.__setRunState(self.STATE_INIT)
		self.sim.load(parser.getParseTree())
		client.transceiver.send(AwlSimMessage_REPLY.make(msg, status))

	def __rx_LOAD_SYMTAB(self, client, msg):
		status = AwlSimMessage_REPLY.STAT_OK
		symbolTable = SymTabParser.parseData(msg.symTabText,
						     autodetectFormat = True,
						     mnemonics = self.sim.cpu.getSpecs().getMnemonics())
		self.__setRunState(self.STATE_INIT)
		self.sim.loadSymbolTable(symbolTable)
		client.transceiver.send(AwlSimMessage_REPLY.make(msg, status))

	def __rx_LOAD_HW(self, client, msg):
		status = AwlSimMessage_REPLY.STAT_OK
		printInfo("Loading hardware module '%s'..." % msg.name)
		hwClass = self.sim.loadHardwareModule(msg.name)
		self.sim.registerHardwareClass(hwClass = hwClass,
					       parameters = msg.paramDict)
		client.transceiver.send(AwlSimMessage_REPLY.make(msg, status))

	def __rx_SET_OPT(self, client, msg):
		status = AwlSimMessage_REPLY.STAT_OK

		if msg.name == "loglevel":
			Logging.setLoglevel(msg.getIntValue())
		elif msg.name == "ob_temp_presets":
			self.sim.cpu.enableObTempPresets(msg.getBoolValue())
		elif msg.name == "extended_insns":
			self.sim.cpu.enableExtendedInsns(msg.getBoolValue())
		elif msg.name == "periodic_dump_int":
			client.dumpInterval = msg.getIntValue()
			if client.dumpInterval:
				client.nextDump = self.sim.cpu.now
			else:
				client.nextDump = None
			self.__updateCpuBlockExitCallback()
		elif msg.name == "cycle_time_limit":
			self.sim.cpu.setCycleTimeLimit(msg.getFloatValue())
		else:
			status = AwlSimMessage_REPLY.STAT_FAIL

		client.transceiver.send(AwlSimMessage_REPLY.make(msg, status))

	def __rx_GET_CPUSPECS(self, client, msg):
		reply = AwlSimMessage_CPUSPECS(self.sim.cpu.getSpecs())
		client.transceiver.send(reply)

	def __rx_CPUSPECS(self, client, msg):
		status = AwlSimMessage_REPLY.STAT_OK
		self.sim.cpu.getSpecs().assignFrom(msg.cpuspecs)
		client.transceiver.send(AwlSimMessage_REPLY.make(msg, status))

	def __rx_REQ_MEMORY(self, client, msg):
		client.memReadRequestMsg = AwlSimMessage_MEMORY(0, msg.memAreas)
		client.repetitionFactor = msg.repetitionFactor
		client.repetitionCount = client.repetitionFactor
		if msg.flags & msg.FLG_SYNC:
			client.transceiver.send(AwlSimMessage_REPLY.make(
				msg, AwlSimMessage_REPLY.STAT_OK)
			)

	def __rx_MEMORY(self, client, msg):
		cpu = self.sim.cpu
		for memArea in msg.memAreas:
			memArea.writeToCpu(cpu)
		if msg.flags & msg.FLG_SYNC:
			client.transceiver.send(AwlSimMessage_REPLY.make(
				msg, AwlSimMessage_REPLY.STAT_OK)
			)

	__msgRxHandlers = {
		AwlSimMessage.MSG_ID_PING		: __rx_PING,
		AwlSimMessage.MSG_ID_PONG		: __rx_PONG,
		AwlSimMessage.MSG_ID_RESET		: __rx_RESET,
		AwlSimMessage.MSG_ID_RUNSTATE		: __rx_RUNSTATE,
		AwlSimMessage.MSG_ID_LOAD_CODE		: __rx_LOAD_CODE,
		AwlSimMessage.MSG_ID_LOAD_SYMTAB	: __rx_LOAD_SYMTAB,
		AwlSimMessage.MSG_ID_LOAD_HW		: __rx_LOAD_HW,
		AwlSimMessage.MSG_ID_SET_OPT		: __rx_SET_OPT,
		AwlSimMessage.MSG_ID_GET_CPUSPECS	: __rx_GET_CPUSPECS,
		AwlSimMessage.MSG_ID_CPUSPECS		: __rx_CPUSPECS,
		AwlSimMessage.MSG_ID_REQ_MEMORY		: __rx_REQ_MEMORY,
		AwlSimMessage.MSG_ID_MEMORY		: __rx_MEMORY,
	}

	def __handleClientComm(self, client):
		try:
			msg = client.transceiver.receive()
		except AwlSimMessageTransceiver.RemoteEndDied as e:
			printInfo("AwlSimServer: Client '%s (port %d)' died" %\
				(client.host, client.port))
			self.__clientRemove(client)
			return
		except (TransferError, socket.error) as e:
			printInfo("AwlSimServer: Client '%s (port %d)' data "
				"transfer error:\n%s" %\
				(client.host, client.port, str(e)))
			return
		if not msg:
			return
		try:
			handler = self.__msgRxHandlers[msg.msgId]
		except KeyError:
			printInfo("AwlSimServer: Received unsupported "
				"message 0x%02X" % msg.msgId)
			return
		handler(self, client, msg)

	def __handleCommunication(self):
		while 1:
			try:
				rlist, wlist, xlist = select.select(self.__selectRlist, [], [], 0)
			except Exception as e:
				raise AwlSimError("AwlSimServer: Communication error. "
					"'select' failed")
			if not rlist:
				break
			if self.socket in rlist:
				rlist.remove(self.socket)
				self.__accept()
			for sock in rlist:
				client = [ c for c in self.clients if c.socket is sock ][0]
				self.__handleClientComm(client)

	def __handleMemReadReqs(self):
		for client in self.clients:
			if not client.memReadRequestMsg:
				continue
			client.repetitionCount -= 1
			if client.repetitionCount <= 0:
				cpu, memAreas = self.sim.cpu, client.memReadRequestMsg.memAreas
				for memArea in memAreas:
					memArea.readFromCpu(cpu)
				client.transceiver.send(client.memReadRequestMsg)
				client.repetitionCount = client.repetitionFactor
				if not client.repetitionFactor:
					self.memReadRequestMsg = None

	def run(self, host, port):
		"""Run the server on 'host':'port'."""

		self.__listen(host, port)
		self.__rebuildSelectReadList()

		self.sim = AwlSim()
		nextComm = 0.0

		while self.state != self.STATE_EXIT:
			try:
				sim = self.sim

				if self.state == self.STATE_INIT:
					while self.state == self.STATE_INIT:
						self.__handleCommunication()
						time.sleep(0.01)
					continue

				if self.state == self.STATE_RUN:
					while self.__running:
						self.__handleCommunication()
						sim.runCycle()
						self.__handleMemReadReqs()
					continue

			except (AwlSimError, AwlParserError) as e:
				msg = AwlSimMessage_EXCEPTION(e.getReport())
				for client in self.clients:
					try:
						client.transceiver.send(msg)
					except TransferError as e:
						printError("AwlSimServer: Failed to forward "
							   "exception to client.")
				self.__setRunState(self.STATE_INIT)
			except MaintenanceRequest as e:
				try:
					if self.clients:
						# Forward it to the first client
						msg = AwlSimMessage_MAINTREQ(e.requestType)
						self.clients[0].transceiver.send(msg)
				except TransferError as e:
					pass
			except TransferError as e:
				printError("AwlSimServer: Transfer error: " + str(e))
				self.__setRunState(self.STATE_INIT)

	def __listen(self, host, port):
		"""Listen on 'host':'port'."""

		self.close()
		printInfo("AwlSimServer: Listening on %s (port %d)..." % (host, port))
		try:
			family, socktype, proto, canonname, sockaddr =\
				socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)[0]
			sock = socket.socket(family, socktype)
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			sock.setblocking(False)
			sock.bind(sockaddr)
			sock.listen(5)
		except socket.error as e:
			raise AwlSimError("AwlSimServer: Failed to create server "
				"socket: " + str(e))
		self.socket = sock

	def __accept(self):
		"""Accept a client connection.
		Returns the Client instance or None."""

		if not self.socket:
			raise AwlSimError("AwlSimServer: No server socket")

		try:
			clientSock, addrInfo = self.socket.accept()
			clientHost, clientPort = addrInfo[:2]
		except socket.error as e:
			if e.errno == errno.EWOULDBLOCK or\
			   e.errno == errno.EAGAIN:
				return None
			raise AwlSimError("AwlSimServer: accept() failed: %s" % str(e))
		host, port = addrInfo[0], addrInfo[1]
		printInfo("AwlSimServer: Client '%s (port %d)' connected" % (host, port))

		client = self.Client(clientSock, clientHost, clientPort)
		self.__clientAdd(client)

		return client

	def __clientAdd(self, client):
		self.clients.append(client)
		self.__rebuildSelectReadList()

	def __clientRemove(self, client):
		self.clients.remove(client)
		self.__rebuildSelectReadList()

	def close(self):
		"""Closes all client sockets and the main socket."""

		if self.socket:
			printInfo("AwlSimServer: Shutting down.")

		if self.sim:
			self.sim.shutdown()
			self.sim = None

		for client in self.clients:
			client.transceiver.shutdown()
			client.transceiver = None
			client.socket = None
		self.clients = []

		if self.socket:
			try:
				self.socket.shutdown(socket.SHUT_RDWR)
			except socket.error as e:
				pass
			try:
				self.socket.close()
			except socket.error as e:
				pass
			self.socket = None

	def signalHandler(self, sig, frame):
		printInfo("AwlSimServer: Received signal %d" % sig)
		if sig in (signal.SIGTERM, signal.SIGINT):
			self.__setRunState(self.STATE_EXIT)

if __name__ == "__main__":
	# Run a server process.
	# Parameters are passed via environment.
	sys.exit(AwlSimServer._execute())
