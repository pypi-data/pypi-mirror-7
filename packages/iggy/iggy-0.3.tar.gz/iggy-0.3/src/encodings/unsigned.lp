% input facts
% obs_vlabel(Experiment, Vertex , Sign)
% edge(X,Y)
% obs_elabel(X,Y,Sign).
% vertex(Name)

exp(E) :- obs_vlabel(E,V,S).
exp(E) :- input(E,V).
vertex(V) :- obs_vlabel(E,V,S).
edge(X,Y) :- obs_elabel(X,Y,S).
vertex(X) :- edge(X,Y).
vertex(Y) :- edge(X,Y).

input(E,V):- exp(E), input(V).

% for this encoding all variations and all influences are unsigned

% for each vertex the measurements are either changing or not 
1{vlabel(V,0), vlabel(V,1)}1 :- vertex(V).

% A vertex variation has been observed
vlabel(V,1) :- vertex(V), obs_vlabel(X, V,-1).
vlabel(V,1) :- vertex(V), obs_vlabel(X, V, 1).
vlabel(V,0) :- vertex(V), obs_vlabel(X, V, 0).


% every variation change must be explained.

explained(V) :- input(V).
explained(V) :- edge(X,V), vlabel(X,1).

:- vlabel(V,1), not explained(V), not input(V).




#hide.

#show vlabel(X,1).
%#minimize[vlabel(X,1), not false].

