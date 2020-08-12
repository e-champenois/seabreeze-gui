#!/usr/bin/python3
import numpy as np
from pyqtgraph.Qt import QtCore, QtGui, uic
import pyqtgraph as pg
from seabreeze.spectrometers import list_devices, Spectrometer
from datetime import datetime

from sys import path
path.append("/home/xmas/Documents/Python/modules")
import paths

class SpectraViewer():

	def __init__(self, spec=None):
		if spec is None:
			dev = list_devices()[0]
			self.spec = Spectrometer(dev)
		else:
			self.spec = spec
		self.lmbd = self.spec.wavelengths()
		self.bg = np.zeros_like(self.lmbd)
		self.calibration = np.load("/home/xmas/Documents/Python/xmas/oceanoptics/calibration.npy")

		self.app = QtGui.QApplication([])
		self.ui = uic.loadUi("/home/xmas/Documents/Python/xmas/oceanoptics/spectrum.ui")
		self.plot_live = pg.PlotCurveItem()
		self.pen = pg.mkPen(color='r')
		self.ui.plot_full.addItem(self.plot_live)
		self.ui.show()

		self.ui.plot_full.showGrid(x=True, y=True, alpha=1.0)
		self.ui.xmin.setMinimum(0)
		self.ui.xmax.setMinimum(0)
		self.ui.xmin.setMaximum(self.lmbd.max()*2)
		self.ui.xmax.setMaximum(self.lmbd.max()*2)
		#self.ui.xmin.setValue(self.lmbd.min())
		#self.ui.xmax.setValue(self.lmbd.max())
		self.ui.xmin.setValue(960)
		self.ui.xmax.setValue(1100)
		self.ui.integration.setMinimum(self.spec.integration_time_micros_limits[0]/1000.0)
		self.ui.integration.setMaximum(self.spec.integration_time_micros_limits[1]/1000.0)
		self.ui.integration.setValue(self.spec.integration_time_micros_limits[0]/1000.0)
		self.set_integration_cb()
		self.update_range_cb()

		self.ui.integration.valueChanged.connect(self.set_integration_cb)
		self.ui.xmin.valueChanged.connect(self.update_range_cb)
		self.ui.xmax.valueChanged.connect(self.update_range_cb)
		self.ui.autoY.clicked.connect(self.autoY)
		self.ui.autoXY.clicked.connect(self.autoXY)

		self.reset_avg()

		self.timer = pg.QtCore.QTimer()
		self.timer.timeout.connect(self.acquire)
		self.timer.start(5)

		self.app.exec_()

	def reset_avg(self):
		self.n = 0
		self.spectra_avg = np.zeros_like(self.lmbd)

	def autoXY(self):
		self.ui.xmin.setValue(self.lmbd.min())
		self.ui.xmax.setValue(self.lmbd.max())
		self.update_range_cb()
		self.autoY()

	def autoY(self, pad=0.05):
		ydata = self.plot_live.getData()[1]
		ymin, ymax = ydata.min(), ydata.max()
		diff = ymax - ymin
		self.ui.plot_full.setYRange(ymin-diff*pad, ymax+diff*pad)

	def acquire(self):
		self.spectra_avg += self.spec.intensities()
		self.n += 1
		if self.n == self.ui.n_average.value():
			self.update_plot()
		elif self.n > self.ui.n_average.value():
			self.reset_avg()

	def update_range_cb(self):
		self.ui.plot_full.setXRange(self.ui.xmin.value(), self.ui.xmax.value())

	def save_spectrum(self, all=False):
		name = self.ui.savepath.text()
		if name == '':
			name = 'spectrum'
		if all:
			name = paths.return_folder(paths.oceanoptics() + name) + "/" + name
		else:
			name = paths.oceanoptics() + name
			self.ui.saveone_button.setChecked(False)
		np.save(name + "_" + datetime.today().strftime("%H%M%S_%f"), self.spectra_avg)

	def update_plot(self):
		self.spectra_avg /= self.ui.n_average.value()

		if self.ui.saveBG.isChecked():
			self.bg = self.spectra_avg.copy()
			self.ui.saveBG.setChecked(False)
		elif self.ui.saveall_button.isChecked():
			self.save_spectrum(all=True)
		elif self.ui.saveone_button.isChecked():
			self.save_spectrum(all=False)
			self.ui.saveone_button.setChecked(False)

		if self.ui.subBG.isChecked():
			self.spectra_avg -= self.bg

		if self.ui.calibrate.isChecked():
			self.spectra_avg *= self.calibration

		self.plot_live.setData(x=self.lmbd, y=self.spectra_avg, pen=self.pen)
		self.reset_avg()

	def set_integration_cb(self):
		self.spec.integration_time_micros(int(self.ui.integration.value() * 1000))
		self.reset_avg()

if __name__ == "__main__":
    sviewer = SpectraViewer()