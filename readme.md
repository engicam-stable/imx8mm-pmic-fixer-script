
# iMx8MM-icore PMIC software solution

Engicam replaced on icoremx8mm SOC the PMIC PF8100 with PCA9450. 

In order to manage in the simplest way the new PMIC mounted on icoremx8m mini SOM, 
we provide a simple software solution that includes a devicetree with the new settings
and a python3 script that can help the customers to easily swap, if needed , the device 
tree for the old PMIC with the new one , and viceversa. 

## The device tree

The supported kernel are:

```
linux-engicam-nxp (https://github.com/engicam-stable/linux-engicam-nxp) 5.4.70 and 5.10.9 branch
linux-engicam_4.19.35 (https://github.com/engicam-stable/linux-engicam_4.19.35)
linux-engicam_4.14.98 (https://github.com/engicam-stable/linux-engicam_4.14.98)
```


The idea is to provide a new device tree written to include the customer device tree , 
and replace from it the old pmic settings with the new one. 

We provide an example for the starterkit devicetree at thhis link: 

https://github.com/engicam-stable/linux-engicam-nxp/blob/5.4.70/arch/arm64/boot/dts/engicam/imx8mm-icore-pca9450.dts

As you can see at line 8 we include the old starterkit device tree , based on PF8100 ,
named **imx8mm-icore.dts** , and from it replace all PMIC nodes with the new one. 
 
After kernel build we will obtain 2 different devicetree for starterkit:

```
* imx8mm-icore.dtb (old pmic PF8100)
* imx8mm-icore-pca9450.dtb (old pmic PCA9450)
```

So you need to change the default device tree load from system with the right one.

To do this we write a simple python script that checks what PMIC is present on SOM
and set , if needed , the new devicetree as default devicetree. 

The script must be run during the production phase, not in the field. 
Read carefully the *known issue* chapter.

In this example the naming convetion user for dtbs is:

```
<original-dtb-name>.dtb the old one
<original-dtb-name>-pca9450.dtb the new one
```

basically the new dtb name is the old one added with postfix **-pca9450**


# The python script

The script uses the tools below:

```
i2cdetect
fw_setenv
fw_printenv
```

At the beginning, it checks if these tools exist on filesystem or not, next, it checks if 
the script was already run by checking the existence of file */etc/pmic.done* and finally it tests 
on i2c bus what PMIC is present and if it already probed from the system.
If not, it changes the fdt_file u-boot variable with the right devicetree using 
the fw_setenv tools.

The naming convention for the devicetrees is described in previous chapter.
 


## known issues

The reboot of the SOM is done by the PMIC using the WDOG_B signal from the SOC.
If the PMIC is not properly set by the driver the SOM will stuck in reset condition.
This means that a system booted with the wrong devicetree is unable to reboot.
After DTB settings you must remove the power to the system in order to reboot it. 
