#pragma OPENCL EXTENSION cl_khr_fp64: enable
__constant float zEps = 1.e-12;
__constant bool isParametric = false;
__constant int maxIteration = 100;
__constant float PI = 3.141592653589793238;

float2 rotate_x(float y, float z, float cosangle, float sinangle)
{
  float2 res;
  res.s0 = cosangle*y - sinangle*z;
  res.s1 = sinangle*y + cosangle*z;
  return res;
}

float2 rotate_y(float x, float z, float cosangle, float sinangle)
{
  float2 res;
  res.x = cosangle*x + sinangle*z;
  res.y = -sinangle*x + cosangle*z;
  return res;
}

MY_LOCAL_Z

MY_LOCAL_N

MY_XYZPARAM

float4 find_dz(__global float *cl_plist,
               int local_f, float t, float x0, float y0, float z0, 
               float a, float b, float c, int invertNormal, int derivOrder)
{
        /*Returns the z or r difference (in the local system) between the ray
        and the surface. Used for finding the intersection point.*/

        float x = x0 + a * t;
        float y = y0 + b * t;
        float z = z0 + c * t;
        float surf, dz;
        float3 surf3;
        int diffSign = 1;

        if (derivOrder == 0)
          {
            if (isParametric) 
              {
                diffSign = -1;
                surf3 = xyz_to_param(cl_plist, x, y, z);
                x = surf3.x; y = surf3.y; z = surf3.z;
                surf = local_z(cl_plist, local_f, x, y);
              }
            else
              {
                surf = local_z(cl_plist, local_f, x, y);
              }
            if (!isnormal(surf)) surf = 0;
            dz = (z - surf) * diffSign * invertNormal;
          }
        else
          {
            surf3 = local_n(cl_plist, local_f, x, y);
            if (!isnormal(surf))
              {
                surf3.x = 0;
                surf3.y = 0;
                surf3.z = 1;
              }
            dz = (a * surf3.x + b * surf3.y + c * surf3.z) * invertNormal;
          }
        //barrier(CLK_GLOBAL_MEM_FENCE);
        return (float4)(dz, x, y, z);
}

float4 _use_my_method(__global float *cl_plist,
                      int local_f, float tMin, float tMax, float t1, float t2,
                      float x, float y, float z, 
                      float a, float b, float c, 
                      int invertNormal, int derivOrder, float dz1, float dz2, 
                      float x2, float y2, float z2)
{

        float4 tmp;
        unsigned int numit=2;
        float t, dz;
        while ((fabs(dz2) > zEps) & (numit < maxIteration))
          {
            t = t1;
            dz = dz1;
            t1 = t2;
            dz1 = dz2;
            t2 = t - (t1 - t) * dz / (dz1 - dz);

            if (t2 < tMin) t2 = tMin;
            if (t2 > tMax) t2 = tMax;

            tmp = find_dz(cl_plist, local_f, t2, x, y, z, a, b, c,
                          invertNormal, derivOrder);

            dz2 = tmp.s0;
            x2 = tmp.s1;
            y2 = tmp.s2;
            z2 = tmp.s3;

            if (sign(dz2) == sign(dz1))
              {
                t1 = t;
                dz1 = dz;
              }
            numit++;
          }
        //barrier(CLK_GLOBAL_MEM_FENCE);
        return (float4)(t2, x2, y2, z2);
}
float4 _use_Brent_method(__global float *cl_plist,
                      int local_f, float tMin, float tMax, float t1, float t2,
                      float x, float y, float z,
                      float a, float b, float c,
                      int invertNormal, int derivOrder, float dz1, float dz2,
                      float x2, float y2, float z2)
{
        float4 tmp;
        float tmpt, t3, t4, dz3, xa, xb, xc, xd, xs, xai, xbi, xci;
        float fa, fb, fc, fai, fbi, fci, fs;
        bool mflag, mf, cond1, cond2, cond3, cond4, cond5, conds, fafsNeg;


        if (fabs(dz1) < fabs(dz2))
          {
            tmpt = t1; t1 = t2; t2 = tmpt;
            tmpt = dz1; dz1 = dz2; dz2 = tmpt;
          }
        
        t3 = t1;
        dz3 = dz1;
        t4 = 0;

        mflag = true;
        unsigned int numit = 2;

        while ((fabs(dz2) > zEps) & (numit < maxIteration))
          {

            xa = t1; xb = t2; xc = t3; xd = t4;
            fa = dz1; fb = dz2; fc = dz3;
            mf = mflag;
            xs = 0;

            if ((fa != fc) & (fb != fc))
              {
                xai = xa; xbi = xb; xci = xc;
                fai = fa; fbi = fb; fci = fc;
                xs = xai * fbi * fci / (fai - fbi) / (fai - fci) + 
                    fai * xbi * fci / (fbi - fai) / (fbi - fci) + 
                    fai * fbi * xci / (fci - fai) / (fci - fbi); 
              }
            else
              {
                xai = xa; xbi = xb;
                fai = fa; fbi = fb;
                xs = xbi - fbi * (xbi - xai) / (fbi - fai);
              }

            cond1 = (((xs < (3*xa + xb) / 4.) & (xs < xb)) |
                     ((xs > (3*xa + xb) / 4.) & (xs > xb)));
            cond2 = (mf & (fabs(xs - xb) >= (fabs(xb - xc) / 2.)));
            cond3 = ((!mf) & (fabs(xs - xb) >= (fabs(xc - xd) / 2.)));
            cond4 = (mf & (fabs(xb - xc) < zEps));
            cond5 = ((!mf) & (fabs(xc - xd) < zEps));
            conds = (cond1 | cond2 | cond3 | cond4 | cond5);

            if (conds)
              {
                xs = (xa + xb) / 2;
              }

            mf = conds;
            tmp = find_dz(cl_plist, local_f, xs, x, y, z, a, b, c,
                          invertNormal, derivOrder);

            fs = tmp.s0;
            x2 = tmp.s1;
            y2 = tmp.s2;
            z2 = tmp.s3;

            xd = xc; xc = xb; fc = fb;

            fafsNeg = (((fa < 0) & (fs > 0)) | ((fa > 0) & (fs < 0)));

            if (fafsNeg)
              {
                xb = xs; fb = fs;
              }
            else
              {
                xa = xs; fa = fs;
              }

            if (fabs(fa) < fabs(fb))
              {
                tmpt = xa; xa = xb; xb = tmpt;
                tmpt = fa; fa = fb; fb = tmpt;
              }

            t1 = xa; t2 = xb; t3 = xc; t4 = xd; 
            dz1 = fa; dz2 = fb; dz3 = fc;
            mflag = mf;

            numit++;
          }

        return (float4)(t2, x2, y2, z2);
}


