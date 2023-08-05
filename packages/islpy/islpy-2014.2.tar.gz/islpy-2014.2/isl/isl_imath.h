#include <imath.h>
#include <gmp_compat.h>

uint32_t isl_imath_hash(mp_int v, uint32_t hash);
void isl_imath_gcdext(mp_int G, mp_int S, mp_int T, mp_int A, mp_int B);
double isl_imath_get_d(mp_int op);
int isl_imath_fits_ulong_p(mp_int op);
int isl_imath_fits_slong_p(mp_int op);
void isl_imath_addmul_ui(mp_int rop, mp_int op1, unsigned long op2);
void isl_imath_submul_ui(mp_int rop, mp_int op1, unsigned long op2);
