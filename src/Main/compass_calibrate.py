#!/usr/bin/env python3
"""
CMPS12 Compass Calibration Utility

- Shows live calibration status for System, Gyro, Accel, Magnetometer (register 0x1E)
- Guides the user through movements until fully calibrated
- Saves calibration profile (write 0xF0, 0xF5, 0xF6 to register 0x00 with 20ms delays)
- Optional: erase stored calibration profile, or change I2C address

Usage examples:
  - Run interactive calibration and save automatically when fully calibrated:
      python3 compass_calibrate.py
  - Erase stored profile:
      python3 compass_calibrate.py --erase
  - Change address to 0xC2 (ensure only one compass is on the bus):
      python3 compass_calibrate.py --set-addr 0xC2

Notes:
- This script is designed for MicroPython or CircuitPython environments providing `machine.I2C`.
- On non-MicroPython hosts, it will exit with an informative message.
"""

import sys
import time

# Try to import MicroPython I2C. If not available, exit gracefully.
try:
	from machine import Pin, I2C
except Exception as e:
	print("This script must run on a MicroPython-compatible device (machine.I2C not available).")
	print(f"Import error: {e}")
	sys.exit(1)

# Load defaults from central config when available
try:
	from config import get_config
except Exception:
	get_config = None

# Default CMPS12 I2C settings (can be overridden by args)
DEFAULT_I2C_ID = 1
DEFAULT_SDA_PIN = 14
DEFAULT_SCL_PIN = 15
DEFAULT_ADDR = 0x60  # CMPS12 default address

# CMPS12 registers
REG_COMMAND_OR_VERSION = 0x00  # write: command register, read: software version
REG_BEARING_16 = 0x02          # 0-3599 (0-359.9°)
REG_CALIBRATION = 0x1E         # calibration status bits

# Command sequences
SAVE_PROFILE_SEQ = [0xF0, 0xF5, 0xF6]
ERASE_PROFILE_SEQ = [0xE0, 0xE5, 0xE2]


def parse_args():
	"""Parse CLI args if argparse is available; return None on MicroPython."""
	try:
		import argparse  # Lazy import; not present on MicroPython
		parser = argparse.ArgumentParser(description="CMPS12 Compass Calibration Utility")
		parser.add_argument("--i2c-id", type=int, default=DEFAULT_I2C_ID, help="I2C bus id (default: 1)")
		parser.add_argument("--sda", type=int, default=DEFAULT_SDA_PIN, help="SDA pin (default: 14)")
		parser.add_argument("--scl", type=int, default=DEFAULT_SCL_PIN, help="SCL pin (default: 15)")
		parser.add_argument("--addr", type=lambda x: int(x, 0), default=DEFAULT_ADDR, help="I2C address (default: 0x60)")
		parser.add_argument("--erase", action="store_true", help="Erase stored calibration profile and exit")
		parser.add_argument("--set-addr", type=lambda x: int(x, 0), help="Change I2C address (e.g., 0xC2). Only one device must be on the bus.")
		parser.add_argument("--no-save", action="store_true", help="Do not save automatically when fully calibrated")
		parser.add_argument("--quiet", action="store_true", help="Reduce output verbosity")
		return parser.parse_args()
	except Exception:
		return None


def open_i2c(i2c_id: int, sda_pin: int, scl_pin: int) -> I2C:
	return I2C(i2c_id, scl=Pin(scl_pin), sda=Pin(sda_pin))


def scan_for_addr(i2c: I2C, preferred_addr: int) -> int:
	devices = i2c.scan()
	if preferred_addr in devices:
		return preferred_addr
	# Fallback: if preferred not found but any device exists, try using the first
	return preferred_addr


def read_heading_deg(i2c: I2C, addr: int) -> float:
	data = i2c.readfrom_mem(addr, REG_BEARING_16, 2)
	raw = (data[0] << 8) | data[1]
	return raw / 10.0


def read_calibration_byte(i2c: I2C, addr: int) -> int:
	data = i2c.readfrom_mem(addr, REG_CALIBRATION, 1)
	return data[0]


def decode_calibration(byte_val: int):
	# Bits: [7:6]=System, [5:4]=Gyro, [3:2]=Accel, [1:0]=Mag; 0..3 scale
	sys_lvl = (byte_val >> 6) & 0x03
	gyro_lvl = (byte_val >> 4) & 0x03
	accel_lvl = (byte_val >> 2) & 0x03
	mag_lvl = byte_val & 0x03
	return sys_lvl, gyro_lvl, accel_lvl, mag_lvl


