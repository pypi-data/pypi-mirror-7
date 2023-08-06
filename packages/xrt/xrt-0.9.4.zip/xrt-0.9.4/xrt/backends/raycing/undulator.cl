//__author__ = "Konstantin Klementiev", "Roman Chernikov"
//__date__ = "3 Apr 2014"

#pragma OPENCL EXTENSION cl_khr_fp64: enable

__kernel void undulator(const float alpha,
                    const float Kx,
                    const float Kx2,
                    const float Ky,
                    const float Ky2,
                    const float phase,
                    const int jend,
                    __global float* gamma,
                    __global float* gamma2,
                    __global float* wu,
                    __global float* w, 
                    __global float* ww1,
                    __global float* ddphi,
                    __global float* ddpsi,
                    __global float* tg, 
                    __global float* ag,
                    __global float2* Is_gl,
                    __global float2* Ip_gl)
{
//        const float PI = 3.14159265;
        unsigned int ii = get_global_id(0);
        int j;

        float3 beta;

        float2 eucos;
        float ucos;
        float2 Is, Ip;
        //float ab = (float)(0.5 * w[ii] / PI / wu[ii] * 
        //        sinpi((double)Np * ww1[ii]) / sinpi(ww1[ii]));
        /*
        double3 r, n0;
        double betam = 1 - 1/(2 * gamma2[ii]) - Kx2 / (4 * gamma2[ii]) -
                    Ky2 / (4 * gamma2[ii]);
        n0.x = ddphi[ii];
        n0.y = ddpsi[ii];
        n0.z = 1 - 0.5 * (ddphi[ii]*ddphi[ii] + ddpsi[ii]*ddpsi[ii]);*/

        Is = (float2)(0,0);
        Ip = Is;

        for(j=0; j<jend; j++)
          {
          /*r.x = Ky / gamma[ii] * sin(tg[j]);
          r.y = -Kx / gamma[ii] * sin(tg[j] + phase);
          r.z = betam * tg[j] - 0.125 / gamma2[ii] * 
                (Ky2 * sin (2 * tg[j]) + Kx2 * sin (2 * (tg[j] + phase)));

          ucos = w[ii] / wu[ii] * (tg[j] - dot(n0,r));*/

          ucos = (ww1[ii]) * tg[j] + w[ii] / gamma[ii] / wu[ii] *
               (-Ky * ddphi[ii] * (sin(tg[j])) +
                Kx * ddpsi[ii] * sin(tg[j] + phase) +
                0.125 / gamma[ii] * (Ky2 * sin(2. * tg[j]) +
                Kx2 * sin(2. * (tg[j] + phase))));

          eucos.x = cos(ucos);
          eucos.y = sin(ucos);

          beta.x = Ky / gamma[ii] * cos(tg[j]);
          beta.y = Kx / gamma[ii] * cos(tg[j] + phase);
          //beta.z = 1;

          Is += (ag[j] * (ddphi[ii] - beta.x)) * eucos;
          Ip += (ag[j] * (ddpsi[ii] + beta.y)) * eucos;
          }

        Is_gl[ii] = Is;
        Ip_gl[ii] = Ip;
}

