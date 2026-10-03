clear all, close all, clc

Vcc = 12;
Bn = 100;
Bp = 100;
Rbd = 1000000;
Red = 47;
R1e = 120000;
R2e = 27000;
Rce = 6800;
Ree = 1200;
R1s = 47000;
R2s = 100000;
Rcb = 100;
Res = 10;
Ro  = 75/10;
Rl  = 8;
Vbb = (Vcc*R2e)/(R2e+R1e);
Rbb = (R1e*R2e)/(R1e+R2e);
a   = Bn/(Bn+1);
Vbbn = (Vcc*R2s)/(R1s+R2s);
Rbbn = (R1s*R2s)/(R1s+R2s);

   %%% POLARIZACIÓN %%%

   % Darlington

% e1 Ibq1*0 + Icq1*0 + Ieq1*0 + Vceq1*0 + Ibq2*0 + Icq2*0 + Ieq2*Red + Vceq2 = Vcc
% e2 Ibq1*0 + Icq1*0 + Ieq1*Bn*Red + Vceq1 + Ibq2*0 + Icq2*0 + Ieq2*0 + Vceq2*0 = Vcc-0.7
% e3 Ibq1*Rbd + Icq1*0 + Ieq1*Bn*Red + Vceq1*0 + Ibq2*0 + Icq2*0 + Ieq2*0 + Vceq2*0 = Vcc-1.4
% e4 Ibq1*Bn + Icq1*-1 + Ieq1*0 + Vceq1*0 + Ibq2*0 + Icq2*0 + Ieq2*0 + Vceq2*0 = 0
% e5 Ibq1*0 + Icq1*0 + Ieq1*0 + Vceq1*0 + Ibq2*Bn + Icq2*-1 + Ieq2*0 + Vceq2*0 = 0
% e6 Ibq1*0 + Icq1*0 + Ieq1 + Vceq1*0 + Ibq2*-1 + Icq2*0 + Ieq2*0 + Vceq2*0 = 0
% e7 Ibq1*-1 + Icq1*-1 + Ieq1 + Vceq1*0 + Ibq2*0 + Icq2*0 + Ieq2*0 + Vceq2*0 = 0
% e8 Ibq1*0 + Icq1*0 + Ieq1*0 + Vceq1*0 + Ibq2*-1 + Icq2*-1 + Ieq2 + Vceq2*0 = 0

Q1 = zeros(8, 8);
S1 = zeros(8, 1);

%e1
Q1(1, 7) = Red;
Q1(1, 8) = 1;
%e2
Q1(2, 3) = Bn*Red;
Q1(2, 4) = 1;
%e3
Q1(3, 1) = Rbd;
Q1(3, 3) = Bn*Red;
%e4
Q1(4, 1) = Bn;
Q1(4, 2) = -1;
%e5
Q1(5, 5) = Bn;
Q1(5, 6) = -1;
%e6
Q1(6, 3) = 1;
Q1(6, 5) = -1;
%e7
Q1(7, 1) = -1;
Q1(7, 2) = -1;
Q1(7, 3) = 1;
%e8
Q1(8, 5) = -1;
Q1(8, 6) = -1;
Q1(8, 7) = 1;

S1(1) = Vcc;
S1(2) = Vcc - 0.7;
S1(3) = Vcc - 1.4;

%[Ibq1, Icq1, Ieq1, Vceq1, Ibq2, Icq2, Ieq2, Vceq2]
R1 = Q1\S1;

   %Emisor común

##   eq1 = Ibeq*Rbb + Iceq*0 + Ieeq*Ree + Vceq*0 == Vbb - 7/10;
##   eq2 = Ibeq*0 + Iceq*Rce  + Ieeq*Ree + Vceeq  == Vcc;
##   eq3 = Ibeq*B - Iceq + Ieeq*0 + Vceq*0 == 0;
##   eq4 = -Ibeq - Iceq + Ieeq + Vcea*0 == 0;

Q2 = zeros(4,4);
S2 = zeros(4,1);

