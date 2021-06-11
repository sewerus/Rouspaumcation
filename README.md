# Rouspaumcation
Simulation program designed to solve problem of dynamic routing, space and spectrum allocation (RSSA) of unicast demands in flex-grid network with assistive sotrage.

Needed data set:
- .net file with network dimensions: number of nodes, links and adjacent matrix,
- .pat file with k candidate paths (k can be set up in code),
- .spec file with number of slices needed for each path in .pat file,
- .dem files with demands (income iteration, source, target, bitrate and duration).

<span>2</span>

The aim of the project is to propose new created method to solve RSSA problem (Dynamic Routing Space and Spectrum Allocation) with assistive storage. The method consists in creating candidate demand sets for each spectrally-spatially resources and selecting those demands that limit available resources for the fewest other demands. It has been described in detail through the criteria for creating such sets, and a simulation program has been implemented to test it for different traffic volumes. This gives the opportunity to measure how beneficial it is to use assistive storage in various cases.

Introduction
============

Many observations show that Internet traffic is growing faster and faster. The introducing technologies will bring about many changes. A good example is 5G technology, which in 2023 will reach speeds around 13 times faster than mobile traffic in 2018.

The technology that can cope with such an increase in network bandwidth demand is concept of spectrally-spatially flexible optical networks (SS-FONs). It implements space division multiplexing (SDM) with elastic optical networks (EON), what brings benefits like enormous increase in transmission capacity. It is also opportunity to manage network resource in more flexible way.

It works by discretization the optical spectrum in frequency slots (FSs) of 12.5 GHz width. By concatenating multiple adjacent Sub-Channels (Sb-Chs) it is possible to form Super-Channel (SCh) that enables ultra-high bit-rate transmissions.

According to , the global average broadband speed is growing, from 45.9 Mbps in 2018 to 110.4 Mbps in 2023. This is one of the key indicators of increased IP traffic. This raises the need to find better methods of planning unicast traffic using existing infrastructure. The attempt to meet these requirements is working on dynamic routing, spectrum and space allocation (RSSA) problem. The aim is to find for each request a routing path, spatial cores and optical channel. It is also possible to determine a modulation level and handle with routing, modulation level, space and spectrum allocation (RMLSSA), but in this paper modulation level is pre-determined. Many publication consider also routing and spectrum allocation (RSA) problem.

RSSA problem is to find a lightpath in SS-FONs scenario, what requires to focus on spectrum and space allocation in the same time for incoming requests. There are many ways to solve this problem, what we present in the next chapters. We want to create new method basing on probability of using a specific resource of space and spectrum for unicast requests. In this paper we want to describe proposed algorithm and present its implementation. Next we want to conduct research and compare results with results obtained by the SSA algorithm.

Related works
=============

The subject of this article is quite a new field of Internet traffic engineering. Nevertheless, many works have been prepared proposing various approaches to the problem of allocation of the discussed resourches.

In many works RSSA problem is studied with using integer linear programming (ILP). Formulating this problem as ILP model provides to solve optimization problem with decision variables. Hovewer, this technique is low scalability. Mathematical programming (MP) methods for larger instances of complex problems don’t provide results in a reasonable time.

Another way is using heuristic or metaheuristic algorithms, which are faster, but not always reach optimal solution of a problem.

Fixed-Alternate routing and First-Fit frequency assignment (FA-FF) algorithm is proposed in . In authors propose effective heuristic method called Adaptive Frequency Assignment - Collision Avoidance (AFA-CA). In this method the main aim is to select the sequence of processed demands in order to minimize the spectrum use. In authors propose two algorithms solving RSSA-DPP (Dedicated Path Protection) problem using evolutionary algorithm and tabu search. Three different heuristic algorithms called spectrum waste base (SWB) algorithm, intentional spectrum waste with sequential approach (ISW-S) algorithm and intentional spectrum waste with accumulative approach (ISW-A) are proposed in using spectrum waste metric. Another heuristic is developed in , basing on the greedy randomized adaptive search procedure authors propose GRASP metaheuristic approach. They also propose adaptive search procedure (SA) to solve larger instances of the RSSA problem. In authors propose another algorithm using greedy heuristic. Another algorithms are: a variable-group-base (MVG) algorithm , a minimum-block-generated flexible-grouping-based (MBFG) spectrum assignment algorithm and an SLA-provisioning algorithm (SADQ) that employs multilevel differentiation to provision the proposed service level agreement (SLA) parameters.

