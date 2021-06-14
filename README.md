# Rouspaumcation

Simulation program designed to solve problem of dynamic routing, space and spectrum allocation (RSSA) of unicast demands in flex-grid network with assistive sotrage.

Needed data set:
- .net file with network dimensions: number of nodes, links and adjacent matrix,
- .pat file with k candidate paths (k can be set up in code),
- .spec file with number of slices needed for each path in .pat file,
- .dem files with demands (income iteration, source, target, bitrate and duration).

# Project

The aim of the project is to propose new created method to solve RSSA problem (Dynamic Routing Space and Spectrum Allocation) with assistive storage. The method consists in creating candidate demand sets for each spectrally-spatially resources and selecting those demands that limit available resources for the fewest other demands. It has been described in detail through the criteria for creating such sets, and a simulation program has been implemented to test it for different traffic volumes. This gives the opportunity to measure how beneficial it is to use assistive storage in various cases.

## Introduction

Many observations show that Internet traffic is growing faster and faster. The introducing technologies will bring about many changes. A good example is 5G technology, which in 2023 will reach speeds around 13 times faster than mobile traffic in 2018 [1].

The technology that can cope with such an increase in network bandwidth demand is concept of spectrally-spatially flexible optical networks (SS-FONs). It implements space division multiplexing (SDM) [2] with elastic optical networks (EON), what brings benefits like enormous increase in transmission capacity [3, 4]. It is also opportunity to manage network resource in more flexible way.

It works by discretization the optical spectrum in frequency slots (FSs) of 12.5 GHz width [5]. By concatenating multiple adjacent Sub-Channels (Sb-Chs) it is possible to form Super-Channel (SCh) that enables ultra-high bit-rate transmissions [6, 7].

According to [1], the global average broadband speed is growing, from 45.9 Mbps in 2018 to 110.4 Mbps in 2023. This is one of the key indicators of increased IP traffic. This raises the need to find better methods of planning unicast traffic using existing infrastructure. The attempt to meet these requirements is working on dynamic routing, spectrum and space allocation (RSSA) problem. The aim is to find for each request a routing path, spatial cores and optical channel. It is also possible to determine a modulation level and handle with routing, modulation level, space and spectrum allocation (RMLSSA) [8], but in this paper modulation level is pre-determined. Many publication consider also routing and spectrum allocation (RSA) problem. 

RSSA problem is to find a lightpath in SS-FONs scenario, what requires to focus on spectrum and space allocation in the same time for incoming requests. There are many ways to solve this problem, what we present in the next chapters. We want to create new method basing on probability of using a specific resource of space and spectrum for unicast requests. In this paper we want to describe proposed algorithm and present its implementation. Next we want to conduct research and compare results with results obtained by the SSA algorithm.

## Related works

The subject of this article is quite a new field of Internet traffic engineering. Nevertheless, many works have been prepared proposing various approaches to the problem of allocation of the discussed resourches.

In many works RSSA problem is studied with using integer linear programming (ILP) [4, 7, 9, 10] Formulating this problem as ILP model provides to solve optimization problem with decision variables. Hovewer, this technique is low scalability. Mathematical programming (MP) methods for larger instances of complex problems don't provide results in a reasonable time [3].

Another way is using heuristic or metaheuristic algorithms, which are faster, but not always reach optimal solution of a problem.

Fixed-Alternate routing and First-Fit frequency assignment (FA-FF) algorithm is proposed in [11]. In [7] authors propose effective heuristic method called Adaptive Frequency Assignment - Collision Avoidance (AFA-CA). In this method the main aim is to select the sequence of processed demands in order to minimize the spectrum use. In [12] authors propose two algorithms solving RSSA-DPP (Dedicated Path Protection) problem using evolutionary algorithm and tabu search. Three different heuristic algorithms called spectrum waste base (SWB) algorithm, intentional spectrum waste with sequential approach (ISW-S) algorithm and intentional spectrum waste with accumulative approach (ISW-A) are proposed in [8] using spectrum waste metric. Another heuristic is developed in [13], basing on the greedy randomized adaptive search procedure authors propose GRASP metaheuristic approach. They also propose adaptive search procedure (SA) to solve larger instances of the RSSA problem. In [14] authors propose another algorithm using greedy heuristic. Another algorithms are: a variable-group-base (MVG) algorithm [15], a minimum-block-generated flexible-grouping-based (MBFG) spectrum assignment algorithm [16] and an SLA-provisioning algorithm (SADQ) that employs multilevel differentiation to provision the proposed service level agreement (SLA) parameters [17].

