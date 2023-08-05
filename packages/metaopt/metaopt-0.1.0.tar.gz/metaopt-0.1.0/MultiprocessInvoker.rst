# Parallel Implementation

Manages parallel execution of objective functions
automatically, transparently

Optimization problems are inherently parallel
parallelization is a common technique for speeding up optimizations

Python's Multiprocessing
Batteries included, ono dependencies

System-level prcesses
Side Stepping the GIL

The GIL makes the CPython runtime threadsafe by ensuring only one thread can execute python code at a time.
While the GIL allows multiple threads to execute input or output operations in parallel,
    optimization problems are usually CPU-bound rather than I/O-bound.
This makes it impossible to exploit parallel computation in CPython for performance gains.

Multiprocessing starts multiple CPython interpreters, thereby allowing multiple threads to execute python code.
This way, code can be executed in parallel, exploiting the capabilities of multi core machines for speed ups.

# TODO WorkerProcess, WorkerProvider

The processes spawned by the MultiProcessInvoker execute the objective functions and return results.
# TODO tasks / task queue
The return values need to be transferred between the executing worker process and the main process running the Optimizer.
All the results need to be passed to the optimizer, eventually, so a mechanism to buffer a number of results is required.
To pass objects between these processes, interprocess communication is realized using Queues.
The MultiProcessInvoker create and hold references to a result Queue, which it checks for results.
For each result gotten from the result queue, the MultiProcessInvoker calls the on_error respectively on_result methods of its Optmizier.

Additionally, the main process needs to know which process is executing which task at any given time.
Using an unique task id, the process executing a given task can be identified.
Identifying processes is needed to stop and restart the right worker processes in case a timeout has occurred.
Sharing the task being executed between the worker and the main process is a form of sharing state.
Sharing the state is done using a server process, provided by a Manager instance from the multiprocessing module.
The manager instance holds a list of task ids for each worker process.
Task ids are written to the corresponding list by before excution of the task.
So the task list hold the id of the current task especially if it is not yet finished.
Tasks are read and removed from the task lists as the multiprocess invoker upon result or when a task is cancelled.
That way the task lists are kept in chronological order and hold all past tasks that did not finish yet.


