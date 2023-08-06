set /augeas/load/PHP/incl[last()] /etc/bumblebee/bumblebee.conf
set /augeas/load/Xorg/incl[last()] /etc/bumblebee/xorg.conf.nvidia
load
set /files/etc/bumblebee/bumblebee.conf/bumblebeed/KeepUnusedXServer false
set /files/etc/bumblebee/bumblebee.conf/driver-nvidia/PMMethod auto
set /files/etc/bumblebee/bumblebee.conf/driver-nouveau/PMMethod auto
set /files/etc/bumblebee/xorg.conf.nvidia/ServerLayout/Option[last() + 1] "AutoAddDevices"
set /files/etc/bumblebee/xorg.conf.nvidia/ServerLayout/Option[last()]/value "false"
set /files/etc/bumblebee/xorg.conf.nvidia/ServerLayout/Option[last() + 1] "AutoAddGPU"
set /files/etc/bumblebee/xorg.conf.nvidia/ServerLayout/Option[last()]/value "false"
set /files/etc/bumblebee/xorg.conf.nvidia/Device/Option[last() + 1] "UseEDID"
set /files/etc/bumblebee/xorg.conf.nvidia/Device/Option[last()]/value "false"
set /files/etc/bumblebee/xorg.conf.nvidia/Device/Option[last() + 1] "UseDisplayDevice"
set /files/etc/bumblebee/xorg.conf.nvidia/Device/Option[last()]/value "none"
save

