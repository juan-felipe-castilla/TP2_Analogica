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
Ro  = 75/10;
Rl  = 8;
hie1 = 3443.6;
hie2 = 34.095;
hie3 = 2357.3;
hie4 = 310.53;
hie5 = 3.1053;
Rbb  = (R1e*R2e)/(R1e+R2e);
Rbbn = (R1s*R2s)/(R1s+R2s);
Bn = 100;
Bp = 100;

Vi = 1; % Tensión de entrada fijada a 1V

% Matriz G (7x7) y vector independiente B (7x1)
G = zeros(7, 7);
B = zeros(7, 1);

% Nodo N002 (Fila 1)
G(1,1) = (1 - Bn)/hie1 + 1/hie2;
G(1,2) = -1/hie2;

% Nodo N003 (Fila 2)
G(2,1) = -(1 + Bn)/hie2;
G(2,2) = (1 + Bn)/hie2 + 1/Red + 1/Rbb + 1/hie3;

% Nodo N004 (Fila 3)
G(3,3) = 1/Rcb;
G(3,4) = -1/Rcb;
G(3,5) = -Bn/hie4;
G(3,6) = Bn/hie4;

% Nodo N005 (Fila 4)
G(4,3) = -1/Rcb;
G(4,4) = 1/Rcb + 1/hie5;

% Nodo N006 (Fila 5)
G(5,2) = -Bn/hie3;
G(5,5) = 1/Rce + 1/Rbbn + 1/hie4;
G(5,6) = -1/hie4;

% Nodo N007 (Fila 6)
G(6,4) = Bp/hie5;
G(6,5) = -(1 - Bn)/hie4;
G(6,6) = (1 - Bn)/hie4 + 1/Res + 1/Ro;
G(6,7) = -1/Ro;

% Nodo N008 (Fila 7)
G(7,6) = -1/Ro;
G(7,7) = 1/Ro + 1/Rl;

% Excitación
B(1) = (1 - Bn)/hie1;

% Resolución
V = G \ (B * Vi);

% --- Cálculo de la Ganancia ---
Vo = V(7);                % Tensión en el nodo N006
Av = Vo / Vi;             % Ganancia lineal
Av_dB = 20 * log10(abs(Av)); % Ganancia en dB

% --- Mostrar Resultados ---
fprintf('Tensión de salida Vo: %f V\n', Vo);
fprintf('Ganancia de tension (Av = Vo/Vi): %f\n', Av);
fprintf('Ganancia de tension en dB (Av_dB): %f dB\n', Av_dB);
