﻿import numpy as np
from flopy.mbase import Package
from flopy.utils import util_2d

class ModflowUzf1(Package):
    'UZF1 class'
    def __init__(self, model, \
    nuztop = 1, iuzfopt = 0, irunflg = 0, ietflg = 0, iuzfcb1 = 57, iuzfcb2 = 0, ntrail2 = 10, nsets = 20, nuzgag = 0, surfdep = 1.0, \
    iuzfbnd = 1, irunbnd = 0, vks = 1.0E-6, eps = 3.5, thts = 0.35, thtr = 0.15, thti = 0.20, row_col_iftunit_iuzopt = [], \
    specifythtr = 0, specifythti = 0, nosurfleak = 0, \
    finf = 1.0E-8, pet = 5.0E-8, extdp = 15.0, extwc = 0.1, \
    uzfbud_ext = [], extension ='uzf', unitnumber = 19):
        Package.__init__(self, model, extension, ['UZF'], unitnumber) # Call ancestor's init to set self.parent, extension, name and unit number
        if self.parent.get_package('RCH') != None or self.parent.get_package('EVT') != None:
            print 'WARNING!\n The RCH and EVT packages should not be active when the UZF1 package is active!'
        if self.parent.version == 'mf2000':
            print 'WARNING!\nThe UZF1 package is only compatible with MODFLOW-2005 and MODFLOW-NWT!'
        nrow, ncol, nlay, nper = self.parent.nrow_ncol_nlay_nper
        self.heading = '# UZF1 for MODFLOW, generated by Flopy.'
        self.url = 'uzf_unsaturated_zone_flow_pack.htm'
        # Data Set 1a
        self.specifythtr = specifythtr
        self.specifythti = specifythti
        self.nosurfleak  = nosurfleak
        # Data Set 1b
        # NUZTOP IUZFOPT IRUNFLG IETFLG IUZFCB1 IUZFCB2 [NTRAIL2 NSETS2] NUZGAG SURFDEP
        self.nuztop = nuztop
        self.iuzfopt = iuzfopt
        self.irunflg = irunflg
        self.ietflg = ietflg
        self.iuzfcb1 = iuzfcb1
        self.iuzfcb2 = iuzfcb2
        class_nam = ['UZF']
        if (not isinstance(unitnumber, list)):
            unitnumber = [unitnumber]
        if (not isinstance(extension, list)):
            extension = [extension]
        if iuzfcb1 > 0 and iuzfcb2 < 1:
            unitnumber.append(iuzfcb1)
            extension.append(extension[0]+'bt1')
            class_nam += ['DATA(BINARY)']
        elif iuzfcb1 < 1 and iuzfcb2 > 0:
            unitnumber.append(iuzfcb2)
            extension.append(extension[0]+'bt2')
            class_nam += ['DATA(BINARY)']
        elif iuzfcb1 > 0 and iuzfcb2 > 0:
            unitnumber.append(iuzfcb1)
            extension.append(extension[0]+'bt1')
            unitnumber.append(iuzfcb2)
            extension.append(extension[0]+'bt2')
            class_nam += ['DATA(BINARY)','DATA(BINARY)']
        if iuzfopt > 0:
            self.ntrail2 = ntrail2
            self.nsets = nsets
        self.nuzgag = nuzgag
        self.surfdep = surfdep
        #Data Set 2
        #IUZFBND (NCOL, NROW) -- U2DINT            
        self.iuzfbnd = util_2d(model,(nrow,ncol),np.int,iuzfbnd,name='iuzfbnd')
        #If IRUNFLG > 0: Read item 3
        #Data Set 3
        #[IRUNBND (NCOL, NROW)] -- U2DINT
        if irunflg > 0:            
            self.irunbnd = util_2d(model,(nrow,ncol),np.int,irunbnd,name='irunbnd')
        #IF the absolute value of IUZFOPT = 1: Read item 4.
        #Data Set 4
        #[VKS (NCOL, NROW)] -- U2DREL
        if abs(iuzfopt) == 1:            
            self.vks = util_2d(model,(nrow,ncol),np.float32,vks,name='vks')
        if iuzfopt > 0:
            #Data Set 5
            #EPS (NCOL, NROW) -- U2DREL            
            self.eps = util_2d(model,(nrow,ncol),np.float32,eps,name='eps')
            #Data Set 6a
            #THTS (NCOL, NROW) -- U2DREL            
            self.thts = util_2d(model,(nrow,ncol),np.float32,thts,name='thts')
            #Data Set 6b
            #THTS (NCOL, NROW) -- U2DREL
            if self.specifythtr > 0:                
                self.thtr = util_2d(model,(nrow,ncol),np.float32,thtr,name='thtr')
            #Data Set 7
            #[THTI (NCOL, NROW)] -- U2DREL            
            self.thti = util_2d(model,(nrow,ncol),np.float32,thti,name='thti')
        #Data Set 8
        #[IUZROW] [IUZCOL] IFTUNIT [IUZOPT]
        if len(row_col_iftunit_iuzopt) != nuzgag:
            print "WARNING!\nItem 8 doesn't correspond with NUZGAG.\nNUZGAG set to 0"
            self.nuzgag = 0
            self.row_col_iftunit_iuzopt = []
        else:
            self.row_col_iftunit_iuzopt = row_col_iftunit_iuzopt
            i = 0
            for l in row_col_iftunit_iuzopt:
                unitnumber.append(abs(l[0][2]))
                if uzfbud_ext ==[]:
                    extension.append(extension[0] + 'b' + str(i))
                else:
                    extension.append(uzfbud_ext[i])
                i += 1
            Package.__init__(self,model,extension,class_nam+nuzgag*['DATA'],unit_number=unitnumber)
        #Dataset 9, 11, 13 and 15 will be written automatically in the write_file function
        #Data Set 10
        #[FINF (NCOL, NROW)] – U2DREL
        self.finf = []
        if (not isinstance(finf, list)):
            finf = [finf]
        for i,a in enumerate(finf):          
            b = util_2d(model,(nrow,ncol),np.float32,a,name='finf_'+str(i+1))
            self.finf = self.finf + [b]
        if ietflg > 0:
            #Data Set 12
            #[PET (NCOL, NROW)] – U2DREL
            self.pet = []
            if (not isinstance(pet, list)):
                pet = [pet]
            for i,a in enumerate(pet):               
                b = util_2d(model,(nrow,ncol),np.float32,a,name='pet_'+str(i+1))
                self.pet = self.pet + [b]
            #Data Set 14
            #[EXTDP (NCOL, NROW)] – U2DREL
            self.extdp = []
            if (not isinstance(extdp, list)):
                extdp = [extdp]
            for i,a in enumerate(extdp):               
                b = util_2d(model,(nrow,ncol),np.float32,a,name='extdp_'+str(i+1))
                self.extdp = self.extdp + [b]
            #Data Set 16
            #[EXTWC (NCOL, NROW)] – U2DREL
            if iuzfopt> 0:
                self.extwc = []
                if (not isinstance(extwc, list)):
                    extwc = [extwc]
                for i,a in enumerate(extwc):                   
                    b = util_2d(model,(nrow,ncol),np.float32,a,name='extwc_'+str(i+1))
                    self.extwc = self.extwc + [b]
        self.parent.add_package(self)
    def __repr__( self ):
        return 'UZF1 class'
    def ncells( self):
        # Returns the  maximum number of cells that have recharge (developped for MT3DMS SSM package)
        nrow, ncol, nlay, nper = self.parent.nrow_ncol_nlay_nper
        return (nrow * ncol)
    def write_file(self):
        nrow, ncol, nlay, nper = self.parent.nrow_ncol_nlay_nper
        # Open file for writing
        f_uzf = open(self.fn_path, 'w')
        f_uzf.write('%s\n' % self.heading)
        # Dataset 1a
        specify_temp = ''
        if self.specifythtr > 0:
            specify_temp += 'SPECIFYTHTR '
        if self.specifythti > 0:
            specify_temp += 'SPECIFYTHTI '
        if self.nosurfleak > 0:
            specify_temp += 'NOSURFLEAK'
        if (self.specifythtr + self.specifythti + self.nosurfleak) > 0:
            f_uzf.write('%s\n' % specify_temp)
        del specify_temp
        # Dataset 1b
        if self.iuzfopt > 0:
            comment = ' NUZTOP IUZFOPT IRUNFLG IETFLG IUZFCB1 IUZFCB2 NTRAIL NSETS NUZGAGES'            
            f_uzf.write('{0:10d}{1:10d}{2:10d}{3:10d}{4:10d}{5:10d}{6:10d}{7:10d}{8:10d}{9:15.6E}{10:100s}\n'.\
                format(self.nuztop, self.iuzfopt, self.irunflg, self.ietflg, self.iuzfcb1, self.iuzfcb2, \
                self.ntrail2, self.nsets, self.nuzgag, self.surfdep, comment))
        else:
            comment = ' NUZTOP IUZFOPT IRUNFLG IETFLG IUZFCB1 IUZFCB2 NUZGAGES'            
            f_uzf.write('{0:10d}{1:10d}{2:10d}{3:10d}{4:10d}{5:10d}{6:10d}{7:15.6E}{8:100s}\n'.\
                format(self.nuztop, self.iuzfopt, self.irunflg, self.ietflg, self.iuzfcb1, self.iuzfcb2, \
                self.nuzgag, self.surfdep, comment))       
        f_uzf.write(self.iuzfbnd.get_file_entry())
        if self.irunflg > 0:           
            f_uzf.write(self.irunbnd.get_file_entry())
        #IF the absolute value of IUZFOPT = 1: Read item 4.
        #Data Set 4
        #[VKS (NCOL, NROW)] -- U2DREL
        if abs(self.iuzfopt) == 1:            
            f_uzf.write(self.vks.get_file_entry())
        if self.iuzfopt > 0:
            #Data Set 5
            #EPS (NCOL, NROW) -- U2DREL           
            f_uzf.write(self.eps.get_file_entry())
            #Data Set 6a
            #THTS (NCOL, NROW) -- U2DREL            
            f_uzf.write(self.thts.get_file_entry())
            #Data Set 6b
            #THTR (NCOL, NROW) -- U2DREL
            if self.specifythtr > 0.0:               
                f_uzf.write(self.thtr.get_file_entry())
            #Data Set 7
            #[THTI (NCOL, NROW)] -- U2DREL
            if not self.parent.get_package('DIS').steady[0] or self.specifythti > 0.0:               
                f_uzf.write(self.thti.get_file_entry())
        #If NUZGAG>0: Item 8 is repeated NUZGAG times
        #Data Set 8
        #[IUZROW] [IUZCOL] IFTUNIT [IUZOPT]
        if self.nuzgag > 0:
            for n in range(self.nuzgag):
                if self.row_col_iftunit_iuzopt[n][0][2] > 0:
                    comment = ' IUZROW IUZCOL IFTUNIT IUZOPT'
                    f_uzf.write('%10i%10i%10i%10i%s\n' % (tuple(self.row_col_iftunit_iuzopt[n][0] + [comment])))
                    #f_uzf.write('{0:10d}{1:10d}{2:10d}{3:10d}{4:50s}\n'.\
                    #    format(tuple(self.row_col_iftunit_iuzopt[n][0] + [comment])))
                else:
                    comment = ' IFTUNIT'
                    f_uzf.write('%10i%s\n' % (tuple([self.row_col_iftunit_iuzopt[n][0][2]] + [comment])))
        for n in range(nper):
            comment = ' NUZF1 for stress period ' + str(n + 1)
            if (n < len(self.finf)):
                nuzf1 = 1
            else:
                nuzf1 = -1
            #f_uzf.write('%10i%s\n' % (nuzf1, comment))
            f_uzf.write('{0:10d}{1:20s}\n'.format(nuzf1,comment))
            comment = 'FINF for stress period ' + str(n + 1)
            if (n < len(self.finf)):               
                f_uzf.write(self.finf[n].get_file_entry())
            comment = ' NUZF2 for stress period ' + str(n + 1)
            if self.ietflg > 0:
                if (n < len(self.pet)):
                    nuzf2 = 1
                else:
                    nuzf2 = -1
                #f_uzf.write('%10i%s\n' % (nuzf2, comment))
                f_uzf.write('{0:10d}{1:20s}\n'.format(nuzf2,comment))
                comment = 'PET for stress period ' + str(n + 1)
                if (n < len(self.pet)):                   
                    f_uzf.write(self.pet[n].get_file_entry())
                comment = ' NUZF3 for stress period ' + str(n + 1)
                if (n < len(self.extdp)):
                    nuzf3 = 1
                else:
                    nuzf3 = -1               
                f_uzf.write('{0:10d}{1:20s}\n'.format(nuzf3,comment))
                comment = 'EXTDP for stress period ' + str(n + 1)
                if (n < len(self.extdp)):                    
                    f_uzf.write(self.extdp[n].get_file_entry())
                comment = ' NUZF4 for stress period ' + str(n + 1)
                if self.iuzfopt > 0:
                    if (n < len(self.extwc)):
                        nuzf4 = 1
                    else:
                        nuzf4 = -1                   
                    f_uzf.write('{0:10d}{1:20s}\n'.format(nuzf4,comment))
                    comment = 'EXTWC for stress period ' + str(n + 1)
                    if (n < len(self.extwc)):                       
                        f_uzf.write(self.extwc[n].get_file_entry())
        f_uzf.close()