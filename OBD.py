# import serial
import time
import binascii
import logging
import re

logger = logging.getLogger(__name__)

def hexToString(hexadecimal):
	return str(hex(hexadecimal))[2:].zfill(2)

class OBD():

	__TAXAS = [38400, 9600, 230400, 115200, 57600, 19200]
	__pids_suportados = []
	ELM_PROMPT = b'>'

	def __init__(self, porta):
		self.__conexao = None

		if True == False:
			try:
				self.__conexao = serial.Serial(porta, parity = serial.PARITY_NONE, stopbits = 1, bytesize = 8, timeout = 10)
			except serial.SerialException as e:
				self.__error(e)
				return
			except OSError as e:
				self.__error(e)
				return

			if not self.__setar_taxa_transmissao():
				self.__error("Falha ao setar taxa de transmissão")
				return

			try:
				self.__enviar(b"ATZ", delay=1) # wait 1 second for ELM to initialize
				# return data can be junk, so don't bother checking
			except serial.SerialException as e:
				self.__error(e)
				return

			r = self.__enviar(b"ATE0")
			if not self.__isok(r, expectEcho=True):
				self.__error("ATE0 did not return 'OK'")
				return

		self.__verificar_comandos_suportados()


	def __verificar_comandos_suportados(self):
		logger.info("querying for supported commands")
		pids_de_verificacao = [0x00, 0x20, 0x40]

		retornos = [['41 00 BE 1F A8 13'],['41 20 90 05 B0 15'],['41 40 7A DC 80 01']]

		for i in range(len(pids_de_verificacao)):
			pid_de_verificacao = hexToString(pids_de_verificacao[i])
			retorno = self.__formatar_retorno(pid_de_verificacao, retornos[i])
			# retorno = self.executar_comando(pid_de_verificacao)
			logger.info("Retorno do pid %s: %s" % (pid_de_verificacao, ''.join(retorno)))

			retorno_binario = ''
			for j in range(len(retorno)):
				retorno_binario = retorno_binario + bin(int(retorno[j], 16))[2:].zfill(8)

			for k in range(len(retorno_binario)):
				if retorno_binario[k] == '1':
					pid_suportado = hex(k + 1 + int(pids_de_verificacao[i]))
					self.__pids_suportados.append(pid_suportado)

		print(self.__pids_suportados)

		logger.info("finished querying with %d commands supported" % len(self.__pids_suportados))

	def __formatar_retorno(self, cmd, retorno):
		retorno = retorno[0].split(" ")
		if retorno[0] == '41' and retorno[1] == cmd:
			return retorno[2:]

	def executar_comando(self, cmd, force = False):
		logger.info("Sending command: %s" % str(cmd))
		retorno = self.__enviar(cmd)
		return self.__formatar_retorno(mensagem) # compute a response object

	def __setar_taxa_transmissao(self):
		for taxa in self.__TAXAS:
			self.__conexao.baudrate = taxa
			self.__conexao.flushInput()
			self.__conexao.flushOutput()

			self.__conexao.write(b"\x7F\x7F\r\n")
			self.__conexao.flush()
			response = self.__conexao.read(1024)

			if response.endswith(b">"):
				return True

		return True

	def __enviar(self, cmd, delay = None):
		self.__escrever(cmd)

		if delay is not None:
			time.sleep(delay)

		return self.__ler()

	def __escrever(self, cmd):
		if self.__conexao:
			cmd += b"\r\n"
			logger.debug("write: " + repr(cmd))
			self.__conexao.flushInput()
			self.__conexao.write(cmd)
			self.__conexao.flush()
		else:
			logger.info("cannot perform __escrever() when unconnected")

	def __isok(self, lines, expectEcho=False):
		if not lines:
			return False
		if expectEcho:
			# don't test for the echo itself
			# allow the adapter to already have echo disabled
			return self.__has_message(lines, 'OK')
		else:
			return len(lines) == 1 and lines[0] == 'OK'

	def __has_message(self, lines, text):
		for line in lines:
			if text in line:
				return True
		return False

	def __ler(self):
		if not self.__conexao:
			logger.info("cannot perform __ler() when unconnected")
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