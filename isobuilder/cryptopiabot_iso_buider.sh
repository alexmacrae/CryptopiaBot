#!/bin/bash -v
# CREATE A RASPBIAN JESSIE IMAGE FOR CRYPTOPIABOT
# 2017-05-16
#
# Append " | tee -a output.log" to the end of the sh run line to output console lines to output.log
# To print additions to output.log in realtime from another machine "tail -f output.log". Perhaps you want to
# monitor progress or errors from another machine or remotely from your mobile!
#

set -e

#sudo apt-get update && sudo apt-get install -y cdebootstrap kpartx parted sshpass zip
# !! Might need to sudo, depending on your setup
apt-get update && apt-get install -y cdebootstrap kpartx parted sshpass zip dosfstools

image_name=$(date "+%Y-%m-%d")_cryptopiabot.img
boot_size=64
raspbian_size=1300
image_size=$(($boot_size+$raspbian_size+64))
hostname=cryptopiabot
root_password=root
http=http://mirror.internode.on.net/pub/raspbian/raspbian/
#http=http://mirrordirector.raspbian.org/raspbian/ # at time of compile, some packages were not found and failed. Might work again now

dd if=/dev/zero of=$image_name  bs=1M  count=$image_size
fdisk $image_name <<EOF
o
n



+$(($boot_size))M
t
c
n



+$(($raspbian_size))M
p
n
p


EOF


kpartx -av $image_name
partprobe /dev/loop0
bootpart=/dev/mapper/loop0p1
rootpart=/dev/mapper/loop0p2

mkdosfs -n BOOT $bootpart
mkfs.ext4 -L ROOT $rootpart
sync

fdisk -l $image_name
mkdir -v sdcard
mount -v -t ext4 -o sync $rootpart sdcard

cdebootstrap --arch=armhf jessie sdcard $http --include=locales --allow-unauthenticated
sync

mount -v -t vfat -o sync $bootpart sdcard/boot

echo root:$root_password | chroot sdcard chpasswd

wget -O sdcard/raspberrypi.gpg.key http://archive.raspberrypi.org/debian/raspberrypi.gpg.key
chroot sdcard apt-key add raspberrypi.gpg.key
rm -v sdcard/raspberrypi.gpg.key
wget -O sdcard/raspbian.public.key http://mirrordirector.raspbian.org/raspbian.public.key
chroot sdcard apt-key add raspbian.public.key
rm -v sdcard/raspbian.public.key
chroot sdcard apt-key list

sed -i sdcard/etc/apt/sources.list -e "s/main/main contrib non-free firmware/"
echo "deb http://archive.raspberrypi.org/debian/ jessie main" >> sdcard/etc/apt/sources.list

echo Etc/UTC > sdcard/etc/timezone
echo en_GB.UTF-8 UTF-8 > sdcard/etc/locale.gen
cp -v /etc/default/keyboard sdcard/etc/default/keyboard
echo $hostname > sdcard/etc/hostname
echo "127.0.1.1 $hostname" >> sdcard/etc/hosts
chroot sdcard locale-gen LANG="en_GB.UTF-8"
chroot sdcard dpkg-reconfigure -f noninteractive locales

cat <<EOF > sdcard/boot/cmdline.txt
root=/dev/mmcblk0p2 ro rootwait console=tty1 selinux=0 plymouth.enable=0 smsc95xx.turbo_mode=N dwc_otg.lpm_enable=0 elevator=noop init=/bin/systemd
EOF
# removed: bcm2708.uart_clock=3000000, this hack was only useful for Linux kernel <= 4.4
# http://k3a.me/how-to-make-raspberrypi-truly-read-only-reliable-and-trouble-free/ @ 4.4 Disable filesystem check and swap
# added: fastboot noswap

cat <<EOF > sdcard/boot/config.txt
device_tree_param=i2c_arm=on
enable_uart=1
dtoverlay=pi3-miniuart-bt
dtoverlay=midi-uart0
gpu_mem=64
boot_delay=0
disable_splash=1
disable_audio_dither=1
dtparam=audio=on
dtoverlay=iqaudio-dac
EOF


cat <<EOF > sdcard/etc/fstab
/dev/mmcblk0p0  /               auto    rw,nofail               0       0
/dev/sda1       /media          auto    ro,nofail               0       0
/dev/mmcblk0p1  /boot           vfat    rw,auto,exec            0       2
EOF

###########################################
# NETWORKING

# "allow-hotplug" instead of "auto" very important to prevent blocking on boot if no network present
cat <<EOF > sdcard/etc/network/interfaces
auto lo
iface lo inet loopback

allow-hotplug eth0
iface eth0 inet dhcp

allow-hotplug wlan0
iface wlan0 inet manual
	wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf

allow-hotplug wlan1
iface wlan0 inet manual
	wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf

EOF

mkdir sdcard/etc/wpa_supplicant
cat <<EOF > sdcard/etc/wpa_supplicant/wpa_supplicant.conf
ctrl_interface=DIR=/var/run/wpa_supplicant
update_config=1

# Uncomment and edit below to include your WiFi network's login credentials
#network={
#    ssid="YOUR_NETWORK_NAME"
#    psk="YOUR_NETWORK_PASSWORD"
#}

EOF