%eq1
Q2(1, 1) = Rbb;
Q2(1, 3) = Ree;
%eq2
Q2(2, 2) = Rce;
Q2(2, 3) = Ree;
Q2(2, 4) = 1;
%e3
Q2(3, 1) = Bn;
Q2(3, 2) = -1;
%e4
Q2(4, 1) = -1;
Q2(4, 2) = -1;
Q2(4, 3) = 1;

S2(1) = Vbb-0.7;
S2(2) = Vcc;

% Ibeq Iceq Ieeq Vceq
R2 = Q2\S2;

   %Sziklai

       % Ibnq Icnq Ienq Vceqs Ibpq Icpq Iepq Vecqs
% eq1: Ibnq*0 + Icnq*0 + Ienq*Res + Vceqs*0 + Ibpq*0 + Icpq*Res + Iepq*0 + Vecqs   = Vcc
% eq2: Ibnq*0 + Icnq*0 + Ienq*Res + Vceqs   + Ibpq*Rcb + Icpq*Res + Iepq*0 + Vecqs*0 = Vcc - 7/10
% eq3: Ibnq*Rbbn + Icnq*0 + Ienq*Res + Vceqs*0+ Ibpq*0 + Icpq*Res + Iepq*0 + Vecqs*0  = Vbbn - 7/10
% eq4: Ibnq*Bn - Icnq = 0
% eq5: Ibpq*Bp - Icpq = 0
% eq6: -Icnq + Ibpq = 0
% eq7: -Ibnq - Icnq + Ienq = 0
% eq8: -Ibpq - Icpq + Iepq = 0

Q3 = zeros(8, 8);
S3 = zeros(8, 1);

%eq1
Q3(1, 3) = Res;
Q3(1, 6) = Res;
Q3(1, 8) = 1;
%eq2
Q3(2, 3) = Res;
Q3(2, 4) = 1;
Q3(2, 5) = Rcb;
Q3(2, 6) = Res;
%eq3
Q3(3, 1) = Rbbn;
Q3(3, 3) = Res;
Q3(3, 6) = Res;
%eq4
Q3(4, 1) = Bn;
Q3(4, 2) = -1;
%eq5
Q3(5, 5) = Bp;
Q3(5, 6) = -1;
%eq6
Q3(6, 2) = -1;
Q3(6, 5) = 1;
%eq7
Q3(7, 5) = -1;
Q3(7, 6) = -1;
Q3(7, 7) = 1;
%eq8
Q3(8, 1) = -1;
Q3(8, 2) = -1;
Q3(8, 3) = 1;

S3(1) = Vcc;
S3(2) = Vcc - 0.7;
S3(3) = Vcc - 1.4;

R3 = Q3\S3;

Vt = 25/1000;
disp("");
hie1 = double((Vt*Bn)/(R1(3)))
disp("");
hie2 = double((Vt*Bn)/R1(7))
disp("");
hie3 = double((Vt*Bn)/R2(3))
disp("");
hie4 = double((Vt*Bn)/R3(3))
disp("");
hie5 = double((Vt*Bp)/R3(7))

Vcc = 12;
ZiEC = 2129.54; % Impedancia de entrada del amplificador Em Com
ZiSz = 441; % Impedancia de entrada del amplificador Sziklai

% Rectas de carga

%Gráfico Transistor Q1
x1 = linspace(0, 11.3, 100);
Ic1 = (Vcc-0.7)/(Bn*Red) - x1/(Bn*Red);
Rca1 = Bn/(1/Red + 1/ZiEC);
x2 = linspace(0, R1(2)*Rca1+R1(4), 100);
ic1 = R1(2) - 1/Rca1 *(x2 - R1(4));

figure(1);
plot(x1, Ic1, 'r', 'LineWidth', 1.5);
hold on;
plot(x2, ic1, 'r', 'LineWidth', 1);
hold on;
%Punto Q
plot(R1(4), R1(2), 'ro', 'markersize', 8, 'markerfacecolor', 'r');
title('Recta de Carga CC - CA - Q1 (Darlington)');
xlabel('Vce1 [V]'); ylabel('Ic1 [A]');
grid on;
hold off;

