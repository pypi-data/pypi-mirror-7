 % keep observed variations
 :- obs_vlabel(E,X, S), vlabel(E,X,T),  S!=T.
 
 % keep observed variations
vlabel(E,V,-1) :- vertex(V), obs_vlabel(E,V,-1).
vlabel(E,V, 1) :- vertex(V), obs_vlabel(E,V, 1).
vlabel(E,V, 0) :- vertex(V), obs_vlabel(E,V, 0).

% A weak vertex variation has been observed
% 1{vlabel(E,V,-1), vlabel(E,V,0)}1 :- vertex(V), obs_vlabel(E,V,"not 1").
% 1{vlabel(E,V, 1), vlabel(E,V,0)}1 :- vertex(V), obs_vlabel(E,V,"not -1").

