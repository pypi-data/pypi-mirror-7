#!/usr/bin/env python

"""
This module provides classes to comparsion the structures of the two
molecule. As long as the two molecule have the same bond connection tables,
the molecules are deemed to be same. The atom in the two molecule must be
paired accordingly.
This module is supposed to perform rough comparisons with the atom order
correspondence prerequisite, while molecule_matcher is supposed to do exact
comparisons without the atom order correspondence prerequisite.
"""
import itertools
from pymatgen.serializers.json_coders import MSONable

__author__ = "Xiaohui Qu"
__copyright__ = "Copyright 2011, The Materials Project"
__version__ = "1.0"
__maintainer__ = "Xiaohui Qu"
__email__ = "xhqu1981@gmail.com"
__status__ = "Experimental"
__date__ = "Jan 22, 2014"


class CovalentRadius():
    """
    Covalent Radius of the elements.

    Beatriz C. et al. Dalton Trans. 2008, 2832-2838. DOI: 10.1039/b801115j
    """

    def __init__(self):
        pass

    radius = {'H': 0.31, 'He': 0.28, 'Li': 1.28, 'Be': 0.96,
              'B': 0.84, 'C': 0.73, 'N': 0.71, 'O': 0.66,
              'F': 0.57, 'Ne': 0.58, 'Na': 1.66, 'Mg': 1.41,
              'Al': 1.21, 'Si': 1.11, 'P': 1.07, 'S': 1.05,
              'Cl': 1.02, 'Ar': 1.06, 'K': 2.03, 'Ca': 1.76,
              'Sc': 1.70, 'Ti': 1.60, 'V': 1.53, 'Cr': 1.39,
              'Mn': 1.50, 'Fe': 1.42, 'Co': 1.38, 'Ni': 1.24,
              'Cu': 1.32, 'Zn': 1.22, 'Ga': 1.22, 'Ge': 1.20,
              'As': 1.19, 'Se': 1.20, 'Br': 1.20, 'Kr': 1.16,
              'Rb': 2.20, 'Sr': 1.95, 'Y': 1.90, 'Zr': 1.75,
              'Nb': 1.64, 'Mo': 1.54, 'Tc': 1.47, 'Ru': 1.46,
              'Rh': 1.42, 'Pd': 1.39, 'Ag': 1.45, 'Cd': 1.44,
              'In': 1.42, 'Sn': 1.39, 'Sb': 1.39, 'Te': 1.38,
              'I': 1.39, 'Xe': 1.40, 'Cs': 2.44, 'Ba': 2.15,
              'La': 2.07, 'Ce': 2.04, 'Pr': 2.03, 'Nd': 2.01,
              'Pm': 1.99, 'Sm': 1.98, 'Eu': 1.98, 'Gd': 1.96,
              'Tb': 1.94, 'Dy': 1.92, 'Ho': 1.92, 'Er': 1.89,
              'Tm': 1.90, 'Yb': 1.87, 'Lu': 1.87, 'Hf': 1.75,
              'Ta': 1.70, 'W': 1.62, 'Re': 1.51, 'Os': 1.44,
              'Ir': 1.41, 'Pt': 1.36, 'Au': 1.36, 'Hg': 1.32,
              'Tl': 1.45, 'Pb': 1.46, 'Bi': 1.48, 'Po': 1.40,
              'At': 1.50, 'Rn': 1.50, 'Fr': 2.60, 'Ra': 2.21,
              'Ac': 2.15, 'Th': 2.06, 'Pa': 2.00, 'U': 1.96,
              'Np': 1.90, 'Pu': 1.87, 'Am': 1.80, 'Cm': 1.69}


class MoleculeStructureComparator(MSONable):

    """
    Class to check whether the connection tables of the two molecules are the
    same. The atom in the two molecule must be paired accordingly.

    Args:
        bond_length_cap: The ratio of the elongation of the bond to be
            acknowledged. If the distance between two atoms is less than (
            empirical covalent bond length) X (1 + bond_length_cap), the bond
            between the two atoms will be acknowledged.
        covalent_radius: The covalent radius of the atoms.
            dict (element symbol -> radius)
        priority_bonds: The bonds that are known to be existed in the initial
            molecule. Such bonds will be acknowledged in a loose criteria.
            The index should start from 0.
        priority_cap: The ratio of the elongation of the bond to be
            acknowledged for the priority bonds.
    """
    def __init__(self, bond_length_cap=0.3,
                 covalent_radius=CovalentRadius.radius,
                 priority_bonds=(),
                 priority_cap=0.8):
        self.bond_length_cap = bond_length_cap
        self.covalent_radius = covalent_radius
        self.priority_bonds = [tuple(sorted(b)) for b in priority_bonds]
        self.priority_cap = priority_cap

    def are_equal(self, mol1, mol2):
        """
        Compare the bond table of the two molecules.

        Args:
            mol1: first molecule. pymatgen Molecule object.
            mol2: second moleculs. pymatgen Molecule objec.
        """
        b1 = set(self._get_bonds(mol1))
        b2 = set(self._get_bonds(mol2))
        return b1 == b2

    def _get_bonds(self, mol):
        """
        Find all the bond in a molcule

        Args:
            mol: the molecule. pymatgen Molecule object

        Returns:
            List of tuple. Each tuple correspond to a bond represented by the
            id of the two end atoms.
        """
        num_atoms = len(mol)
        # index starting from 0
        all_pairs = list(itertools.combinations(range(num_atoms), 2))
        pair_dists = [mol.get_distance(*p) for p in all_pairs]
        elements = mol.composition.to_dict.keys()
        unavailable_elements = list(set(elements) -
                                    set(self.covalent_radius.keys()))
        if len(unavailable_elements) > 0:
            raise ValueError("The covalent radius for element {} is not "
                             "available".format(unavailable_elements))
        max_length = [(self.covalent_radius[mol.sites[p[0]].specie.symbol] +
                       self.covalent_radius[mol.sites[p[1]].specie.symbol]) *
                      (1 + (self.priority_cap
                            if p in self.priority_bonds
                            else self.bond_length_cap))
                      for p in all_pairs]
        bonds = [bond
                 for bond, dist, cap in zip(all_pairs, pair_dists, max_length)
                 if dist <= cap]
        return bonds

    @property
    def to_dict(self):
        return {"version": __version__, "@module": self.__class__.__module__,
                "@class": self.__class__.__name__,
                "bond_length_cap": self.bond_length_cap,
                "covalent_radius": self.covalent_radius,
                "priority_bonds": self.priority_bonds,
                "priority_cap": self.priority_cap}

    @classmethod
    def from_dict(cls, d):
        return MoleculeStructureComparator(
            bond_length_cap=d["bond_length_cap"],
            covalent_radius=d["covalent_radius"],
            priority_bonds=d["priority_bonds"],
            priority_cap=d["priority_cap"])
