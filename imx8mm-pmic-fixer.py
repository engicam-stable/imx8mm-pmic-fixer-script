#!/usr/bin/python3

import subprocess
import os.path
from pathlib import Path

CONFFILE = "/tmp/fw_env_eng.conf"
PMICFILE = "/etc/pmic.done"
I2CDETECT="/usr/sbin/i2cdetect"
FW_SETENV="/sbin/fw_setenv"
FW_PRINTENV="/sbin/fw_printenv"
NOTPMICFOUND = 0
PCA9450 = 1
PF8100 = 2


def checkMX8MMsoc():
    file = open('/proc/device-tree/compatible', mode='r')
    compatible = file.read()
    file.close()
    return 'mx8mm' in compatible


def getMountDevice():
    file = open('/proc/cmdline', mode='r')
    cmdline = file.read()
    file.close()

    for x in range(6):
        mnt = "mmcblk" + str(x)
        if mnt in cmdline:
            return mnt

    return None


def createConfigFile(mountdev):
    line = "/dev/" + mountdev + "             0x400000        0x1000          0x1000"
    f = open(CONFFILE, "w+")
    f.write(line)
    f.close()


def getDefaultDTB():
    result = subprocess.run(['fw_printenv', '-c', CONFFILE, 'fdt_file'], stdout=subprocess.PIPE)
    value = result.stdout.decode('utf-8')
    if "not defined" in value:
        return None

    return value.replace('fdt_file=', '')


def setDefaultDTB(dtb):
    result = subprocess.run([FW_SETENV, '-c', CONFFILE, 'fdt_file', dtb], stdout=subprocess.PIPE)


def checkPMIC():
	# checking for PF8100
	result = subprocess.run([I2CDETECT, '-y', '0', '0x08', '0x08'], stdout=subprocess.PIPE)
	value = result.stdout.decode('utf-8')

	if 'UU' in value:
		return True, None

	if '08' in value:
		return False, PF8100

	# checking for PCA9450
	result = subprocess.run([I2CDETECT, '-y', '0', '0x25', '0x25'], stdout=subprocess.PIPE)
	value = result.stdout.decode('utf-8')

	if 'UU' in value:
		return True, None

	if '25' in value:
		return False, PCA9450

	return False,NOTPMICFOUND


def checkTools():

	ret = True

	i2cdetect = Path(I2CDETECT)
	fwsetenv = Path(FW_SETENV)
	fwprintenv= Path(FW_PRINTENV)

	if not i2cdetect.exists():
		print("i2cdetect not found")
		ret = False

	if not fwsetenv.exists():
		print("fw_setenv not found")
		ret = False

	if not fwprintenv.exists():
		print("fw_printenv not found")
		ret = False

	return ret


def createDoneFile():
	f = open(PMICFILE, "w")
	f.write("done")
	f.close()


def main():
	donefile = Path(PMICFILE)
	if donefile.exists():
		print("PMIC dtb set already done")
		exit(0)

	if not checkMX8MMsoc():
		print("no MX8MM found")
		exit(0)
	else:
		print("MX8MM found")

	if not checkTools():
		exit(-1)

	pmicstatus,pmicindex = checkPMIC()

	if pmicstatus:
		print("PMIC OK")
		createDoneFile()
		exit(0)
	else:
		if pmicindex == NOTPMICFOUND:
			print("No PMIC found")
			exit(-2)

		# it needs to update the devicetree
		mountdevice = getMountDevice()
		if mountdevice is None:
			print("No valid mountpoint found !")
			exit(-1)

		print("Rootfs mounted on:" + mountdevice)
		createConfigFile(mountdevice)

		dtb = getDefaultDTB()
		if dtb is None:
			print("Unable to find devicetree")
			exit(-2)

		print("Device tree set: " + dtb)

		if pmicindex==PCA9450:
			print("Found PMIC PCA9450")
			newdtb = dtb.replace('.dtb', '-pca9450.dtb')
			print("Setting new dtb: " + newdtb)
			setDefaultDTB(newdtb)
			dtb = getDefaultDTB()
			if dtb.strip() == newdtb.strip():
				print("Setting done...")
			else:
				print("DTB Setting ERROR...")
				exit(-3)

		if pmicindex==PF8100:
			print("Found PMIC PF8100")
			newdtb = dtb.replace('-pca9450.dtb','.dtb')
			print("Setting new dtb: " + newdtb)
			setDefaultDTB(newdtb)
			dtb = getDefaultDTB()
			if dtb.strip() == newdtb.strip():
				print("Setting done...")
			else:
				print("DTB Setting ERROR...")
				exit(-3)

		createDoneFile()


if __name__ == "__main__":
	main()