The last way to solve discussed problem is to use the techniques of artificial intelligence (AI). In described is using AI in optical networks, what can improve the configuration and operation of network devices, optical performance monitoring and quality of transmission (QoT) estimation. AI systems gives opportunities for automating operations and introducing intelligence decisions by planning use and management of network resources.

Problem definition
==================

In this section we want to present a way to describe RSSA problem as a mathematical model. There are two cases: static network parameters and variables of resources that are used by incoming demands.

Static network parameters refers to network dimensions. The SS-FON can be modeled as a directed graph \(G = (V, E)\), where \(V\) is a set of network nodes, \(E\) is a set of directed physical network links. On each link there is a set of available spatial modes \(K\) and on each mode there is a set of frequency slices \(S\). Channel in such a flex-grid SDM network is a set of adjacent slices on the same fiber mode.

For each pair of two network nodes \((v_i, v_j)\) there is a set of candidate routing paths \(P_{ij}\). Constant \(\delta_{epij}\) is equal to \(1\) if a link \(e\) is a part of a candidate path \(p\) between nodes \(v_i\) and \(v_j\). Otherwise \(\delta_{epij}\) is equal to \(0\).

To describe the occurrence of incoming requests, we will treat time as successive iterations \(n = 1, 2, ..., N\). Each demand from set \(D\) is described by its iteration of arrival \(a_d\), source node \(s_d\), destination node \(t_d\), bit-rate \(h_d\) (in Gbps) and duration \(l_d\) (number of iterations). On the basis of made determinations, there is a set of candidate paths for the each request \(d\) described as \(P_d = P_{s_d t_d}\) and constant \(\delta_{epd} = \delta_{ep s_d t_d}\).

For each link \(e\) there is a function \(f_e(h)\), which returns number of needed frequency slices for a given bit-rate \(h\) in Gbps. For each network node \(v\) there is a buffer that is limited by the maximum number of requests \(B_v\) it can remember.

The solution of the problem is to determine how long each request should be stored in a buffer, through which routing path should be sent and which spectrally-spatially resources should be used.

If demand \(d\) after its arrival iteration \(a_d\) is not stored in its source node buffer but starts to be processed immediately, then \(b_d = 0\). Otherwise \(b_d\) is equal to number of iterations, that demand \(d\) is stored in this buffer. That means, that each demand \(d\) begins to be processed in iteration \(a_d + b_d\) and ends to be processed at iteration \(a_d + b_d + l_d\). If demand \(d\) is rejected from a buffer without processing, then \(r_d = 1\), otherwise \(r_d = 0\). At each iteration number of stored demands in buffer on node \(v\) can not be greater than \(B_v\). This constraint is defined in ([aqn:buffer]).

When demand \(d\) starts to be processed, the routing path is selected and free resources are allocated. In this paper we consider non-bifurcated flows. If for demand \(d\) chosen is path \(p \in P_d\), then \(x_{dp} = 1\), otherwise \(x_{dp} = 0\). This constraint is defined in ([aqn:onepath]). On mentioned path \(p\) allocated resources form a channel with adjacent slices on selected fiber mode. This channel is determined by variable \(c_{dks}\), which is equal to 1 if demand \(d\) uses fiber mode \(k\) and adjacent frequency slices beginning with slice \(s\), otherwise \(c_{dks} = 0\). Constraint about allocation slices on only one mode is defined in ([aqn:onemode]).

