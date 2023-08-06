#!/usr/bin/env python
# coding=utf-8
# Copyright (C) 2013 Nathan Charles
#
# This program is free software. See terms in LICENSE file.

"""Calculate expedited permit process info"""
import logging
logger = logging.getLogger(__name__)

import epw
import geo
import pv
import ee
import vd
import modules
from math import degrees
import sys
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

try:
    import geomag
except:
    logger.warning("geomag not loaded.  Magnetic declination unavailible")

def string_notes(system, run=0.0, station_class = 3):
    """page 5"""

    name, usaf = geo.closest_usaf( geo.zip_coordinates(system.zipcode), station_class)
    mintemp = epw.minimum(usaf)
    twopercentTemp = epw.twopercent(usaf)
    ac_kva_rated = 0.0
    dc_rated = 0.0
    ac_kw = 0.0
    for i in system.shape:
        dc_rated += i.array.p_max
        try:
            if i.phase == 1:
                ac_kva_rated += i.current * i.ac_voltage
            else:
                ac_kva_rated += i.phase * i.current * i.ac_voltage/ 3**.5
        except:
            ac_kva_rated += i.p_aco
            pass
        ac_kw += i.p_aco
    notes = []
    notes.append("%s KVA AC RATED" % round(ac_kva_rated/1000.0,2))
    notes.append("%s KW AC RATED" % round(ac_kw/1000.0,2))
    notes.append("%s KW DC RATED" % round(dc_rated/1000.0,2))
    #BUG: This doesn't work for unbalanced 3 phase
    if system.phase == 1:
        Aac = round(ac_kva_rated/i.ac_voltage,1)
    else:
        Aac = round(ac_kva_rated/i.ac_voltage/3**.5,1)
    notes.append( "System AC Output Current: %s A" % Aac)

    notes.append("Nominal AC Voltage: %s V" % i.ac_voltage)
    notes.append("")
    notes.append("Minimum Temperature: %s C" % mintemp)
    notes.append("2 Percent Max Temperature: %s C" % twopercentTemp)
    notes.append("Weather Source: %s %s" % (name, usaf))
    notes.append("")
    di, dp = system.describe()
    aMax = 0
    for i in system.shape:
        moduleN = i.array.dump()['panel']
        if dp.has_key(moduleN):
            m = modules.Module(moduleN) 
            notes.append( "PV Module Ratings @ STC")
            notes.append("Module Make: %s" % m.make)
            notes.append("Module Model: %s" % m.model)
            notes.append("Quantity: %s" % dp[moduleN])
            notes.append("Max Power-Point Current (Imp): %s A" % m.i_mpp)
            notes.append("Max Power-Point Voltage (Vmp): %s V" % m.v_mpp)
            notes.append("Open-Circuit Voltage (Voc): %s V" % m.v_oc)
            notes.append("Short-Circuit Current (Isc): %s A" % m.i_sc)
            notes.append("Maximum Power (Pmax): %s W" % round(m.p_max,1))
            #notes.append("Module Rated Max Voltage: %s V" % i.array.panel.Vrated)

            notes.append("")
            dp.pop(moduleN)
        if di.has_key(i.model):
            notes.append("Inverter Make: %s" % i.make)
            notes.append("Inverter Model: %s" % i.model)
            notes.append("Quantity: %s" % di[i.model])
            notes.append("Max Power: %s KW" % round(i.p_aco/1000.0,1))
            #this is hack... This should be calculated based upon power cores
            if hasattr(i,'current'):
                notes.append("Max AC Current: %s A" % round(i.current,1))
            elif i.ac_voltage == 480:
                notes.append("Max AC Current: %s A" % round(i.p_aco*1.0/i.ac_voltage/3**.5,1))
            else:
                notes.append("Max AC Current: %s A" % round(i.p_aco*1.0/i.ac_voltage,1))
            #greater than 1 in parallel
            if i.array.mcount() > 1:
                pass
                notes.append("DC Operating Current: %s A" % \
                        round(i.array.i_mpp(),1))
                notes.append("DC Short Circuit Current: %s A" % \
                        round(i.array.i_sc(),1))
            #greater than 1 in series
            if i.array.mcount() > 1:
                notes.append("DC Operating Voltage: %s V" % round(i.array.v_dc(),1))
                notes.append("System Max DC Voltage: %s V" % round(i.array.v_max(mintemp),1))
                if i.array.v_max(mintemp) > 600:
                    logger.warning("WARNING: Array exceeds 600V DC")
                notes.append("Pnom Ratio: %s" % round((i.array.p_max/i.p_aco),2))
                if (i.array.v_dc(twopercentTemp) *.9) < i.mppt_low:
                    logger.warning("WARNING: Array IV Knee drops out of Inverter range")
                if (i.array.p_max/i.p_aco) < 1.1:
                    logger.warning("WARNING: Array potentially undersized")
            notes.append("")
            di.pop(i.model)
        if i.array.v_max(mintemp) > aMax:
            aMax = i.array.v_max(mintemp)

    notes.append("Array Azimuth: %s Degrees" % system.azimuth)
    notes.append("Array Tilt: %s Degrees" % system.tilt)
    s9 = system.solstice(9)
    s15 = system.solstice(15)
    notes.append("December 21 9:00 AM Sun Azimuth: %s Degrees" % \
            (round(degrees(s9[1]),1)))
    notes.append("December 21 9:00 AM Sun Altitude: %s Degrees" % \
            (round(degrees(s9[0]),1)))
    notes.append("December 21 3:00 PM Sun Azimuth: %s Degrees" % \
            (round(degrees(s15[1]),1)))
    notes.append("December 21 3:00 PM Sun Altitude: %s Degrees" % \
            (round(degrees(s9[0]),1)))
    if 'geomag' in sys.modules:
        notes.append("Magnetic declination: %s Degrees" % \
                round(geomag.declination(dlat=system.place[0],dlon=system.place[1])))
    notes.append("Minimum Row space ratio: %s" % \
            round(system.min_row_space(1.0),2))
    if __name__ == '__main__':
        print "\n".join(notes)
    else:
        logger.info("Plant Details:\n" + "\n".join(notes))

    print ""
    print "Minimum Bundle"
    minC = vd.vd(Aac,5,verbose=False)
    try:
        ee.assemble(minC,Aac,conduit='STEEL')
        if run > 0:
            print "Long Run"
            minC = vd.vd(Aac,run,v=i.ac_voltage,tAmb=15,pf=.95,material='AL',verbose=False)
            ee.assemble(minC,Aac,conduit='PVC')
    except:
        print "Warning: Multiple sets of conductors"
    return notes

