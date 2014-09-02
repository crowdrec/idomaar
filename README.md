reference-framework
===================

CrowdRec reference framework (http://rf.crowdrec.eu)

At the highest abstraction level, the reference framework can be split into the following blocks:
* the algorithms to test, both state-of-the-art algorithms and new solutions implemented within the CrowdRec project, e.g,. the algorithms developed in WP4.
The algorithms are implemented within the *computing environments*
* the evaluation logic, experimenting with the available algorithms in order to compute both quality (e.g., RMSE, recall) and system (e.g., execution and response time) metrics. The framework will include some evaluation policies, free to be extended.
The evaluation logic is implemented by an *orchestrator* and an *evaluator*.
* the data, i.e., the datasets made available to the practitioners (e.g., the MovieTweetings). 
Algorithms, evaluation logic, and data will be as decoupled as possible to allow to experiment with most existing solutions - no matter the technology they are implemented on - granting reproducible and consistent comparisons.
The data are contained in the *data container*

