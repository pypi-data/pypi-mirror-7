#pragma OPENCL EXTENSION cl_khr_fp64: enable
//#pragma OPENCL EXTENSION cl_khr_int64_base_atomics:

__kernel void integrate_kirchhoff(
                    const int imax,
                    const int jmax,
                    const unsigned int nrays,
                    __global double* center_gl,
                    __global double* x_gl,
                    __global double* z_gl,
                    __global double* cosGamma,
                    __global double* xloc,
                    __global double* zloc,
                    __global double* Jss_in,
                    __global double* Jpp_in,
                    __global double* Jss_loc,
                    __global double* Jpp_loc,                    
                    __global double* k_wave,                    
                    __global double3* beamOEglo, 
                    __global double3* oe_surface_normal,
                    __global double* beam_OE_loc_path,
                    __global double* path_gl,
                    __global double* blox,
                    __global double* bloz,
                    __global double2* KirchS_gl,
                    __global double2* KirchP_gl,
                    __global double2* KirchN_gl)
{
    double3 beam_coord_glo;
    double3 beam_angle_glo;
    double3 center;
    center.x = center_gl[0];
    center.y = center_gl[1];
    center.z = center_gl[2];
    double3 x;
    x.x=x_gl[0];
    x.y=x_gl[1];
    x.z=x_gl[2];
    double3 z;
    z.x=z_gl[0];
    z.y=z_gl[1];
    z.z=z_gl[2];
    
    double pathAfter;
    double cosAlpha;
    double path;
    double cr;
    double2 ccomp;
    unsigned int i, j, jj;
    double drays = (double)nrays;
    double path_loc, sqJss, sqJpp;
    
    double2 KirchS_loc;
    double2 KirchP_loc;
    double2 KirchN_loc;
    
    unsigned int id       = get_local_id(0);                   
    unsigned int group_id = get_group_id(0);
    unsigned int nloc     = get_local_size(0);
    unsigned int ii = nloc * group_id + id;    
    //printf("ii: %i\n", ii);    
    j = floor((double)ii/(double)jmax);
    jj = ii - j*jmax;
    
    //printf("imax, jmax: %i %i\n", imax, jmax);
    //printf("ii, j, jj: %i %i %i\n", ii, j, jj);
    //printf("center.x, center.y, center.z: %f %f %f\n", center.x, center.y, center.z);
    //printf("z.x, z.y, z.z: %f %f %f\n", z.x, z.y, z.z);
    blox[ii] = xloc[j];
    bloz[ii] = zloc[jj];
    
    path_loc=0;
    KirchS_loc.x=0;
    KirchS_loc.y=0;
    KirchP_loc.x=0;
    KirchP_loc.y=0;
    KirchN_loc.x=0;
    KirchN_loc.y=0;

    //printf("blo.x, blo.z: %f, %f\n", blox[ii], bloz[ii]);    
    //printf("ready to start element %ix%i\n",j,jj);       
    //printf("nrays: %i\n", nrays);
    barrier(CLK_LOCAL_MEM_FENCE);
    for (i=0;i<nrays;i++)
      {
        //printf("ray %i, element %i\n",i,ii);

        beam_coord_glo.x = center.x + x.x * blox[ii] + z.x * bloz[ii];
        beam_coord_glo.y = center.y + x.y * blox[ii] + z.y * bloz[ii];
        beam_coord_glo.z = center.z + x.z * blox[ii] + z.z * bloz[ii];
        barrier(CLK_LOCAL_MEM_FENCE);
        //printf("ray %i\n", i);
        //printf("beam_coord_glo.x, .y, .z: %f %f %f\n", beam_coord_glo.x, beam_coord_glo.y, beam_coord_glo.z);
        //printf("beam_OE_glo.x, .y, .z: %f %f %f\n", beamOEglo[i].x, beamOEglo[i].y, beamOEglo[i].z);
                
        
        beam_angle_glo.x = beam_coord_glo.x - beamOEglo[i].x;
        beam_angle_glo.y = beam_coord_glo.y - beamOEglo[i].y;
        beam_angle_glo.z = beam_coord_glo.z - beamOEglo[i].z;
        //printf("beam_angle_glo.x, .y, .z: %f %f %f\n", beam_angle_glo.x, beam_angle_glo.y, beam_angle_glo.z);
        //printf("surface_normal.x, .y, .z: %f %f %f\n", surface_normal[i].x, surface_normal[i].y, surface_normal[i].z);
        pathAfter = length(beam_angle_glo);
        //printf("pathAfter %f\n", pathAfter);
        cosAlpha = dot(beam_angle_glo,oe_surface_normal[i])/pathAfter;
        //printf("cosAlpha %f\n", cosAlpha);
        path = beam_OE_loc_path[i] + pathAfter;
        //printf("path %f\n", path);
        cr = (cosGamma[i] + cosAlpha) / (Jss_in[i] + Jpp_in[i]);
        
        ccomp.x = cr * cos(k_wave[i] * path);
        ccomp.y = cr * sin(k_wave[i] * path);
        //printf("c %f + i%f\n", ccomp.x, ccomp.y);
        
        path_loc += path/drays;
        
        sqJss = sqrt(Jss_loc[i]);
        sqJpp = sqrt(Jpp_loc[i]);
        
        //printf("sqJss %f\n", sqJss);
         
        KirchS_loc.x += ccomp.x * sqJss;
        KirchS_loc.y += ccomp.y * sqJss;
        
        //printf("KirchS: %f + %fj\n", (ccomp.x * sqJss), (ccomp.y * sqJss));
        
        KirchP_loc.x += ccomp.x * sqJpp;
        KirchP_loc.y += ccomp.y * sqJpp;        

        KirchN_loc.x += ccomp.x;
        KirchN_loc.y += ccomp.y;        
        //printf("ray %i, KirchS.x %f\n", i, KirchS_loc.x);
       }
  //printf("Sum KirchS: %f + %fj\n", KirchS_loc.x, KirchS_loc.y);
  path_gl[ii] = path_loc;
  KirchS_gl[ii] = KirchS_loc;
  KirchP_gl[ii] = KirchP_loc;
  KirchN_gl[ii] = KirchN_loc;

}        
