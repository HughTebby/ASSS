#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2010 Hugh Tebby
# Simple Sampler plays a sound when you push its button.
import pygtk
pygtk.require('2.0')
import gtk
import os
from os import *
from signal import SIGTERM
import subprocess
from subprocess import Popen

class SoundPlayer:
  def __init__(self, file, time = ''):
    self.sound_file = file
    self.time = time
    
  def play(self):
    if override.get_active():
      self.time2 = start_time.get_value()
    elif self.time:
      self.time2 = float(self.time)/10
    else:
      self.time2=0
    self.freqs_mplayer = ''
    for freq in freqs:
      self.freqs_mplayer = self.freqs_mplayer + str(freq.get_value())+':'
    self.freqs_mplayer = self.freqs_mplayer[0:len(self.freqs_mplayer)-1]
    self.sound_process = Popen(['mplayer','-ss',str(self.time2),'-af','equalizer=' + str(self.freqs_mplayer),str(self.sound_file)])
   
  # stop playing
  def stop(self):
    os.kill(self.sound_process.pid, SIGTERM)

# This class create a gtk.ToggleButton linked to a sound file.
# Send "toggle", it plays the sound. Send "toggle" again, it stops.
class SamplerButton(gtk.ToggleButton):
  def __init__(self, file = ''):
    filename = os.path.basename(file)
    filename = os.path.splitext(filename)
    filename_array = filename[0].split('#')
    label = filename_array[0]
    if len(filename_array) == 2:
      time = filename_array[1]
    else:
      time = ''
    label = label.capitalize()
    label = label[0:15]
    self.sound = SoundPlayer(file, time)
    super(SamplerButton,self).__init__(label)
    self.connect('toggled', self.toggle)
  
  def play(self):
    self.sound.play()

  def stop(self):
    self.sound.stop()

  def toggle(self,widget):
    if self.get_active():
      self.play()
    else:
      self.stop()


# 1. Initialize a gtk window
# 2. Add a frame for each subdirectory of 'sounds'
# 3. Add a column for each sub-subdirectory
# 4. Add a button for each sound

class Sampler():
  def equalizer_init(self, widget):
    for freq in freqs:
      freq.set_value(0)
      
  def set_volume(self, widget):
    subprocess.Popen( ['aumix','-v',str(self.volume.get_value())] )
      
  def __init__(self):
    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.set_title("Simple sampler")
    window.set_border_width(10)
    window.connect('delete_event',gtk.main_quit)
    
    main_panel = gtk.VPaned()

    # Add 10 frequency equalizer
    equalizer = gtk.HBox(True, 5)
    equalizer_init_button = gtk.Button('Init Eq')
    equalizer.add(equalizer_init_button)

    global freqs
    freqs = []
    for i in range(0,10):
      freqs.append( gtk.VScale(gtk.Adjustment(value=0.0, lower=-10, upper=10, step_incr=0.1)) )
      freqs[i].set_inverted(True)
      equalizer.add(freqs[i])

    equalizer_init_button.connect('clicked',self.equalizer_init)
    
    main_panel.add(equalizer)
    bottom_panel = gtk.HPaned()
    notebook = gtk.Notebook()

    soundsdir = os.listdir('sounds')
    soundsdir.sort()  

    # Add tab for each directory
    for directory in soundsdir:
      tab_label = gtk.Label(directory)    
      framebox = gtk.HBox(True, 5)
      scrolled_window = gtk.ScrolledWindow(None, None)   
      scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
      scrolled_window.shadow_type=(gtk.SHADOW_NONE)
      
      # Add frame for each subdirectory
      soundssubdir = os.listdir('sounds/'+directory)
      for subdir in soundssubdir:        
	scrolled_frame = gtk.ScrolledWindow(None, None)   
	scrolled_frame.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)    
	scrolled_frame.shadow_type=(gtk.SHADOW_NONE)

	soundbox = gtk.VButtonBox()
	soundbox.set_layout(gtk.BUTTONBOX_START)
	
	soundbox.add(gtk.Label(subdir))

	# Add button for each sound in directory
	sounds = os.listdir('sounds/'+directory+'/'+subdir)
	for sound in sounds:             
	  soundbox.add(SamplerButton('sounds/'+directory+'/'+subdir+'/'+sound))
	
	scrolled_frame.add_with_viewport(soundbox)
	framebox.pack_start_defaults(scrolled_frame)
      
      scrolled_window.add_with_viewport(framebox)
      notebook.append_page(scrolled_window, tab_label)
    
    bottom_panel.add(notebook)
  
    side_panel = gtk.VBox(True,5)
    
    self.volume = gtk.VScale(gtk.Adjustment(value=75, lower=0, upper=100, step_incr=10))
    self.volume.set_inverted(True)
    #vol = subprocess.Popen( 'aumix -w'+str(volume.get_value())+' -v'+str(volume.get_value()) )
    vol = self.set_volume
    side_panel.add(self.volume)
    
    self.volume.connect('value-changed',self.set_volume)

    start_time_box = gtk.HBox(False,2)
    global start_time
    start_time = gtk.SpinButton(gtk.Adjustment(value=0, lower=0, upper=200, step_incr=0.1),digits=1)
    global override
    override= gtk.CheckButton()
    start_time_box.add(start_time)
    start_time_box.add(override)

    side_panel.add(start_time_box)

    bottom_panel.add(side_panel)

    main_panel.add(bottom_panel)
    window.add(main_panel)
    window.show_all()

