#ifndef __PYX_HAVE__thriftpy__protocol__cybinary
#define __PYX_HAVE__thriftpy__protocol__cybinary


/* "thriftpy/protocol/cybinary.pyx":19
 * 
 * 
 * cdef public enum TType:             # <<<<<<<<<<<<<<
 *     STOP = 0
 *     VOID = 1
 */
enum TType {
  STOP = 0,
  VOID = 1,
  BOOL = 2,
  BYTE = 3,
  I08 = 3,
  DOUBLE = 4,
  I16 = 6,
  I32 = 8,
  I64 = 10,
  STRING = 11,
  UTF7 = 11,
  STRUCT = 12,
  MAP = 13,
  SET = 14,
  LIST = 15,
  UTF8 = 16,
  UTF16 = 17
};

#ifndef __PYX_HAVE_API__thriftpy__protocol__cybinary

#ifndef __PYX_EXTERN_C
  #ifdef __cplusplus
    #define __PYX_EXTERN_C extern "C"
  #else
    #define __PYX_EXTERN_C extern
  #endif
#endif

#endif /* !__PYX_HAVE_API__thriftpy__protocol__cybinary */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC initcybinary(void);
#else
PyMODINIT_FUNC PyInit_cybinary(void);
#endif

#endif /* !__PYX_HAVE__thriftpy__protocol__cybinary */