The last way to solve discussed problem is to use the techniques of artificial intelligence (AI). In [18] described is using AI in optical networks, what can improve the configuration and operation of network devices, optical performance monitoring and quality of transmission (QoT) estimation. AI systems gives opportunities for automating operations and introducing intelligence decisions by planning use and management of network resources.

## Problem definition

In this section we want to present a way to describe RSSA problem as a mathematical model. There are two cases: static network parameters and variables of resources that are used by incoming demands.

Static network parameters refers to network dimensions. The SS-FON can be modeled as a directed graph $G = (V, E)$, where $V$ is a set of network nodes, $E$ is a set of directed physical network links. On each link there is a set of available spatial modes $K$ and on each mode there is a set of frequency slices $S$. Channel in such a flex-grid SDM network is a set of adjacent slices on the same fiber mode.

For each pair of two network nodes $(v_i, v_j)$ there is a set of candidate routing paths $P_{ij}$. Constant $\delta_{epij}$ is equal to $1$ if a link $e$ is a part of a candidate path $p$ between nodes $v_i$ and $v_j$. Otherwise $\delta_{epij}$ is equal to $0$.

To describe the occurrence of incoming requests, we will treat time as successive iterations $n = 1, 2, ..., N$. Each demand from set $D$ is described by its iteration of arrival $a_d$, source node $s_d$, destination node $t_d$, bit-rate $h_d$ (in Gbps) and duration $l_d$ (number of iterations). On the basis of made determinations, there is a set of candidate paths for the each request $d$ described as $P_d = P_{s_d t_d}$ and constant $\delta_{epd} = \delta_{ep s_d t_d}$.

For each link $e$ there is a function $f_e(h)$, which returns number of needed frequency slices for a given bit-rate $h$ in Gbps. For each network node $v$ there is a buffer that is limited by the maximum number of requests $B_v$ it can remember.

The solution of the problem is to determine how long each request should be stored in a buffer, through which routing path should be sent and which spectrally-spatially resources should be used.

If demand $d$ after its arrival iteration $a_d$ is not stored in its source node buffer but starts to be processed immediately, then $b_d = 0$. Otherwise $b_d$ is equal to number of iterations, that demand $d$ is stored in this buffer. That means, that each demand $d$ begins to be processed in iteration $a_d + b_d$ and ends to be processed at iteration $a_d + b_d + l_d$. If demand $d$ is rejected from a buffer without processing, then $r_d = 1$, otherwise $r_d = 0$. At each iteration number of stored demands in buffer on node $v$ can not be greater than $B_v$. This constraint is defined in (\@ref(eq:buffer)).

When demand $d$ starts to be processed, the routing path is selected and free resources are allocated. In this paper we consider non-bifurcated flows. If for demand $d$ chosen is path $p \in P_d$, then $x_{dp} = 1$, otherwise $x_{dp} = 0$. This constraint is defined in (\@ref(eq:onepath)). On mentioned path $p$ allocated resources form a channel with adjacent slices on selected fiber mode. This channel is determined by variable $c_{dks}$, which is equal to 1 if demand $d$ uses fiber mode $k$ and adjacent frequency slices beginning with slice $s$, otherwise $c_{dks} = 0$. Constraint about allocation slices on only one mode is defined in (\@ref(eq:onemode)).

