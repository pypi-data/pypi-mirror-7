pred_plus(E,X) :- vlabel(E,X,1), not obs_vlabel(E,X,S2): sign(S2): exp(E). 
pred_minus(E,X) :- vlabel(E,X,-1), not obs_vlabel(E,X,S2): sign(S2): exp(E). 
pred_nochange(E,X) :- vlabel(E,X,0), not obs_vlabel(E,X,S2): sign(S2): exp(E). 

% further rules for predicting signs

pred_not_plus(E,V):- vlabel(E,V, 0), not obs_vlabel(E,V,S2): sign(S2): exp(E). 
pred_not_plus(E,V):- vlabel(E,V, -1), not obs_vlabel(E,V,S2): sign(S2): exp(E). 

pred_not_minus(E,V):- vlabel(E,V, 0), not obs_vlabel(E,V,S2): sign(S2): exp(E). 
pred_not_minus(E,V):- vlabel(E,V, 1), not obs_vlabel(E,V,S2): sign(S2): exp(E).
 
pred_change(E,V):- vlabel(E,V, 1), not obs_vlabel(E,V,S2): sign(S2): exp(E).
pred_change(E,V):- vlabel(E,V, -1), not obs_vlabel(E,V,S2): sign(S2): exp(E). 
 
#show pred_plus/2.
#show pred_minus/2.
#show pred_nochange/2.
#show pred_not_plus/2.
#show pred_not_minus/2.
#show pred_change/2.