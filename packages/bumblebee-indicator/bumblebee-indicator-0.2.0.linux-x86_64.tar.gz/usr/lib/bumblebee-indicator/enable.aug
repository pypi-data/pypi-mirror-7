set /augeas/load/PHP/incl[last()] /etc/bumblebee/bumblebee.conf
set /augeas/load/Xorg/incl[last()] /etc/bumblebee/xorg.conf.nvidia
load
set /files/etc/bumblebee/bumblebee.conf/bumblebeed/KeepUnusedXServer true
set /files/etc/bumblebee/bumblebee.conf/driver-nvidia/PMMethod none
set /files/etc/bumblebee/bumblebee.conf/driver-nouveau/PMMethod none
rm /files/etc/bumblebee/xorg.conf.nvidia/ServerLayout/Option[. = "AutoAddDevices"]
rm /files/etc/bumblebee/xorg.conf.nvidia/ServerLayout/Option[. = "AutoAddGPU"]
rm /files/etc/bumblebee/xorg.conf.nvidia/Device/Option[. = "UseDisplayDevice"]
rm /files/etc/bumblebee/xorg.conf.nvidia/Device/Option[. = "UseEDID"]
save