def main():
  gtk.main()

if __name__ == "__main__":
  sampler = Sampler()
  main()


# setting volume in Windows ?

#import ctypes

#mixerSetControlDetails = (
    #ctypes.windll.winmm.mixerSetControlDetails)
    
#mixerGetControlDetails = (
    #ctypes.windll.winmm.mixerGetControlDetailsA)

## Some constants
#MIXER_OBJECTF_MIXER = 0 # mmsystem.h
#VOLUME_CONTROL_ID = 0     # Same on all machines?
#SPEAKER_LINE_FADER_ID = 1 # "Identifier <identifier> in OID value does not resolve to a positive integer"
#MINIMUM_VOLUME = 0     # fader control (MSDN Library)
#MAXIMUM_VOLUME = 65535 # fader control (MSDN Library)

#class MIXERCONTROLDETAILS(ctypes.Structure):
    #_pack_ = 1
    #_fields_ = [('cbStruct', ctypes.c_ulong),
                #('dwControlID', ctypes.c_ulong),
                #('cChannels', ctypes.c_ulong),
                #('cMultipleItems', ctypes.c_ulong),
                #('cbDetails', ctypes.c_ulong),
                #('paDetails', ctypes.POINTER(ctypes.c_ulong))]


#def setVolume(volume):
    #"""Set the speaker volume on the 'Volume Control' mixer"""
    #if not (MINIMUM_VOLUME <= volume <= MAXIMUM_VOLUME):
        #raise ValueError, "Volume out of range"
    #cd = MIXERCONTROLDETAILS(ctypes.sizeof(MIXERCONTROLDETAILS),
                             #SPEAKER_LINE_FADER_ID,
                             #1, 0,
                             #ctypes.sizeof(ctypes.c_ulong),
                             #ctypes.pointer(ctypes.c_ulong(volume)))
    #ret = mixerSetControlDetails(VOLUME_CONTROL_ID,
                                 #ctypes.byref(cd),
                                 #MIXER_OBJECTF_MIXER)
    #if ret != 0:
        #print WindowsError, "Error %d while setting volume" % ret
        
    #ret = mixerGetControlDetails(VOLUME_CONTROL_ID,
                                 #ctypes.byref(cd),
                                 #MIXER_OBJECTF_MIXER)
    #if ret != 0:
        #print WindowsError, "Error %d while setting volume" % ret
    #else:
        #print 'cbStruct', cd.cbStruct
        #print 'dwControlID', cd.dwControlID
        #print 'cChannels', cd.cChannels
        #print 'cMultipleItems', cd.cMultipleItems
        #print 'cbDetails', cd.cbDetails
        #print 'paDetails', cd.paDetails.contents
    #return

#setVolume((2**16-1)/2) 