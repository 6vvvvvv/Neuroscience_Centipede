from brian2 import *
import math
start_scope()
# ==================================================================================
# 1.setting up differential equations 
# 2.N should be pair which including the total number of central neuron and 
#   attached neuron of individual leg and the sensor, in this case N = 6(hexapod)
# + 1(central neuron) + 1(sensor)
# 3.We particularly distinguish the odd and even stage by imposing different 
#   initial values. Here for the odd is 0.1 and even is 0(excluding last 2 neurons)
# 4. In order to simplify the code, we only simulated the case which the sensor is 
# placed at the front left(connected to neuron 0) so that the hexapod will turn
# right when the sensor detects an obstacle in front of it. The other simulations
# of part 2 has the same idea, what we should do is to change the connection 
# between neuron 7 and other neurons so that the hexapod would perform mouvements
# in others directions. 
# ==================================================================================    
N = 8
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
for i in range(0, N-2):
    if i % 2 == 0:
        G.v[i] = v_reset_even
    else:
        G.v[i] = v_reset_odd
G.v[N-1] = -5 #parametre pour le capteur

taulist = [50]*N
taulist[N-1] = 200 #parametre pour le capteur
G.tau = taulist*ms

reflist = [0]*N
reflist[N-2] = 100000
reflist[N-1] = 100000 #parametre pour le capteur
G.ref = reflist*ms

S = Synapses(G,G,'w : 1', pre='v_post += w')

#configuration:
#          6
#         | |
#        |   |
# 7-----0-----3
#       |     |
#       |     |
#       1-----4
#       |     |
#       |     |
#       2-----5

#poid0 initial weight imposed by central neuron
#poid1 positive weight after initial stage
#poid2 negative weight after initial stage
#poid3 positive weight imposed by sensor
poid0 = 0.1
poid1 = 0.1
poid2 = -0.1
poid3 = 0.5

# =============================================================================
# connect the central neuron to all neurons
# =============================================================================
list = range(N)
S.connect(i=N-2,j=list[0:N-2])
for i in range(0,N-2):
    S.w[N-2,i] = poid0
    
# =============================================================================
# connect the sensor to neuron 0
# =============================================================================
S.connect(i=N-1,j=0)

# =============================================================================
# 1.connecting all pairs of neuros i to j in condition that i different from j
# 2.setting up the weight of each pair
# =============================================================================
S.connect(condition='i!=j and i<N-1 and j<N-1')
for i in range(0,N-2):
    for j in range(0,N-2):
        if i!=j:
            if (i+j)%2==0:
                S.w[i,j]=poid1
            else:
                S.w[i,j]=poid2
# Set up weight betwen sensor and neuron 0                
S.w[N-1,0] = 0.5
# =============================================================================
# tracing the performance of each neuron and comparing the result
# =============================================================================
State = StateMonitor(G, 'v', record=True)
run(1000*ms)
figure(figsize=(26,4))

# La detection d'un obstacle est simule par le neurone 7, qui se presente par la
# ligne rose dans le figure, quand il se decharge(t=380ms), on peut observer que
# le neurone 0(ligne bleue) recoit une excitation et decharge plus vite, qui va
# conduire l'hexapod de trouner vers la droite
for x in range(0,N):
    if x!=(N-2):
        plot(State.t/ms,State.v[x]+(x))
   