On given network link \(e\) if there is demand \(d\) that uses channel formed by spatial mode \(k\) and adjacent slices beginning with slice \(s\), then all slices from \(s\) to \(s + f_e(h_d) + 1\) are used, because \(f_e(h_d)\) is equal to number of slices needed for demand \(d\) basing on its bit-rate. There is one additional slice because of guard-band. That means, if on that link \(e\) and mode \(k\) demand \(d\) uses slice \(s\), there is slice \(s' \in \left< s-\left( f_e(h_d) + 1 \right); s \right>\) which is beginning of formed channel for this demand, so \(\sum_{s' \in \left< s-\left( f_e(h_d) + 1 \right); s \right>} c_{dks'} = 1\).

Variable \(c_{dks}\) is related to auxiliary variable \(y_{neks}\), which is equal to 1 if at iteration \(n\) on physical link \(e\) frequency slice \(s\) on spatial mode \(k\) is in use, otherwise \(y_{neks} = 0\). At each iteration single frequency slice can be allocated to only one channel for only one demand, what is defined in ([aqn:onechannel]).

The aim of the considered optimization problem is to allocate as much demands as it is possible. Objective functions we want to minimize are demand blocking probability (DBP) defined in ([aqn:dbp]) and bit-rate blocking probability (BBP) defined in ([aqn:bbp]).

\[\label{aqn:buffer}
\begin{split}
\forall_{n \in N} \forall_{v \in V} \vert \{ d \in D: s_d = v \land b_d > 0 \\
\land a_d + b_d = n \land r_d = 0 \} \vert \leq B_v
\end{split}\]

\[\label{aqn:onepath}
\forall_{d \in D} \sum_{p \in P_d} x_{pd} = 1\]

\[\label{aqn:onemode}
\forall_{d \in D} \exists!_{k \in K} \sum_{s \in S} c_{dks} = 1\]

\[\label{aqn:onechannel}
\begin{split}
\forall_{n \in N} \forall_{e \in E} \forall_{k \in K} \forall_{s \in S} y_{neks} = \vert \{ d \in D : \\
r_d = 0 \\
\land a_d + b_d \leq n \leq a_d + b_d + l_d \\
\land \left( \exists!_{p \in P_d} x_{pd} = 1 \land \delta_{epd} = 1 \right) \\
\land \sum_{s' \in \left< s-\left( f_e(h_d) + 1 \right); s \right>} c_{dks'} = 1 \} \vert \\
\in \{0, 1\}
\end{split}\]

\[\label{aqn:dbp}
DBP = \frac{\sum_{d \in D} r_d}{|D|}\]

\[\label{aqn:bbp}
BBP = \frac{\sum_{d \in D} r_d \cdot h_d}{\sum_{d \in D} h_d}\]

Description of the method
=========================

In this section we propose method that consists of creating candidate request sets for resources. We present new variables in each step with mathematical formulas basing on assumed network model.

Method steps
------------

General idea of proposed method is to find at subsequent iterations for each spatial mode \(k\) and each frequency slice \(s\) on each physical link \(e\) how many demands can use this resource as beginning slice of its channel. That means, that for each space and spectrum resource we need to find a list of candidate demands \(D_{eks} \subset D\). If tested resource determined by \(e, k, s\) is currently in use, then current list of candidate demands \(D_{eks}\) is empty. Moreover, after preparing lists \(D_{eks}\) for each resource, for each demand \(d\) that could start processing in current iteration there are prepared candidate pairs of paths and channels described as \(c'_{d}\).

We introduce also two auxiliary variables: \(q_d\) that is equal to \(1\) if demand \(d\) is processing, otherwise is equal to \(0\); and \(m_d\) that is equal to \(1\) if demand \(d\) processing is completed, otherwise is equal to \(0\).

At a given iteration \(n\) included in preparing sets \(D_{eks}\) demands that are not rejected (\(r_d = 0\)), not processing (\(q_d  = 0\)), not completed (\(m_d = 0\)) and can be processed in current \(n\)-th iteration(\(n = a_d + b_d\)). Considered demands can use physical link \(e\), what can be described as \(\sum_{p \in P_d} \delta_{epd} > 0\). It is also necessary to check if there are enough unused adjacent slices, what is determined in ([aqn:enoughtslices]). It is also needed to ensure slices of guard-bands - slice \(s-1\) and slice \(s+1\), what is determined in ([aqn:guardband]).

\[\label{aqn:enoughtslices}
s+f_e(h_d) \leq |S| \land \sum_{s' \in \left< s; s+f_e(h_d) \right>} y_{neks'} = 0\]

\[\label{aqn:guardband}
\begin{split}
\left(s > 1 \implies y_{nek(s-1)} = 0 \right) \\
\land \left( s+f_e(h_d) < |S| \implies y_{nek(s+1)} = 0 \right)
\end{split}\]

Basing on the presented assumptions, it is possible to prepare at given \(n\)-th iteration sets of candidate demands \(D_{eks}\) for each space and spectrum resource on each link by formula ([aqn:deks]).

Knowing set \(D_{eks}\) it is possible to find candidate pairs of paths and channels, what is determined in ([aqn:cd]). This set respects that candidate resources for a demand \(d\) have to be provided on all physical links included in the candidate path. Set \(D_{eks}\) treats links forming paths separately.

Having information about candidate paths and channels for each demand, it is possible to prepare new set of candidate demands for all frequency slices included in each spatial mode on each physical link respecting, that for each demand all resources have to be allocated all along a path in the same way. This new set is \(D'_{eks}\) and is determined in ([aqn:improveddeks]).

\[\label{aqn:deks}
\begin{split}
\forall_{e \in E} 
\forall_{k \in K} 
\forall_{s \in S} 
D_{eks} = 
\end{split}
\begin{cases}
    \emptyset,& \text{if } y_{neks} = 1\\
    
    \{ d \in D:
    r_d = 0 
    \land q_d = 0 
    \land m_d = 0 
    \land n = a_d + b_d \\
    \hspace{1.5cm} \land \sum_{p \in P_d} \delta_{epd} > 0 
    \land s+f_e(h_d) \leq |S| 
    \land \sum_{s' \in \left< s; s+f_e(h_d) \right>} y_{neks'} = 0 \\
    \hspace{1.5cm} \land \left(s > 1 \implies y_{nek(s-1)} = 0 \right) 
    \land \left( s+f_e(h_d) < |S| \implies y_{nek(s+1)} = 0 \right)
    
    \},              & \text{otherwise}
\end{cases}\]

<span>2</span>

\[\label{aqn:cd}
\begin{split}
c'_d = \{ (p, k, s) \in P_d \times K \times S : \forall_{e \in p} d \in D_{eks} \}
\end{split}\]

\[\label{aqn:improveddeks}
\begin{split}
D'_{eks} = \{ d \in D_{eks} : \exists_{p \in P_d} (p, k, s) \in c'_d \}
\end{split}\]

In this method we find resource with the least numerous set of candidate demands (but not empty). If we assign one demand to this resource, number of other demands that now can not use this resource is the smallest. If there are more than one resources with the least numerous set of candidate demands, they are ordered ascending by delay of demand with the smallest delay (\(l_d\)) included in each set, because demands with shortest delay affect the least of resources in subsequent iterations, and after ordering chosen is a first set. Let mark this set as \(D'_{e'k's'}\) and determine by ([aqn:smallestdeks]).

\[\label{aqn:smallestdeks}
\begin{split}
\forall_{e \in E} 
\forall_{k \in K} 
\forall_{s \in S} 0 < | D'_{e'k's'} | \leq | D'_{eks} | \\
\land \left( | D'_{e'k's'} | = | D'_{eks} | \implies \forall_{d \in D'_{eks}}\exists_{d' \in D'_{e'k's'}} l_d' \leq l_d \right) \\
\land | D'_{e'k's'} | > 0 \\
\land | D'_{eks} | > 0
\end{split}\]

