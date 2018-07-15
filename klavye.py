#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from __future__ import print_function
import pyxhook
import time
import os 
import RPi.GPIO as GPIO
import time
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
GPIO.setmode(GPIO.BOARD)

global ms1a
global msa2
global mso1
global mso2
global msoa1
global msoa2
global msoo1
global msoo2
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#Sag
ms1a=3
msa2=5
mso1=7
mso2=11
#############
#Sol
msoa1=13
msoa2=15
msoo1=19
msoo2=21
def ileri():
    #sag ileri
    GPIO.output(ms1a,GPIO.HIGH)
    GPIO.output(msa2,GPIO.LOW)
    GPIO.output(mso1,GPIO.HIGH)
    GPIO.output(mso2,GPIO.LOW)
    ##########################
    #sol ileri
    GPIO.output(msoa1,GPIO.HIGH)
    GPIO.output(msoa2,GPIO.LOW)
    GPIO.output(msoo1,GPIO.HIGH)
    GPIO.output(msoo2,GPIO.LOW)
####################################################
def geri():
    #sag geri
    GPIO.output(ms1a,GPIO.LOW)
    GPIO.output(msa2,GPIO.HIGH)
    GPIO.output(mso1,GPIO.LOW)
    GPIO.output(mso2,GPIO.HIGH)
    ##########################
    #sol geri
    GPIO.output(msoa1,GPIO.LOW)
    GPIO.output(msoa2,GPIO.HIGH)
    GPIO.output(msoo1,GPIO.LOW)
    GPIO.output(msoo2,GPIO.HIGH)
####################################################
def sag()
    #sag geri
    GPIO.output(ms1a,GPIO.LOW)
    GPIO.output(msa2,GPIO.HIGH)
    GPIO.output(mso1,GPIO.LOW)
    GPIO.output(mso2,GPIO.HIGH)
    ##########################
    #sol ileri
    GPIO.output(msoa1,GPIO.HIGH)
    GPIO.output(msoa2,GPIO.LOW)
    GPIO.output(msoo1,GPIO.HIGH)
    GPIO.output(msoo2,GPIO.LOW)
####################################################
def sol():
    #sag ileri
    GPIO.output(ms1a,GPIO.HIGH)
    GPIO.output(msa2,GPIO.LOW)
    GPIO.output(mso1,GPIO.HIGH)
    GPIO.output(mso2,GPIO.LOW)
    ##########################
    GPIO.output(msoa1,GPIO.LOW)
    GPIO.output(msoa2,GPIO.HIGH)
    GPIO.output(msoo1,GPIO.LOW)
    GPIO.output(msoo2,GPIO.HIGH)
####################################################
def dur():
    #sag dur
    GPIO.output(ms1a,GPIO.LOW)
    GPIO.output(msa2,GPIO.LOW)
    GPIO.output(mso1,GPIO.LOW)
    GPIO.output(mso2,GPIO.LOW)  
    ##########################  
    #sol dur
    GPIO.output(msoa1,GPIO.LOW)
    GPIO.output(msoa2,GPIO.LOW)
    GPIO.output(msoo1,GPIO.LOW)
    GPIO.output(msoo2,GPIO.LOW)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def kbevent(event):
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    GPIO.setup(ms1a, GPIO.OUT)
    GPIO.setup(msa2, GPIO.OUT)
    GPIO.setup(mso1, GPIO.OUT)
    GPIO.setup(mso2, GPIO.OUT)
    #############
    GPIO.setup(msoa1,GPIO.OUT)
    GPIO.setup(msoa2,GPIO.OUT)
    GPIO.setup(msoo1,GPIO.OUT)
    GPIO.setup(msoo2,GPIO.OUT)
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

     if event.Ascii == 119:
        print("ileri")
        ileri()
        time.sleep(0.01)
        dur()
    ############################################################################################################################################################
    if event.Ascii == 115:
        print("geri")
        geri()
        time.sleep(0.05)
        dur()
    ############################################################################################################################################################
    if event.Ascii == 97:
        sag()
        time.sleep(0.01)
        dur()
    ############################################################################################################################################################   
    if  event.Ascii == 100:
        print("sag")
        sol()
        time.sleep(0.01)
        dur()
    ############################################################################################################################################################
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
hookman = pyxhook.HookManager()
hookman.KeyDown = kbevent
hookman.HookKeyboard()
hookman.start()
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
GPIO.cleanup()
