#!/usr/bin/env python3

import socket
import struct
import fcntl

def sdp_inq_raw():
    print("Run sdp_inq_raw() ... ")
    port = 1

    sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_RAW, socket.BTPROTO_HCI)
    sock.settimeout(30)

    # https://android.googlesource.com/platform/system/sepolicy/+/master/public/ioctl_defines
    HCIINQUIRY = 0x800448f0 

    # Core.pdf, 7.1.1 Inquiry Command
    # This is the LAP from which the inquiry access code should be derived
    # when the inquiry procedure is made; see Bluetooth Assigned Numbers
    # General/Unlimited Inquiry Access Code (GIAC): http://www.yts.rdy.jp/pic/GB002/hcic.html
    lap = [0x9e, 0x8b, 0x33]

    # Maximum amount of time specified before the Inquiry is halted.
    # 0x01 – 0x30 : Time = N * 1.28 (1.28 – 61.44 s)
    inq_len = 0x08

    # Unlimited number of inq_resonses.
    # 0x00        : Unlimited number of inq_resonses.
    # 0x01 - 0xFF : Maximum number of inq_resonses from the Inquiry before the Inquiry is halted.
    num_res = 0x03 # 3 devices

    # msg = HCI Inquiry Command + inq_resonse(set 0x00)
    # inq_resonse = divice_num * 14 byte (HCI Events - Inquiry Result: after BD_ADDR)
    format_string = "1I5B" + str(num_res * 14) + "B"

    try:
        buffer = struct.pack(format_string, 0x00, lap[-1], lap[-2], lap[-3], inq_len, num_res, *((0,) * 14 * num_res))
        ret = fcntl.ioctl(sock.fileno(), HCIINQUIRY, buffer)
    except Exception as e:
        print(e)
        sock.close()
        exit(1)
    sock.close()

    # Check number of devices
    if ret[8] == 0x00:
        print("No devices found")
        exit(1)
    
    print("Found {} devices".format(ret[8]))

    # HCI Events - Inquiry Result: after BD_ADDR
    inq_res = ret[10:]
    for device_num in range(0, ret[8]):
        payload = inq_res[device_num * 14:(device_num +1) * 14]
        print("BD Addr {:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}".format(payload[5], payload[4], payload[3], payload[2], payload[1], payload[0]))

if __name__ == "__main__":
    sdp_inq_raw()