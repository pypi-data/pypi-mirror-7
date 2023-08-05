import os
import flopy
from flopy.mbase import BaseModel, Package
from flopy.utils import mfreadnam


class ModflowGlobal(Package):
    'Global Package class'
    def __init__(self, model, extension='glo'):
        Package.__init__(self, model, extension, 'GLOBAL', 1) # Call ancestor's init to set self.parent, extension, name and unit number
        #self.parent.add_package(self) This Package is not added to the base model so that it is not included in get_name_file_entries()
    def __repr__( self ):
        return 'Global Package class'
    def write_file(self):
    	# Not implemented for global class
    	return


class ModflowList(Package):
    'List Package class'
    def __init__(self, model, extension='list', unitnumber=2):
        Package.__init__(self, model, extension, 'LIST', unitnumber) # Call ancestor's init to set self.parent, extension, name and unit number
        #self.parent.add_package(self) This Package is not added to the base model so that it is not included in get_name_file_entries()
    def __repr__( self ):
        return 'List Package class'
    def write_file(self):
    	# Not implemented for list class
    	return


class Modflow(BaseModel):
    """
    MODFLOW Model Class.

    Parameters
    ----------
    modelname : string, optional
        Name of model.  This string will be used to name the MODFLOW input
        that are created with write_model. (the default is 'modflowtest')
    namefile_ext : string, optional
        Extension for the namefile (the default is 'nam')
    version : string, optional
        Version of MODFLOW to use (the default is 'mf2005').
    exe_name : string, optional
        The name of the executable to use (the default is
        'mf2005').
    listunit : integer, optional
        Unit number for the list file (the default is 2).
    model_ws : string, optional
        model workspace.  Directory name to create model data sets.
        (default is the present working directory).
    external_path : string
        Location for external files (default is None).
    verbose : boolean, optional
        Print additional information to the screen (default is False).
    load : boolean, optional
         (default is True).
    silent : integer
        (default is 0)

    Attributes
    ----------

    Methods
    -------

    See Also
    --------

    Notes
    -----

    Examples
    --------

    >>> import flopy
    >>> m = flopy.modflow.Modflow()

    """

    def __init__(self, modelname = 'modflowtest', namefile_ext = 'nam',
                 version='mf2005', exe_name='mf2005.exe',
                 listunit=2, model_ws=None,external_path=None,
                 verbose=False, load=True, silent = 0):
        '''
        external_path - used to activate external array option
        external_binflag -  controls ASCII vs. binary for external property arrays
                            does not influence data added using add_external()
        load - flag to control loading of existing arrays into FLOPY or simple passing
               string names through

        verbose controls Package _repr_ screen output
        '''
        BaseModel.__init__(self, modelname, namefile_ext, exe_name, model_ws)
        self.heading = '# Name file for ' + version + ', generated by Flopy.'
        if version == 'mf2k':
            self.glo = ModflowGlobal(self)
        self.lst = ModflowList(self, unitnumber=listunit)
        self.version = version  # So that we can do something different for mf2005
        #--external option stuff
        self.free_format = True
        self.external_fnames = []
        self.external_units = []
        self.external_binflag = []
        self.external_path = external_path
        self.external = False
        self.load = load
        #--the starting external data unit number
        self.__next_ext_unit = 1000
        if external_path is not None:
            assert os.path.exists(external_path),'external_path does not exist'
            self.external = True
        self.verbose = verbose
        self.silent = silent

        #Create a dictionary to map package with package object.
        #This is used for loading models.
        self.mfnam_packages = {
            "bas6": flopy.modflow.ModflowBas,
            "dis": flopy.modflow.ModflowDis,
            "lpf": flopy.modflow.ModflowLpf,
            "wel": flopy.modflow.ModflowWel,
            "drn": flopy.modflow.ModflowDrn,
            "rch": flopy.modflow.ModflowRch,
            "riv": flopy.modflow.ModflowRiv,
            "pcg": flopy.modflow.ModflowPcg,
            "oc" : flopy.modflow.ModflowOc
                                }
        return

    def __repr__( self ):
        nrow, ncol, nlay, nper = self.get_nrow_ncol_nlay_nper()
        return 'MODFLOW %d layer(s), %d row(s), %d column(s), %d stress period(s)' % ( nlay, nrow, ncol, nper)

    #--function to encapsulate next_ext_unit attribute
    def next_ext_unit(self):
        self.__next_ext_unit += 1
        return self.__next_ext_unit

    def get_nrow_ncol_nlay_nper(self):
        dis = self.get_package('DIS')
        if (dis):
            return dis.nrow, dis.ncol, dis.nlay, dis.nper
        else:
            return 0, 0, 0, 0
    nrow_ncol_nlay_nper = property(get_nrow_ncol_nlay_nper) # Property has no setter, so read-only

    def get_ifrefm(self):
        bas = self.get_package('BAS6')
        if (bas):
            return bas.ifrefm
        else:
            return False

    def set_name(self, value):
        # Overrides BaseModel's setter for name property
        BaseModel.set_name(self, value)

        for i in range(len(self.glo.extension)):
            self.glo.file_name[i] = self.name + '.' + self.glo.extension[i]

        for i in range(len(self.lst.extension)):
            self.lst.file_name[i] = self.name + '.' + self.lst.extension[i]
    name = property(BaseModel.get_name, set_name) # Property must be redeclared to override basemodels setter method

    def write_name_file(self):
        """
        Write the model files.
        """
        fn_path = os.path.join(self.model_ws,self.namefile)
        f_nam = open(fn_path, 'w')
        f_nam.write('%s\n' % (self.heading) )
        if self.version == 'mf2k':
            f_nam.write('%s %3i %s\n' % (self.glo.name[0], self.glo.unit_number[0], self.glo.file_name[0]))
        f_nam.write('%s %3i %s\n' % (self.lst.name[0], self.lst.unit_number[0], self.lst.file_name[0]))
        f_nam.write('%s' % self.get_name_file_entries())
        for u,f,b in zip(self.external_units,self.external_fnames,self.external_binflag):
            if b:
                f_nam.write('DATA(BINARY)  {0:3d}  '.format(u)+f+' REPLACE\n'	)
            else:
                f_nam.write('DATA  {0:3d}  '.format(u)+f+'\n'	)
        f_nam.close()

    @staticmethod
    def load(f, version='mf2k', exe_name='mf2005.exe', 
             verbose=False, model_ws=None):
        """
        Load an existing model.

        Parameters
        ----------
        f : MODFLOW name file
            File to load.
        
        model_ws : model workspace path

        Returns
        -------
        ml : Modflow object

        Examples
        --------

        >>> import flopy
        >>> ml = flopy.modflow.Modflow.load(f)

        """
        ml = Modflow(f.split('.')[0], version=version, exe_name=exe_name, 
                     verbose=False, model_ws=model_ws)
        try:
            namefile_path = os.path.join(ml.model_ws, ml.namefile)
            ext_unit_dict = mfreadnam.parsenamefile(namefile_path, ml.mfnam_packages)
        except Exception as e:
            print "error loading namfile entries from file"
            print str(e)
            return None
        dis = None
        dis_key = None
        for key, item in ext_unit_dict.iteritems():
            if item.filetype.lower() == "dis":
                dis = item
                dis_key = key
        pck = dis.package.load(dis.filename, ml, ext_unit_dict=ext_unit_dict)
        ext_unit_dict.pop(dis_key)
        if verbose:
            print ext_unit_dict
        for key, item in ext_unit_dict.iteritems():
            if item.package is not None:
                pck = item.package.load(item.filename, ml, ext_unit_dict=ext_unit_dict)
                pass
            elif "data" not in item.filetype.lower():
                if verbose:
                    print "skipping package", item.filetype, item.filename
        return ml



