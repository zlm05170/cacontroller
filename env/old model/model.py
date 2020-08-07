import math
import scipy.linalg
import numpy as np
from scipy import interpolate

class ship_model:
    def __init__(self,
                m = 401.8*1025,
                x_g=1.8,
                L_pp = 28.9,
                rho = 1025,
                x_prop = -13.5,
                y_prop = 2.7,
                Max_RRoT = 0.1*180/math.pi,
                wp = 0.26, #propeller wake
                t = 0.25, #thrust deduction
                Dp = 2, #propeller diameter
                Xudot = -100000, 
                Yvdot = -453413,
                Yrdot = -26543,
                Nvdot = 2425837,
                Nrdot = -3800854,
                V_c = 0, 
                alfa_c = 0,
                ):

        self.rho = rho
        self.wp = wp
        self.t = t
        self.Dp = Dp
        self.L_pp = L_pp
        self.x_prop = x_prop

        self.r_z = L_pp / 2
        self.I_z = m * self.r_z**2
        self.x_rud = - L_pp/2
        self.X_coeff = np.array([17496.74972, -4475.434732, -15679.11679, 175249.6048])

        self.Y_coeff = np.array([1093539, -185048, 4177435, -29940,
                                723602, 1570919, -16493927, -226243])

        self.N_coeff = np.array([-8614233, -508092, -2180055, -70853,
                                -3434695, -1307083, 7020848, 3912253]) 

        self.M = np.array([[m-Xudot, 0, 0],
                            [0, m- Yvdot, m* x_g-Yrdot],
                            [0, m* x_g-Nvdot, self.I_z- Nrdot]])
    
    def HydrodynamicForces(self, velocity):
        X_h = -(2.6528 * velocity[0]**4 - 58.026*velocity[0]**3 + 480.12*velocity[0]**2 - 1756.2*velocity[0] + 2400.8)*1000 \
            + self.X_coeff * np.transpose([velocity[1]**2, velocity[0]*(velocity[1]**2), velocity[0]*velocity[1]*velocity[2], velocity[1]*velocity[2]])
        
        Y_h = self.Y_coeff * np.transpose([velocity[2], velocity[1], velocity[1]*np.abs(velocity[2]), \
         velocity[1]*np.abs(velocity[1]), velocity[2]*np.abs(velocity[1]), velocity[1]*np.abs(velocity[2]), \
          velocity[1]*velocity[2]**2, velocity[1]**2*velocity[2]])

        N_h = self.N_coeff * np.transpose([velocity[2], velocity[1], velocity[2]*np.abs(velocity[2]), velocity[1]*np.abs(velocity[1]), velocity[2]*np.abs(velocity[1]), \
            velocity[1]*np.abs(velocity[2]), velocity[1]*velocity[2]**2, velocity[1]**2*velocity[2]])
        F_h = np.array([X_h, Y_h, N_h])

        return F_h

    def PropulsionForces(self, velocity, n):
        if n == 0:
            F_p =0
        else:
            J = velocity[0]*(1-self.wp)/n/self.Dp
            Kt = -0.3362*J**3 + 0.3983*J**2 - 0.7193*J + 0.7716            
            # Thrust from 2 propulsors
            F_p = 2*(1-self.t) * 1025 * (n**2) * (self.Dp**4) * Kt
        F_p[1:2, 0] = 0
        return F_p
    
    def RudderForces(self, velocity, n, delta, side):
        if side == "SB":
            y_rud = 2.7
        elif side == "PT":
            y_rud = -2.7
        Area_rud = 2.42

        # Correction due to distance between rudder and propeller
        K_R = 0.5+0.5/(1+0.15/(np.abs(self.x_rud-self.x_prop)/self.Dp))
        # long. inflow velocity to propeller
        U_prop_inf = (velocity[0]-velocity[2]*y_rud)*(1-self.wp)
       
        # long. inflow velocity to rudder
        if n == 0:
            U_rud_inf = U_prop_inf
        else:
            J = U_prop_inf/n/self.Dp
            K_t = -0.3362*J**3 + 0.3983*J**2 - 0.7193*J + 0.7716
           
            U_rud_inf = - U_prop_inf * ( 1 + K_R*((1+8*K_t/np.pi/J/J)**0.5 - 1))
        
        # perpendicular inflow velocity to rudder
        V_rud_inf = - ( velocity[1] + velocity[2]*self.x_rud)
       
        gamma = np.arctan2(V_rud_inf, U_rud_inf) #arctanac
        alfa_eff = delta - gamma
        U_rud = (U_rud_inf**2 + V_rud_inf**2)**0.5

        q = 0.5*self.rho*U_rud**2
       
        inflow_ang_grid = np.array([0, 0.09, 0.17, 0.26, 0.35, 0.44, 0.52, 0.61, 0.7, 0.79, 1.2])
        C_l_grid = np.array([0, 0.6, 1.27, 1.75, 2.1, 2.2, 2.3, 2.2, 1.65, 1.5, 1])
        C_d_grid = np.array([0.08, 0.17, 0.4, 0.7, 1.05, 1.27, 1.7, 1.9, 2, 2, 2])
        # interp function seems different matlab and python, check
        C_l = np.sign(alfa_eff)*np.interp(np.abs(alfa_eff), inflow_ang_grid, C_l_grid)
        C_d = np.interp(np.abs(alfa_eff), inflow_ang_grid, C_d_grid)
           
        L = C_l*q*Area_rud
        D = C_d*q*Area_rud
       
        L_body = L*np.transpose([np.sin(gamma), np.cos(gamma)])
        D_body = D*np.transpose([-np.cos(gamma), np.sin(gamma)])
       
        #F[(0:1,1)] = L_body + D_body
        F[(3,1)] = self.x_rud*F(2,1) - self.y_rud*F1,1)
        return F 

        def WindForces(self, position, velocity, beta_w, Vw):
            A_L = 172
            u_wr = Vw*np.cos(beta_w-position[2])+velocity[0]
            v_wr = Vw*np.sin(beta_w-position[2])+velocity[1]

            Ua = np.sqrt(u_wr**2 + v_wr**2)
            epsilon = np.arctan2(v_wr, u_wr)
            dir = np.array([])
            # [m**2] longitudinal projected area
            dir = np.arange(0,190,10)/180*np.pi
            CX = np.array([-0.53 -0.59 -0.65 -0.59 -0.51 -0.47 -0.4 -0.29 -0.2 -0.18 -0.14 -0.05 0.12 0.37 0.61 0.82 0.86 0.72 0.62])
            CY = np.array([0 0.22 0.42 0.66 0.83 0.9 0.88 0.87 0.86 0.85 0.83 0.82 0.81 0.73 0.58 0.46 0.26 0.09 0])
            CN = np.array([0 0.05 0.1 0.135 0.149 0.148 0.114 0.093 0.075 0.04 0.02 -0.013 -0.035 -0.041 -0.045 -0.04 -0.029 -0.014 0])
        
            # matlab: interp1(x,v,xq); python: numpy.interp(xq,x,v)

            X = interp1(dir,CX,abs(epsilon),'spline')*1.23/2*Ua**2*A_L
            Y = -np.sign(epsilon)*interp1(dir,CY,np.abs(epsilon),'spline')*1.23/2*Ua**2*A_L
            N = -np.sign(epsilon)*interp1(dir,CN,np.abs(epsilon),'spline')*1.23/2*Ua**2*A_L*self.L_pp
        
            F_wind = np.transpose([X, Y, N])
            return F_wind

        def odefun(self, PropulsionForces, HydrodynamicForces, RudderForces, WindForces, t, position, velocity):
            input = np.array([position[0], position[1], position[2]*math.pi/180, velocity[0], velocity[1], velocity[2]*math.pi/180])
            # input3 <-> input5 - Nu_dot - velocities in {body}: u, v, r
            #u = input[3]
            v = input[4]
            r = input[5]
            x = input[0]
            y = input[1]
            psi = input[2]

            U_grid = np.transpose([5.7, 5.7, 3.8, 3.8])
            T_grid = np.transpose([0, 60, 100, 500])
            U_dot_grid = np.transpose([0, 0, -0.0475, -0.0475, 0, 0])
            T_dot_grid = np.transpose([0, 59.9, 60, 99.9, 100, 500])
            u = np.interp(t, T_grid, U_grid)
            u_dot = np.interp(t,T_dot_grid,U_dot_grid)

            # res = (u*cos-v*sin, u*sin+v*cos, r)
            res = np.transpose([input[3]*cos(input[2])-input[4]*sin(input[2]),
            input[3]*sin(input[2])+input[4]*cos(input[2]),
            input[5]])

            #relative velocities
            u_r = u - V_c*cos(alfa_c - psi)
            v_r = v - V_c*sin(alfa_c - psi)

            # hydrodynamic forces depending on velocities
            F_total = PropulsionForces(u_r, RPM/60)
            F_total = F_total + HydrodynamicForces(u_r,v_r,r)
            # rudder forces
            F_rudder_SB = RudderForces(u_r,v_r,r,RPM/60,R_SB/180*np.pi,'SB')
            F_rudder_PT = RudderForces(u_r,v_r,r,RPM/60,R_PT/180*np.pi,'PT')

            F_wind = WindForces(psi, beta_w, u, v, V_w)
            #F_wind = 0
            F_total = F_total + F_wind + F_rudder_SB + F_rudder_PT + 
            np.transpose([Xudot*(-V_c*sin(alfa_c-psi)*r),
                Yvdot*(V_c*cos(alfa_c-psi)*r),
                Nvdot*(V_c*cos(alfa_c-psi)*r)])
                           
            res(4:6,1) = self.M**(-1)*F_total
            res(4,1) = u_dot 

                     


