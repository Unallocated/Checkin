#!/usr/bin/python

# buddy : 2015-12-05 : barcode checking system

###############################################################################
# Start Python Script
###############################################################################

import sys
import getopt
import os
import glob
import datetime
import time
import base64

for arg in sys.argv: # Getting command-line arguments to trigger closing the space process.
 if arg == 'closing':
  fclosing = open('../Users/ciusers', 'w')
  fclosing.writelines('')
  fclosing.close()
  print "Removing logged in users."
  # sys.exit(0)

SpeakEnable = True

bcAdmin = "9781441888068"
bcDevice = glob.glob('/dev/hidraw*')[0]
bcTemp = open(bcDevice)
print bcTemp
bcValue = ''

ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

phrase = '"The Check-In system is online."'
if SpeakEnable:
     os.system('espeak ' + phrase + ' | paplay')

###############################################################################
# Functions
###############################################################################
def only_numerics(seq):
    seq_type= type(seq)
    return seq_type().join(filter(seq_type.isdigit, seq))

def guFile(fi): # Get user from user file.
        f=open(fi,'r')
        usrar={}
        for line in f:
                usr,id=line.strip().split(':')
                usrar[id]=usr
        f.close()
        return usrar

def auFile(fi,user,id): # Add user to user file.
        global bcReader
	f=open(fi,'a')
        f.write("%s:%s\n" % (user,id))
        f.close()
	bcReader[fi][id]=user

def ruFile(fi,user,id): # Remove user from user file.
        global bcReader
	fdelete = open(fi)
	output = []
	for line in fdelete:
	    if not user+":"+id in line:
	        output.append(line)
	fdelete.close()
	fdelete = open(fi, 'w')
	fdelete.writelines(output)
	fdelete.close()
	bcReader[fi][id]=user

def checkinUser(id,user): # Check-In user.
        global bcReader
	phrase = '"Welcome back to the space, ' + user + '"'
        if SpeakEnable: 
		os.system('espeak ' + phrase + ' | paplay')

        bcReader['../Users/users'][id]=user
        auFile('../Users/ciusers',user,id)
        bcReader['../Users/ciusers'][id]=user
        print user+" has checked into the space. (" + id + ")"
	MsgText = user+" has checked into the space. (" + id + ")"

	f=open("../Users/checkin.log","a")
	f.write(st +" "+MsgText+"\n")
	f.close()

def checkoutUser(id,user): # Check-Out user.
        global bcReader
	phrase = '"Good bye, ' + user + '"'
        if SpeakEnable: 
                os.system('espeak ' + phrase + ' | paplay')
 
        bcReader['../Users/users'][id]=user
        ruFile('../Users/ciusers',user,id)
        bcReader['../Users/ciusers'][id]=user
        print user+" has checked out of the space. (" + id + ")"
	MsgText = user+" has checked out of the space. (" + id + ")"

	f=open("../Users/checkin.log","a")
	f.write(st +" "+MsgText+"\n")
	f.close()

def statusUser(bcData): # Reads and modifies users.

        global bcReader
        bcReader['../Users/users']=guFile('../Users/users')
        bcReader['../Users/ciusers']=guFile('../Users/ciusers')

	if bcData in bcReader['../Users/users'] and bcData in bcReader['../Users/ciusers']: # User already checked in.
                #print bcReader['../Users/users'][bcData]+" has already checked in. ("+bcData+")"
		checkoutUser(bcData,bcReader['../Users/users'][bcData])
		bcReader['last_code'] = bcData

        elif bcData in bcReader['../Users/users']: # User not checked in.
                checkinUser(bcData,bcReader['../Users/users'][bcData])
		bcReader['last_code'] = bcData

	#admin barcode to add users.
        elif bcData == bcAdmin and bcReader['last_code'] != '':

		phrase = '"Entering admin barcode mode, scan a unknown barcode."'
		if SpeakEnable:
			os.system('espeak ' + phrase + ' | paplay')

		print "Entering admin barcode mode. ("+bcData+")"

		if bcReader['last_code'] != bcAdmin and bcReader['last_code'] not in bcReader['../Users/users']:
               		print "add the barcode. ("+bcReader['last_code']+")"
			phrase = '"Adding unknown barcode '+bcReader['last_code']+' with admin barcode. Please enter a new user now."'
        		if SpeakEnable: 
				os.system('espeak ' + phrase + ' | paplay')
                        new_user=raw_input('Please enter a new user: ')
               		#might as well filter input here
			auFile('../Users/users',new_user,bcReader['last_code'])
			print "added user %s " % new_user

    	elif bcData not in bcReader['../Users/users'] and bcData != '': # Unknown barcode.
		phrase = '"Unknown Barcode"'
        	if SpeakEnable: 
			os.system('espeak ' + phrase + ' | paplay')

		print "Unknown barcode. (Barecode: "+bcData+", Base64: "+base64.b64encode(bcData)+")"
		bcReader['last_code'] = bcData


###############################################################################
# Updates barcode reader's status.
###############################################################################
bcReader={}
bcReader['last_code'] = ''
bcReader['code']=''
bcReader['../Users/users'] = guFile('../Users/users')
bcReader['../Users/ciusers'] = guFile('../Users/ciusers')

###############################################################################
# Checks barcode readers connection.
###############################################################################
if bcDevice == False:
  print "Unable to open handle to barcode scanner!"
else:
  try:
    print "Opened handle to barcode scanner on",bcDevice
  except Exception, e:
    print "Unable to open",bcDevice,": ",str(e)
if bcValue == False:
  print "Unable to open handle to barcode scanner!"
  exit()

###############################################################################
# Loops barcode reader entries.
##############################################################################
while True:
    
	bcValue = bcTemp.read(32) # Reads temporary barcode string.
	bcValue = bcValue.strip("\x00") # Cleans up NULL(NUL) ascii hex
	bcValue = bcValue.strip("\x06") # Cleans up ACKNOWLEDGE (ACK) ascii hex
	bcValue = bcValue.strip("\x08") # Cleans up BACKSPACE (BS) ascii hex.
	bcValue = bcValue.strip() # Cleans up WHITE SPACE ascii hex.
	if bcValue is None:
		continue
        statusUser(bcValue)


#only_numerics(bcValue)
    	
###############################################################################
# End
###############################################################################
