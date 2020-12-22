# TODO test capacitor effectiveness (once bought)
# TODO work out button subroutines

import RPi.GPIO as GPIO
import os
import pathlib
import _thread

GPIO.setmode(GPIO.BCM)

# TODO confirm gpio pins
mnt_sw = 2
mnt_led_g = 27 # will possibly be in series with mnt_sw
mnt_led_r = 22

chk_sw = 3
chk_led_g = 23 # will possibly be in series with chk_sw
chk_led_r = 24

key_sw = 4
key_led = 10 # might just put these in series

btn_a_led = 9
btn_b_led = 25
btn_c_led = 11
btn_d_led = 8

btn_a = 14
btn_b = 15
btn_c = 17
btn_d = 18

inputs = [mnt_sw, chk_sw, key_sw, btn_a, btn_b, btn_c, btn_d]
outputs = [mnt_led_g, mnt_led_r, chk_led_g, chk_led_r, key_led, btn_a_led, btn_b_led, btn_c_led, btn_d_led]
GPIO.setup(inputs, GPIO.IN)
GPIO.setup(outputs, GPIO.OUT)
# raises a warning if program has already been run, might be a problem

mounted = False
checked = False
keyturn = False
sh_a = False
sh_b = False
sh_c = False
sh_d = False

def mnt():
	global mounted
	cmd_code = os.system("sudo mount /dev/sda1 /mnt")
	GPIO.output(mnt_led_g, True)
	if cmd_code == 8192:
		GPIO.output(mnt_led_r, True)
		mounted = False
	else:
		mounted = True
		if GPIO.input(chk_sw) == 1:
			chk()

def umnt():
	global mounted
	os.system("sudo umount /mnt")
	GPIO.output(mnt_led_g, False)
	GPIO.output(mnt_led_r, False)
	mounted = False
	uchk()

def mnt_sub():
	while True:
		GPIO.wait_for_edge(mnt_sw, GPIO.BOTH)
		if GPIO.input(mnt_sw) == 1:
			mnt()
		else:
			umnt()

def chk():
	global sh_a
	global sh_b
	global sh_c
	global sh_d
	global checked
	if mounted:
		sh_a = pathlib.Path("/mnt/a.sh").exists()
		sh_b = pathlib.Path("/mnt/b.sh").exists()
		sh_c = pathlib.Path("/mnt/c.sh").exists()
		sh_d = pathlib.Path("/mnt/d.sh").exists()
		GPIO.output(chk_led_g, True)
		if not(sh_a or sh_b or sh_c or sh_d):
			GPIO.output(chk_led_r, True)
		checked = True
		if GPIO.input(key_sw) == 1:
			key()

def uchk():
	global sh_a
	global sh_b
	global sh_c
	global sh_d
	global checked
	sh_a = False
	sh_b = False
	sh_c = False
	sh_d = False
	GPIO.output(chk_led_g, False)
	GPIO.output(chk_led_r, False)
	checked = False
	ukey()

def chk_sub():
	while True:
		GPIO.wait_for_edge(chk_sw, GPIO.BOTH)
		if GPIO.input(chk_sw) == 1 and mounted == True:
			chk()
		else:
			uchk()

def key():
	global keyturn
	if checked:
		GPIO.output(btn_a_led, sh_a)
		GPIO.output(btn_b_led, sh_b)
		GPIO.output(btn_c_led, sh_c)
		GPIO.output(btn_d_led, sh_d)
		GPIO.output(key_led, True)
		keyturn = True

def ukey():
	global keyturn
	GPIO.output(btn_a_led, False)
	GPIO.output(btn_b_led, False)
	GPIO.output(btn_c_led, False)
	GPIO.output(btn_d_led, False)
	GPIO.output(key_led, False)
	keyturn = False
	ubtn()

def key_sub():
	while True:
		GPIO.wait_for_edge(key_sw, GPIO.BOTH)
		if GPIO.input(key_sw) == 1:
			key()
		else:
			ukey() # THIS ASSUMES THAT THE KEYS STAY IN POSITION WHEN TURNED, CHANGE IF THIS IS NOT THE CASE!!!

def btn(sh):
	global running
	if keyturn and not(running):
		os.system("sudo /mnt/"+sh+".sh")
		running = True

def ubtn(sh):
	pass # TODO in v1/v2 terminate running scripts

def btn_sub(btn, sh):
	while True:
		GPIO.wait_for_edge(btn, GPIO.BOTH)
		if GPIO.input(btn) == 1:
			btn(sh)

_thread.start_new_thread(mnt_sub, ())
_thread.start_new_thread(chk_sub, ())
_thread.start_new_thread(key_sub, ())
_thread.start_new_thread(btn_sub, (btn_a, "a"))
_thread.start_new_thread(btn_sub, (btn_b, "b"))
_thread.start_new_thread(btn_sub, (btn_c, "c"))
_thread.start_new_thread(btn_sub, (btn_d, "d"))


while True:
	input()
