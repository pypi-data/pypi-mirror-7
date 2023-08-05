from Tkinter import *
import math,time
from bldmat import *
from matutil import insertmat,evalmat
from tkMessageBox import showerror
from disreport import DisReport

class MkReport():
	""" class MkReport is a continuation of the NetAna application.
	This part writes the output results for both the AC and DC analysis.
	"""
	def __init_(self,parent):
		self.parent = parent

	def mkreport(self):
		try:
			if not isinstance(self.NetDict['VG'],float):
				raise TypeError
		except TypeError:
			self.showerror('Error','VG must be of type float')

		self.AcDc = 'DC'
		for key in self.NetDict:
			if key[0] in ['L','C']: self.AcDc='AC'


		# Start evaluating equations
		self.outfile = open(self.ReportFile, 'w')
		self.matvalues = self.EvalEqu(self.Mat)   # Convert Equation string to values
		print >> self.outfile,"# Analysis Created by 'NetAna'."
		when = time.ctime()
		lend = "\n# Date Created: "+when+"\n#\n\n"
		if self.AcDc == 'AC':
			if self.AnalType == 'Node':
				# AC Node Analysis
				print >> self.outfile, "# AC Node Analysis of file: ", self.FileName
				print >> self.outfile, "# Report file created: ", self.ReportFile, lend
				self.DoACAnalysis('IG')
			else:
				# AC Mash Analysis
				print >> self.outfile, "# AC Mash Analysis of file: ", self.FileName
				print >> self.outfile, "# Report file created: ", self.ReportFile, lend
				self.DoACAnalysis('VG')
		else:
			if self.AnalType == 'Node':
				# DC Node Analysis
				print >> self.outfile, "# DC Node Analysis of file: ", self.FileName
				print >> self.outfile, "# Report file created: ", self.ReportFile, lend
				self.DoDCAnalysis('IG')
			else:
				# DC Mash Analysis
				print >> self.outfile, "# DC Mash Analysis of file: ", self.FileName
				print >> self.outfile, "# Report file created: ", self.ReportFile, lend
				self.DoDCAnalysis('VG')

	def DoACAnalysis(self,source='VG'):
		if source == 'VG':
			uLab = 'i'
			dLab = 'Amps'
		else:
			uLab = 'e'
			dLab = 'Volts'

		if 'IGLIST' in self.NetDict :
			m = self.NetDict['IGLIST']
		elif 'VGLIST' in self.NetDict:
			m = self.NetDict['VGLIST']
		else:
			m = bldmat(1,self.Nodes,0)
			# Input 'VG' or 'IG'
			m[0] = self.NetDict[source]

		outbuf = []
		print >> self.outfile,'##### Units =', dLab, '####\n'
		try:
			fstart, fstop, finc, flab = self.NetDict['FREQ']
		except:
			self.showerror("Error",'"FREQ" not defined!')
		else:
			# Save the Component values in a separate dictonary XCompDict
			self.SaveCompValues()
			# Print Header
			self.FreqUnits = flab # Save freq. units
			s1 = " "*7; s2= " "*4
			print >>self.outfile, '# Frequency(%s)%sMagnitude(db)%sPhase Angle(deg)' % (flab,s1,s2)
			for freq in self.genfreq(fstart, fstop, finc):
				print >> self.outfile, "%10.2f" % (freq),
				tox = 2*math.pi*freq*1j
				for n in range(self.Nodes):   # Do all nodes
					# Convert reactive components to reactances
					for key in self.XCompDict:
						if key[0] in ['L','C']:
							self.NetDict[key] = self.XCompDict[key] * tox
					# Convert Equation string to values
					self.matvalues = self.EvalEqu(self.Mat)
					# Solve for all voltages or currents.
					determ = insertmat(self.matvalues,m,n)
					num = evalmat(determ)
					dem = evalmat(self.matvalues)
					res = num/dem
					res_key = uLab.upper()+str(n+1)
					self.NetDict[res_key] = res


				# Now finished nodes for this frequency
				# Get User Transfer Function and Evaluate it.
				try:
					stf = self.NetDict['TF']
				except:
					self.showerror("Error",'Transfer Function "TF" not defined!')
					break
				else:
					tf = eval(stf,self.GlobalDict,self.NetDict)
					# See if tf is near or eq zero
					# if it is set it to small value
					if abs(tf) < 1.0e-6: tf = complex(1.0e-30, 0.0)
					mag = 20.0*math.log10(abs(tf))
					angle = math.degrees(math.atan(tf.imag/tf.real))
					print >> self.outfile, "%s%+10.4f%s%+8.4f" \
					% (" "*10, mag, " "*10, angle )



		self.outfile.close()

		# Show Report
		DisReport(self.parent, self.ReportFile)



	def DoDCAnalysis(self,source='VG'):
		if source == 'VG':
			uLab = 'i'
			dLab = 'Amps'
		else:
			uLab = 'e'
			dLab = 'Volts'

		if 'IGLIST' in self.NetDict :
			m = self.NetDict['IGLIST']
		elif 'VGLIST' in self.NetDict:
			m = self.NetDict['VGLIST']
		else:
			m = bldmat(1,self.Nodes,0)
			m[0] = self.NetDict[source]

		dem = evalmat(self.matvalues)
		outbuf = []
		print >> self.outfile,'#### Units =', dLab,'####\n'
		for n in range(self.Nodes):
			determ = insertmat(self.matvalues,m,n)
			num = evalmat(determ)
			res = num/dem
			outbuf.append(res)
			reskey = uLab.upper()+str(n+1)
			self.NetDict[reskey] = res
			print >> self.outfile,'%s%d = %g' % (uLab,n+1,res)

		# Write GOALS to Report File
		if 'GOALS' in self.NetDict:
			print >> self.outfile	# Write one \n
			for goalnb in range(self.NetDict['GOALS']):
				goalkey = 'GOAL'+ str(goalnb+1)
				goal_result = eval(self.NetDict[goalkey][0],self.NetDict,self.NetDict)
				# Add goal result to dict for goal chaining
				gres = 'GR' + str(goalnb+1)
				self.NetDict[gres] = goal_result
				gUnit = self.NetDict[goalkey][1]
				print >> self.outfile,'%s = %g %s\t%s' % ( goalkey, goal_result,\
				 gUnit, self.NetDict[goalkey] )

		self.outfile.close()

		# Display Report
		DisReport(self.parent, self.ReportFile)

	def EvalEqu(self,equ):
		""" Converts the equation strings to numeric values
		by using the function 'eval' on the strings."""
		res = []
		for r in range(len(equ)):
			temp = []
			for c in range(len(equ)):
				try:
					temp.append(eval(equ[r][c],self.NetDict,self.NetDict))
				except:
					self.showerror("errror","Equation Syntax Error row = %s col = %s" % (r,c))
			res.append(temp)
		return res


	def SaveCompValues(self):
		for key in self.NetDict:
			if key[0] in ['L','C']:
				self.XCompDict[key] = self.NetDict[key]


	def genfreq(self,start,stop,inc):
		""" This method returns the next number in a sequence
		using the Python "yield" statment in order to return one value
		at a time instead of a list all at once.
		call:  genfreq(start, stop, increment)
		"""
		freq = start
		while freq < stop:
			yield freq
			freq += inc

