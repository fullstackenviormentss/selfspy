from Foundation import NSObject, NSLog
from AppKit import NSApplication, NSApp, NSWorkspace
from Cocoa import (NSEvent,
                   NSKeyDown, NSKeyDownMask, NSKeyUp, NSKeyUpMask,
                   NSLeftMouseUp, NSLeftMouseDown, NSLeftMouseUpMask, NSLeftMouseDownMask,
                   NSRightMouseUp, NSRightMouseDown, NSRightMouseUpMask, NSRightMouseDownMask,
                   NSMouseMoved, NSMouseMovedMask,
                   NSScrollWheel, NSScrollWheelMask,
                   NSAlternateKeyMask, NSCommandKeyMask, NSControlKeyMask)
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
from PyObjCTools import AppHelper

class SniffCocoa:
    def __init__(self):
        self.key_hook = lambda x: True
        self.mouse_button_hook = lambda x: True
        self.mouse_move_hook = lambda x: True
        self.screen_hook = lambda x: True

    def createAppDelegate (self) :
        sc = self
        class AppDelegate(NSObject):
            def applicationDidFinishLaunching_(self, notification):
                mask = (NSKeyDownMask 
                        | NSKeyUpMask
                        | NSLeftMouseDownMask 
                        | NSLeftMouseUpMask
                        | NSRightMouseDownMask 
                        | NSRightMouseUpMask
                        | NSMouseMovedMask 
                        | NSScrollWheelMask)
                NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(mask, sc.handler)
        return AppDelegate

    def run(self):
        NSApplication.sharedApplication()
        delegate = self.createAppDelegate().alloc().init()
        NSApp().setDelegate_(delegate)
        self.workspace = NSWorkspace.sharedWorkspace()
        AppHelper.runEventLoop()

    def cancel(self):
        AppHelper.stopEventLoop()
    
    def handler(self, event):
        try:
            options = kCGWindowListOptionOnScreenOnly 
            windowList = CGWindowListCopyWindowInfo(options,
                                                    kCGNullWindowID)
            # Should see if it is possible to use NSWindow instead from
            # [event window]. The problem is to get the window owner name.
            for window in windowList:
                if window['kCGWindowOwnerName'] == event.windowNumber():
                    geometry = window['kCGWindowBounds'] 
                    process_name = window['kCGWindowOwnerName']
                    window_name = window('kCGWindowName', u'')
                    if not window_name:
                        window_name = process_name
                    self.screen_hook(process_name,
                                     window_name,
                                     geometry['X'], 
                                     geometry['Y'], 
                                     geometry['Width'], 
                                     geometry['Height'])
                    break
            loc = NSEvent.mouseLocation()
            if event.type() == NSLeftMouseDown:
                self.mouse_button_hook(1, loc.x, loc.y)
#           elif event.type() == NSLeftMouseUp:
#               self.mouse_button_hook(1, loc.x, loc.y)
            elif event.type() == NSRightMouseDown:
                self.mouse_button_hook(3, loc.x, loc.y,)
#           elif event.type() == NSRightMouseUp:
#               self.mouse_button_hook(2, loc.x, loc.y)
            elif event.type() == NSScrollWheel:
                if event.deltaY() > 0:
                    self.mouse_button_hook(4, loc.x, loc.y)
                elif event.deltaY() < 0:
                    self.mouse_button_hook(5, loc.x, loc.y)
                if event.deltaX() > 0:
                    self.mouse_button_hook(6, loc.x, loc.y)
                elif event.deltaX() < 0:
                    self.mouse_button_hook(7, loc.x, loc.y)
#               if event.deltaX() > 0:
#                   self.mouse_button_hook(8, loc.x, loc.y)
#               elif event.deltaX() < 0:
#                   self.mouse_button_hook(9, loc.x, loc.y)
            elif event.type() == NSKeyDown:
                flags = event.modifierFlags()
                modifiers = [] # OS X api doesn't care it if is left or right
                if (flags & NSControlKeyMask):
                    modifiers.append('CONTROL')
                if (flags & NSAlternateKeyMask):
                    modifiers.append('ALTERNATE')
                if (flags & NSCommandKeyMask):
                    modifiers.append('COMMAND')
                self.key_hook(event.keyCode(), 
                              modifiers,
                              event.charactersIgnoringModifiers(),
                              event.isARepeat())
            elif event.type() == NSMouseMoved:
                self.mouse_move_hook(loc.x, loc.y)
        except (Exception, KeyboardInterrupt):
            AppHelper.stopEventLoop()
            raise

if __name__ == '__main__':
    sc = SniffCocoa()
    sc.run()

