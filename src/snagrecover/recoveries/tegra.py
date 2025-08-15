# This file is part of Snagboot
# Copyright (C) 2025 Bootlin
#
# Written by Thomas Perrot <thomas.perrot@bootlin.com> in 2025.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import usb
import logging
import time

logger = logging.getLogger("snagrecover")
from snagrecover.firmware.firmware import run_firmware
from snagrecover.utils import get_usb
from snagrecover.config import recovery_config


def main():
	usb_addr = recovery_config["usb_path"]
	dev = get_usb(usb_addr)

	# Send bootloader via APX protocol
	run_firmware(dev, "bootloader")

	# USB device should re-enumerate at this point
	usb.util.dispose_resources(dev)
	time.sleep(1)

	# Get device again after re-enumeration
	dev = get_usb(usb_addr)

	# For Tegra, we typically need to send U-Boot next
	run_firmware(dev, "u-boot")

	time.sleep(2)
