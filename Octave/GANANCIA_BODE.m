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
hie2 = 34.0;
hie3 = 2357.3;
hie4 = 310.53;
hie5 = 3.1053;
Rbb  = (R1e*R2e)/(R1e+R2e);
Rbbn = (R1s*R2s)/(R1s+R2s);
Bn = 100;
Bp = 100;

##% --- Capacitores ---
##C1 = 10e-6;
##C2 = 33e-6 * (B + 1);
##C3 = 10e-6;
##C4 = 10e-6;
##C5 = 10e-6;
##
##% --- Configuración del Análisis en Frecuencia ---
##f = logspace(1, 5, 2000); % Frecuencia desde 1 Hz hasta 1 MHz (ajustar si es necesario)
##w = 2 * pi * f;
##H = zeros(1, length(f));  % Vector para guardar la respuesta de salida
##Vi = 1;                   % Voltaje de entrada normalizado a 1V
##
##% --- Resolución Matricial Y * V = J ---
##for k = 1:length(f)
##    s = 1i * w(k);
##
##    Y = zeros(11, 11);
##    J = zeros(11, 1);
##
##    % Nota sobre los índices de la matriz:
##    % Índices 1 al 11 corresponden a los nodos V2 al V12 respectivamente.
##
##    % Nodo 2 (índice 1)
##    Y(1, 1) = s*C1 + 1/Rbd + 1/hie1;
##    Y(1, 2) = -1/hie1;
##    J(1) = Vi * s * C1;
##
##    % Nodo 3 (índice 2)
##    Y(2, 1) = -(1-B)/hie1;
##    Y(2, 2) = (1-B)/hie1 + 1/hie2;
##    Y(2, 3) = -1/hie2;
##
##    % Nodo 4 (índice 3)
##    Y(3, 2) = -(1+B)/hie2;
##    Y(3, 3) = (1+B)/hie2 + 1/Red + s*C3;
##    Y(3, 4) = -s*C3;
##
##    % Nodo 5 (índice 4)
##    Y(4, 3) = -s*C3;
##    Y(4, 4) = 1/Rbb + 1/hie3 + s*C3;
##    Y(4, 5) = -1/hie3;
##
##    % Nodo 6 (índice 5)
##    Y(5, 4) = -1/hie3;
##    Y(5, 5) = 1/hie3 + 1/(Ree*(B+1)) + s*C2;
##
##    % Nodo 7 (índice 6)
##    Y(6, 4) = -B/hie3;
##    Y(6, 5) = B/hie3;
##    Y(6, 6) = 1/Rce + s*C4;
##    Y(6, 7) = -s*C4;
##
##    % Nodo 8 (índice 7)
##    Y(7, 6) = -s*C4;
##    Y(7, 7) = 1/Rbbn + 1/hie4 + s*C4;
##    Y(7, 8) = -1/hie4;
##
##    % Nodo 9 (índice 8)
##    Y(8, 7) = -(1-B)/hie4;
##    Y(8, 8) = (1-B)/hie4 + 1/Ro + 1/Res;
##    Y(8, 9) = -1/Ro;
##    Y(8, 11) = -B/hie5;
##
##    % Nodo 10 (índice 9)
##    Y(9, 8) = -1/Ro;
##    Y(9, 9) = 1/Ro + s*C5;
##    Y(9, 10) = -s*C5;
##
##    % Nodo 11 (índice 10)
##    Y(10, 9) = -s*C5;
##    Y(10, 10) = 1/Rl + s*C5;
##
##    % Nodo 12 (índice 11)
##    Y(11, 7) = -B/hie4;
##    Y(11, 8) = B/hie4;
##    Y(11, 11) = 1/hie5;
##
##    % Resolver el sistema de ecuaciones para esta frecuencia
##    V = Y \ J;
##
##    % La salida es el nodo 11 (V_11), que corresponde al índice 10
##    H(k) = V(10);
##end
##
##% --- Generar Diagrama de Bode ---
##figure('Name', 'Diagrama de Bode del Amplificador', 'NumberTitle', 'off');
##
##% Gráfico de Magnitud
##subplot(2, 1, 1);
##semilogx(f, 20*log10(abs(H)), 'b', 'LineWidth', 1.5);
##title('Respuesta en Frecuencia - Magnitud');
##xlabel('Frecuencia (Hz)');
##ylabel('Ganancia (dB)');
##grid on;
##
##% Gráfico de Fase
##subplot(2, 1, 2);
##semilogx(f, angle(H)*180/pi-180, 'r', 'LineWidth', 1.5);
##title('Respuesta en Frecuencia - Fase');
##xlabel('Frecuencia (Hz)');
##ylabel('Fase (grados)');
##grid on;

