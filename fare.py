
from __future__ import print_function

import sys
import re
import time
import threading
import os 
import RPi.GPIO as GPIO

from Xlib import X, XK, display
from Xlib.ext import record
from Xlib.protocol import rq

GPIO.setmode(GPIO.BOARD)

global ss1
global ss2
global ay1
global ay2
global ats
#Sag-Sol
ss1=29
ss2=31
#############
#Yukari-Asagi
ay1=33
ay2=35
#############
ats=37
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
GPIO.setup(ss1, GPIO.OUT)
GPIO.setup(ss2, GPIO.OUT)
GPIO.setup(ay1, GPIO.OUT)
GPIO.setup(ay2, GPIO.OUT)
##########################

'''
                #Ates et
                GPIO.output(ats,GPIO.HIGH)
                ##########################
                #Ates kes
                GPIO.output(ats,GPIO.LOW)
                ##########################
                #Sag
                GPIO.output(ss1,GPIO.HIGH)
                GPIO.output(ss2,GPIO.LOW)
                ##########################
                #Sol
                GPIO.output(ss1,GPIO.LOW)
                GPIO.output(ss2,GPIO.HIGH)
                ##########################
                #Yukari
                GPIO.output(ay1,GPIO.HIGH)
                GPIO.output(ay2,GPIO.LOW)
                ##########################
                #Asagi
                GPIO.output(ay1,GPIO.LOW)
                GPIO.output(ay2,GPIO.HIGH)
                ##########################
                
                
                
                
                
'''
class HookManager(threading.Thread):

    def __init__(self,parameters=False):
        threading.Thread.__init__(self)
        self.finished = threading.Event()
        self.mouse_position_x = 0
        self.mouse_position_y = 0
        self.ison = {"shift": False, "caps": False}


        self.isshift = re.compile('^Shift')
        self.iscaps = re.compile('^Caps_Lock')
        self.shiftablechar = re.compile('|'.join((
            '^[a-z0-9]$',
            '^minus$',
            '^equal$',
            '^bracketleft$',
            '^bracketright$',
            '^semicolon$',
            '^backslash$',
            '^apostrophe$',
            '^comma$',
            '^period$',
            '^slash$',
            '^grave$'
        )))
        self.logrelease = re.compile('.*')
        self.isspace = re.compile('^space$')

        self.parameters=parameters
        if parameters:
            self.lambda_function=lambda x,y: True
        else:
            self.lambda_function=lambda x: True

        self.KeyDown = self.lambda_function
        self.KeyUp = self.lambda_function
        self.MouseAllButtonsDown = self.lambda_function
        self.MouseAllButtonsUp = self.lambda_function
        self.MouseMovement = self.lambda_function
        
        self.KeyDownParameters = {}
        self.KeyUpParameters = {}
        self.MouseAllButtonsDownParameters = {}
        self.MouseAllButtonsUpParameters= {}
        self.MouseMovementParameters = {}

        self.contextEventMask = [X.KeyPress, X.MotionNotify]

        self.local_dpy = display.Display()
        self.record_dpy = display.Display()

    def run(self):

        if not self.record_dpy.has_extension("RECORD"):
            print("RECORD extension not found", file=sys.stderr)
            sys.exit(1)

        self.ctx = self.record_dpy.record_create_context(
            0,
            [record.AllClients],
            [{
                'core_requests': (0, 0),
                'core_replies': (0, 0),
                'ext_requests': (0, 0, 0, 0),
                'ext_replies': (0, 0, 0, 0),
                'delivered_events': (0, 0),

                'device_events': tuple(self.contextEventMask),
                'errors': (0, 0),
                'client_started': False,
                'client_died': False,
            }])


        self.record_dpy.record_enable_context(self.ctx, self.processevents)

        self.record_dpy.record_free_context(self.ctx)

    def cancel(self):
        self.finished.set()
        self.local_dpy.record_disable_context(self.ctx)
        self.local_dpy.flush()

    def printevent(self, event):
        print(event)



    def HookKeyboard(self):

        pass

    def HookMouse(self):

        pass

    def processhookevents(self,action_type,action_parameters,events):

        if self.parameters:
            action_type(events,action_parameters)
        else:
            action_type(events)


    def processevents(self, reply):
        if reply.category != record.FromServer:
            return
        if reply.client_swapped:
            print("* received swapped protocol data, cowardly ignored")
            return
        try:

            intval = ord(reply.data[0])
        except TypeError:

            intval = reply.data[0]
        if (not reply.data) or (intval < 2):

            return
        data = reply.data
        while len(data):
            event, data = rq.EventField(None).parse_binary_value(
                data,
                self.record_dpy.display,
                None,
                None
            )
            if event.type == X.KeyPress:
                hookevent = self.keypressevent(event)
                self.processhookevents(self.KeyDown,self.KeyDownParameters,hookevent)
            elif event.type == X.KeyRelease:
                hookevent = self.keyreleaseevent(event)
                self.processhookevents(self.KeyUp,self.KeyUpParameters,hookevent)
            elif event.type == X.ButtonPress:
                hookevent = self.buttonpressevent(event)
                self.processhookevents(self.MouseAllButtonsDown,self.MouseAllButtonsDownParameters,hookevent)
            elif event.type == X.ButtonRelease:
                hookevent = self.buttonreleaseevent(event)
                self.processhookevents(self.MouseAllButtonsUp,self.MouseAllButtonsUpParameters,hookevent)
            elif event.type == X.MotionNotify:

                hookevent = self.mousemoveevent(event)
                self.processhookevents(self.MouseMovement,self.MouseMovementParameters,hookevent)



    def keypressevent(self, event):
        matchto = self.lookup_keysym(
            self.local_dpy.keycode_to_keysym(event.detail, 0)
        )
        if self.shiftablechar.match(
                self.lookup_keysym(
                    self.local_dpy.keycode_to_keysym(event.detail, 0))):

            if not self.ison["shift"]:
                keysym = self.local_dpy.keycode_to_keysym(event.detail, 0)
                return self.makekeyhookevent(keysym, event)
            else:
                keysym = self.local_dpy.keycode_to_keysym(event.detail, 1)
                return self.makekeyhookevent(keysym, event)
        else:

            keysym = self.local_dpy.keycode_to_keysym(event.detail, 0)
            if self.isshift.match(matchto):
                self.ison["shift"] = self.ison["shift"] + 1
            elif self.iscaps.match(matchto):
                if not self.ison["caps"]:
                    self.ison["shift"] = self.ison["shift"] + 1
                    self.ison["caps"] = True
                if self.ison["caps"]:
                    self.ison["shift"] = self.ison["shift"] - 1
                    self.ison["caps"] = False
            return self.makekeyhookevent(keysym, event)

    def keyreleaseevent(self, event):
        if self.shiftablechar.match(
                self.lookup_keysym(
                    self.local_dpy.keycode_to_keysym(event.detail, 0))):
            if not self.ison["shift"]:
                keysym = self.local_dpy.keycode_to_keysym(event.detail, 0)
            else:
                keysym = self.local_dpy.keycode_to_keysym(event.detail, 1)
        else:
            keysym = self.local_dpy.keycode_to_keysym(event.detail, 0)
        matchto = self.lookup_keysym(keysym)
        if self.isshift.match(matchto):
            self.ison["shift"] = self.ison["shift"] - 1
        return self.makekeyhookevent(keysym, event)

    def buttonpressevent(self, event):

        return self.makemousehookevent(event)

    def buttonreleaseevent(self, event):

        return self.makemousehookevent(event)

    def mousemoveevent(self, event):
        self.mouse_position_x = event.root_x
        self.mouse_position_y = event.root_y 
        
        xp=event.root_x
        yp=event.root_y

        #print(str(xp)+"_"+str(yp))
        
        '''
                #Sag
                GPIO.output(ss1,GPIO.HIGH)
                GPIO.output(ss2,GPIO.LOW)
                ##########################
                #Sol
                GPIO.output(ss1,GPIO.LOW)
                GPIO.output(ss2,GPIO.HIGH)
                ##########################
                #Yukari
                GPIO.output(ay1,GPIO.HIGH)
                GPIO.output(ay2,GPIO.LOW)
                ##########################
                #Asagi
                GPIO.output(ay1,GPIO.LOW)
                GPIO.output(ay2,GPIO.HIGH)
                ##########################
                #Dur
                GPIO.output(ss1,GPIO.LOW)
                GPIO.output(ss2,GPIO.LOW)
                GPIO.output(ay1,GPIO.LOW)
                GPIO.output(ay2,GPIO.LOW)
                ##########################
        '''
        
        
        if(int(xp)<=455 and int(xp)>=0 ): 
            if(int(yp)>=0 and int(yp)<=256):
                print("Sol ust")
                #Sol
                GPIO.output(ss1,GPIO.LOW)
                GPIO.output(ss2,GPIO.HIGH)
                ##########################
                GPIO.output(ay1,GPIO.HIGH)
                GPIO.output(ay2,GPIO.LOW)
                ##########################
        if(int(xp)<=455 and int(xp)>=0 ): 
            if(int(yp)>=256 and int(yp)<=516):
                print("Sol")
                #Sol
                GPIO.output(ss1,GPIO.LOW)
                GPIO.output(ss2,GPIO.HIGH)
                ##########################
        if(int(xp)<=455 and int(xp)>=0 ): 
            if(int(yp)>=516 and int(yp)<=767):
                print("Sol alt")
                #Sol
                GPIO.output(ss1,GPIO.LOW)
                GPIO.output(ss2,GPIO.HIGH)
                ##########################
                #Asagi
                GPIO.output(ay1,GPIO.LOW)
                GPIO.output(ay2,GPIO.HIGH)
                ##########################
        if(int(xp)<=910 and int(xp)>=455 ): 
            if(int(yp)>=0 and int(yp)<=256):
                print("Ust")
                #Yukari
                GPIO.output(ay1,GPIO.HIGH)
                GPIO.output(ay2,GPIO.LOW)
                ##########################  
        if(int(xp)<=910 and int(xp)>=455 ): 
            if(int(yp)>=256 and int(yp)<=516):
                print("Dur")
                #Dur
                GPIO.output(ss1,GPIO.LOW)
                GPIO.output(ss2,GPIO.LOW)
                GPIO.output(ay1,GPIO.LOW)
                GPIO.output(ay2,GPIO.LOW)
                ##########################
        if(int(xp)<=910 and int(xp)>=455 ): 
            if(int(yp)>=516 and int(yp)<=767):
                print("Alt")
                #Asagi
                GPIO.output(ay1,GPIO.LOW)
                GPIO.output(ay2,GPIO.HIGH)
                ##########################
        if(int(xp)<=1365 and int(xp)>=910 ): 
            if(int(yp)>=0 and int(yp)<=256):
                print("Sag ust")
                #Sag
                GPIO.output(ss1,GPIO.HIGH)
                GPIO.output(ss2,GPIO.LOW)
                ##########################
        if(int(xp)<=1365 and int(xp)>=910 ): 
            if(int(yp)>=256 and int(yp)<=516):
                print("Sag")
                #Sag
                GPIO.output(ss1,GPIO.HIGH)
                GPIO.output(ss2,GPIO.LOW)
                ##########################
        if(int(xp)<=1365 and int(xp)>=910 ): 
            if(int(yp)>=516 and int(yp)<=767):
                print("Sag alt")
                #Sag
                GPIO.output(ss1,GPIO.HIGH)
                GPIO.output(ss2,GPIO.LOW)
                ##########################
                #Asagi
                GPIO.output(ay1,GPIO.LOW)
                GPIO.output(ay2,GPIO.HIGH)
                ##########################


        return self.makemousehookevent(event)

 
    def lookup_keysym(self, keysym):
        for name in dir(XK):
            if name.startswith("XK_") and getattr(XK, name) == keysym:
                return name.lstrip("XK_")
        return "[{}]".format(keysym)

    def asciivalue(self, keysym):
        asciinum = XK.string_to_keysym(self.lookup_keysym(keysym))
        return asciinum % 256

    def makekeyhookevent(self, keysym, event):
        storewm = self.xwindowinfo()
        if event.type == X.KeyPress:
            MessageName = "key down"
        elif event.type == X.KeyRelease:
            MessageName = "key up"
        return pyxhookkeyevent(
            storewm["handle"],
            storewm["name"],
            storewm["class"],
            self.lookup_keysym(keysym),
            self.asciivalue(keysym),
            False,
            event.detail,
            MessageName
        )

    def makemousehookevent(self, event):
        storewm = self.xwindowinfo()
        if event.detail == 1:
            MessageName = ""
            print("ates")
            #Ates et
            GPIO.output(ats,GPIO.HIGH)
            ##########################
        elif event.detail == 3:
            MessageName = "mouse right "
        elif event.detail == 2:
            MessageName = "mouse middle "
        elif event.detail == 5:
            MessageName = "mouse wheel down "
        elif event.detail == 4:
            MessageName = "mouse wheel up "
        else:
            MessageName = "mouse {} ".format(event.detail)
            #Ates kes
            GPIO.output(ats,GPIO.LOW)
            ##########################
        if event.type == X.ButtonPress:
            MessageName = "{}".format(MessageName)
        elif event.type == X.ButtonRelease:
            MessageName = "{}".format(MessageName)
        
        else:
            MessageName = "Fare hareket ediyor"
        return pyxhookmouseevent(
            storewm["handle"],
            storewm["name"],
            storewm["class"],
            (self.mouse_position_x, self.mouse_position_y),
            MessageName
        )

    def xwindowinfo(self):
        try:
            windowvar = self.local_dpy.get_input_focus().focus
            wmname = windowvar.get_wm_name()
            wmclass = windowvar.get_wm_class()
            wmhandle = str(windowvar)[20:30]
        except:

            return {"name": None, "class": None, "handle": None}
        if (wmname is None) and (wmclass is None):
            try:
                windowvar = windowvar.query_tree().parent
                wmname = windowvar.get_wm_name()
                wmclass = windowvar.get_wm_class()
                wmhandle = str(windowvar)[20:30]
            except:

                return {"name": None, "class": None, "handle": None}
        if wmclass is None:
            return {"name": wmname, "class": wmclass, "handle": wmhandle}
        else:
            return {"name": wmname, "class": wmclass[0], "handle": wmhandle}


