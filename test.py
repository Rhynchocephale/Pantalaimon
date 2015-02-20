import os

def minuslen(thing):
	return -len(thing[0])
	
a = open("/home/clement/subfolders.txt","w")
for k in sorted(os.walk("/home/clement/Pictures"),key=minuslen):
	a.write(str(k)+"\n")
a.close()