__kernel void undulator_taper(const float alpha,
                    const float Kx,
                    const float Kx2,
                    const float Ky,
                    const float Ky2,
                    const float phase,
                    const int jend,
                    __global float* gamma,
                    __global float* gamma2,
                    __global float* wu,
                    __global float* w, 
                    __global float* ww1,
                    __global float* ddtheta,
                    __global float* ddpsi,
                    __global float* tg, 
                    __global float* ag,
                    __global float2* Is_gl,
                    __global float2* Ip_gl)
{
        const float E2W = 1.51926751475e15;
        const float C = 2.9979458e11;

        unsigned int i        = get_local_id(0);
        unsigned int group_id = get_group_id(0);
        unsigned int nloc     = get_local_size(0);
        unsigned int ii = nloc * group_id + i;
        int j;

        float2 eucos;
        float ucos;
        float2 Is;
        float2 Ip;

        Is.x = 0.0f;
        Is.y = 0.0f;
        Ip.x = 0.0f;
        Ip.y = 0.0f;

        for(j=0; j<jend; j++)
          {ucos = ww1[ii] * tg[j] + 
               w[ii] / gamma[ii] / wu[ii] * (-Ky * ddtheta[ii] *(sin(tg[j]) + 
               alpha * C / wu[ii] / E2W *
               (1 - cos(tg[j]) - tg[j] * sin(tg[j]))) +
               Kx * ddpsi[ii] * sin(tg[j] + phase) +
               0.125 / gamma[ii] * (Ky2 * sin(2. * tg[j]) +
                                    Kx2 * sin(2. * (tg[j] + phase)))) - 
               0.125 * w[ii] * alpha * Ky2 / gamma2[ii] / wu[ii] / wu[ii] *
               C / E2W *  (2 * tg[j] * tg[j] + 1 + cos(2 * tg[j]) +
               2 * tg[j] * sin(2 * tg[j]));

          //barrier(CLK_LOCAL_MEM_FENCE);

          eucos.x = cos(ucos);
          eucos.y = sin(ucos);

          //barrier(CLK_LOCAL_MEM_FENCE);        

          Is.x += ag[j] * (ddtheta[ii] - Ky / gamma[ii] * 
              (1 - alpha * C * tg[j] / wu[ii] / E2W) * cos(tg[j])) * eucos.x;
          Is.y += ag[j] * (ddtheta[ii] - Ky / gamma[ii] *
              (1 - alpha * C * tg[j] / wu[ii] / E2W) * cos(tg[j])) * eucos.y;

          Ip.x += ag[j] * (ddpsi[ii] + Kx / gamma[ii] * cos(tg[j] + phase)) * 
                     eucos.x; 
          Ip.y += ag[j] * (ddpsi[ii] + Kx / gamma[ii] * cos(tg[j] + phase)) * 
                     eucos.y;
          }

        //barrier(CLK_LOCAL_MEM_FENCE);

        Is_gl[ii].x = Is.x;
        Is_gl[ii].y = Is.y;
        Ip_gl[ii].x = Ip.x;
        Ip_gl[ii].y = Ip.y;

        //barrier(CLK_LOCAL_MEM_FENCE);            
}

__kernel void undulator_nf(const float R0, const float L0,
                    const float Kx,
                    const float Kx2,
                    const float Ky,
                    const float Ky2,
                    const float phase,
                    const int jend,
                    __global float* gamma,
                    __global float* gamma2,
                    __global float* wu,
                    __global float* w, 
                    __global float* ww1,
                    __global float* ddphi,
                    __global float* ddpsi,
                    __global float* tg, 
                    __global float* ag,
                    __global float2* Is_gl,
                    __global float2* Ip_gl)
{
        const float E2W = 1.51926751475e15;
        const float C = 2.9979458e11;
//        const float PI = 3.141592653589793238;

        unsigned int ii = get_global_id(0);
        int j;

        float2 eucos;
        float ucos;
        float2 Is;
        float2 Ip;
        float3 r, r0;
//        float p1;
        Is.x = 0.0f;
        Is.y = 0.0f;
        Ip.x = 0.0f;
        Ip.y = 0.0f;

        float betam = 1 - 1/(2 * gamma2[ii]) - Kx2 / (4 * gamma2[ii]) -
                    Ky2 / (4 * gamma2[ii]);

        float wR0 = R0 / C * E2W;

        r0.x = wR0 * tan(-ddphi[ii]);
        r0.y = wR0 * tan(ddpsi[ii]);
        r0.z = wR0;

        for(j=0; j<jend; j++)
          {

           r.x = Ky / wu[ii] / gamma[ii] * sin(tg[j]);
           r.y = -Kx / wu[ii] / gamma[ii] * sin(tg[j] + phase);
           r.z = betam * tg[j] / wu[ii] - 0.125 / wu[ii] / gamma2[ii] * 
                (Ky2 * sin (2 * tg[j]) + Kx2 * sin (2 * (tg[j] + phase)));

           ucos = w[ii] * ( tg[j] / wu[ii] + length(r0 - r));

          eucos.x = cos(ucos);
          eucos.y = sin(ucos);

          Is.x += ag[j] * (-ddphi[ii] - Ky / gamma[ii] * cos(tg[j])) * eucos.x;
          Is.y += ag[j] * (-ddphi[ii] - Ky / gamma[ii] * cos(tg[j])) * eucos.y;

          Ip.x += ag[j] * (ddpsi[ii] + Kx / gamma[ii] * cos(tg[j] + phase)) * 
                     eucos.x; 
          Ip.y += ag[j] * (ddpsi[ii] + Kx / gamma[ii] * cos(tg[j] + phase)) * 
                     eucos.y;
          barrier(CLK_LOCAL_MEM_FENCE);
          }
        barrier(CLK_LOCAL_MEM_FENCE);

        Is_gl[ii].x = Is.x;
        Is_gl[ii].y = Is.y;
        Ip_gl[ii].x = Ip.x;
        Ip_gl[ii].y = Ip.y;

}