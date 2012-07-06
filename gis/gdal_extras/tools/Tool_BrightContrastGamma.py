###############################################################################
# $Id: Tool_BrightnessContrastGamma.py,v 1.1 2008/02/08 15:17:13 sujoy_chaudhuri Exp $
#
# Project:  OpenEV Python tools
# Purpose:  Tool to change brightness, contrast and gamma 
# Author:   Sujoy Chaudhuri, ecollage@gmail.com
#
###############################################################################
# Copyright (c) 2006, Sujoy Chaudhuri <ecollage@gmail.com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
###################################################################
#
#  $Log: Tool_BrightnessContrastGamma.py,v $
#  Revision 1.1  unchecked sujoy_chaudhuri
#  New.
#
#

from gtk import *
import gtk
import GtkExtra
from gdalconst import *
import gview
import gviewapp
import gdalnumeric
import gvutils
import gdal
import pgufilesel
import gvhtml
import math
import Numeric
import gettext

spc=5

def layer_is_raster():
    layer = gview.app.sel_manager.get_active_layer()
    if (layer is None) or (gvutils.is_of_class( layer.__class__, 'GvRasterLayer' ) == 0):
        gvutils.warning('Please select a raster layer using the layer dialog.\n')
        return
    BCG_Dialog()

def clip_result(numtype, array):
	if numtype is Numeric.UnsignedInt8:
	    return Numeric.clip(array, 0.0, 255.0)
	elif numtype is Numeric.Int16:
	    return Numeric.clip(array, -32768.0, 32767.0)
	elif numtype is Numeric.Int32:
	    return Numeric.clip(array, -2147483648.0, 2147483647.0)
	else:
	    return array

class BCG_Tool(gviewapp.Tool_GViewApp):
    
    def __init__(self,app=None):
        gettext.install('openev')
        
        gviewapp.Tool_GViewApp.__init__(self,app)
        self.init_menu()
        #self.init_icon()

    def launch_dialog(self,*args):
        self.win = layer_is_raster()
        #self.win.show_all()

    def init_menu(self):
        self.menu_entries.set_entry("Image/BCG Tool",2,self.launch_dialog)

    def init_icon(self):
        self.icon_entries.set_entry("bcg_tool.xpm",_("Adjust Brightness,Contrast,Gamma"),9,self.launch_dialog)