After choosing this resource \(D'_{e'k's'}\), demand with smallest delay is indicated from set of candidate demands for this resource. Let the index of this demand be \(d'\) and is determined in ([aqn:shortestd]).

\[\label{aqn:shortestd}
\begin{split}
\forall_{d \in D'_{e'k's'}} l_{d'} \leq l_d
\end{split}\]

In this way first demand to allocate resources at given iteration \(n\) is chosen. There can be many candidate paths \(P'\) for this demand which includes physical link \(e'\) and resources determined by \(k'\) and \(s'\) ([aqn:conflictp]). In this case should be chosen this path \(p' \in P'\), which has the least effect on other candidate demands on resources on this path, what is precised in ([aqn:bestpath]) in two ways (recommended is the second one, because each demand in this way is counted only once).

\[\label{aqn:conflictp}
\begin{split}
P' = \{p \in P_{d'} : (p, k', s') \in c'_{d'} \land \delta_{e'pd'} = 1\}
\end{split}\]

\[\label{aqn:bestpath}
\begin{split}
\forall_{p \in P'} \sum_{e \in E} \left( \delta_{ep'd'} \cdot | D'_{ek's'}| \right) \leq \sum_{e \in E} \left( \delta_{epd'} \cdot | D'_{ek's'}| \right)
\\
or
\\
\forall_{p \in P'} \left| \bigcup_{e \in E : \delta_{ep'd'} = 1}  D'_{ek's'} \right| \leq \left| \bigcup_{e \in E : \delta_{epd'} = 1}  D'_{ek's'} \right|
\end{split}\]

Knowing path \(p'\), spatial mode \(k'\) and frequency slice \(s'\) is enough to allocate resources to demand \(d'\) ([aqn:allocating]).

\[\label{aqn:allocating}
\begin{split}
x_{d'p'} = 1 \\
c_{d'k's'} = 1 \\
\forall_{n' \in \left < a_{d'} + b_{d'}; a_{d'} + b_{d'}+ l_{d'} \right>} y_{n'e'k's'} = 1 \\
q_{d'} = 1
\end{split}\]

Next, all resources, that demand \(d'\) uses, should be found and their sets of candidate demands \(D_{eks}\) should be emptied. That operation is described in ([aqn:empting]). This demand should be also removed from all other sets \(D_{eks}\).

\[\label{aqn:empting}
\begin{split}
\forall_{d \in D : \delta_{ep'd'} = 1} D_{ek's'} := \emptyset \\
\forall_{d \in D : \delta_{ep'd'} = 0} D_{ek's'} := D_{ek's'} \setminus d'
\end{split}\]

After that operation, next demand should be found in the same way. Repeating steps ([aqn:cd] ) - ([aqn:empting]) as long as there are possibly found demands \(d'\).

The next step of this method is to use of assistive storage for unprocessed unrejected demands. Let mark a set of these demands as \(d'' \in D'' \subset D\). Each demand \(d''\) has no allocated recources, so \(q_{d''} = 0\) and at given \(n\)-th iteration is stored in a buffer or arrived at this iteration, so \(a_{d''} + b_{d''} = n\). We can describe set \(D''\) by ([aqn:buffer]).

\[\label{aqn:buffer}
\begin{split}
D'' = \{ d \in D : r_d + q_d + m_d = 0 \land a_{d''} + b_{d''} = n \}
\end{split}\]

Next, for each network node \(v\) it is checked if there are enough storage for demands arrived on this node. Set of stored or arrived at this iteration demands on node \(v\) is marked as \(D''_v \subset D''\) and is determined in ([aqn:nodebuffer]).

\[\label{aqn:nodebuffer}
\begin{split}
D''_v = \{ d \in D'' : a_d = v \}
\end{split}\]

Buffer on network node \(v\) can store at most \(B_v\) demands. If \(|D''_v| > B_v\), it is necessary to decide, which demands from \(D''_v\) should be rejected. In this method, way to do it is to reject \(B_v - |D''_v|\) demands \(d'' \in D''_v\) with the greatest value of delay \(l_d\). This procedure can be described as ([aqn:rejecting]).

\[\label{aqn:rejecting}
\begin{split}
\forall_{v \in V} \exists_{l_v \in \mathbb{N}} \left| \{ d \in D''v : l_d \geq l_v \} \right| = B_v - |D''_v| \\
\forall_{v \in V} \forall_{d \in D''_v : l_d \geq l_v} r_d = 1
\end{split}\]

For not rejected demand value of number of iterations that this demand is stored in a buffer is inceasing by 1: \(b_d := b_d + 1\).

Last step of this method is to release resources, which were used by demands that end processing in a given iteration \(n\). Set of these demands is marked by \(D'''\) and determined in ([aqn:ended]). Each demand from this set should be marked as completed by changing value of \(m_d\).

\[\label{aqn:ended}
\begin{split}
D''' = \{ d \in D : r_d = 0 \land a_d + b_d + l_d = n \} \\
\forall_{d \in D'''} m_d = 1
\end{split}\]

Demand \(d\) uses resources determined in variable \(y_{neks}\) at iterations \(a_d + b_d \leq n \leq a_d + b_d + l_d\). So in iteration \(n > a_d + b_d + l_d\) values of resources described by variable \(y_{neks}\) are not used by this demand \(d\).

Implementation note
-------------------

It is not necessary to store variable \(y_{neks}\) for all \(|N|\) iterations. In this method it is needed at \(n'\)-th iteration to know value of this variable for \(n\)-th iteration determined by: \(n' \leq n \leq n' + l_{max}\), where \(l_{max}\) is equal to number iterations of demand with the longest duration that is being processed in \(n'\)-th iteration. So, it is needed to store variable \(y_{neks}\) for only \(l_{max}\) iterations. This fact can avoid using too much program memory while implementing this method, because it is possible to reduce first dimension size from \(|N|\) to \(l_{max}\) by reindexing variable \(y_{neks}\) after each iteration like in ([aqn:reindexing]). After reindexing values of \(y_{(l_{max} + 1)eks}\) are unknown, but it can be calculated using dependence described in ([aqn:onechannel]). It is also needed to take into account that this number \(l_{max}\) will vary in subsequent iterations.

\[\label{aqn:reindexing}
\begin{split}
\forall_{n \in <1; l_{max}>} y_{neks} := y_{(n+1)eks}
\end{split}\]

Research plan and simulation program
====================================

In order to test the possibilities of the method proposed by us in the previous chapter, it is necessary to create a tool that will enable simulations.

Simulation program
------------------

Descibed method was implemented in created simulation program. We chose Python 3.9 with tool Numpy thanks to which we could easily store and manipulate data in arrays.

The program code has been posted in the public repository: <https://github.com/sewerus/Rouspaumcation>.

Data sets
---------

We also got a simulation data for traffics volumes from 100 E to 2000 E, 10 data sets for each traffic volume. The data covers 2000 iterations over a network with 16 nodes and 48 links. There are also 30 candidate paths between each two network nodes.

We can compare our results with the results of the SSA algorithm for 7 cores and 30 candidate paths between each two network nodes.

Computational complexity
------------------------

Each step of proposed method was implemented in main.py file. Unfortunately, with more requests coming in a given iteration or stored in assistive storage, the computation time is significantly longer. The size of the network (number of nodes, links and cores) and the number of candidate paths are also important.

The longest computation is for the value of \(D_{eks}\) described in ([aqn:deks]). This array is computed for each iteration and depends linearly on the number of links and cores, the number of demands and the number of candidate paths.

The second quantity that takes the longest time to compute is \(c_d'\) described in ([aqn:cd]). It is computed in each iteration as many times as the most allocable demand is searched for. The computation complexity depends linearly on the number of demands to check, the number of cores and the number of candidate paths.

Research plan
-------------

Conducting a simulation for a network with the same parameters as the one for which we have the results of the SSA algorithm, takes too much time and exceeds our capabilities.

We decided to run simulations for networks with much lower parameters. In our research, we limited the number of cores to 2, and we limited the number of candidate paths to 3. As a result, the time needed to perform a single simulation ranges from 1 hour to 25 hours depending on the traffic volume (from about 2 seconds per iteration to about 40 seconds per iteration).

Conducted research and results
==============================

The SSA algorithm for traffic volumes up to 1000 E did not report any rejected requests. The results may be different in a lower-performing network. We want to use our method to check whether any requests will be rejected without using assistive storage and how it will change with assistive storage of different sizes. We will perform this test for traffic volumes of 300 E, 400 E, 500 E and 600 E. Thanks to this comparison, we will see how the use of assistive storage affects the allocation of requests.

[charts]

[] [tab:results]

|<span> **Traffic**</span>|<span> **Test**</span>|<span> **\(|Pd|\)**</span>|<span> **\(|K|\)**</span>|<span> **Storage**</span>|<span> </span>|<span> </span>|<span> </span>|<span> </span>|<span> </span>|<span> </span>|<span> **DBP**</span>|<span> **BBP**</span>|
|:-----------------------:|:--------------------:|:------------------------:|:-----------------------:|:-----------------------:|:------------:|:------------:|:------------:|:------------:|:------------:|:------------:|:-------------------:|:-------------------:|
|<span> </span>|<span> </span>|<span> </span>|<span> </span>|<span> 0</span>|<span> 15107220</span>|<span> 14951401</span>|<span> 155819</span>|<span> 28976</span>|<span> 28688</span>|<span> 288</span>|<span> 0,0099</span>|<span> 0,0103</span>|
|<span> </span>|<span> </span>|<span> </span>|<span> </span>|<span> 10</span>|<span> 15107220</span>|<span> 14951401</span>|<span> 155819</span>|<span> 28976</span>|<span> 28688</span>|<span> 288</span>|<span> 0,0099</span>|<span> 0,0103</span>|
|||||<span> 30</span>|<span> 15107220</span>|<span> 14951401</span>|<span> 155819</span>|<span> 28976</span>|<span> 28688</span>|<span> 288</span>|<span> 0,0099</span>|<span> 0,0103</span>|
|<span> </span>|<span> </span>|<span> </span>|<span> </span>|<span> 0</span>|<span> 15104870</span>|<span> 14900784</span>|<span> 204086</span>|<span> 28976</span>|<span> 28594</span>|<span> 382</span>|<span> 0,0132</span>|<span> 0,0135</span>|
|||||<span> 10</span>|<span> 15104870</span>|<span> 14900784</span>|<span> 204086</span>|<span> 28976</span>|<span> 28594</span>|<span> 382</span>|<span> 0,0132</span>|<span> 0,0135</span>|
|<span> </span>|<span> </span>|<span> </span>|<span> </span>|<span> 0</span>|<span> 15097904</span>|<span> 14839532</span>|<span> 258372</span>|<span> 28976</span>|<span> 28491</span>|<span> 485</span>|<span> 0,0167</span>|<span> 0,0171</span>|
|||||<span> 10</span>|<span> 15097904</span>|<span> 14839532</span>|<span> 258372</span>|<span> 28976</span>|<span> 28491</span>|<span> 485</span>|<span> 0,0167</span>|<span> 0,0171</span>|
|<span> </span>|<span> </span>|<span> </span>|<span> </span>|<span> 0</span>|<span> 15098323</span>|<span> 1493859</span>|<span> 13604464</span>|<span> 28976</span>|<span> 28400</span>|<span> 576</span>|<span> 0,0199</span>|<span> 0,9011</span>|
|<span> </span>|<span> </span>|<span> </span>|<span> </span>|<span> 10</span>|<span> 15098323</span>|<span> 1493859</span>|<span> 13604464</span>|<span> 28976</span>|<span> 28400</span>|<span> 576</span>|<span> 0,0199</span>|<span> 0,9011</span>|
|||||<span> 20</span>|<span> 15098323</span>|<span> 1493859</span>|<span> 13604464</span>|<span> 28976</span>|<span> 28400</span>|<span> 576</span>|<span> 0,0199</span>|<span> 0,9011</span>|
|<span> </span>|<span> </span>|<span> </span>|<span> </span>|<span> 0</span>|<span> 15098139</span>|<span> 12442521</span>|<span> 2655618</span>|<span> 28976</span>|<span> 24991</span>|<span> 3985</span>|<span> 0,1375</span>|<span> 0,1759</span>|
|<span> </span>|<span> </span>|<span> </span>|<span> </span>|<span> 10</span>|<span> 15098139</span>|<span> 13660835</span>|<span> 1437304</span>|<span> 28976</span>|<span> 26721</span>|<span> 2255</span>|<span> 0,0778</span>|<span> 0,0952</span>|
|||||<span> 20</span>|<span> 15098139</span>|<span> 14006028</span>|<span> 1092111</span>|<span> 28976</span>|<span> 27210</span>|<span> 1766</span>|<span> 0,0609</span>|<span> 0,0723</span>|
|<span> </span>|<span> </span>|<span> </span>|<span> </span>|<span> 0</span>|<span> 15134248</span>|<span> 11203183</span>|<span> 3931065</span>|<span> 28976</span>|<span> 22937</span>|<span> 6039</span>|<span> 0,2084</span>|<span> 0,2597</span>|
|<span> </span>|<span> </span>|<span> </span>|<span> </span>|<span> 10</span>|<span> 15134248</span>|<span> 11258735</span>|<span> 3875513</span>|<span> 28976</span>|<span> 23007</span>|<span> 5969</span>|<span> 0,2060</span>|<span> 0,2561</span>|
|<span> </span>|<span> </span>|<span> </span>|<span> </span>|<span> 20</span>|<span> 15134248</span>|<span> 11258735</span>|<span> 3875513</span>|<span> 28976</span>|<span> 23007</span>|<span> 5969</span>|<span> 0,2060</span>|<span> 0,2561</span>|
|||||<span> 30</span>|<span> 15134248</span>|<span> 11258735</span>|<span> 3875513</span>|<span> 28976</span>|<span> 23007</span>|<span> 5969</span>|<span> 0,2060</span>|<span> 0,2561</span>|
|<span> 1500</span>|<span> 1</span>|<span> 3</span>|<span> 7</span>|<span> 0</span>|<span> 15170426</span>|<span> 34099</span>|<span> 15136327</span>|<span> 28976</span>|<span> 27475</span>|<span> 1501</span>|<span> 0,0518</span>|<span> 0,9978</span>|
|<span> </span>|<span> </span>|<span> </span>|<span> </span>|<span> 0</span>|<span> 30115206</span>|<span> 8217437</span>|<span> 21897769</span>|<span> 28976</span>|<span> 16278</span>|<span> 12698</span>|<span> 0,4382</span>|<span> 0,7271</span>|
|<span> </span>|<span> </span>|<span> </span>|<span> </span>|<span> 10</span>|<span> 30115206</span>|<span> 10881946</span>|<span> 19233260</span>|<span> 28976</span>|<span> 21506</span>|<span> 7470</span>|<span> 0,2578</span>|<span> 0,6387</span>|
|<span> </span>|<span> </span>|<span> </span>|<span> </span>|<span> 20</span>|<span> 30115206</span>|<span> 10844820</span>|<span> 19270386</span>|<span> 28976</span>|<span> 21550</span>|<span> 7426</span>|<span> 0,2563</span>|<span> 0,6399</span>|
|<span> </span>|<span> </span>|<span> </span>|<span> </span>|<span> 30</span>|<span> 30115206</span>|<span> 10851561</span>|<span> 19263645</span>|<span> 28976</span>|<span> 21664</span>|<span> 7312</span>|<span> 0,2523</span>|<span> 0,6397</span>|
|||||<span> 40</span>|<span> 30115206</span>|<span> 10801027</span>|<span> 19314179</span>|<span> 28976</span>|<span> 21645</span>|<span> 7331</span>|<span> 0,2530</span>|<span> 0,6413</span>|
|<span> </span>|<span> </span>|<span> </span>|<span> </span>|<span> 0</span>|<span> 15104625</span>|<span> 9157159</span>|<span> 5947466</span>|<span> 28976</span>|<span> 19466</span>|<span> 9510</span>|<span> 0,3282</span>|<span> 0,3938</span>|
|<span> </span>|<span> </span>|<span> </span>|<span> </span>|<span> 10</span>|<span> 15104625</span>|<span> 10313211</span>|<span> 4791414</span>|<span> 28976</span>|<span> 21263</span>|<span> 7713</span>|<span> 0,2662</span>|<span> 0,3172</span>|
|||||<span> 20</span>|<span> 15104625</span>|<span> 10760596</span>|<span> 4344029</span>|<span> 28976</span>|<span> 21919</span>|<span> 7057</span>|<span> 0,2435</span>|<span> 0,2876</span>|

<span>2</span>

We also want to check what the results will be for higher traffic volumes. We chose 1000 E, 1300 E, 1800 E and 2000 E. Similar simulations will be performed to check how the number of rejected demands changes depending on the size of assistive storage.

We also conducted only one test with 7 cores for traffic volume of 1500 E, but with only 3 candidate paths for each demand. Thanks to it we can see, what is the different between our results and SSA algorithm’s results, remembering about different number of candidate paths.

All the results of each simulation are shown in Table [tab:results] and Fig. [charts].

Conclusions
===========

The most important conclusion is that the designed method is not useful in real cases. The linear dependence of the calculation time on the network parameters allows only basic simulations to be made.

Other methods, such as linear programming, use matrix and number operations. Their computation times are much shorter. Our method requires searching resource and request sets, which greatly increases the number of instructions that the program has to execute.

Despite the few results obtained with our simulation program, we can draw conclusions regarding the use of assistive storage.

Based on the results obtained for low traffic:

-   if the number of rejected demands without the use of assistive storage is low, using assistive storage does not improve the results. This is evidenced by the results obtained for the traffic volumes of 300 E - 600 E.

Based on the results obtained for high traffic:

-   if the number of rejected demands without the use of assistive storage is high, the use of base assistive storage significantly reduces the number of rejected demands and reduces the DBP and BBP values. Further increasing the size of assistive storage only slightly improves the results. This is evidenced by the results obtained for the traffic volume of 1000 E, 1300 E and 1800 E,

-   using assistive storage increases the number of operations and the computation time. This is because there are more candidate demands to allocate resources.

Based on the results obtained for 7 cores:

-   the created method copes well with assigning resources to successive demands. The presented results are for networks with worse parameters. The result obtained for 1500 E rejected 1501 demands, and for the same data and the same network, but with 10 times more candidate paths, the SSA algorithm rejected 567 demands. We could not run the test for the 30 candidate paths as it would take 10 times longer.

