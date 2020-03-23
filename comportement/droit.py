from brian2 import *
import math
start_scope()

# =============================================================================
# 1.setting up differential equations 
# 2.N should be odd which including the total number of central neuron and 
#   attached neuron of individual leg， in this case N = 6(hexapod) + 1(central neuron)
# 3.We particularly distinguish the odd and even stage by imposing different 
#   initial values. Here for the odd is 0.1 and even is 0
# =============================================================================
N = 7
eqs = '''
dv/dt = (2-v)/tau : 1 (unless refractory)
tau : second
ref : second
'''
v_reset_even = 0
v_reset_odd = 0.1
# =============================================================================
# setting up neuron group, driving currents, time scales and refractory
# =============================================================================
G = NeuronGroup(N,eqs,threshold='v>1', reset='v = 0',refractory = 'ref', method='exact')
# les pattes ne commencent pas en meme temps
for i in range(0, N-1):
    if i % 2 == 0:
        G.v[i] = v_reset_even
    else:
        G.v[i] = v_reset_odd
        
taulist = [50]*N
G.tau = taulist*ms

#le derniere neurone est le controleur contral
#il n'aura qu'une seule pique donc on lui associe une valeur de refractory tres grande 
reflist = [0]*N
reflist[N-1] = 100000
G.ref = reflist*ms

S = Synapses(G,G,'w : 1', pre='v_post += w')

#configuration:
#   6
#  | |
# |   |
#0-----3
#|     |
#|     |
#1-----4
#|     |
#|     |
#2-----5

#poid0 initial weight imposed by central neuron
#poid1 positive weight after initial stage
#poid2 negative weight after initial stage
poid0 = 0.1
poid1 = 0.1
poid2 = -0.1

# =============================================================================
# connect the central neuron to all neurons
# =============================================================================
list = range(N)
S.connect(i=N-1,j=list[0:N-1])
for i in range(0,N-1):
    S.w[N-1,i] = poid0

# =============================================================================
# 1.connecting all pairs of neuros i to j in condition that i different from j
# 2.setting up the weight of each pair
# =============================================================================
S.connect(condition='i!=j and i!=N and j!=N')
for i in range(0,N-1):
    for j in range(0,N-1):
        if i!=j:
            if (i+j)%2==0:
                S.w[i,j]=poid1
            else:
                S.w[i,j]=poid2
                
# =============================================================================
# tracing the performance of each neuron and comparing the result
# =============================================================================
State = StateMonitor(G, 'v', record=True)
run(2000*ms)

# On peut voir que les neurones d'indices inpaires sont bien decale de 50% avec les neurones d'indices paires.
# Les neurones de meme parite ont le meme pas de decharge.
figure(figsize=(26,4))
for x in range(0,N-1):
    plot(State.t/ms,State.v[x]+(x))
   

