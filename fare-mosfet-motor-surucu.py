from __future__ import print_function

import RPi.GPIO as GPIO
import sys
import re
import time
import threading

from Xlib import X, XK, display
from Xlib.ext import record
from Xlib.protocol import rq

global yon
yon="Dur"

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
        GPIO.setmode(GPIO.BOARD)
	    #Sag-Sol
	    sag=29
	    sol=31
	    #############
	    #Yukari-Asagi
	    asagi=33
	    ayukari=35
	    #############
	    ats=37
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	    GPIO.setup(sag, GPIO.OUT)
	    GPIO.setup(sol, GPIO.OUT)
	    GPIO.setup(asagi, GPIO.OUT)
	    GPIO.setup(yukari, GPIO.OUT)
	    ##########################
	    #Ekran cozunurlugu
        x=640
        y=480
        x1=(x/3)*1
        x2=(x/3)*2
        y1=(y/3)*1
        y2=(y/3)*2
	    ##########################
	    '''
                #Ates et
                GPIO.output(ats,GPIO.HIGH)
                ##########################
                #Ates kes
                GPIO.output(ats,GPIO.LOW)
                ##########################
                #Sag- Sol
                GPIO.output(sag,GPIO.HIGH)
                GPIO.output(sol,GPIO.HIGH)
                ##########################
                #Yukari - Asagi
                GPIO.output(yukari,GPIO.HIGH)
                GPIO.output(asagi,GPIO.HIGH)
                ##########################

                
	    '''
        if(int(xp)<=x1 and int(xp)>=0 ): 
            if(int(yp)>=0 and int(yp)<=y1):
                print("Sol ust")
                yon ="sol_ust"

        if(int(xp)<=x1 and int(xp)>=0 ): 
            if(int(yp)>=y1 and int(yp)<=y2):
                print("Sol")
                yon ="sol"

        if(int(xp)<=x1 and int(xp)>=0 ): 
            if(int(yp)>=y2 and int(yp)<=y):
                print("Sol alt")
                yon ="sol_alt"

        if(int(xp)<=x2 and int(xp)>=x1 ): 
            if(int(yp)>=0 and int(yp)<=y1):
                print("Ust")
                yon ="ust"

        if(int(xp)<=x2 and int(xp)>=x1 ): 
            if(int(yp)>=y1 and int(yp)<=y2):
                print("Dur")
                yon ="dur"

        if(int(xp)<=x2 and int(xp)>=x1 ): 
            if(int(yp)>=y2 and int(yp)<=y):
                print("Alt")
                yon ="alt"

        if(int(xp)<=x and int(xp)>=x2 ): 
            if(int(yp)>=0 and int(yp)<=y1):
                print("Sag ust")
                yon ="sag_ust"

        if(int(xp)<=x and int(xp)>=x2 ): 
            if(int(yp)>=y1 and int(yp)<=y2):
                print("Sag")
                yon ="sag"

        if(int(xp)<=x and int(xp)>=x2 ): 
            if(int(yp)>=y2 and int(yp)<=y):
                print("Sag alt")
                yon ="sag_alt"

	    if(yon=="sol_ust"):
		    #Sol
            GPIO.output(sol,GPIO.HIGH)
            ##########################
            #Yukari
            GPIO.output(yukari,GPIO.HIGH)
            ########################## 

	    if(yon=="sol"):
		    #Sol
            GPIO.output(sol,GPIO.HIGH)
            ##########################

	    if(yon=="sol_alt"):
		    #Sol
            GPIO.output(sol,GPIO.HIGH)
            ##########################
            #Asagi
            GPIO.output(asagi,GPIO.HIGH)
            ##########################

	     if(yon=="ust"):
            #Yukari
            GPIO.output(yukari,GPIO.HIGH)
            ########################## 
    
	     if(yon=="dur"):
		    #Dur
		    GPIO.output(yukari,GPIO.LOW)
            GPIO.output(asagi,GPIO.LOW)
            GPIO.output(sag,GPIO.LOW)
            GPIO.output(sol,GPIO.LOW)
            ##########################

	     if(yon=="alt"):
		    #Asagi
            GPIO.output(asagi,GPIO.HIGH)
            ##########################

	     if(yon=="sag_ust"):
		    #Sag
            GPIO.output(sag,GPIO.HIGH)
            ##########################
            #Ust
            GPIO.output(yukari,GPIO.HIGH)
            ##########################
            
	      if(yon=="sag"):
		    #Sag
            GPIO.output(sag,GPIO.HIGH)
            ##########################

	      if(yon=="sag_alt"):
		     #Sag
             GPIO.output(sag,GPIO.HIGH)
             ##########################
             #Asagi
             GPIO.output(asagi,GPIO.HIGH)
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

        if event.type == X.ButtonPress:
            MessageName = "{}".format(MessageName)
        elif event.type == X.ButtonRelease:
            MessageName = "{}".format(MessageName)
        
        else:
            MessageName = "mouse moved"
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
