# 38400, 9600 are the possible boot bauds (unless reprogrammed via
# PP 0C).  19200, 38400, 57600, 115200, 230400, 500000 are listed on
# p.46 of the ELM327 datasheet.
#
# Once pyserial supports non-standard baud rates on platforms other
# than Linux, we'll add 500K to this list.
#
# We check the two default baud rates first, then go fastest to
# slowest, on the theory that anyone who's using a slow baud rate is
# going to be less picky about the time required to detect it.
import OBD
import comandos
import sympy


OBD.logger.setLevel(OBD.logging.DEBUG)

# OBD.OBD('/dev/rfcomm1')


# print(comandos.comandos)

A = 2
B = 3
C = 4
D = 5

for k in comandos.comandos:
	comando = comandos.comandos[k]
	retorno = '0F15CD11'
	A = retorno[0:2]
	B = retorno[2:4]
	C = retorno[4:6]
	D = retorno[6:8]

	# if comando != None and comando['sistema_numerico'] == 'dec':
		# print(comando['descricao'])
		# for conversor in comando['conversor']:
			# print(sympy.sympify(conversor).subs(dict(A=int(A, 16), B=int(B, 16), C=int(C, 16), D=int(D, 16))))
	if comando != None and comando['sistema_numerico'] == 'bin':
		retorno_binario = bin(int(retorno, 16))[2:]
		print(retorno_binario)
		for i in range(comando['bytes'])