%Gráfico Transistor Q2
x3 = linspace(0, 12, 100);
Ic2 = Vcc/Red - x3/Red;
Rca2 = 1/((1/Red+1/ZiEC));
x4 = linspace(0, R1(6)*Rca2+R1(8), 100);
ic2 = R1(6) - 1/Rca2 *(x4 - R1(8));

figure(2);
plot(x3, Ic2, 'b', 'LineWidth', 1.5);
hold on;
plot(x4, ic2, 'b', 'LineWidth', 1);
hold on;
%Punto Q
plot(R1(8), R1(6), 'bo', 'markersize', 8, 'markerfacecolor', 'b');
title('Recta de Carga CC - CA - Q2 (Darlington)');
xlabel('Vce2 [V]'); ylabel('Ic2 [A]');
grid on;
hold off;

%Gráfico Transistor Q3
x5 = linspace(0, 12, 100);
Rcc3 = Ree + (Bn*Rce)/(Bn+1);
Ic3 = Vcc/Rcc3 - x5/Rcc3;
Rca3 = 1/(1/Rce+1/ZiSz);
x6 = linspace(0, R2(2)*Rca3+R2(4), 100);
ic3 = R2(2) - (x6 - R2(4))/Rca3;

figure(3);
plot(x5, Ic3, 'g', 'LineWidth', 1.5);
hold on;
plot(x6, ic3, 'g', 'LineWidth', 1);
hold on;
%Punto Q
plot(R2(4), R2(2), 'go', 'markersize', 8, 'markerfacecolor', 'g');
title('Recta de Carga CC - CA - Q3 (Emisor Común)');
xlabel('Vce3 [V]'); ylabel('Ic3 [A]');
grid on;
hold off;

%Gráfico Transistor Q4
x7 = linspace(0, Vcc-0.7, 100);
Ic4 = ((1+Bn)*(Vcc-0.7-x7))/(Res*(Bn*Bp+Bn+1)+Bn*Rcb);
Rca4 = ((1/(1/Res + 1/(Ro+Rl)))*(Bn*Bp+Bn+1)+Bn*Rcb)/Bn;
ic4 = R3(2)-(x7-R3(4))/Rca4;

figure(4);
plot(x7, Ic4, 'y', 'LineWidth', 1.5);
hold on;
plot(x7, ic4, 'y', 'LineWidth', 1);
hold on;
%Punto Q
plot(R3(4), R3(2), 'yo', 'markersize', 8, 'markerfacecolor', 'y');
title('Recta de Carga CC - CA - Q4 (Sziklai)');
xlabel('Vce4 [V]'); ylabel('Ic4 [A]');
grid on;
hold off;

%Gráfico Transistor Q5
x8 = linspace(0, Vcc, 100);
Ic5 = (Bn*(1+Bp)*(Vcc-x8))/(Res*(Bn*Bp+Bn+1));
Rca5 = ((1/(1/Res + 1/(Ro+Rl)))*(Bn*Bp+Bn+1))/(Bn*(Bp+1));
ic5 = R3(6) - (x8-R3(8))/Rca5;

figure(5);
plot(x8, Ic5, 'm', 'LineWidth', 1.5);
hold on;
plot(x8, ic5, 'm', 'LineWidth', 1);
hold on;
%Punto Q
plot(R3(8), R3(6), 'mo', 'markersize', 8, 'markerfacecolor', 'm');
title('Recta de Carga CC - CA - Q5 (Sziklai)');
xlabel('Vce3 [V]'); ylabel('Ic3 [A]');
grid on;
hold off;