% Capacitores
C1 = 10e-6;
C2 = 33e-6 * (Bn + 1);
C3 = 10e-6;
C4 = 10e-6;
C5 = 10e-6;

Ree_prime = Ree * (Bn + 1);

Vi = 1;

% Vector de frecuencias (1 Hz a 100 MHz)
f = logspace(1, 6, 1000);
Av_mag = zeros(size(f));
Av_phase = zeros(size(f));

for k = 1:length(f)
    s = 1i * 2 * pi * f(k);

    % Construcción de la matriz G(s) de 12x12|
    G = zeros(12, 12);

    % N002
    G(1,1) = 1/Rbd + 1/hie1 + s*C1;
    G(1,2) = -1/hie1;

    % N003
    G(2,1) = -(1 - Bn)/hie1;
    G(2,2) = (1 - Bn)/hie1 + 1/hie2;
    G(2,3) = -1/hie2;

    % N004
    G(3,2) = -(1 + Bn)/hie2;
    G(3,3) = (1 + Bn)/hie2 + 1/Red + s*C3;
    G(3,4) = -s*C3;

    % N005
    G(4,3) = -s*C3;
    G(4,4) = 1/Rbb + 1/hie3 + s*C3;
    G(4,5) = -1/hie3;

    % N006
    G(5,4) = -1/hie3;
    G(5,5) = 1/hie3 + 1/Ree_prime + s*C2;

    % N007
    G(6,6) = 1/Rcb;
    G(6,7) = -1/Rcb;
    G(6,9) = -Bn/hie4;
    G(6,10) = Bn/hie4;

    % N008
    G(7,6) = -1/Rcb;
    G(7,7) = 1/Rcb + 1/hie5;

    % N009
    G(8,4) = -Bn/hie3;
    G(8,5) = Bn/hie3;
    G(8,8) = 1/Rce + s*C4;
    G(8,9) = -s*C4;

    % N010
    G(9,8) = -s*C4;
    G(9,9) = 1/Rbbn + 1/hie4 + s*C4;
    G(9,10) = -1/hie4;

    % N011
    G(10,7) = Bp/hie5;
    G(10,9) = -(1 - Bn)/hie4;
    G(10,10) = (1 - Bn)/hie4 + 1/Res + 1/Ro;
    G(10,11) = -1/Ro;

    % N012
    G(11,10) = -1/Ro;
    G(11,11) = 1/Ro + s*C5;
    G(11,12) = -s*C5;

    % N013
    G(12,11) = -s*C5;
    G(12,12) = 1/Rl + s*C5;

    % Vector B(s)
    B = zeros(12, 1);
    B(1) = s * C1;

    % Resolver V(s)
    V = G \ (B * Vi);

    vo = V(12); % Tensión en la carga Rl (N013)
    Av = vo / Vi;

    Av_mag(k) = 20 * log10(abs(Av));
    Av_phase(k) = angle(Av) * (180 / pi) - 180;
end

% Gráfica de Bode
figure;
subplot(2,1,1);
semilogx(f, Av_mag, 'b', 'LineWidth', 1.5);
grid on;
title('Diagrama de Bode - Magnitud');
xlabel('Frecuencia (Hz)');
ylabel('Ganancia |Av| (dB)');

subplot(2,1,2);
semilogx(f, Av_phase, 'r', 'LineWidth', 1.5);
grid on;
title('Diagrama de Bode - Fase');
xlabel('Frecuencia (Hz)');
ylabel('Fase (grados)');

Gain_5kHz = 10^(Av_mag(540)/20);
Vi = [2e-3, 5e-3, 10e-3, 15e-3, 17e-3, 20e-3, 25e-3, 50e-3, 75e-3, 100e-3]; %Vi en mV
Vo = zeros(1, length(Vi));  % Vector para guardar la respuesta de salida
Vo = abs(Gain_5kHz)*Vi;

disp('Gananica a 5kHz: ')
disp(abs(Gain_5kHz));

fprintf('\n   Vi (mV)     Vo de salida (V)\n');
fprintf('---------------------------------\n');
for k = 1:length(Vi)
    fprintf('   %7.1f       %10.4f\n', Vi(k)*1000, Vo(k));
end

