Getting Started
===============

batchOpenMPI requires mpi4py which in turn requires `mpi4py <http://mpi4py.scipy.org/>`_.
Once these are installed, you are good to go.

The way batchOpenMPI works is as follows

* all processes run the script up until the **batchOpenMPI.begin_MPI_loop()** call. Afterwhithe master process continue processing the script, while the worker processes wait for jobs from the master.
* jobs are managed using **batchOpenMPI.batchFunction** wrapper, which has the **addtoBatch** method. When addtoBatch is called on the master process, a job is created, which is later excuted on a worker process when the **batchOpenMPI.processBatch()** is called.
* when a **batchOpenMPI.batchFunction** is called on the master process, the batch processing results are checked against the requested input. If the input has been processed the already processed result is returned, otherwise the output is calculated on the master. Calculating on the master is not ideal, but occasionally is unavoidable. 

Basic example script (*ex1.py*):

.. literalinclude:: ../examples/ex1.py
   :lines: 5-

Which is can be run on Linux as follows ::

  $ mpirun -np 4 python ex1.py

The **batchOpenMPI.end_MPI_loop** call because of the *print_stats=True* should produce an output similar to ::

  --------- batchOpenMPI Stats ---------
  process    jobs completed      time: uW/ sR/ wI* (s)    utilisation(%)
     1              1            0.00/    0.00/    0.00       33.88
     2              5            0.00/    0.00/    0.00        0.78
     3              4            0.00/    0.00/    0.00        0.56
     * time doing; uW - useful work, sR - sending results, wI - waiting for instructions, Total
    time running master (s) :             0.003 
    total CPU time (s) :                  0.011 
    total CPU time actually used (s) :    0.002
    overall utilization : 21.85 %
  function stats :
  - solved on master  [0]
  - solved on workers [10]
  - jobs uncollected  [0]
  - jobs dropped      [0]
