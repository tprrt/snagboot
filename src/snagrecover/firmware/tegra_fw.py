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

import os
import logging
from snagrecover.protocols import apx

logger = logging.getLogger("snagrecover")

# Default load addresses for Tegra SoCs
TEGRA_BOOTLOADER_LOAD_ADDR = 0x80108000  # Typical bootloader load address
TEGRA_UBOOT_LOAD_ADDR = 0x80110000  # Typical U-Boot load address


def send_tegra_firmware(dev, filepath, load_address=None):
	"""Send firmware to Tegra device via APX protocol"""
	if not os.path.exists(filepath):
		raise FileNotFoundError(f"Firmware file not found: {filepath}")

	with open(filepath, "rb") as f:
		firmware_data = f.read()

	logger.info(f"Loading Tegra firmware: {filepath} ({len(firmware_data)} bytes)")

	# Use default address if not specified
	if load_address is None:
		if "bootloader" in os.path.basename(filepath).lower():
			load_address = TEGRA_BOOTLOADER_LOAD_ADDR
		else:
			load_address = TEGRA_UBOOT_LOAD_ADDR

	# Query device info first
	try:
		apx.query_device_info(dev)
	except apx.APXError as e:
		logger.warning(f"Could not query device info: {e}")

	# Download firmware to RAM
	apx.download_to_ram(dev, load_address, firmware_data)

	logger.info(f"Firmware loaded successfully to address 0x{load_address:08x}")


def run_bootloader(dev, fw_dict):
	"""Run bootloader on Tegra device"""
	filepath = fw_dict["bootloader"]
	send_tegra_firmware(dev, filepath, TEGRA_BOOTLOADER_LOAD_ADDR)


def run_uboot(dev, fw_dict):
	"""Run U-Boot on Tegra device"""
	filepath = fw_dict["u-boot"]
	send_tegra_firmware(dev, filepath, TEGRA_UBOOT_LOAD_ADDR)
