#-------------------------------------------------------------------------------
# . File      : MolarisAtomsFile.py
# . Program   : MolarisTools
# . Copyright : USC, Mikolaj Feliks (2016)
# . License   : GNU GPL v3.0       (http://www.gnu.org/licenses/gpl-3.0.en.html)
#-------------------------------------------------------------------------------
from   Atom        import Atom
from   Units       import *
from   Utilities   import TokenizeLine, WriteData
import collections

Force = collections.namedtuple ("Force" , "x y z")


class MolarisAtomsFile (object):
    """A class representing atoms for the QC/MM calculation."""

    def __init__ (self, filename="atoms.inp", replaceSymbols=None):
        """Constructor."""
        self.inputfile      = filename
        self.replaceSymbols = replaceSymbols
        self._Parse ()


    def _LineToAtom (self, line, includeCharge=False):
        tokens = TokenizeLine (line, converters=[None, float, float, float, float])
        symbol = tokens[0]
        # . Replace selected atomic symbols (a workaround for a persisting bug in Molaris)
        if self.replaceSymbols:
            for (symbolOld, symbolNew) in self.replaceSymbols:
                if symbolOld == symbol:
                    symbol = symbolNew
                    break
        # . Create an atom
        atom   = Atom (
            label  =  symbol,
            charge = (tokens[4] if includeCharge else None) ,
            x      =  tokens[1]  ,
            y      =  tokens[2]  ,
            z      =  tokens[3]  ,)
        return atom


    def _ReadAtoms (self, openfile, natoms, includeCharge=False):
        atoms = []
        for nq in range (natoms):
            line = next (openfile)
            atom = self._LineToAtom (line, includeCharge)
            atoms.append (atom)
        return atoms


    def _Parse (self):
        lines   = open (self.inputfile)
        line    = next (lines)
        # . Get step number and total energy
        step, G = TokenizeLine (line, converters=[int, float])
        try:
            while True:
                line = next (lines)
                # . Read the QM section
                if line.count ("# of qmmm atoms"):
                    nquantum, nlink = TokenizeLine (line, converters=[int, int])
                    # . Read QM atoms proper
                    self.qatoms = self._ReadAtoms (lines, nquantum)
                    # . Read QM link atoms
                    self.latoms = self._ReadAtoms (lines, nlink)
                elif line.count ("# of total frozen protein atoms, # of groups in Region I`"):
                    pass
                elif line.count ("# of frozen water atoms in Region I`"):
                    pass
                # . Read the protein section
                elif line.count ("# of non-frozen protein atoms in Region II"):
                    nprot = TokenizeLine (line, converters=[int])[0]
                    self.patoms = self._ReadAtoms (lines, nprot, includeCharge=True)
                # . Read the free water section
                elif line.count ("# of non-frozen water atoms in the system"):
                    nwater = TokenizeLine (line, converters=[int])[0]
                    self.watoms = self._ReadAtoms (lines, nwater, includeCharge=True)
        except StopIteration:
            pass
        # . Close the file
        lines.close ()


    def WriteQM (self, filename="qm.xyz", link=False, append=False, caption=""):
        """Write QM atoms to an XYZ file."""
        self._WriteSection (filename, (self.qatoms + self.latoms) if link else self.qatoms, includeCharge=False, append=append, caption=caption)


    def WriteProtein (self, filename="prot.xyz"):
        """Write protein atoms to an XYZ file."""
        self._WriteSection (filename, self.patoms, includeCharge=True)


    def WriteWater (self, filename="wat.xyz"):
        """Write protein atoms to an XYZ file."""
        self._WriteSection (filename, self.watoms, includeCharge=True)


    def _WriteSection (self, filename, atoms, includeCharge=False, skipSymbol=False, append=False, caption=""):
        """Write an XYZ file."""
        natoms = len (atoms)
        data   = ["%d\n%s\n" % (natoms, caption if caption else filename)]
        for atom in atoms:
            data.append ("%2s    %8.3f    %8.3f    %8.3f    %8s\n" % ("" if skipSymbol else atom.label, atom.x, atom.y, atom.z, ("%8.4f" % atom.charge) if includeCharge else ""))
        WriteData (data, filename, append=append)


    def WriteMopacInput (self, filename="run.mop", method="PM3", charge=0, multiplicity=1, eps=78.4, cosmo=False, qmmm=False):
        """Write an input file for MOPAC."""
        pass


    def WriteGaussianInput  (self, filename="run.inp", methodBasis="PM3", charge=0, multiplicity=1, qmmm=False):
        """Write an input file for Gaussian."""
        pass


#===============================================================================
# . Main program
#===============================================================================
if __name__ == "__main__": pass