class pyxhookkeyevent:


    def __init__(
            self, Window, WindowName, WindowProcName, Key, Ascii, KeyID,
            ScanCode, MessageName):
        self.Window = Window
        self.WindowName = WindowName
        self.WindowProcName = WindowProcName
        self.Key = Key
        self.Ascii = Ascii
        self.KeyID = KeyID
        self.ScanCode = ScanCode
        self.MessageName = MessageName

    def __str__(self):
        return '\n'.join((
            #'Window Handle: {s.Window}',
            #'Window Name: {s.WindowName}',
            #'Window\'s Process Name: {s.WindowProcName}',
            'Key Pressed: {s.Key}',
            'Ascii Value: {s.Ascii}',
            #'KeyID: {s.KeyID}',
            #'ScanCode: {s.ScanCode}',
            #'MessageName: {s.MessageName}',
        )).format(s=self)


class pyxhookmouseevent:

    def __init__(
            self, Window, WindowName, WindowProcName, Position, MessageName):
        self.Window = Window
        self.WindowName = WindowName
        self.WindowProcName = WindowProcName
        self.Position = Position
        self.MessageName = MessageName

    def __str__(self):
        return '\n'.join((
            #'Window Handle: {s.Window}',
            #'Window\'s Process Name: {s.WindowProcName}',
            #'Position: {s.Position}',
            'MessageName: {s.MessageName}',
        )).format(s=self)
        
        
        
if __name__ == '__main__':
    hm = HookManager()
    #hm.HookKeyboard()
    hm.HookMouse()
    
    #hm.KeyDown = hm.printevent
    #hm.KeyUp = hm.printevent
    #hm.MouseAllButtonsDown = hm.printevent
    #hm.MouseAllButtonsUp = hm.printevent
    #hm.MouseMovement = hm.printevent
    hm.start()
    #time.sleep(10)
