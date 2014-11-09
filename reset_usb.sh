$(lsusb -d 12d1:1506 | awk -F '[ :]'  '{ print "/dev/bus/usb/"$2"/"$4 }' | xargs -I {} echo "./usbreset {}")
