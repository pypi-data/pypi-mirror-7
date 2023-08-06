.. _validate:

Validation
==========

.. sectionauthor:: Matt Swain <m.swain@me.com>

The MolVS :class:`~molvs.metal.Validator` provides a way to identify and log unusual and potentially troublesome
characteristics of a molecule.


Validating a molecule
---------------------

The :func:`~molvs.validate.validate_smiles` function is a convenient way to quickly validate a single SMILES
string::

    >>> from molvs import validate_smiles
    >>> validate_smiles('O=C([O-])c1ccccc1')
    ['INFO: [NeutralValidation] Not an overall neutral system (-1)']

It returns a list of log messages as strings.

The :class:`~molvs.metal.Validator` class provides more flexibility when working with multiple molecules or when a
custom :class:`~molvs.metal.Validation` list is required::

    >>> fmt = '%(asctime)s - %(levelname)s - %(validation)s - %(message)s'
    >>> validator = Validator(log_format=fmt)
    >>> mol = Chem.MolFromSmiles('[2H]C(Cl)(Cl)Cl')
    >>> validator.validate(mol)
    ['2014-08-05 16:04:23,682 - INFO - IsotopeValidation - Molecule contains isotope 2H']



Available validations
---------------------

The :ref:`API documentation <molvs_validations>` contains a full list of the individual validations that are available.
