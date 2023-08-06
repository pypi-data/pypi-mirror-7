% input facts
% obs_vlabel(Experiment, Vertex , Sign)
% edge(X,Y)
% obs_elabel(X,Y,Sign).
% vertex(Name)

sign(1;-1;0).
obs(1;-1;0;notPlus;notMinus).
exp(E) :- obs_vlabel(E,V,S).
exp(E) :- input(E,V).
vertex(V) :- obs_vlabel(E,V,S).
edge(X,Y) :- obs_elabel(X,Y,S).
vertex(X) :- edge(X,Y).
vertex(Y) :- edge(X,Y).


{ active(V) } :- vertex(V).

% for each vertex the measurements are either changing (1,-1) or not (0)
1 {vlabel(E,V,1), vlabel(E,V,-1), vlabel(E,V,0)} 1 :- active(V), vertex(V), exp(E).
 infl(E,V,S*T) :- elabel(U,V,S), vlabel(E,U,T) active(U), active(V).
 
bot :- active(V), vlabel(E,V, 1), not infl(E,V,1),  not input(E,V).
bot :- active(V), vlabel(E,V,-1), not infl(E,V,-1), not input(E,V).

:- not bot.

#minimize{not false, active(V)}.