def calib_text(level: int) -> str:
	return ["Uncalibrated", "Poor", "Fair", "Good"][level] if 0 <= level <= 3 else f"{level}"


def write_command_sequence(i2c: I2C, addr: int, seq):
	for b in seq:
		i2c.writeto_mem(addr, REG_COMMAND_OR_VERSION, bytes([b]))
		time.sleep_ms(20)


def save_profile(i2c: I2C, addr: int):
	write_command_sequence(i2c, addr, SAVE_PROFILE_SEQ)


def erase_profile(i2c: I2C, addr: int):
	write_command_sequence(i2c, addr, ERASE_PROFILE_SEQ)


def change_address(i2c: I2C, current_addr: int, new_addr: int):
	# Sequence: 0xA0, 0xAA, 0xA5, then the new address byte
	for b in [0xA0, 0xAA, 0xA5]:
		i2c.writeto_mem(current_addr, REG_COMMAND_OR_VERSION, bytes([b]))
		time.sleep_ms(20)
	# Final write: new address
	i2c.writeto_mem(current_addr, REG_COMMAND_OR_VERSION, bytes([new_addr & 0xFF]))
	# Note: Take effect after power cycle


def print_status_line(sys_lvl, gyro_lvl, accel_lvl, mag_lvl, heading_deg, quiet=False):
	if quiet:
		return
	status = (
		f"System: {sys_lvl}/3 ({calib_text(sys_lvl)})  "
		f"Gyro: {gyro_lvl}/3 ({calib_text(gyro_lvl)})  "
		f"Accel: {accel_lvl}/3 ({calib_text(accel_lvl)})  "
		f"Mag: {mag_lvl}/3 ({calib_text(mag_lvl)})  "
		f"Heading: {heading_deg:6.1f}°"
	)
	print(status)


def guidance(sys_lvl, gyro_lvl, accel_lvl, mag_lvl, quiet=False):
	if quiet:
		return
	msgs = []
	if gyro_lvl < 3:
		msgs.append("Keep the module stationary for a few seconds (gyro).")
	if accel_lvl < 3:
		msgs.append("Tilt to ~45° and ~90° on each axis (accel).")
	if mag_lvl < 3:
		msgs.append("Make smooth figure-8 or random rotations (mag).")
	if not msgs:
		msgs = ["Fully calibrated. Saving..."]
	for m in msgs:
		print("- " + m)


def _input_int(prompt: str, default: int, base_auto: bool = True) -> int:
	try:
		text = input(f"{prompt} [{hex(default) if base_auto else default}]: ").strip()
		if not text:
			return default
		return int(text, 0) if base_auto else int(text)
	except Exception:
		print("Invalid input, using default.")
		return default


