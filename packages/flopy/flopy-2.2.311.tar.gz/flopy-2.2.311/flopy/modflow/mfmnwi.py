from flopy.mbase import Package

class ModflowMnwi(Package):
    'Multi-node well information package class\n'

    def __init__( self, model, wel1flag=1, qsumflag=1, byndflag=1, mnwobs=1, wellid_unit_qndflag_qhbflag_concflag=None,
                  extension='mnwi', unitnumber=58 ):
        Package.__init__(self, model, extension, 'MNWI', unitnumber) # Call ancestor's init to set self.parent, extension, name, and unit number
        self.url = 'mnwi.htm'
        self.heading = '# Multi-node well information (MNWI) file for MODFLOW, generated by Flopy'
        self.wel1flag = wel1flag        #-integer flag indicating output to be written for each MNW node at the end of each stress period
        self.qsumflag = qsumflag        #-integer flag indicating output to be written for each multi-node well
        self.byndflag = byndflag        #-integer flag indicating output to be written for each MNW node
        self.mnwobs = mnwobs            #-number of multi-node wells for which detailed flow, head, and solute data re to be saved
        self.wellid_unit_qndflag_qhbflag_concflag = wellid_unit_qndflag_qhbflag_concflag #-list of lists containing wells and related information to be output (length = [MNWOBS][4or5])

        #-input format checks:
        assert self.wel1flag >= 0, 'WEL1flag must be greater than or equal to zero.'
        assert self.qsumflag >= 0, 'QSUMflag must be greater than or equal to zero.'
        assert self.byndflag >= 0, 'BYNDflag must be greater than or equal to zero.'

        if len(self.wellid_unit_qndflag_qhbflag_concflag) != self.mnwobs:
            print 'WARNING: number of listed well ids to be monitored does not match MNWOBS.'

        self.parent.add_package(self)
    def __repr__( self ):
        return 'Multi-node well information package class'
    def write_file( self ):
        
        #-open file for writing
        f_mnwi = open( self.file_name[0], 'w' )

        #-write header
        f_mnwi.write( '%s\n' % self.heading )

        #-Section 1 - WEL1flag QSUMflag SYNDflag
        f_mnwi.write( '%10i%10i%10i\n' % ( self.wel1flag, self.qsumflag, self.byndflag ) )

        #-Section 2 - MNWOBS
        f_mnwi.write( '%10i\n' % self.mnwobs )

        #-Section 3 - WELLID UNIT QNDflag QBHflag {CONCflag} (Repeat MNWOBS times)
        for i in range(self.mnwobs):
            wellid = self.wellid_unit_qndflag_qhbflag_concflag[i][0]
            unit = self.wellid_unit_qndflag_qhbflag_concflag[i][1]
            qndflag = self.wellid_unit_qndflag_qhbflag_concflag[i][2]
            qhbflag = self.wellid_unit_qndflag_qhbflag_concflag[i][3]
            assert qndflag >= 0, 'QNDflag must be greater than or equal to zero.'
            assert qhbflag >= 0, 'QHBflag must be greater than or equal to zero.'
            if len(self.wellid_unit_qndflag_qhbflag_concflag[i]) == 4:
                f_mnwi.write( '%s %2i%10i%10i\n' % ( wellid, unit, qndflag, qhbflag ) )
            elif len(self.wellid_unit_qndflag_qhbflag_concflag[i]) == 5:
                concflag = self.wellid_unit_qndflag_qhbflag_concflag[i][4]
                assert 0 <= concflag <= 3, 'CONCflag must be an integer between 0 and 3.'
                assert isinstance(concflag,int), 'CONCflag must be an integer between 0 and 3.'
                f_mnwi.write( '%s %2i%10i%10i%10i\n' % ( wellid, unit, qndflag, qhbflag, concflag ) )

        f_mnwi.close()

