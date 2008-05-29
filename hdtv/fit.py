import ROOT
import gspec
from peak import Peak

class Fit:
	"""
	Fit object

	all internal values are uncalibrated values (in channels),
	if spec has a calibration then the values will be automatically converted
	between channels and energies when interacting with the user (Input/Output).
	"""
	def __init__(self, spec, region=None, peaklist=None, bglist=None, 
							 lTail=0, rTail=0):
		self.spec = spec
		self.region = region
		self.peaklist = peaklist
		self.bglist = bglist
		self.leftTail = lTail
		self.rightTail = rTail
		self.fitter = None
		self.fittedPeaks = []
		self.peakFuncID = None
		self.bgFuncID = None
		self.viewport=None

	def __setattr__(self, key, val):
		"""
		Set fit parameter (overwrites the normal set function!)
		 
		The fitter must be reinitilized before the next fit, if the value of 
		spec, region, peaklist, bglist, leftTail or rightTail changed.
		Moreover some values have to be transfered to uncalibrated ones,
		before saving.
		"""
		reset = ["spec", "region", "peaklist", "bglist", "leftTail", "rightTail"]
		if key in reset: 
			# reset fitter as it is deprecated now
			self.__dict__["fitter"] = None
			# and clear the peaklist
			self.__dict__["fittedPeaks"] = []
		if key in ["region", "peaklist"]:
			# convert to uncalibrated values
			val = [self.spec.E2Ch(i) for i in val]
			self.__dict__[key] = val 
		elif key == "bglist":
			# convert all paires to uncalibrated values
			val = [[self.spec.E2Ch(i[0]), self.spec.E2Ch(i[1])] for i in val] 
			self.__dict__[key] = val
		else:
			# use all other values as they are
			self.__dict__[key] = val

	def InitFitter(self):
		"""
		Initialized a new Fitter Object
		"""
		# define a fitter and a region
		fitter = ROOT.GSFitter(self.region[0],self.region[1])
		# add all peaks
		for peak in self.peaklist:
			fitter.AddPeak(peak)
		# add all background regions
		for bg in self.bglist:
			fitter.AddBgRegion(bg[0],bg[1])
		# add LeftTail
		if self.leftTail:
			fitter.SetLeftTails(self.leftTail)
		# add RightTail
		if self.rightTail:
			fitter.SetRightTails(self.rightTail)
		self.fitter = fitter

	def DoPeakFit(self, bgfunc=None, update=True):
		""" 
		Fit all peaks in the current region
		"""
		# check if there is already a fitter available
		if not self.fitter:
			self.InitFitter()
		# TODO: without bg?
		func = self.fitter.Fit(self.spec.fHist, bgfunc)
		numPeaks = int(func.GetParameter(0))
		# information for each peak
		peaks = []
		for i in range(0, numPeaks):
			mean= ROOT.GSFitter.GetPeakPos(func, i)
			fwhm = ROOT.GSFitter.GetPeakFWHM(func, i)
			vol = ROOT.GSFitter.GetPeakVol(func, i)
			lt=ROOT.GSFitter.GetPeakLT(func, i)
			rt=ROOT.GSFitter.GetPeakRT(func, i)
			peaks.append(Peak(mean, fwhm, vol))
		# draw function to viewport
		if self.viewport:
			viewport = self.viewport
			self.peakFuncID = viewport.AddFunc(func, 10, False)
			if self.spec.fCal:
				viewport.GetDisplayFunc(self.peakFuncID).SetCal(self.spec.fCal)
			if update:
				viewport.Update(True)
		return peaks

	def DoBgFit(self, update=True):
		"""
		Fit the background function in the current region
		"""
		# check if there is already a fitter available
		if not self.fitter:
			self.InitFitter()
		bgfunc = self.fitter.FitBackground(self.spec.fHist)
		# draw function to viewport
		if self.viewport:
			viewport = self.viewport
			self.bgFuncID = viewport.AddFunc(bgfunc, 25, False)
			if self.spec.fCal:
				viewport.GetDisplayFunc(self.bgFuncID).SetCal(self.spec.fCal)
			if update:
				viewport.Update(True)
		return bgfunc

	def DoFit(self):
		"""
		Fit first the background and then the peaks
		"""
		if not self.fitter:
			self.InitFitter()
		# fit the background
		bgfunc = self.DoBgFit(update=False)
		# fit the peaks
		peaks = self.DoPeakFit(bgfunc, update=True)
		return peaks

	def Realize(self, viewport, update=True):
		"""
		Draw this spectrum to the window
		"""
		# save the viewport
		self.viewport = viewport
		# TODO: set all markers for this fit (remove old ones before)

		# finally update the viewport
		if update:
			viewport.Update(True)
			
	def Delete(self, update=True):
		"""
		Delete this fit from the window
		"""
		if self.viewport:
			# TODO: markers?

			# background function
			if not self.bgFuncID==None:
				self.viewport.DeleteFunc(self.bgFuncID)
				self.bgFuncID = None
			# peak function
			if not self.peakFuncID==None:
				self.viewport.DeleteFunc(self.peakFuncID)
				self.peakFuncID = None
			# update the viewport
			if update:
				self.viewport.Update(True)
			# finally remove the viewport from this object
			self.viewport = None

	def Update(self, update=True):
		""" 
		Update the screen
		"""
		if not self.bgFuncID==None:
			self.viewport.GetDisplayFunc(self.bgFuncID).SetCal(self.spec.fCal)
		if not self.peakFuncID==None:
			self.viewport.GetDisplayFunc(self.peakFuncID).SetCal(self.spec.fCal)

	def Report(self, output=None):
		"""
		Print the results of the fit to output
		If no output object is given use stdout.
		"""
		pass
