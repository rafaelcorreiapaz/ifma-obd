import OBD
import comandos
import sympy


# ['41 00 BE 1F A8 13']
# ['41 20 90 05 B0 15']
# ['41 40 7A DC 80 01']


OBD.logger.setLevel(OBD.logging.DEBUG)

obd = OBD.OBD('/dev/rfcomm0')
print(obd.retornar_codigos_de_erro())
# pids_suportados = obd.retornar_pids_suportados()

# print(pids_suportados)
# for k in pids_suportados:
# 	if k in comandos.comandos:
# 		comando = comandos.comandos[k]
# 		if comando != None:
# 			print(k, end=' - ')
# 			retorno = obd.executar_comando(comando['comando'])
# 			if comando['sistema_numerico'] == 'dec':
# 				if retorno != None:
# 					A = retorno[0]
# 					B = retorno[1] if 1 in retorno else '0'
# 					C = retorno[2] if 2 in retorno else '0'
# 					D = retorno[3] if 3 in retorno else '0'

# 					print(comando['descricao'], end=': ')
# 					for i in range(len(comando['conversor'])):
# 						print(eval(str(sympy.sympify(comando['conversor'][i]).subs(dict(A=int(A, 16), B=int(B, 16), C=int(C, 16), D=int(D, 16))))), end=' ')
# 						print(comando['unidade'][i], end=', ')
# 					print()
# 			elif comando['sistema_numerico'] == 'bin':
# 				print(comando['descricao'], end=': ')
# 				retorno_binario = ''
# 				for j in range(len(retorno)):
# 					retorno_binario = retorno_binario + bin(int(retorno[j], 16))[2:].zfill(8)

# 				for k in range(len(retorno_binario)):
# 					if retorno_binario[k] == '1':
# 						print(comando['conversor'][k], end = '')

# 			else:
# 				print(retorno)
# 				# print(comando['sistema_numerico'])

