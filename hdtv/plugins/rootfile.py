# -*- coding: utf-8 -*-

# HDTV - A ROOT-based spectrum analysis software
#  Copyright (C) 2006-2009  The HDTV development team (see file AUTHORS)
#
# This file is part of HDTV.
#
# HDTV is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# HDTV is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with HDTV; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

# Preliminary ROOT file interface for hdtv

import ROOT
import hdtv.cmdline
import hdtv.tabformat
import hdtv.spectrum
import fnmatch

class RootFile:
	def __init__(self, window, spectra, caldict):
		print "Loaded user interface for working with root files"
		self.window = window
		self.spectra = spectra
		self.caldict = caldict
		self.rootfile = None
		self.browser = None
		self.matviews = list()
		
		hdtv.cmdline.AddCommand("root browse", self.RootBrowse, nargs=0)
		hdtv.cmdline.AddCommand("root ls", self.RootLs, maxargs=1)
		hdtv.cmdline.AddCommand("root ll", self.RootLL, maxargs=1, level=2)
		hdtv.cmdline.AddCommand("root cd", self.RootCd, nargs=1, fileargs=True)

		parser = hdtv.cmdline.HDTVOptionParser(prog="root get", usage="%prog [OPTIONS] <pattern>")
		parser.add_option("-r", "--replace", action="store_true",
    		              default=False, help="replace existing histogram list")
		parser.add_option("-c", "--load-cal", action="store_true",
		                  default=False, help="load calibration from calibration dictionary")
		parser.add_option("-v", "--invisible", action="store_true",
		                  default=False, help="do not make histograms visible, only add to display list")
		hdtv.cmdline.AddCommand("root get", self.RootGet, nargs=1, completer=self.RootGet_Completer,
		                        parser=parser)
		
		hdtv.cmdline.AddCommand("root matrix", self.RootMatrix, nargs=1,
		                        completer=self.RootGet_Completer,
		                        usage="root matrix <matname>")
	
	def RootBrowse(self, args):
		self.browser = ROOT.TBrowser()
		
		if self.rootfile != None and not self.rootfile.IsZombie():
			self.rootfile.Browse(self.browser)

	def RootLs(self, args):
		if self.rootfile == None or self.rootfile.IsZombie():
			print "Error: no root file"
			return
		
		keys = self.rootfile.GetListOfKeys()
		names = [k.GetName() for k in keys]
	
		if len(args) > 0:
			names = fnmatch.filter(names, args[0])
		
		names.sort()
		hdtv.tabformat.tabformat(names)
	
	def RootLL(self, args):
		if self.rootfile == None or self.rootfile.IsZombie():
			print "Error: no root file"
			return
			
		if len(args) == 0:
			self.rootfile.ls()
		else:
			self.rootfile.ls(args[0])
			
	def RootCd(self, args):
		if self.rootfile != None:
			self.rootfile.Close()
		
		self.rootfile = ROOT.TFile(args[0])
		if self.rootfile.IsZombie():
			print "Error: failed to open file"
			self.rootfile = None
			
		hdtv.cmdline.RegisterInteractive("gRootFile", self.rootfile)
		
	def RootGet_Completer(self, text):
		if self.rootfile == None or self.rootfile.IsZombie():
			# Autocompleter must not complain...
			return
			
		keys = self.rootfile.GetListOfKeys()
		names = [k.GetName() for k in keys]
	
		options = []
		l = len(text)
		for name in names:
			if name[0:l] == text:
				options.append(name)
				
		return options
		
	def RootMatrix(self, args):
		if self.rootfile == None or self.rootfile.IsZombie():
			print "Error: no root file"
			return
			
		hist = self.rootfile.Get(args[0])
		if hist == None or not isinstance(hist, ROOT.TH2):
			print "Error: %s is not a 2d histogram" % args[0]
		
		title = hist.GetTitle()
		viewer = ROOT.HDTV.Display.MTViewer(400, 400, hist, title)
		self.matviews.append(viewer)
	
	def RootGet(self, args, options):
		if self.rootfile == None or self.rootfile.IsZombie():
			print "Error: no root file"
			return
			
		if options.replace:
			self.spectra.RemoveAll()
			
		nloaded = 0
		keys = self.rootfile.GetListOfKeys()
		self.window.viewport.LockUpdate()
		for key in keys:
			if fnmatch.fnmatch(key.GetName(), args[0]):
				obj = key.ReadObj()
				if isinstance(obj, ROOT.TH1):
					spec = hdtv.spectrum.Spectrum(obj)
					ID = self.spectra.Add(spec)
					spec.SetColor(hdtv.color.ColorForID(ID))
					
					if options.load_cal:
						if obj.GetName() in self.caldict:
							spec.SetCal(self.caldict[obj.GetName()])
						else:
							print "Warning: no calibration found for %s" % obj.GetName()
					
					if options.invisible:
						self.spectra.HideObjects(ID)
					else:
						self.spectra.ActivateObject(ID)
					
					nloaded += 1
				else:
					print "Warning: %s is not a 1D histogram object" % key.GetName()
					
		print "%d spectra loaded" % nloaded
		
		self.window.viewport.UnlockUpdate()


# plugin initialisation
import __main__
import specInterface 
r = RootFile(__main__.window, __main__.spectra, __main__.s.caldict)
