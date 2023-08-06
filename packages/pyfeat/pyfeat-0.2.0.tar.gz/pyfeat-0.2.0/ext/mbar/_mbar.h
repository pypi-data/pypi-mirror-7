/*

	_mbar.h - MBAR implementation in C (header file)

    author: cwehmeyer <christoph.wehmeyer@fu-berlin.de>

*/

#ifndef PYFEE_MBAR
#define PYFEE_MBAR

#include <stdlib.h>
#include <math.h>

/* MBAR iteration */
void _mbar_eq_fixed_N( double *emf, double *eu, int K, int N, double *emf_new );
void _mbar_eq( double *emf, double *eu, int K, int *n, int N, double *emf_new );

/* binning operation */
void _mbar_binning( double *emf, double *eu, double *eshift, int K, int *n, int N, int *s, int M, double *p );
void _mbar_binning_state( double *emf, double *eu, int state, int K, int *n, int N, int *s, int M, double *p );
void _mbar_binning_fixed_N( double *emf, double *eu, double *eshift, int K, int N, int *s, int M, double *p );
void _mbar_binning_state_fixed_N( double *emf, double *eu, int state, int K, int N, int *s, int M, double *p );

#endif