def menu_loop():
	"""Interactive menu for Raspberry Pi Pico / MicroPython."""
	print("\nCMPS12 Calibration Menu")
	print("(Press Ctrl+C to exit at any time)\n")
	global REG_BEARING_16

	# Configure I2C using config.py defaults when available
	if get_config:
		cfg = get_config().get_hardware_config('compass') or {}
		default_i2c_id = cfg.get('i2c_id', DEFAULT_I2C_ID)
		default_sda = cfg.get('sda_pin', DEFAULT_SDA_PIN)
		default_scl = cfg.get('scl_pin', DEFAULT_SCL_PIN)
		default_addr = cfg.get('addr', DEFAULT_ADDR)
		default_reg = cfg.get('reg', REG_BEARING_16)
		# Update global heading register if config specifies it
		try:
			REG_BEARING_16 = int(default_reg)
		except Exception:
			pass


	i2c_id =DEFAULT_I2C_ID
	sda_pin = DEFAULT_SDA_PIN
	scl_pin =DEFAULT_SCL_PIN
	addr = DEFAULT_ADDR

	try:
		i2c = open_i2c(i2c_id, sda_pin, scl_pin)
	except Exception as e:
		print(f"Failed to open I2C: {e}")
		return

	while True:
		print("\n=== MENU ===")
		print("1) Show live calibration status")
		print("2) Start interactive calibration (auto-save)")
		print("3) Save profile now")
		print("4) Erase stored profile")
		print("5) Change I2C address")
		print("6) Show heading once")
		print("0) Exit")
		choice = input("Select: ").strip()

		if choice == "1":
			try:
				print("Showing live status (Ctrl+C to return)...")
				while True:
					heading = read_heading_deg(i2c, addr)
					calib_byte = read_calibration_byte(i2c, addr)
					sys_lvl, gyro_lvl, accel_lvl, mag_lvl = decode_calibration(calib_byte)
					print_status_line(sys_lvl, gyro_lvl, accel_lvl, mag_lvl, heading, quiet=False)
					time.sleep_ms(500)
			except KeyboardInterrupt:
				print("\nReturning to menu...")
			except Exception as e:
				print(f"Error: {e}")

		elif choice == "2":
			interactive_calibration(i2c, addr, auto_save=True, quiet=False)

		elif choice == "3":
			try:
				save_profile(i2c, addr)
				print("Save sequence sent.")
			except Exception as e:
				print(f"Save failed: {e}")

		elif choice == "4":
			try:
				erase_profile(i2c, addr)
				print("Erase sequence sent.")
			except Exception as e:
				print(f"Erase failed: {e}")

		elif choice == "5":
			try:
				new_addr = _input_int("New I2C address", addr, base_auto=True)
				print("Ensure only one CMPS12 is on the bus before proceeding.")
				change_address(i2c, addr, new_addr)
				print("Address change sequence sent. Power cycle to apply.")
				addr = new_addr
			except Exception as e:
				print(f"Address change failed: {e}")

		elif choice == "6":
			try:
				heading = read_heading_deg(i2c, addr)
				print(f"Heading: {heading:.1f}°")
			except Exception as e:
				print(f"Read failed: {e}")

		elif choice == "0":
			print("Goodbye.")
			return

		else:
			print("Invalid choice.")


def interactive_calibration(i2c: I2C, addr: int, auto_save: bool = True, quiet: bool = False):
	print(f"Using I2C addr {hex(addr)}; registers: heading=0x02, calib=0x1E, cmd=0x00")
	last_print_ms = 0
	while True:
		try:
			heading = read_heading_deg(i2c, addr)
			calib_byte = read_calibration_byte(i2c, addr)
			sys_lvl, gyro_lvl, accel_lvl, mag_lvl = decode_calibration(calib_byte)
			now = time.ticks_ms()
			if time.ticks_diff(now, last_print_ms) > 500:
				print_status_line(sys_lvl, gyro_lvl, accel_lvl, mag_lvl, heading, quiet=quiet)
				guidance(sys_lvl, gyro_lvl, accel_lvl, mag_lvl, quiet=quiet)
				last_print_ms = now
			time.sleep_ms(100)

			if sys_lvl == gyro_lvl == accel_lvl == mag_lvl == 3:
				if auto_save:
					print("Calibration complete. Saving profile...")
					save_profile(i2c, addr)
					print("Save sequence sent. Power cycle to ensure persistence if needed.")
				else:
					print("Calibration complete. Use --no-save to skip saving or press Ctrl+C to exit.")
				return
		except KeyboardInterrupt:
			print("\nInterrupted by user.")
			return
		except Exception as e:
			print(f"Error: {e}")
			time.sleep_ms(300)


def main():
	args = parse_args()
	if args is None:
		# MicroPython mode: show menu
		menu_loop()
		return

	# Host/argparse mode
	try:
		i2c = open_i2c(args.i2c_id, args.sda, args.scl)
	except Exception as e:
		print(f"Failed to open I2C: {e}")
		sys.exit(1)

	addr = scan_for_addr(i2c, args.addr)

	if args.erase:
		try:
			print(f"Erasing stored profile at {hex(addr)}...")
			erase_profile(i2c, addr)
			print("Erase sequence sent.")
		except Exception as e:
			print(f"Erase failed: {e}")
		sys.exit(0)

	if args.set_addr is not None:
		try:
			print(f"Changing address from {hex(addr)} to {hex(args.set_addr)}...")
			change_address(i2c, addr, args.set_addr)
			print("Address change sequence sent. Power cycle the device to apply.")
		except Exception as e:
			print(f"Address change failed: {e}")
		sys.exit(0)

	print("Starting interactive calibration. Move the module as instructed below.")
	interactive_calibration(i2c, addr, auto_save=(not args.no_save), quiet=args.quiet)
	print("Done.")


if __name__ == "__main__":
	main()

