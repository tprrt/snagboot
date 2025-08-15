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

import struct
import usb.core
import usb.util
import logging

logger = logging.getLogger("snagrecover")

# APX protocol constants
APX_CMD_DOWNLOAD = 0x04
APX_CMD_QUERY_DEVICE = 0x02
APX_CMD_RESET = 0x06


class APXError(Exception):
	def __init__(self, message):
		self.message = message
		super().__init__(self.message)

	def __str__(self):
		return f"APX error: {self.message}"


def send_apx_command(dev, command, data=b""):
	"""Send an APX command to the device"""
	try:
		# APX commands are sent via control transfer
		# Standard APX command structure
		ret = dev.ctrl_transfer(
			usb.util.CTRL_OUT | usb.util.CTRL_TYPE_VENDOR,
			command,
			0,
			0,
			data,
			timeout=5000,
		)
		return ret
	except usb.core.USBError as e:
		raise APXError(f"Failed to send APX command: {e}") from e


def download_to_ram(dev, address, data):
	"""Download data to RAM via APX protocol"""
	logger.debug(f"Downloading {len(data)} bytes to address 0x{address:08x}")

	# Send download command with address and size
	cmd_data = struct.pack("<II", address, len(data))
	send_apx_command(dev, APX_CMD_DOWNLOAD, cmd_data)

	# Send the actual data
	try:
		# APX typically uses bulk transfers for data
		cfg = dev.get_active_configuration()
		ep_out = None

		for intf in cfg.interfaces():
			for ep in intf.endpoints():
				if (
					usb.util.endpoint_direction(ep.bEndpointAddress)
					== usb.util.ENDPOINT_OUT
				):
					if (
						usb.util.endpoint_type(ep.bmAttributes)
						== usb.util.ENDPOINT_TYPE_BULK
					):
						ep_out = ep.bEndpointAddress
						break
			if ep_out:
				break

		if not ep_out:
			raise APXError("No bulk OUT endpoint found")

		# Send data in chunks
		chunk_size = 0x1000  # 4KB chunks
		for i in range(0, len(data), chunk_size):
			chunk = data[i : i + chunk_size]
			dev.write(ep_out, chunk, timeout=5000)

		logger.debug("Data download completed")

	except usb.core.USBError as e:
		raise APXError(f"Failed to download data: {e}") from e


def query_device_info(dev):
	"""Query device information via APX"""
	try:
		ret = dev.ctrl_transfer(
			usb.util.CTRL_IN | usb.util.CTRL_TYPE_VENDOR,
			APX_CMD_QUERY_DEVICE,
			0,
			0,
			64,
			timeout=5000,
		)
		logger.debug(f"Device info: {ret}")
		return ret
	except usb.core.USBError as e:
		raise APXError(f"Failed to query device: {e}") from e


def reset_device(dev):
	"""Reset device via APX"""
	try:
		send_apx_command(dev, APX_CMD_RESET)
		logger.debug("Device reset command sent")
	except usb.core.USBError as e:
		raise APXError(f"Failed to reset device: {e}") from e
