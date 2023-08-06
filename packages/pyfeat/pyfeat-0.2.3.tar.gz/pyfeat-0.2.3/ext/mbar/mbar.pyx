import numpy as np
cimport numpy as np

cdef extern from "_mbar.h":
    # MBAR iteration
    void _mbar_eq_fixed_N( double *emf, double *eu, int K, int N, double *emf_new )
    void _mbar_eq( double *emf, double *eu, int K, int *n, int N, double *emf_new )
    # binning operations
    void _mbar_binning( double *emf, double *eu, double *eshift, int K, int *n, int N, int *s, int M, double *p )
    void _mbar_binning_state( double *emf, double *eu, int state, int K, int *n, int N, int *s, int M, double *p )
    void _mbar_binning_fixed_N( double *emf, double *eu, double *eshift, int K, int N, int *s, int M, double *p )
    void _mbar_binning_state_fixed_N( double *emf, double *eu, int state, int K, int N, int *s, int M, double *p )

def mbar_eq(
        np.ndarray[double, ndim=1, mode="c"] emf not None,
        np.ndarray[double, ndim=3, mode="c"] eu not None,
        np.ndarray[double, ndim=1, mode="c"] emf_new not None,
        np.ndarray[int, ndim=1, mode="c"] n = None
    ):
    if None == n:
        _mbar_eq_fixed_N(
                <double*> np.PyArray_DATA( emf ),
                <double*> np.PyArray_DATA( eu ),
                eu.shape[0],
                eu.shape[2],
                <double*> np.PyArray_DATA( emf_new )
            )
    else:
        _mbar_eq(
                <double*> np.PyArray_DATA( emf ),
                <double*> np.PyArray_DATA( eu ),
                eu.shape[0],
                <int*> np.PyArray_DATA( n ),
                eu.shape[2],
                <double*> np.PyArray_DATA( emf_new )
            )

def mbar_binning(
        np.ndarray[double, ndim=1, mode="c"] emf not None,
        np.ndarray[double, ndim=3, mode="c"] eu not None,
        np.ndarray[double, ndim=2, mode="c"] eshift not None,
        np.ndarray[int, ndim=2, mode="c"] s not None,
        np.ndarray[double, ndim=1, mode="c"] p not None,
        np.ndarray[int, ndim=1, mode="c"] n = None
    ):
    if None == n:
        _mbar_binning_fixed_N(
                <double*> np.PyArray_DATA( emf ),
                <double*> np.PyArray_DATA( eu ),
                <double*> np.PyArray_DATA( eshift ),
                eu.shape[0],
                eu.shape[2],
                <int*> np.PyArray_DATA( s ),
                p.shape[0],
                <double*> np.PyArray_DATA( p )
            )
    else:
        _mbar_binning(
                <double*> np.PyArray_DATA( emf ),
                <double*> np.PyArray_DATA( eu ),
                <double*> np.PyArray_DATA( eshift ),
                eu.shape[0],
                <int*> np.PyArray_DATA( n ),
                eu.shape[2],
                <int*> np.PyArray_DATA( s ),
                p.shape[0],
                <double*> np.PyArray_DATA( p )
            )

def mbar_binning_state(
        np.ndarray[double, ndim=1, mode="c"] emf not None,
        np.ndarray[double, ndim=3, mode="c"] eu not None,
        state not None,
        np.ndarray[int, ndim=2, mode="c"] s not None,
        np.ndarray[double, ndim=1, mode="c"] p not None,
        np.ndarray[int, ndim=1, mode="c"] n = None
    ):
    if None == n:
        _mbar_binning_state_fixed_N(
                <double*> np.PyArray_DATA( emf ),
                <double*> np.PyArray_DATA( eu ),
                state,
                eu.shape[0],
                eu.shape[2],
                <int*> np.PyArray_DATA( s ),
                p.shape[0],
                <double*> np.PyArray_DATA( p )
            )
    else:
        _mbar_binning_state(
                <double*> np.PyArray_DATA( emf ),
                <double*> np.PyArray_DATA( eu ),
                state,
                eu.shape[0],
                <int*> np.PyArray_DATA( n ),
                eu.shape[2],
                <int*> np.PyArray_DATA( s ),
                p.shape[0],
                <double*> np.PyArray_DATA( p )
            )
