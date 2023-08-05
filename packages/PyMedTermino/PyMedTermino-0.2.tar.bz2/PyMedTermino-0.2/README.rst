PyMedTermino
============

PyMedTermino (Medical Terminologies for Python) is a Python module for
easy access to the main medical terminologies in Python. The following terminologies are available: SNOMED CT, ICD10, UMLS, VCM
icons (an iconic terminology developped at Paris 13 University).

PyMedTermino has been created at the LIMICS reseach lab,
University Paris 13, Sorbonne Paris Cité, INSERM UMRS 1142, Paris 6 University, by
Jean-Baptiste Lamy. PyMedTermino is available under the GNU LGPL licence.

In case of trouble, please contact Jean-Baptiste Lamy <jean-baptiste.lamy *@* univ-paris13 *.* fr>

::

  LIMICS
  University Paris 13, Sorbonne Paris Cité
  Bureau 149
  74 rue Marcel Cachin
  93017 BOBIGNY
  FRANCE


What can I do with PyMedTermino?
--------------------------------

  >>> SNOMEDCT.search("tachycardia*")
  [SNOMEDCT[3424008]  # Tachycardia (finding)
  , SNOMEDCT[4006006]  # Fetal tachycardia affecting management of mother (disorder)
  , SNOMEDCT[6456007]  # Supraventricular tachycardia (disorder)
  ...]
  >>> SNOMEDCT[3424008].parents
  [SNOMEDCT[301113001]  # Finding of heart rate (finding)
  ]
  >>> SNOMEDCT[3424008].children
  [SNOMEDCT[11092001]  # Sinus tachycardia (finding)
  , SNOMEDCT[278086000]  # Baseline tachycardia (finding)
  , SNOMEDCT[162992001]  # On examination - pulse rate tachycardia (finding)
  ...]
  >>> list(SNOMEDCT[3424008].ancestors_no_double())
  [SNOMEDCT[301113001]  # Finding of heart rate (finding)
  , SNOMEDCT[106066004]  # Cardiac rhythm AND/OR rate finding (finding)
  , SNOMEDCT[250171008]  # Clinical history and observation findings (finding)
  , SNOMEDCT[404684003]  # Clinical finding (finding)
  , SNOMEDCT[138875005]  # SNOMED CT Concept (SNOMED RT+CTV3)
  ...]
  >>> SNOMEDCT[3424008].relations
  set(['INVERSE_has_definitional_manifestation', 'finding_site', 'interprets', 'has_interpretation', 'INVERSE_associated_with'])
  >>> SNOMEDCT[3424008].finding_site
  [SNOMEDCT[24964005]  # Cardiac conducting system structure (body structure)
  ]
  >>> SNOMEDCT[3424008] >> VCM   # Maps the SNOMED CT concept to VCM icon
  Concepts([
    VCM[u"current--hyper--heart_rhythm"]  # 
  ])

PyMedTermino can also be used without Python, just for converting SNOMED CT and ICD10 XML data into SQL databases.


Links
-----

PyMedTermino on BitBucket (development repository): https://bitbucket.org/jibalamy/pymedtermino

PyMedTermino on PyPI (Python Package Index, stable release): https://pypi.python.org/pypi/PyMedTermino