class BCG_Dialog(gtk.GtkWindow):
    def __init__(self,app=None):
        tooltips = gtk.GtkTooltips()
        
        gtk.GtkWindow.__init__(self)
        self.set_title(_('Adjust Brightness,Contrast,Gamma'))
        self.set_policy(gtk.FALSE, gtk.TRUE, gtk.TRUE)
        self.set_border_width(10)

        self.pan_value = []
        
        self.vpanel = gtk.GtkVBox(spacing=spc)
        self.hpanel = gtk.GtkHBox(spacing=spc)
        self.add(self.vpanel)
        self.tips=gtk.GtkTooltips()

        #gvhtml.set_help_topic( self, "profileplot.html" )

        butbox = gtk.GtkVBox()
        tooltips = gtk.GtkTooltips()
        opts = (('zoomin.xpm', _('Zoom in. You can also press CTRL+left mouse button to zoom in.'), self.zoomin),
                ('zoomout.xpm', _('Zoom out x 2. You can also press CTRL+right mouse button to zoom out.'), self.zoomout))
        for opt in opts:
            but = gtk.GtkButton()
            pixmap = gtk.GtkPixmap(self,os.path.join(gview.home_dir,'pics',opt[0]))
            but.add(pixmap)
            tooltips.set_tip(but, opt[1])
            but.connect('clicked', opt[2])
            but.set_usize(26,26)
            butbox.pack_start(but, expand=FALSE)

        # pan toggle
        panView  = (('hand.xpm', _('Pan View')))
        pantoggle = gtk.GtkToggleButton()
        pantoggle.set_name('pan')
        pantoggle.add(gtk.GtkPixmap(self,os.path.join(gview.home_dir,'pics',panView[0])))
        tooltips.set_tip(pantoggle, panView[1])
        #pantoggle.connect('clicked', self.pan, 'pan')
        butbox.pack_start(pantoggle, expand=FALSE)
        tooltips.set_tip(pantoggle,'Click and drag in the BEFORE window to pan the image')
        self.pantoggle = pantoggle

        self.hpanel.pack_start(butbox)            

        lab_box = gtk.GtkHBox()
        lab = gtk.GtkLabel('Before')
        lab_box.pack_start(lab)
        lab = gtk.GtkLabel('After')
        lab_box.pack_start(lab)
        self.vpanel.pack_start(lab_box)

        self.vpanel.pack_start(self.hpanel)

        self.viewarea1 = gview.GvViewArea()
        self.viewarea1.set_usize(250,250)
        self.viewarea1.connect('view-state-changed',self.view_linker)
        # Set up viewarea for panning
        self.viewarea1.connect('button-press-event',self.motion_cb)
        self.viewarea1.connect('button-release-event',self.dragend_cb)
        self.viewarea1.connect('motion-notify-event',self.drag_cb)
        self.hpanel.pack_start(self.viewarea1)

        self.viewarea2 = gview.GvViewArea()
        self.viewarea2.set_usize(250,250)
        #self.viewarea2.connect('view-state-changed',self.view_linker)
        self.hpanel.pack_start(self.viewarea2)

        #brightness
        box = gtk.GtkHBox()
        lab = gtk.GtkLabel('Brightness')
        lab.set_usize(75,20)
        lab.set_justify(0)
        self.bright_adjustment = GtkAdjustment(0,
                                -100, 101, 1, 1, 1)
        self.bright_adjustment.connect('value-changed',self.image_adjust)
        self.bright_slider = GtkHScale(self.bright_adjustment)
        self.bright_slider.set_digits(0)
        self.bright_entry = GtkEntry(maxlen=3)
        self.bright_entry.set_usize(60,25)
        self.bright_entry.set_text('0')
        self.bright_entry.connect('activate',self.entry_cb)
        self.bright_entry.connect('leave-notify-event',self.entry_cb)
        box.pack_end(self.bright_entry,expand=FALSE)
        box.pack_start(lab, expand=FALSE, padding=3)
        box.pack_start(self.bright_slider)
        self.vpanel.pack_start(box)

        #contrast
        box = gtk.GtkHBox()
        lab = gtk.GtkLabel('Contrast')
        lab.set_usize(75,20)
        lab.set_justify(0)
        self.contrast_adjustment = GtkAdjustment(0,
                                -100, 101, 1, 1, 1)
        self.contrast_adjustment.connect('value-changed',self.image_adjust)
        self.contrast_slider = GtkHScale(self.contrast_adjustment)
        self.contrast_slider.set_digits(0)
        self.contrast_entry = GtkEntry(maxlen=3)
        self.contrast_entry.set_usize(60,25)
        self.contrast_entry.set_text('0')
        self.contrast_entry.connect('activate',self.entry_cb)
        self.contrast_entry.connect('leave-notify-event',self.entry_cb)
        box.pack_end(self.contrast_entry,expand=FALSE)
        box.pack_start(lab, expand=FALSE, padding=3)
        box.pack_start(self.contrast_slider)
        
        self.vpanel.pack_start(box)
        
        #gamma
        box = gtk.GtkHBox()
        lab = gtk.GtkLabel('Gamma')
        lab.set_usize(75,20)
        lab.set_justify(0)
        self.gamma_adjustment = GtkAdjustment(1,
                                0.2, 5, 0.2, 1, 1)
        self.gamma_adjustment.connect('value-changed',self.image_adjust)
        self.gamma_slider = GtkHScale(self.gamma_adjustment)
        self.gamma_slider.set_digits(2)
        self.gamma_entry = GtkEntry(maxlen=3)
        self.gamma_entry.set_usize(60,25)
        self.gamma_entry.set_text('1.0')
        self.gamma_entry.connect('activate',self.entry_cb)
        self.gamma_entry.connect('leave-notify-event',self.entry_cb)
        box.pack_end(self.gamma_entry,expand=FALSE)
        box.pack_start(lab, expand=FALSE, padding=3)
        box.pack_start(self.gamma_slider)
        self.vpanel.pack_start(box)

        sep = gtk.GtkHSeparator()
        self.vpanel.pack_start(sep)

        box = gtk.GtkHBox()

        but = gtk.GtkRadioButton(None, 'Overwrite', None)
