#include <isl_int.h>

static void free_wrapper(void *p, size_t unused)
{
	free(p);
}

static void *realloc_wrapper(void *p, size_t unused, size_t size)
{
	return realloc(p,size);
}

void imath_get_memory_functions(
		void *(**alloc_func_ptr) (size_t),
		void *(**realloc_func_ptr) (void *, size_t, size_t),
		void (**free_func_ptr) (void *, size_t))
{
	if (alloc_func_ptr)
		*alloc_func_ptr = malloc;
	if (realloc_func_ptr)
		*realloc_func_ptr = realloc_wrapper;
	if (free_func_ptr)
		*free_func_ptr = free_wrapper;
}

uint32_t isl_imath_hash(mp_int v, uint32_t hash)
{
	unsigned const char *data = (unsigned char *)v->digits;
	unsigned const char *end = data + v->used * sizeof(v->digits[0]);

	if (v->sign == 1)
		isl_hash_byte(hash, 0xFF);
	for (; data < end; ++data)
		isl_hash_byte(hash, *data);
	return hash;
}

/* This function tries to produce outputs that do not depend on
 * the version of GMP that is being used.
 *
 * In particular, when computing the extended gcd of -1 and 9,
 * some versions will produce
 *
 *	1 = -1 * -1 + 0 * 9
 *
 * while other versions will produce
 *
 *	1 = 8 * -1 + 1 * 9
 *
 * If configure detects that we are in the former case, then
 * impz_gcdext will be called directly.  Otherwise, this function
 * is called and then we try to mimic the behavior of the other versions.
 */
void isl_imath_gcdext(mp_int G, mp_int S, mp_int T, mp_int A, mp_int B)
{
	if (impz_divisible_p(B, A)) {
		impz_set_si(S, impz_sgn(A));
		impz_set_si(T, 0);
		impz_abs(G, A);
		return;
	}
	if (impz_divisible_p(A, B)) {
		impz_set_si(S, 0);
		impz_set_si(T, impz_sgn(B));
		impz_abs(G, B);
		return;
	}
	mp_int_egcd(A, B, G, S, T);
}

/* Try a standard conversion that fits into a long. */
int isl_imath_fits_slong_p(mp_int op)
{
	unsigned long out;
	mp_result res = mp_int_to_int(op, &out);
	return res == MP_OK;
}

/* Try a standard conversion that fits into an unsigned long. */
int isl_imath_fits_ulong_p(mp_int op)
{
	unsigned long out;
	mp_result res = mp_int_to_uint(op, &out);
	return res == MP_OK;
}

void isl_imath_addmul_ui(mp_int rop, mp_int op1, unsigned long op2)
{
	isl_int temp;
	isl_int_init(temp);

	isl_int_set_ui(temp, op2);
	isl_int_addmul(rop, op1, temp);

	isl_int_clear(temp);
}

void isl_imath_submul_ui(mp_int rop, mp_int op1, unsigned long op2)
{
	isl_int temp;
	isl_int_init(temp);

	isl_int_set_ui(temp, op2);
	isl_int_submul(rop, op1, temp);

	isl_int_clear(temp);
}
