#from numpy import ones, empty
import numpy as np
from flopy.mbase import Package
from flopy.utils import util_2d

class ModflowEvt(Package):
    'Evapotranspiration class'
    def __init__(self, model, nevtop=3, ievtcb=0, surf=0., evtr=1e-3, exdp=1., ievt=1, extension ='evt', unitnumber=22,external=True):
        '''
        external flag is used to control writing external arrays of constant value
        since this package has the potential to create a lot of external arrays
        '''
        Package.__init__(self, model, extension, 'EVT', unitnumber) # Call ancestor's init to set self.parent, extension, name and unit number
        nrow, ncol, nlay, nper = self.parent.nrow_ncol_nlay_nper
        self.heading = '# EVT for MODFLOW, generated by Flopy.'
        self.url = 'evt.htm'
        self.nevtop = nevtop
        self.ievtcb = ievtcb
        self.surf = []
        self.evtr = []
        self.exdp = []
        self.ievt = []        
        self.external = external
        if self.external is False:
            load = True
        else:
            load = model.load            
        if (not isinstance(surf, list)):
            surf = [surf]
        for i,a in enumerate(surf):
            s = util_2d(model,(nrow,ncol),np.float32,a,name='surf_'+str(i+1))
            self.surf = self.surf + [s]
        if (not isinstance(evtr, list)):
            evtr = [evtr]
        for i,a in enumerate(evtr):
            e = util_2d(model,(nrow,ncol),np.float32,a,name='etvr_'+str(i+1))
            self.evtr = self.evtr + [e]
        if (not isinstance(exdp, list)):
            exdp = [exdp]
        for i,a in enumerate(exdp):
            e = util_2d(model,(nrow,ncol),np.float32,a,name='exdp_'+str(i+1))
            self.exdp = self.exdp + [e]
        if (not isinstance(ievt, list)):
            ievt = [ievt]
        for i,a in enumerate(ievt):
            iv = util_2d(model,(nrow,ncol),np.int,a,name='ievt_'+str(i+1))
            self.ievt = self.ievt + [iv]
        self.np = 0
        self.parent.add_package(self)
    def __repr__( self ):
        return 'Evapotranspiration class'
    def ncells( self):
        # Returns the  maximum number of cells that have 
        # evapotranspiration (developped for MT3DMS SSM package)
        nrow, ncol, nlay, nper = self.parent.nrow_ncol_nlay_nper
        return (nrow * ncol)
    def write_file(self):
        nrow, ncol, nlay, nper = self.parent.nrow_ncol_nlay_nper
        f_evt = open(self.fn_path, 'w')        
        f_evt.write('{0:s}\n'.format(self.heading))        
        f_evt.write('{0:10d}{1:10d}\n'.format(self.nevtop,self.ievtcb))
        for n in range(nper):
            #comment = 'Evapotranspiration array for stress period ' + str(n + 1)
            if (n < len(self.surf)):
                insurf = 1
            else:
                insurf = -1
            if (n < len(self.evtr)):
                inevtr = 1
            else:
                inevtr = -1
            if (n < len(self.exdp)):
                inexdp = 1
            else:
                inexdp = -1
            if (n < len(self.ievt)):
                inievt = 1
            else:
                inievt = -1
            comment = 'Evapotranspiration surface array for stress period ' + str(n + 1)
            f_evt.write('{0:10d}{1:10d}{2:10d}{3:10d} # {4:s}\n'\
                .format(insurf,inevtr,inexdp,inievt,comment))
            
            if (n < len(self.surf)):
                f_evt.write(self.surf[n].get_file_entry())
            comment = 'Evapotranspiration rate array for stress period ' + str(n + 1)
            if (n < len(self.evtr)):
                f_evt.write(self.evtr[n].get_file_entry())
            comment = 'Evapotranspiration extinction depth array for stress period ' + str(n + 1)
            if (n < len(self.exdp)):
                f_evt.write(self.exdp[n].get_file_entry())
            comment = 'Evapotranspiration layers for stress period ' + str(n + 1)
            if ((n < len(self.ievt)) and (self.nevtop == 2)):
                f_evt.write(self.ievt[n].get_file_entry())
        f_evt.close()


