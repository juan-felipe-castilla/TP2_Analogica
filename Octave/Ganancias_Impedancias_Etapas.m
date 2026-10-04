clear all; close all; clc

% --- Parámetros del Circuito ---
Rbd = 1000000;
Red = 47;
R1e = 120000;
R2e = 27000;
Rce = 6800;
Ree = 1200;
R1s = 47000;
R2s = 100000;
Res = 10;
Rcb = 100;
Ro  = 7.5;
Rl  = 8;
hie1 = 3478.1;
hie2 = 34.436;
hie3 = 2380.9;
hie4 = 313.64;
hie5 = 3.1364;
Rbb  = (R1e*R2e)/(R1e+R2e);
Rbbn = (R1s*R2s)/(R1s+R2s);
Bn = 100;
Bp = 100;

% Amplificador Darlington

vi1 = 1;

G1 = [ (1 - Bn)/hie1 + 1/hie2,  -1/hie2;
      -(1 + Bn)/hie2,           (1 + Bn)/hie2 + 1/Red];

B1 = [(1 - Bn)/hie1;
      0];

V1 = G1 \ (B1 * vi1);
v_N002 = V1(1);
v_N005 = V1(2);
disp('Ganancia Darlington');
Av1 = v_N005 / vi1
disp('');
disp(' Impedancia' );
ZinD = 1/(1/Rbd + 1/((hie1+(Bn+1)*(hie2+(Bn+1)*Red))))
ZoutD = 1/(1/Red + 1/(hie2/(Bn+1) + (Rbd+hie1)/(Bn+1)^2))

% Amplificador Emisor Común

vi2 = 1;

G2 = 1 / Rce;
B2 = Bn / hie3;

V2_sol = G2 \ (B2 * vi2);
v_N004 = V2_sol;
disp('');
disp('Ganancia Emisor Común');
Av2 = v_N004 / vi2
disp('');
disp(' Impedancia' );
ZinEC = 1/(1/Rbb + 1/hie3)
ZoutEC = Rce

% Amplificador Sziklai

vi3 = 1;

G3 = [ 1/Rcb, -1/Rcb,          Bn/hie4,                     0;
      -1/Rcb,  1/Rcb + 1/hie5,  0,                        0;
       0,     -Bp/hie5,        (1 - Bn)/hie4 + 1/Res + 1/Ro, -1/Ro;
       0,      0,              -1/Ro,                     1/Ro + 1/Rl];

B3 = [Bn/hie4;
      0;
      (1 - Bn)/hie4;
      0];

V3 = G3 \ B3;
v_N006 = V3(1);
v_N007 = V3(2);
v_N009 = V3(3);
v_N010 = V3(4);
disp('');
disp('Ganancia Sziklai');
Av3 = v_N010 / vi3
disp('');
disp(' Impedancia' );
Req1 = (Bn+1)*(Bp+1)*(1/(1/Res+1/(Ro+Rl)));
ZinS = 1/(1/Rbbn + 1/(hie4+Req1))
Req2 = (hie4+Rbbn)/((Bn+1)*(Bp+1));
ZoutS = (1/(1/Res + 1/Req2)) + Ro



