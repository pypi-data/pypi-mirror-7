#ifndef PRIV_H_GUARD
#define PRIV_H_GUARD

#include "glbopts.h"
#include "scs.h"
#include "cs.h"
#include "external/amd.h"
#include "external/ldl.h"

struct PRIVATE_DATA {
	cs * L; /* KKT, and factorization matrix L resp. */
	pfloat * D; /* diagonal matrix of factorization */
	idxint * P; /* permutation of KKT matrix for factorization */
	pfloat * bp; /* workspace memory for solves */
};

#endif