float4 find_intersection_internal(__global float *cl_plist, 
                          int local_f, float tMin, float tMax, 
                          float t1, float t2, 
                          float x, float y, float z, 
                          float a, float b, float c, 
                          int invertNormal, int derivOrder)
{
        /*Finds the ray parameter *t* at the intersection point with the
        surface. Requires *t1* and *t2* as input bracketing. The ray is
        determined by its origin point (*x*, *y*, *z*) and its normalized
        direction (*a*, *b*, *c*). *t* is then the distance between the origin
        point and the intersection point. *derivOrder* tells if minimized is
        the z-difference (=0) or its derivative (=1).*/
        float4 tmp1, res;
        float dz1, dz2;
        int state = 1;

        res = find_dz(cl_plist, local_f,
            t1, x, y, z, a, b, c, invertNormal, derivOrder);
        barrier(CLK_LOCAL_MEM_FENCE);
        tmp1 = find_dz(cl_plist, local_f,
            t2, x, y, z, a, b, c, invertNormal, derivOrder);
        barrier(CLK_LOCAL_MEM_FENCE);
        dz1 = res.s0;
        dz2 = tmp1.s0;

        if (dz1 <= 0) state = -1;
        if (dz2 >= 0) state = -2;

        tmp1.s0 = t2;

        if (state == -1) tmp1.s0 = t1;

        res = tmp1;

        if (state > 0)
          {
            if (fabs(dz2) > fabs(dz1) * 20.)
              {
                res = _use_Brent_method(cl_plist, local_f,
                  tMin, tMax, t1, t2, x, y, z, a, b, c, 
                  invertNormal, derivOrder, dz1, dz2, res.s1, res.s2, res.s3);
              }
            else
              {
                res = _use_my_method(cl_plist, local_f,
                  tMin, tMax, t1, t2, x, y, z, a, b, c, 
                  invertNormal, derivOrder, dz1, dz2, res.s1, res.s2, res.s3);              
              }
          }
        barrier(CLK_LOCAL_MEM_FENCE);
        return res;
}


__kernel void find_intersection(
                  __global float *cl_plist,
                  const int invertNormal,
                  const int derivOrder,
                  const int local_zN,
                  const float tMin,
                  const float tMax,
                  __global float *t1,
                  __global float *t2,
                  __global float *x,
                  __global float *y,
                  __global float *z,
                  __global float *a,
                  __global float *b,
                  __global float *c,
                  __global float *x2,
                  __global float *y2,
                  __global float *z2
                  )
{
      float4 res;

      //unsigned int i = get_local_id(0);
      //unsigned int group_id = get_group_id(0);
      //unsigned int nloc = get_local_size(0);
      //unsigned int ii = nloc * group_id + i;
      unsigned int ii = get_global_id(0);
      res = find_intersection_internal(cl_plist, local_zN, 
                                       tMin, tMax, t1[ii], t2[ii], 
                                       x[ii], y[ii], z[ii], 
                                       a[ii], b[ii], c[ii], 
                                       invertNormal, derivOrder);
      //barrier(CLK_GLOBAL_MEM_FENCE);
      t2[ii] = res.s0; x2[ii] = res.s1; y2[ii] = res.s2; z2[ii] = res.s3;
}