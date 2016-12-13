#from inputs import outputList

aline = 1
eline = 1

not_found = False
logList = []

def actLine(): return aline
def expLine(): return eline
def notFound(): return not_found

def compare(e,a,s,act_list,exp_list):
	global eline,aline,not_found
	expected = open(e)
	actual = open(a)
	seqLog = open(s, 'a+')

	for line in range(act_list):
		actual_line = actual.readline().strip() ##for line in range(act_list)
	for line in range(exp_list):
		expected_line = expected.readline().strip() ##for line in range(exp_list)

	while expected_line != '':
		# if cannot find match before EOF
		if actual_line == '':
			actual.close()
			actual = open(a)
			for line in range(act_list):
				actual_line = actual.readline().strip() ##for line in range(act_list)
		# if match found
		if actual_line.find(expected_line) != -1:
			logList.append(actual_line)
			seqLog.write("Expected line %d matches actual line %d! " % (exp_list,act_list) + expected_line + " > " + actual_line + '\n')
			actual_line = actual.readline().strip()
			act_list += 1
		else:
			if expected_line.find("SEQUENCE") != -1 : pass
			else:
				seqLog.write("Line %d not found during actual test. " % exp_list + expected_line + '\n')
				not_found = True
				logList.append("FAILED")
		expected_line = expected.readline().strip()
		exp_list += 1

	aline = act_list
	eline = exp_list

	actual.close()
	expected.close()
	seqLog.close()

	actLine()
	expLine()
	notFound()