On given network link $e$ if there is demand $d$ that uses channel formed by spatial mode $k$ and adjacent slices beginning with slice $s$, then all slices from $s$ to $s + f_e(h_d) + 1$ are used, because $f_e(h_d)$ is equal to number of slices needed for demand $d$ basing on its bit-rate. There is one additional slice because of guard-band. That means, if on that link $e$ and mode $k$ demand $d$ uses slice $s$, there is slice $s' \in \left< s-\left( f_e(h_d) + 1 \right); s \right>$ which is beginning of formed channel for this demand, so $\sum_{s' \in \left< s-\left( f_e(h_d) + 1 \right); s \right>} c_{dks'} = 1$.

### Nomenclature
#### Sets and indices
$v \in V$ : Network nodes
$e \in E$ : Network physical links
$k \in K$ : Spatial modes of a single link
$s \in S$ : Frequency slices of a single mode
$p \in P_{ij}$ : Candidate routing paths between $v_i$ and $v_j$
$n \in N$ : Iterations
$d \in D$ : Demands
$p \in P_d$ : Candidate paths for demand $d$

#### Constants and functions
$s_d$ : Source node of demand $d$
$t_d$ : Target node of demand $d$
$h_d$ : Bit-rate in Gbps of demand $d$
$a_d$ : Iteration of demand $d$ arrival
$l_d$ : Duration of demand $d$ (number of iterations)
$\delta_{epij}$ : $=1$ if $\exists_{ p \in P_{ij}} e \in p$; $0$, otherwise
$\delta_{epd}$ : $=1$ if $\exists_{ p \in P_d} e \in p$; $0$, otherwise
$B_v$ : Number of demands that can be stored in assistive storage on node $v$
$f_e(h)$ : Function that returns number of needed slices for bit-rate $h$ on a link $e$

#### Variables
$r_d$ : $=1$ if demand $d$ is rejected; $0$, otherwise
$b_d$ : Number of iteration that demand $d$ is stored in its source buffer
$x_{dp}$ : $=1$ if for demand $d$ chosen is path $p \in P_d$'; $0$, otherwise
$c_{dks}$ : $=1$ if demand $d$ uses fiber mode $k$ and frequency slices beginning with slice $s$; $0$, otherwise
$y_{neks}$ : $=1$ if at iteration $n$ on physical link $e$ frequency slice $s$ on  mode $k$ is in use; $0$, otherwise; auxiliary variable

Variable $c_{dks}$ is related to auxiliary variable $y_{neks}$, which is equal to 1 if at iteration $n$ on physical link $e$ frequency slice $s$ on spatial mode $k$ is in use, otherwise $y_{neks} = 0$. At each iteration single frequency slice can be allocated to only one channel for only one demand, what is defined in (\@ref(eq:onechannel)).

The aim of the considered optimization problem is to allocate as much demands as it is possible. Objective functions we want to minimize are demand blocking probability (DBP) defined in (\@ref(eq:dbp)) and bit-rate blocking probability (BBP) defined in (\@ref(eq:bpp)).

$$
\begin{equation}
\begin{split}
\forall_{n \in N} \forall_{v \in V} \vert \{ d \in D: s_d = v \land b_d > 0 \\
\land a_d + b_d = n \land r_d = 0 \} \vert \leq B_v
\end{split}
(\#eq:buffer)
\end{equation}
$$

$$
\begin{equation}
\forall_{d \in D} \sum_{p \in P_d} x_{pd} = 1
(\#eq:onepath)
\end{equation}
$$

$$
\begin{equation}
\forall_{d \in D} \exists!_{k \in K} \sum_{s \in S} c_{dks} = 1
(\#eq:onemode)
\end{equation}
$$

$$
\begin{equation}
\begin{split}
\forall_{n \in N} \forall_{e \in E} \forall_{k \in K} \forall_{s \in S} y_{neks} = \vert \{ d \in D : \\
r_d = 0 \\
\land a_d + b_d \leq n \leq a_d + b_d + l_d \\
\land \left( \exists!_{p \in P_d} x_{pd} = 1 \land \delta_{epd} = 1 \right) \\
\land \sum_{s' \in \left< s-\left( f_e(h_d) + 1 \right); s \right>} c_{dks'} = 1 \} \vert \\
\in \{0, 1\}
\end{split}
(\#eq:onechannel)
\end{equation}
$$

$$
\begin{equation}
BBP = \frac{\sum_{d \in D} r_d \cdot h_d}{\sum_{d \in D} h_d}
(\#eq:bpp)
\end{equation}
$$

$$
\begin{equation}
DBP = \frac{\sum_{d \in D} r_d}{|D|}
(\#eq:dbp)
\end{equation}
$$


## References
[1]: CISCO, “Cisco Annual Internet Report (2018-2023) White Paper,”CISCO, Tech. Rep., 2020.
[2]: W. KmiecikandK.Walkowiak,“A performance study of dynamic routing algorithm for sdm translucent optical networks with assistive storage,”Optical Switching and Networking,vol. 38, p. 100572, 2020. [Online]. Available: http://www.sciencedirect.com/science/article/pii/S157342771930150X
[3]: M. Klinkowski,P. Lechowicz, and K. Walkowiak, “Survey of resource allocation schemes and algorithms in spectrally-spatially flexible optical networking,”Optical Switching and Networking, vol. 27, pp. 58 – 78, 2018. [Online]. Available: http://www.sciencedirect.com/science/article/pii/S157342771730053X
[4]: B. Chatterjee, N. Sarma, and E. Oki, “Routing and spectrum allocationin elastic optical networks: A tutorial, ”IEEE Communications Surveysamp Tutorials, vol. 17, pp. 1776–1800, 07 2015.
[5]: International Telecommunication Union - ITU-T, “G.694.1 (02/2012), spectral grids for WDM applications: DWDM frequency grid,” Tech. Rep., 2012.
[6]: R. Rumipamba-Zambrano, F.-J. Moreno-Muro, J. Perelló, P. Pavón-Mariño, S. Spadaro, “Space continuity constraint in dynamic flex-grid/sdm optical core networks: An evaluation withspatial and spectral super-channels, ”Computer Communications,vol. 126, pp. 38–49, 2018. [Online]. Available: http://www.sciencedirect.com/science/article/pii/S0140366417310162
[7]: M. Klinkowski and K. Walkowiak, “Routing and spectrum assignment in spectrum sliced elastic optical path network, ”IEEE Communications Letters, vol. 15, pp. 884–886, 08 2011.
[8]: A. Ghadesi, A. Ghaffarpour Rahbar, M. Yaghubi-Namaad, and A. Abi, “Intentional spectrum waste to reduce blocking probability in space division multiplexed elastic optical networks, ”Optical Fiber Technology, vol. 52, p. 101968, 2019. [Online]. Available: http://www.sciencedirect.com/science/article/pii/S1068520019301051
[9]: R. Goścień and P. Lechowicz, “On the complexity of RSSA of anycast demands in spectrally-spatially flexible optical networks,” in INOC, 2019.
[10]: D. T. Hai, “On routing, spectrum and network coding assignment problem for transparent flex-grid optical networks with dedicated protection, ”Computer Communications, vol. 147, pp. 198 – 208, 2019. [Online]. Available: http://www.sciencedirect.com/science/article/pii/S0140366418306546
[11]: M. Jinno, B. Kozicki, H. Takara, A. Watanabe, Y. Sone, T. Tanaka, and A. Hirano, “Distance-adaptive spectrum resource allocation in spectrum-sliced elastic optical path network [topics in optical communications], ”IEEE Communications Magazine, vol. 48, no. 8, pp. 138–145, 2010.
[12]: M. W. Przewozniczek, R. Goścień, P. Lechowicz, and K. Walkowiak, “Metaheuristic algorithms with solution encoding mixing for effective optimization of sdm optical networks, ”Engineering Applications of Artificial Intelligence, vol. 95, p. 103843, 2020. [Online]. Available: http://www.sciencedirect.com/science/article/pii/S0952197620302074
[13]: P. Lechowicz, K. Walkowiak, and M. Klinkowski, “Greedy randomized adaptive search procedure for joint optimization of unicast and anycast traffic in spectrally-spatially flexible optical networks, ”Computer Networks, vol. 146, pp. 167 – 182, 2018. [Online]. Available: http://www.sciencedirect.com/science/article/pii/S1389128618308995
[14]: R. Rumipamba-Zambrano, J. Perell ́o, J. M. Gen ́e, and S. Spadaro, “On the scalability of dynamic flex-grid/sdm optical core networks, ”Computer Networks, vol. 142, pp. 208 – 222, 2018. [Online]. Available: http://www.sciencedirect.com/science/article/pii/S1389128618303712
[15]: Y. Qiu, “An efficient spectrum assignment algorithm based on variable-grouping mechanism for flex-grid optical networks, ”Optical Switching and Networking, vol. 24, pp. 39 – 46, 2017. [Online]. Available: http://www.sciencedirect.com/science/article/pii/S1573427716300467
[16]: Y. Qiu and J. Xu, “Minimum-block-generated flexible-grouping-based spectrum assignment for flex-grid optical networks, ”Optical Fiber Technology, vol. 38, pp. 51 – 60, 2017. [Online]. Available: http://www.sciencedirect.com/science/article/pii/S1068520017302572
[17]: A. Agrawal, U. Vyas, V. Bhatia, and S. Prakash, “Sla-aware differentiated qos in elastic optical networks, ”Optical FiberTechnology, vol. 36, pp. 41 – 50, 2017. [Online]. Available: http://www.sciencedirect.com/science/article/pii/S1068520017300536
[18]: J. Mata, I. de Miguel, R. J. Dur ́an, N. Merayo, S. K. Singh, A. Jukan, and M. Chamania, “Artificial intelligence (ai) methods in optical networks: A comprehensive survey, ”Optical Switchingand Networking, vol. 28, pp. 43 – 57, 2018. [Online]. Available: http://www.sciencedirect.com/science/article/pii/S157342771730231X