def micro_calcs(system,d,Vnominal=240):
    """page 4"""
    print ""
    print vd.vd(sum([i.p_aco for i in system.shape])/Vnominal,d)
    pass

def write_notes(system, filename='output', Vnominal=240.0):
    station_class = 1
    name, usaf = geo.closest_usaf( geo.zip_coordinates(system.zipcode), station_class)
    mintemp = epw.minimum(usaf)
    twopercentTemp = epw.twopercent(usaf)
    fields = []
    for i in set(system.shape):
        moduleN = i.array.dump()['panel']
        m = modules.Module(moduleN) 
        print "PV Module Ratings @ STC"
        print "Module Make:", m.make
        fields.append(('Text1ModuleMake',m.make))
        print "Module Model:", m.model
        fields.append(('Text1ModuleModel',m.model))
        print "Max Power-Point Current (Imp):",m.i_mpp
        fields.append(('MAX POWERPOINT CURRENT IMP',m.i_mpp))
        print "Max Power-Point Voltage (Vmp):",m.v_mpp
        fields.append(('MAX POWERPOINT VOLTAGE VMP',m.v_mpp))
        print "Open-Circuit Voltage (v_oc):",m.v_oc
        fields.append(('OPENCIRCUIT VOLTAGE VOC',m.v_oc))
        print "Short-Circuit Current (i_sc):",m.i_sc
        fields.append(('SHORTCIRCUIT CURRENT ISC',m.i_sc))
        fields.append(('MAX SERIES FUSE OCPD','15'))
        print "Maximum Power (p_max):",m.p_max
        fields.append(('MAXIMUM POWER PMAX',m.p_max))
        print "Module Rated Max Voltage:",m.Vrated
        fields.append(('MAX VOLTAGE TYP 600VDC',m.Vrated))
        fields.append(('VOC TEMP COEFF mVoC or oC',round(m.tk_v_oc,2)))
        fields.append(('VOC TEMP COEFF mVoC','On'))
        print "Inverter Make:",i.make
        fields.append(('INVERTER MAKE',i.make))
        print "Inverter Model:",i.model
        fields.append(('INVERTER MODEL',i.model))
        print "Max Power", i.p_aco
        fields.append(('MAX POWER  40oC',i.p_aco))
        fields.append(('NOMINAL AC VOLTAGE',240))
        print "Max AC Current: %s" % round(i.p_aco/Vnominal,2)
        fields.append(('MAX AC CURRENT', round(i.p_aco/Vnominal,2)))
        fields.append(('MAX DC VOLT RATING',i.mppt_hi))
        print "Max AC OCPD Rating: %s" % ee.ocp_size(i.p_aco/Vnominal*1.25)
        print "Max System Voltage:",round(m.v_max(mintemp),1)
    print "AC Output Current: %s" % \
            round(sum([i.p_aco for i in system.shape])/Vnominal,2)
    fields.append(('AC OUTPUT CURRENT', \
            round(sum([i.p_aco for i in system.shape])/Vnominal,2)))
    print "Nominal AC Voltage: %s" % Vnominal
    fields.append(('NOMINAL AC VOLTAGE_2',i.ac_voltage))

    print "Minimum Temperature: %s C" % mintemp
    print "2 Percent Max: %s C" % twopercentTemp
    from fdfgen import forge_fdf
    fdf = forge_fdf("",fields,[],[],[])
    fdf_file = open("data.fdf","w")
    fdf_file.write(fdf)
    fdf_file.close()
    import shlex
    from subprocess import call
    cmd = shlex.split("pdftk Example2-Micro-Inverter.pdf fill_form data.fdf %s output.pdf flatten" % filename)
    rc = call(cmd)

if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description='Model a PV system. Currently displays annual output and graph')
    parser.add_argument('-f', '--file')
    args = vars(parser.parse_args())
    try:
        #start program
        jsonP = json.loads(open(args['file']).read())
        if 'address' in jsonP:
            print '%s - %s %s' % \
                (jsonP['system_name'].upper(),jsonP['address'],jsonP['zipcode'])
        plant = pv.json_system(jsonP)
        if "run" in jsonP:
            string_notes(plant,jsonP["run"])
            pass
        else:

            string_notes(plant)
        #graph = plant.model()
        #graph.savefig('pv_output_%s.png' % plant.zipcode)

    except (KeyboardInterrupt, SystemExit):
        sys.exit(1)
    except:
        raise
