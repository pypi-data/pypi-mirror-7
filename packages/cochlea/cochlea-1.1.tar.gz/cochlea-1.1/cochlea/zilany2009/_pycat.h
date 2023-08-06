#ifndef __PYX_HAVE__cochlea__zilany2009___pycat
#define __PYX_HAVE__cochlea__zilany2009___pycat


#ifndef __PYX_HAVE_API__cochlea__zilany2009___pycat

#ifndef __PYX_EXTERN_C
  #ifdef __cplusplus
    #define __PYX_EXTERN_C extern "C"
  #else
    #define __PYX_EXTERN_C extern
  #endif
#endif

__PYX_EXTERN_C DL_IMPORT(double) *generate_random_numbers(long);
__PYX_EXTERN_C DL_IMPORT(double) *decimate(int, double *, int);
__PYX_EXTERN_C DL_IMPORT(double) *ffGn(int, double, double, double, int);

#endif /* !__PYX_HAVE_API__cochlea__zilany2009___pycat */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC init_pycat(void);
#else
PyMODINIT_FUNC PyInit__pycat(void);
#endif

#endif /* !__PYX_HAVE__cochlea__zilany2009___pycat */
