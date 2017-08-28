import serial
import time
import logging

logger = logging.getLogger(__name__)

class OBD():

	TAXAS = [38400, 9600, 230400, 115200, 57600, 19200]

	def __init__(self, porta):
		try:
			#self.__conexao = serial.Serial(porta, parity = serial.PARITY_NONE, stopbits = 1, bytesize = 8, timeout = 10)
			self.__conexao = None
		except serial.SerialException as e:
			self.__error(e)
			return
		except OSError as e:
			self.__error(e)
			return

		if not self.setar_taxa_transmissao():
			self.__error("Failed to set baudrate")
			return

		try:
			self.__send(b"ATZ", delay=1) # wait 1 second for ELM to initialize
			# return data can be junk, so don't bother checking
		except serial.SerialException as e:
			self.__error(e)
			return

		r = self.__send(b"ATE0")
		if not self.__isok(r, expectEcho=True):
			self.__error("ATE0 did not return 'OK'")
			return

		r = self.__send(b"ATH1")
		if not self.__isok(r):
			self.__error("ATH1 did not return 'OK', or echoing is still ON")
			return

		r = self.__send(b"ATL0")
		if not self.__isok(r):
			self.__error("ATL0 did not return 'OK'")
			return

		# -------------- try the ELM's auto protocol mode --------------
		r = self.__send(b"ATSP0")

		# -------------- 0100 (first command, SEARCH protocols) --------------
		r0100 = self.__send(b"0100")

		# ------------------- ATDPN (list protocol number) -------------------
		r = self.__send(b"ATDPN")
		if len(r) != 1:
			logger.error("Failed to retrieve current protocol")
			return False

		self.__load_commands()

	def __load_commands(self):
		logger.info("querying for supported commands")
		pid_getters = commands.pid_getters()
		for get in pid_getters:
			if not self.test_cmd(get, warn=False):
				continue

			response = self.executar_query(self, get)
			if response.is_null():
				logger.info("No valid data for PID listing command: %s" % get)
				continue

			for i, bit in enumerate(response.value):
				if bit:

					mode = get.mode
					pid  = get.pid + i + 1

					if commands.has_pid(mode, pid):
						self.supported_commands.add(commands[mode][pid])

					# set support for mode 2 commands
					if mode == 1 and commands.has_pid(2, pid):
						self.supported_commands.add(commands[2][pid])

		logger.info("finished querying with %d commands supported" % len(self.supported_commands))


	def executar_query(self, cmd, force = False):
		logger.info("Sending command: %s" % str(cmd))
		messages = self.__send(cmd)

		if not messages:
			logger.info("No valid OBD Messages returned")
			return OBDResponse()

		return cmd(messages) # compute a response object

	def setar_taxa_transmissao(self):
		for taxa in self.TAXAS:
			self.__conexao.baudrate = taxa
			self.__conexao.flushInput()
			self.__conexao.flushOutput()

			self.__conexao.write(b"\x7F\x7F\r\n")
			self.__conexao.flush()
			response = self.__conexao.read(1024)

			if response.endswith(b">"):
				return True

		return True

	def __send(self, cmd, delay = None):
		self.__write(cmd)

		if delay is not None:
			time.sleep(delay)

		return self.__read()

	def __write(self, cmd):
		if self.__conexao:
			cmd += b"\r\n"
			logger.debug("write: " + repr(cmd))
			self.__conexao.flushInput()
			self.__conexao.write(cmd)
			self.__conexao.flush()
		else:
			logger.info("cannot perform __write() when unconnected")

	def __read(self):
		if not self.__conexao:
			logger.info("cannot perform __read() when unconnected")
			return []

		buffer = bytearray()

		while True:
			# retrieve as much data as possible
			data = self.__conexao.read(self.__conexao.in_waiting or 1)

			# if nothing was recieved
			if not data:
				logger.warning("Failed to read port")
				break

			buffer.extend(data)

			# end on chevron (ELM prompt character)
			if self.ELM_PROMPT in buffer:
				break

		# log, and remove the "bytearray(   ...   )" part
		logger.debug("read: " + repr(buffer)[10:-1])

		# clean out any null characters
		buffer = re.sub(b"\x00", b"", buffer)

		# remove the prompt character
		if buffer.endswith(self.ELM_PROMPT):
			buffer = buffer[:-1]

		# convert bytes into a standard string
		string = buffer.decode()

		# splits into lines while removing empty lines and trailing spaces
		lines = [ s.strip() for s in re.split("[\r\n]", string) if bool(s) ]

		return lines