#        box.pack_start(but)
        but.set_active(1)
        self.owrite_but = but

        but = gtk.GtkRadioButton(but, 'Create Copy', None)
#        box.pack_start(but)
        self.copy_but = but
                
        but = gtk.GtkButton(' Reload Original ')
        but.connect('clicked',self.reset)
        tooltips.set_tip(but,'Remove All B-C-G Enhancements')
        box.pack_start(but)

        but = gtk.GtkButton('  Preview  ')
        but.connect('clicked',self.apply)
        tooltips.set_tip(but,'Preview your changes in the main view')
        box.pack_start(but)

        but = gtk.GtkButton('  Save  ')
        but.connect('clicked',self.save_cb)
        tooltips.set_tip(but,'Save your changes to the original file. Note: This is irreversible.')
        box.pack_start(but)
        
        but = gtk.GtkButton(' Close ')
        but.connect('clicked',self.cancel_cb)
        tooltips.set_tip(but,'Close this Dialog')
        box.pack_start(but)
        self.vpanel.pack_start(box)

        self.show_all()
        self.load_active()

    def entry_cb(self,*args):
        bright = self.bright_entry.get_text()
        cont = self.contrast_entry.get_text()
        gamma = self.gamma_entry.get_text()

        self.bright_adjustment.set_value(float(bright))
        self.contrast_adjustment.set_value(float(cont))
        self.gamma_adjustment.set_value(float(gamma))

    def reset(self, *args):
        self.bright_adjustment.set_value(0)
        self.contrast_adjustment.set_value(0)
        self.gamma_adjustment.set_value(1.0)

        self.load_active()
        self.reset_image()

    def cancel_cb(self,*args):
        self.reset_image()
        self.destroy()

    def reset_image(self,*args):
        lay = gview.app.sel_manager.get_active_layer()
        lay_name = lay.get_name()
        if (lay is None) or (gvutils.is_of_class( lay.__class__, 'GvRasterLayer' ) == 0):
            gvutils.warning('Please select a raster layer using the layer dialog.\n')
            return
        layfname = lay.get_parent().get_name()[:-2]

        view = gview.app.sel_manager.get_active_view()
        viewwin = gview.app.sel_manager.get_active_view_window()

        row = gview.app.layerdlg.list_layers().index(view.active_layer())      

        view.remove_layer(lay)
        viewwin.file_open_by_name(layfname)
        lay = gview.app.sel_manager.get_active_layer()
        lay.set_name(lay_name)

        if row != 0:
            gview.app.layerdlg.layerlist.swap_rows(0,row)
            view.swap_layers(0,row)

        if viewwin.laytoggle.active:
            viewwin.updateLayers()


    def image_adjust(self, adjustment, *args):
        self.bright_entry.set_text(str(self.bright_adjustment.value) + '%')
        self.contrast_entry.set_text(str(self.contrast_adjustment.value) + '%')
        self.gamma_entry.set_text(str(self.gamma_adjustment.value))
        
        layer = self.viewarea2.active_layer()
        contrast_val = (100.0+self.contrast_adjustment.value)/100.0
        gamma_val = self.gamma_adjustment.value

        lut = ''
        for i in range(256):
            value = i + math.floor(self.bright_adjustment.value*255/100)
            if value < 0 :
                value = 0
            elif value >= 255:
                value = 255
            if contrast_val != 1.0:
                value = value * contrast_val
            if value < 0 :
                value = 0
            elif value >= 255:
                value = 255
            if gamma_val != 1:
                value = 255*math.pow(float(abs(value))/255,1.0/gamma_val)
            if value < 0 :
                value = 0
            elif value >= 255:
                value = 255
            value = int(value)
            lut = lut + chr(value)
        #print len(lut)

        try:
            for isrc in range(layer.sources):
                (smin, smax) = layer.autoscale( isource=isrc, viewonly = 1 )

                layer.set_source(isrc, layer.get_data(isrc), smin, smax,
                                layer.get_const_value(isrc), lut,
                                layer.nodata_get(isrc)) 

        except:
            pass

        return lut

    def apply(self, *args):
        layer = gview.app.sel_manager.get_active_layer()
        if (layer is None) or (gvutils.is_of_class( layer.__class__, 'GvRasterLayer' ) == 0):
            gvutils.warning('Please select a raster layer using the layer dialog.\n')
            return

        lut = self.image_adjust(self.bright_adjustment)

        for isrc in range(layer.sources):
            (smin, smax) = layer.autoscale( isource=isrc, viewonly = 1 )

            layer.set_source(isrc, layer.get_data(isrc), smin, smax,
                            layer.get_const_value(isrc), lut,
                            layer.nodata_get(isrc)) 

        #self.destroy()

    def save_cb(self, *args):
        if self.copy_but.active:
            outfile=GtkExtra.file_sel_box(title=_("Output File"))
            if outfile is None:
                return

        ds = self.viewarea1.active_layer().get_parent().get_dataset()
        bright_val = math.floor(self.bright_adjustment.value*255/100)
        contrast_val = (100+self.contrast_adjustment.value)/100
        gamma_val = self.gamma_adjustment.value

        outarray = Numeric.zeros((ds.RasterCount,ds.RasterYSize,ds.RasterXSize),typecode=Numeric.UnsignedInt8)

        try:
            size = ds.RasterYSize
            import EasyDialogs
            progress = EasyDialogs.ProgressBar(title='Working...',maxval=size)
        except:
            pass

        lut = []
        for i in range(256):
            value = i + math.floor(bright_val)
            if value < 0 :
                value = 0
            elif value >= 255:
                value = 255
            if contrast_val != 1.0:
                value = value * contrast_val
            if value < 0 :
                value = 0
            elif value >= 255:
                value = 255
            if gamma_val != 1:
                value = 255*math.pow(float(abs(value))/255,1.0/gamma_val)
            if value < 0 :
                value = 0
            elif value >= 255:
                value = 255
            value = int(value)
            lut.append(value)

        lutarray = Numeric.array((lut),typecode=Numeric.UnsignedInt8)

        for m in range(ds.RasterCount):
            inband = ds.GetRasterBand(m+1)
            for i in range(ds.RasterYSize):
                #inarray = inband.ReadAsArray()
                inarray = inband.ReadAsArray(0, i, inband.XSize, 1, inband.XSize, 1)[0].astype(Numeric.UnsignedInt8)
                #outarray = Numeric.zeros(inarray.shape)

                try:
                    progress.label('Processing Band: ' + str(m+1) + ', Line: '+str(i))
                    progress.set(i)
                except:
                    pass

                outarray[m][i].flat[:] = Numeric.take(lutarray,inarray.flat)

        res_ds = gdalnumeric.OpenArray(outarray,ds)
        res_ds = gview.manager.add_dataset(res_ds)

        view = gview.app.sel_manager.get_active_view_window()
        if self.copy_but.active:
            driver = ds.GetDriver()
            driver.CreateCopy(outfile,res_ds)
            view.file_open_by_name(outfile)
            self.destroy()
        elif self.owrite_but.active:
            for layer in gview.app.sel_manager.get_active_view().list_layers():
                if gvutils.is_of_class( layer.__class__, 'GvRasterLayer' ) == 1:
                    if layer.get_parent().get_dataset().GetDescription() == ds.GetDescription():
                        gview.app.sel_manager.get_active_view().remove_layer(layer)

            fname = ds.GetDescription()
            driver = ds.GetDriver()
            driver.CreateCopy(fname,res_ds)
            view.file_open_by_name(fname)
            view.refresh_cb()
            self.destroy()
                
        del ds
        del res_ds
        del outarray

    def load_active(self,*args):
        layer = gview.app.sel_manager.get_active_layer()
        if (layer is None) or (gvutils.is_of_class( layer.__class__, 'GvRasterLayer' ) == 0):
            gvutils.warning('Please select a raster layer using the layer dialog.\n')
            return
        layer_ds = layer.get_parent().get_name()[:-2]

        ds = gdal.OpenShared(layer_ds)
        gview.manager.add_dataset(ds)

        if ds.RasterCount == 3:
            rlayer1 = gview.manager.get_dataset_raster(ds,1)
            rlayer2 = gview.manager.get_dataset_raster(ds,2)
            rlayer3 = gview.manager.get_dataset_raster(ds,3)
            raster = gview.GvRasterLayer(rlayer1)
            ras_copy = gview.GvRasterLayer(rlayer1)
            raster.set_source(1,rlayer2)
            raster.set_source(2,rlayer3)
            ras_copy.set_source(1,rlayer2)
            ras_copy.set_source(2,rlayer3)
        else:
            rlayer = gview.manager.get_dataset_raster(ds,1)
            raster = gview.GvRasterLayer(rlayer)
            ras_copy = gview.GvRasterLayer(rlayer)

        raster.set_name('RASTER')
        ras_copy.set_name('RASTER')

        oldras1 = self.viewarea1.get_named_layer('RASTER')
        oldras2 = self.viewarea2.get_named_layer('RASTER')

        if oldras1 is not None:
            self.viewarea1.remove_layer(oldras1)
            self.viewarea2.remove_layer(oldras2)
            
        #check for lut:
        lut_name = os.path.splitext(layer_ds)[0] + '.lut'
        if os.path.isfile(lut_name):
            lut_file = open(lut_name,'rb')
            lut = ''
            lut = lut_file.read()
            #print 'loading:', len(lut)

            if lut:
                for isrc in range(raster.sources):
                    #(smin, smax) = raster_layer.autoscale( isource=isrc, viewonly = 1 )
                    #print (smin,smax)

                    raster.set_source(isrc, raster.get_data(isrc), 0, 255,
                                    raster.get_const_value(isrc), lut,
                                    raster.nodata_get(isrc)) 

                    ras_copy.set_source(isrc, ras_copy.get_data(isrc), 0, 255,
                                    ras_copy.get_const_value(isrc), lut,
                                    ras_copy.nodata_get(isrc)) 

            lut_file.close()

        #check for bcg:
        bcg_name = os.path.splitext(layer_ds)[0] + '.bcg'
        if os.path.isfile(bcg_name):
            bcg_file = open(bcg_name,'r')
            bcg = ''
            bcg = bcg_file.readline()
            bcg = bcg.replace('\n','')
            bcg_file.close()

            values = bcg.split(',')

            self.bright_adjustment.set_value(float(values[0]))
            self.contrast_adjustment.set_value(float(values[1]))
            self.gamma_adjustment.set_value(float(values[2]))

        self.viewarea1.add_layer(raster)
        self.viewarea1.set_active_layer(raster)

        self.viewarea2.add_layer(ras_copy)
        self.viewarea2.set_active_layer(ras_copy)

    def view_linker(self, *args):
        bounds = self.viewarea1.get_extents()
        self.viewarea2.fit_extents(bounds[0],bounds[1],bounds[2]-bounds[0],bounds[3]-bounds[1])

    def zoomin(self, *args):
        self.viewarea1.zoom(1)

    def zoomout(self, *args):
        self.viewarea1.zoom(-1)

    def motion_cb(self,*args):
        if self.pantoggle.active:
            x,y = self.viewarea1.get_pointer()
            self.pan_value.append([x,y])
        
    def drag_cb(self,wid,context):
        if self.pantoggle.active:
            x,y = self.viewarea1.get_pointer()
            self.set_panwin(x,y)
            #self.pan_value = []

    def dragend_cb(self,wid,context):
        if self.pantoggle.active:
            x,y = self.viewarea1.get_pointer()
            self.set_panwin(x,y)
            self.pan_value = []

    def set_panwin(self, x=None, y=None, *args):
        try:
            xmin,ymin,xmax,ymax = self.viewarea1.get_extents()
            width = xmax-xmin
            height = ymax-ymin
            if x is None or y is None:
                x,y = self.viewarea.get_pointer()
            if x < self.pan_value[-1][0]:
                xmin = xmin + (self.pan_value[-1][0]-x)
            if y < self.pan_value[-1][1]:
                ymin = ymin + (self.pan_value[-1][1]-y)
            if x > self.pan_value[-1][0]:
                xmin = xmin - (x - self.pan_value[-1][0])
            if y > self.pan_value[-1][1]:
                ymin = ymin - (y - self.pan_value[-1][1])

            self.viewarea1.fit_extents(xmin,ymin,width,height)
        except:
            pass
        
        
TOOL_LIST = ['BCG_Tool']