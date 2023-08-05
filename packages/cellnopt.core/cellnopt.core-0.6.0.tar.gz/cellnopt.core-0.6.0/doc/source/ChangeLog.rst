ChangeLog
=================


.. rubric:: 0.6.0

* refactoring of MIDAS/CNOGraph data structures.

.. rubric:: 0.5.3

* use unicode instead of str in cnograph module to prevent error when sppecial 
  character are used as node name
* mapback: implementing the mapback function. Not yet working for the AND gates
* midas: set CellLine to undefined is not set. added normalise function
* normalisation: implementation of the time and control case


.. rubric:: 0.5.2

* cnograph: add remove_self_loops function ; remove_edge accept key argument 
  (MultiGraph case); split and merge_nodes keep track of colors if any"
* CNOGraphMultiEdges can now plot edges in colors
* fix typo in cnogrpah.CNOGraph.plotdot when using a differnt viewver. 
* populate  node color when calling cnograph.CNOGraph.rename_node"
* XMIDAS implementation. Written from scratch to make use of Pandas dataframe.
  No need for makecnolist. the data is stored in a dataframe.
* CNOGraph uses XMIDAS
* CNOGraphMultiEdges seems to work
* Normalisation (on time zero) available for XMIDAS



.. rubric:: revision 0.4.2

* fix tests
* add or move modules into ./io directory
* cnograph: fix split_node function for AND gates
* cnograph: prevent compression to compress nodes that would lead to multiedge ambiguity.
* cnograph: can accept as input a networkx graph or any instance that contains reacID attribute. 
* cnograph: operator + keeps track of the _stimuli, _signals, _inhibitors  attributes.
* nonc: module usees signals and stimuli parameters instead of cnolist
* move SIF files from ./test directory to share/directory and improved test
  suite
* sif: empty lines may now be present in the SIF. input can be any instance that
  contains a reacID attriute. ands convertion may now fail (if the input
  contains incorrect ANDs).

.. rubric:: revision 0.4.1

* cnograph: fixed bug in compression to keep orphans if there are
  stimuli,inhibitors or signals. + Add properties to get stimuli, inhibitors,
  signals list


.. rubric:: revision 0.4.0

* First release of pypi

.. rubric:: revision 0.3.0

* cnograph stabalised
* normalisation class added
* tutorial done + documentation

.. rubric:: revision 0.2.0

* cnograph and sif modules are still in progress but ready to use
* test coverage of 80%



.. rubric:: revision 0.1.0

* add bunch of modules:
    * cnograph, cutnonc, compression
    * converter modules:
        * converter
        * sif2asp
        * adj2sif
        * sop2sif
    * readers:
        * metabolites
        * reactions
        * sif, midas, metabolites
        * kinexus
    * analysis