disp("");
disp('    TENSIONES CORRIENTE Y POTENCIAS     ');
disp("");
disp('Amplificador Darlington');
disp('');
disp('Q1');
disp("Ibq1 = ");
disp(double(R1(1)));
disp("Icq1 = ");
disp(double(R1(2)));
disp("Ieq1 = ");
disp(double(R1(3)));
disp("Vceq1 = ");
disp(double(R1(4)));
VbD1 = R1(7)*Red+1.4
VcD1 = Vcc
VeD1 = R1(7)*Red+0.7
VceD1 = VcD1-VeD1
PD1 = R1(3)*R1(4)
disp('Q2');
disp("Ibq2 = ");
disp(double(R1(5)));
disp("Icq2 = ");
disp(double(R1(6)));
disp("Ieq2 = ");
disp(double(R1(7)));
disp("Vceq2 = ");
disp(double(R1(8)));
VbD2 = VeD1
VcD2 = Vcc
VeD2 = R1(7)*Red
VceD2 = VcD2-VeD2
PD2 = R1(7)*R1(8)
disp("");
disp('Amplificador Emisor Común');
disp("");
disp('Q3');
disp("Ibeq = ");
disp(double(R2(1)));
disp("Iceq = ");
disp(double(R2(2)));
disp("Ieeq = ");
disp(double(R2(3)));
disp("Vceeq = ");
disp(double(R2(4)));
VbE = Vbb
VcE = R2(3)*Ree+R2(4)
VeE = R2(3)*Ree
VceE = VcE-VeE
PEC = R2(3)*R2(4)
disp("");
disp('Amplificador Sziklai');
disp("");
disp('Q4');
disp("Ibnq = ");
disp(double(R3(1)));
disp("Icnq = ");
disp(double(R3(2)));
disp("Ienq = ");
disp(double(R3(3)));
disp("Vceqs = ");
disp(double(R3(4)));
VbS1 = Vbbn
VcS1 = (R3(3)+R3(6))*Res+R3(4)
VeS1 = (R3(3)+R3(6))*Res
VceS1 = VcS1-VeS1
PS1 = R3(3)*R3(4)
disp('Q5');
disp("Ibpq = ");
disp(double(R3(5)));
disp("Icpq = ");
disp(double(R3(6)));
disp("Iepq = ");
disp(double(R3(7)));
disp("Vecqs = ");
disp(double(R3(8)));
VbS2 = VcS1
VcS2 = VeS1
VeS2 = Vcc
VecS2 = VeS2-VcS2
PS2 = R3(7)*R3(8)

disp("");
disp('Resistencias');
PRbd = R1(1)^2*Rbd
PRed = R1(7)^2*Red
IR1e = Vcc/(R1e+R2e);
PR1e = IR1e^2*R1e
IR2e = IR1e-R2(1);
PR2e = IR2e^2*R2e
PRce = R2(2)^2*Rce
PRee = R2(3)^2*Ree
IR1s = Vcc/(R1s+R2s);
PR1s = IR1s^2*R1s
IR2s = IR1s-R3(1);
PR2s = IR2s^2*R2s
PRes = (R3(3)+R3(6))^2*Res6
vi = 10e-3; %10 mV
Av = 111.798542;
vo = vi*Av;
IRo = vo/(Ro+Rl); % = IRl
PRo = IRo^2*Ro
PRl = IRo^2*Rl

disp('');
disp(' Impedancias' );
disp('');
disp('Darlington');
ZinD = 1/(1/Rbd + 1/((hie1+(Bn+1)*(hie2+(Bn+1)*Red))))
ZoutD = 1/(1/Red + 1/(hie2/(Bn+1) + (Rbd+hie1)/(Bn+1)^2))
disp('');
disp('Emisor Común');
ZinEC = 1/(1/Rbb + 1/hie3)
ZoutEC = Rce
disp('');
disp('Sziklai');
Req1 = 1/(1/Res+1/(Ro+Rl));
Req2 = (1+Bn*Bp)*Req1;
Req3 = Rcb+hie5;
ZinS = 1/(1/Rbbn + 1/(hie4+Req2) +1/Req3)
Req4 = hie4 + 1/(1/(Rcb+hie5) + (Bn*Bp+1)/Rbbn)
ZoutS = (1/(1/Res + 1/Req4))
