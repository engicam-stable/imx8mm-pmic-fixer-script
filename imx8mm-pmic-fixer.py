#!/usr/bin/python3

import subprocess
import os.path

CONFFILE = "/tmp/fw_env_eng.conf"

def checkMX8MMsoc():	
	file = open('/proc/device-tree/compatible',mode='r')
	compatible = file.read()
	file.close()
	return ('mx8mm' in compatible)

def getMountDevicde():
	file = open('/proc/cmdline',mode='r')
	cmdline = file.read()
	file.close()

	for x in range(6):
		mnt = "mmcblk" + str(x)
		if mnt in cmdline:
			return mnt
	
	return None

def createConfigFile(mountdev):
	line ="/dev/" + mountdev + "             0x400000        0x1000          0x1000"
	f= open(CONFFILE,"w+")
	f.write(line)
	f.close


def getDefaultDTB():
	result = subprocess.run(['fw_printenv', '-c',CONFFILE , 'fdt_file'], stdout=subprocess.PIPE)
	value = result.stdout.decode('utf-8')
	if "not defined" in value:
		return None
	
	return value.replace('fdt_file=', '')


def setDefaultDTB(dtb):
	result = subprocess.run(['fw_setenv', '-c',CONFFILE , 'fdt_file', dtb], stdout=subprocess.PIPE)
	

def getPMICSet():

	if os.path.isfile('/sys/bus/i2c/devices/0-0025/name'):
		return 	"pca9450"

	return None

def main():

	if not checkMX8MMsoc():
		print("no MX8MM found")
		exit(0)

	print("MX8MM found")

	mountdevice = getMountDevicde()
	if mountdevice is None:
		print("No valit mountpoint found !")
		exit(-1)

	print("Rootfs mounted on:" + mountdevice)
	createConfigFile(mountdevice)
	dtb = getDefaultDTB()
	if dtb is None:
		print("Unable to find devicetree")
		exit(-2)
	
	print ("Device tree set: " +dtb)

	pmic=getPMICSet()
	if pmic is None:
		print("Unable to find valid PMIC")
		exit(-3)

	print ("Found pmic: "  + pmic)

	if pmic == "pca9450":
		if pmic in dtb:
			print("Default DTB already set.")
			exit(0)
	
	if pmic == "8100":
		if not ("pca9450" in dtb):
			print("Default DTB already set.")
			exit(0)

	print("Set devicetree for PMIC found")

	if pmic == "pca9450":
		newdtb=dtb.replace('.dtb', '-pca9450.dtb')
		print("Setting new dtb: " + newdtb)
		setDefaultDTB(newdtb)



	print("Done")

if __name__ == "__main__":
	main()