# Install packages required for SamplerBox
chroot sdcard apt-get update
chroot sdcard apt-get -y upgrade
chroot sdcard apt-get -y dist-upgrade
chroot sdcard apt-get -y install apache2
chroot sdcard apt-get -y install libraspberrypi-bin libraspberrypi-dev libraspberrypi0 raspberrypi-bootloader ssh wireless-tools usbutils python-tk ntpdate unzip
chroot sdcard apt-get clean
chroot sdcard apt-get -y install wpasupplicant dhcpcd5 firmware-brcm80211 # on-board wifi
chroot sdcard apt-get -y install parted dosfstools # partitioning tools
chroot sdcard apt-get -y install exfat-fuse # exFAT filesystem support
chroot sdcard apt-get -y install psmisc # contains `killall` command
chroot sdcard apt-get -y install dos2unix # converts windows files to unix
chroot sdcard apt-get clean
chroot sdcard apt-get -y install build-essential python-dev python-pip cython python-smbus python-numpy python-rpi.gpio python-serial
chroot sdcard apt-get -y install python-configparser python-psutil python-scipy git portaudio19-dev alsa-utils libportaudio2 libffi-dev
chroot sdcard apt-get clean
chroot sdcard apt-get autoremove -y
chroot sdcard pip install pyaudio cffi sounddevice pyalsaaudio wifi
chroot sdcard sh -c "cd /root ; git clone https://github.com/gesellkammer/rtmidi2 ; cd rtmidi2 ; python setup.py install ; cd .. ; rm -rf rtmidi2"
chroot sdcard sh -c "cd /root ; git clone https://github.com/dbrgn/RPLCD ; cd RPLCD ; python setup.py install ; cd .. ; rm -rf RPLCD" # WARNING: version used 0.9.0. Latest is 1.0.0
chroot sdcard sh -c "cd /root ; git clone https://gitorious.org/pyosc/devel.git ; cd devel ; python setup.py install ; cd .. ; rm -rf devel" # OSC support
chroot sdcard sh -c "cd /root ; git clone https://github.com/proxypoke/wpa_config.git ; cd wpa_config ; python setup.py install ; cd .. ; rm -rf wpa_config"

# Allowing root to log into $release with password... "
sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' sdcard/etc/ssh/sshd_config

## Start wpa_supplicant
#chroot sdcard sh -c "wpa_supplicant -B -i wlan0 -c /boot/networking/wireless_networks.conf" # only need if wpa_supplicant.conf lives somewhere other than the default. eg /boot/networking/wireless_networks.conf
#chroot sdcard sh -c "wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf" # only need if wpa_supplicant.conf lives somewhere other than the default. eg /boot/networking/wireless_networks.conf
#chroot sdcard systemctl enable wpa_supplicant # line may not be needed as package wpasupplicant seems to start service upon reboot
#chroot sdcard systemctl enable dhcpcd # dhcpcd5 enables itself after install

#echo "timeout 10;" >> sdcard/etc/dhcp/dhclient.conf
#echo "retry 1;" >> sdcard/etc/dhcp/dhclient.conf

###########################################

# CryptopiaBot
chroot sdcard sh -c "cd /root ; git clone https://github.com/alexmacrae/CryptopiaBot.git;"

cat <<EOF > sdcard/root/CryptopiaBot/cryptopiabot.sh
#!/bin/sh
date -s "Jan 1 11:11:11 UTC 2018"
python /root/CryptopiaBot/cryptopia.py
EOF

chmod 777 sdcard/root/CryptopiaBot/cryptopiabot.sh
chmod 777 sdcard/root/CryptopiaBot/json/settings.json
chmod 777 sdcard/root/CryptopiaBot/json/wishlist.json
chmod 777 sdcard/root/CryptopiaBot/json/blacklist.json
chmod 777 sdcard/root/CryptopiaBot/json/ownedcoins.json

cat <<EOF > sdcard/etc/wpa_config/wpa_supplicant.conf.head
ctrl_interface=DIR=/var/run/wpa_supplicant
update_config=1
EOF

cat <<EOF > sdcard/etc/wpa_config/wpa_supplicant.conf.tail

EOF

cat <<EOF > sdcard/etc/systemd/system/cryptopiabot.service
[Unit]
Description=Starts CryptopiaBot
DefaultDependencies=false

[Service]
Type=simple
ExecStart=/root/CryptopiaBot/cryptopiabot.sh
WorkingDirectory=/root/CryptopiaBot/

[Install]
WantedBy=local-fs.target
EOF

cat <<EOF > sdcard/etc/motd

Welcome to

_________                        __                .__      __________        __
\_   ___ \_______ ___.__._______/  |_  ____ ______ |__|____ \______   \ _____/  |_
/    \  \/\_  __ <   |  |\____ \   __\/  _ \\____ \|  \__  \ |    |  _//  _ \   __\
\     \____|  | \/\___  ||  |_> >  | (  <_> )  |_> >  |/ __ \|    |   (  <_> )  |
 \______  /|__|   / ____||   __/|__|  \____/|   __/|__(____  /______  /\____/|__|
        \/        \/     |__|               |__|           \/       \/



EOF


chroot sdcard systemctl enable /etc/systemd/system/cryptopiabot.service

echo 'i2c-dev' >> sdcard/etc/modules
echo 'snd_bcm2835' >> sdcard/etc/modules

ln -s /proc/mounts sdcard/etc/mtab                             # because of https://bpaste.net/show/397df349ccf3
ln -nsf /run/resolvconf/resolv.conf sdcard/etc/resolv.conf     # to prevent DNS problems and no internet connection issue

#############################

# Unmounting mount points
sync

umount -v sdcard/boot
umount -v sdcard

kpartx -dv $image_name

sync

zip $image_name.zip $image_name

ls -la -h

#FINISHED

exit 0
