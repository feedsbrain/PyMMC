#!/usr/bin/env python

'''
Created on Nov 25, 2009
@author: Indra Gunawan <indra@indragunawan.com>
'''

import os
import gtk
import pygtk
pygtk.require("2.0")
import subprocess
import gobject
import threading

class PyMMC(object):      
    
    __ffmpeg__ = "/usr/bin/ffmpeg"     
        
    __parameter__ = " -s qcif -acodec libfaac -vcodec h263 -ac 1 -ar 8000 -r 25 -ab 32 -y "
    
    __src_format__ = ['*.avi', '*.mpg', '*.flv', '*.mov', '*.mp4']
    __dst_format__ = ['*.3gp']
    
    gobject.threads_init()
    gtk.gdk.threads_init()
    
    def __init__(self):
        builder = gtk.Builder()
        builder.add_from_file("ui/PyMMC.ui")                
        
        builder.connect_signals({ "on_window_destroy" : gtk.main_quit,
                                 "on_exit_button_clicked" : gtk.main_quit,
                                 "on_about_button_clicked" : self.on_about_button_clicked,                                 
                                 "on_execute_button_clicked" : self.on_execute_button_clicked,                                 
                                 "on_source_browse_button_clicked" : self.on_source_browser_button_clicked,
                                 "on_destination_browse_button_clicked" : self.on_destination_browser_button_clicked })                        
        
        self.source_entry = builder.get_object("source_entry") 
        self.destination_entry = builder.get_object("destination_entry")
        
        self.text_output = builder.get_object("output_text")  
        self.text_buffer = self.text_output.get_buffer()
        
        if os.path.isfile(self.__ffmpeg__):
            command = self.__ffmpeg__+" -version"                        
            self.run_threaded_command(self.text_output, self.text_buffer, command)          
        else: self.text_buffer.set_text("FFmpeg not found!\nPlease install the proper one ...")
           
        self.window = builder.get_object("window")
        self.window.show()    
        
    def run_threaded_command(self, output, buffer, command):
        self.thr = threading.Thread(target = self.read_output(output, buffer, command))
        self.thr.start()
        
    def read_output(self, output, buffer, command):        
        proc = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE)
        while 1:            
            line = proc.stdout.readline()
            if not line:
                break
            gtk.gdk.threads_enter()
            iter = buffer.get_end_iter()
            buffer.place_cursor(iter)
            buffer.insert(iter, line)
            output.scroll_to_mark(buffer.get_insert(), 0.1)
            gtk.gdk.threads_leave()                                      
        
    def is_command_exist(self):
        return os.path.isfile(self.__ffmpeg__)        
    
    def on_about_button_clicked(self, widget, data=None):
        builder = gtk.Builder()
        builder.add_from_file("ui/About.ui")    
        
        self.about = builder.get_object("pymmc_about")
        
        response = self.about.run()
        
        if response == gtk.RESPONSE_CANCEL:
            self.about.destroy()        
        
    def on_execute_button_clicked(self, widget, data=None):        
        source = '"' + self.source_entry.get_text() + '"'
        destination = '"' + self.destination_entry.get_text() + '"'                        
        
        if source != '""' and destination != '""':
            self.text_buffer.set_text("Converting File...\n")
            command = self.__ffmpeg__ + " -i " + source + self.__parameter__ + destination
            self.run_threaded_command(self.text_output, self.text_buffer, command)
            self.text_buffer.set_text("Converting Done...\n")
        else:                         
            self.text_buffer.set_text("Please pick source and destination file ...")
        
    def on_source_browser_button_clicked(self, widget, data=None):
        filename = self.set_video_file_source()
        
        if filename != None:
            self.source_entry.set_text(filename)
        
    def on_destination_browser_button_clicked(self, widget, data=None):
        filename = self.set_video_file_destination()
           
        if filename != None:            
            if os.path.splitext(filename)[1] == "" or os.path.splitext(filename)[1] != os.path.splitext(self.__dst_format__[0])[1]:                
                filename = os.path.splitext(filename)[0] + os.path.splitext(self.__dst_format__[0])[1]               
            self.destination_entry.set_text(filename)
    
    def set_video_file_source(self):
        
        filename = None
        flist = None
        
        format = self.__src_format__                                             
        
        for s in format:
            if flist == None:
                flist = s
            else: flist = flist + ", " + s
        
        dialog = gtk.FileChooserDialog(title="Choose File to Convert",action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                       buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        
        dialog.set_default_response(gtk.RESPONSE_OK)                                                             
        filter = gtk.FileFilter()                                                                   
        
        for s in format:
            filter.add_pattern(s)
            
        filter.set_name("Video Files (" + flist + ")")
        dialog.add_filter(filter)
    
        response = dialog.run()                
    
        if response == gtk.RESPONSE_OK:
            filename = dialog.get_filename()            
        
        dialog.destroy()

        return filename
    
    def set_video_file_destination(self):
        
        filename = None
        flist = None
        
        format = self.__dst_format__                                   
        
        for s in format:
            if flist == None:
                flist = s
            else: flist = flist + ", " + s
        
        dialog = gtk.FileChooserDialog(title="Choose Destination File",action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                       buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        
        dialog.set_default_response(gtk.RESPONSE_OK)
        dialog.set_do_overwrite_confirmation(True)
        filter = gtk.FileFilter()                                                                   
        
        for s in format:
            filter.add_pattern(s)
            
        filter.set_name("Mobile Video Files (" + flist + ")")
        dialog.add_filter(filter)
    
        response = dialog.run()                
    
        if response == gtk.RESPONSE_OK:
            filename = dialog.get_filename()            
        
        dialog.destroy()

        return filename
        
if __name__ == '__main__':
    app = PyMMC()
    gtk.main()