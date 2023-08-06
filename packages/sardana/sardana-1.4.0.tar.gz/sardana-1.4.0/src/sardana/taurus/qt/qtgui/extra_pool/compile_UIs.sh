#!/bin/bash

##############################################################################
##
## This file is part of Sardana
##
## http://www.tango-controls.org/static/sardana/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

taurusuic4 -x ui/TaurusMotorH.ui -o ui_taurusmotorh.py
taurusuic4 -x ui/TaurusMotorH2.ui -o ui_taurusmotorh2.py
taurusuic4 -x ui/TaurusMotorV.ui -o ui_taurusmotorv.py
taurusuic4 -x ui/TaurusMotorV2.ui -o ui_taurusmotorv2.py

taurusuic4 -x ui/PoolMotorSlim.ui -o ui_poolmotorslim.py
pyuic4 -x ui/poolioregisterbuttons.ui -o ui_poolioregisterbuttons.py
