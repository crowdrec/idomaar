Idomaar
===================

**Idomaar** (/i:dɒmæ(r)/) is the [CrowdRec](http://www.crowdrec.eu) recommendation and evaluation reference framework.

At the highest abstraction level, Idomaar can be split into the following blocks:
* the algorithms to test, both state-of-the-art algorithms and new solutions implemented within the [CrowdRec](http://www.crowdrec.eu) project, e.g,. the algorithms developed in WP4.
The algorithms are implemented within the *computing environments*
* the evaluation logic, experimenting with the available algorithms in order to compute both quality (e.g., [RMSE](http://www.recsyswiki.com/wiki/Root_mean_square_error), [recall](http://www.recsyswiki.com/wiki/Recall)) and system (e.g., execution and response time) metrics. Idomaar will include some evaluation policies, free to be extended.
The evaluation logic is implemented by an *orchestrator* and an *evaluator*.
* the data, i.e., the datasets made available to the practitioners (e.g., the [MovieTweetings](https://github.com/sidooms/MovieTweetings)). 
Algorithms, evaluation logic, and data will be as decoupled as possible to allow to experiment with most existing solutions - no matter the technology they are implemented on - granting reproducible and consistent comparisons.
The data are contained in the *data container*

See [usage.md](usage.md) for installation instructions and usage.
