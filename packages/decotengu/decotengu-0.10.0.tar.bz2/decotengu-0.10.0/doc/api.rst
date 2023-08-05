Classes and Functions
=====================

Core API
--------
.. fixme: we need to automate this!
.. autosummary::

   decotengu.create
   decotengu.Engine
   decotengu.DecoTable
   decotengu.engine.Step
   decotengu.engine.GasMix
   decotengu.engine.DecoStop

.. autofunction:: decotengu.create

.. autoclass:: decotengu.Engine
   :members:
   :private-members:

.. autoclass:: decotengu.DecoTable
   :members:

.. autoclass:: decotengu.engine.Step
.. autoclass:: decotengu.engine.GasMix
.. autoclass:: decotengu.engine.DecoStop

Decompression Model
-------------------
.. fixme: we need to automate this!
.. autosummary::

   decotengu.model.Data
   decotengu.model.ZH_L16_GF
   decotengu.model.ZH_L16B_GF
   decotengu.model.ZH_L16C_GF
   decotengu.model.TissueCalculator
   decotengu.model.eq_schreiner
   decotengu.model.eq_gf_limit

.. autoclass:: decotengu.model.Data

.. autoclass:: decotengu.model.ZH_L16_GF
   :members:

.. autoclass:: decotengu.model.ZH_L16B_GF
   :members:

.. autoclass:: decotengu.model.ZH_L16C_GF
   :members:

.. autoclass:: decotengu.model.TissueCalculator
   :members:

.. autofunction:: decotengu.model.eq_schreiner

.. autofunction:: decotengu.model.eq_gf_limit

Dive Phases
-----------
.. fixme: we need to automate this!
.. autosummary::

   decotengu.engine.Phase

.. autoclass:: decotengu.engine.Phase

Dive Profile Expansion
----------------------
.. fixme: we need to automate this!
.. autosummary::

   decotengu.conveyor.Conveyor

.. autoclass:: decotengu.conveyor.Conveyor
   :members: __call__, trays

Tabular Tissue Calculator
-------------------------
.. autosummary::

   decotengu.alt.tab.tab_engine
   decotengu.alt.tab.linearize
   decotengu.alt.tab.eq_schreiner_t
   decotengu.alt.tab.TabTissueCalculator
   decotengu.alt.tab.FirstStopTabFinder

.. autofunction:: decotengu.alt.tab.tab_engine
.. autofunction:: decotengu.alt.tab.linearize
.. autofunction:: decotengu.alt.tab.eq_schreiner_t

.. autoclass:: decotengu.alt.tab.TabTissueCalculator
   :members:

.. autoclass:: decotengu.alt.tab.FirstStopTabFinder
   :members: __call__

First Decompression Stop Binary Search
--------------------------------------
.. autosummary::

   decotengu.alt.bisect.BisectFindFirstStop

.. autoclass:: decotengu.alt.bisect.BisectFindFirstStop
   :members: __call__

Naive Algorithms
----------------
.. autosummary::

   decotengu.alt.naive.DecoStopStepper

.. autoclass:: decotengu.alt.naive.DecoStopStepper
   :members: __call__

.. vim: sw=4:et:ai
