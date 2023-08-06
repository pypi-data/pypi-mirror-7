/*

    _mbar.c - MBAR implementation in C

    author: cwehmeyer <christoph.wehmeyer@fu-berlin.de>

*/

#include "_mbar.h"

/* MBAR iteration */

void _mbar_eq_fixed_N( double *emf, double *eu, int K, int N, double *emf_new )
{
    int i, j, k, t;
    int jN, NK = N*K;
    double sum;
    for( i=0; i<K; ++i )
        emf_new[i] = 0.0;
    for( j=0; j<K; ++j )
    {
        jN = j*N;
        for( t=0; t<N; ++t )
        {
            sum = 0.0;
            for( k=0; k<K; ++k )
                sum +=  eu[k*NK+jN+t] / emf[k];
            for( i=0; i<K; ++i )
                emf_new[i] += eu[i*NK+jN+t] / sum;
        }
    }
    for( i=0; i<K; ++i )
        emf_new[i] /= (double) N;
}

void _mbar_eq( double *emf, double *eu, int K, int *n, int N, double *emf_new )
{
    int i, j, k, t;
    int jN, NK = N*K;
    double sum;
    for( i=0; i<K; ++i )
        emf_new[i] = 0.0;
    for( j=0; j<K; ++j )
    {
        jN = j*N;
        for( t=0; t<n[j]; ++t )
        {
            sum = 0.0;
            for( k=0; k<K; ++k )
                sum += (double) n[k] * ( eu[k*NK+jN+t] / emf[k] );
            for( i=0; i<K; ++i )
                emf_new[i] += eu[i*NK+jN+t] / sum;
        }
    }
}

/* binning operation */

void _mbar_binning( double *emf, double *eu, double *eshift, int K, int *n, int N, int *s, int M, double *p )
{
    int j, k;
    int t;
    int NK = N*K, jN;
    double sum, factor, divisor1 = 0.0, divisor2;
    for( j=0; j<M; ++j )
        p[j] = 0.0;
    for( j=0; j<K; ++j )
    {
        jN = j*N;
        divisor2 = 0.0;
        for( t=0; t<n[j]; ++t )
        {
            sum = 0.0;
            for( k=0; k<K; ++k )
                sum += (double) n[k] * ( eu[k*NK+jN+t] / emf[k] );
            factor = eshift[jN+t] / sum;
            divisor2 += factor;
            p[s[jN+t]] += factor;
        }
        divisor1 += divisor2;
    }
    for( j=0; j<M; ++j )
        p[j] /= divisor1;
}

void _mbar_binning_state( double *emf, double *eu, int state, int K, int *n, int N, int *s, int M, double *p )
{
    int j, k;
    int t;
    int NK = N*K, jN;
    int INK = state * NK;
    double sum, factor, divisor1 = 0.0, divisor2;
    for( j=0; j<M; ++j )
        p[j] = 0.0;
    for( j=0; j<K; ++j )
    {
        jN = j*N;
        divisor2 = 0.0;
        for( t=0; t<n[j]; ++t )
        {
            sum = 0.0;
            for( k=0; k<K; ++k )
                sum += (double) n[k] * ( eu[k*NK+jN+t] / emf[k] );
            factor = eu[INK+jN+t] / sum;
            divisor2 += factor;
            p[s[jN+t]] += factor;
        }
        divisor1 += divisor2;
    }
    for( j=0; j<M; ++j )
        p[j] /= divisor1;
}

void _mbar_binning_fixed_N( double *emf, double *eu, double *eshift, int K, int N, int *s, int M, double *p )
{
    int j, k;
    int t;
    int NK = N*K, jN;
    double sum, factor, divisor1 = 0.0, divisor2;
    for( j=0; j<M; ++j )
        p[j] = 0.0;
    for( j=0; j<K; ++j )
    {
        jN = j*N;
        divisor2 = 0.0;
        for( t=0; t<N; ++t )
        {
            sum = 0.0;
            for( k=0; k<K; ++k )
                sum +=  eu[k*NK+jN+t] / emf[k];
            factor = eshift[jN+t] / sum;
            divisor2 += factor;
            p[s[jN+t]] += factor;
        }
        divisor1 += divisor2;
    }
    for( j=0; j<M; ++j )
        p[j] /= divisor1 * (double) N;
}

void _mbar_binning_state_fixed_N( double *emf, double *eu, int state, int K, int N, int *s, int M, double *p )
{
    int j, k;
    int t;
    int NK = N*K, jN;
    int INK = state * NK;
    double sum, factor, divisor1 = 0.0, divisor2;
    for( j=0; j<M; ++j )
        p[j] = 0.0;
    for( j=0; j<K; ++j )
    {
        jN = j*N;
        divisor2 = 0.0;
        for( t=0; t<N; ++t )
        {
            sum = 0.0;
            for( k=0; k<K; ++k )
                sum +=  eu[k*NK+jN+t] / emf[k];
            factor = eu[INK+jN+t] / sum;
            divisor2 += factor;
            p[s[jN+t]] += factor;
        }
        divisor1 += divisor2;
    }
    for( j=0; j<M; ++j )
        p[j] /= divisor1 * (double) N;
}
