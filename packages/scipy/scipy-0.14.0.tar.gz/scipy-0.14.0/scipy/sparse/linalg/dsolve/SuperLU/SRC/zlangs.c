
/*! @file zlangs.c
 * \brief Returns the value of the one norm
 *
 * <pre>
 * -- SuperLU routine (version 2.0) --
 * Univ. of California Berkeley, Xerox Palo Alto Research Center,
 * and Lawrence Berkeley National Lab.
 * November 15, 1997
 *
 * Modified from lapack routine ZLANGE 
 * </pre>
 */
/*
 * File name:	zlangs.c
 * History:     Modified from lapack routine ZLANGE
 */
#include <math.h>
#include "slu_zdefs.h"

/*! \brief
 *
 * <pre>
 * Purpose   
 *   =======   
 *
 *   ZLANGS returns the value of the one norm, or the Frobenius norm, or 
 *   the infinity norm, or the element of largest absolute value of a 
 *   real matrix A.   
 *
 *   Description   
 *   ===========   
 *
 *   ZLANGE returns the value   
 *
 *      ZLANGE = ( max(abs(A(i,j))), NORM = 'M' or 'm'   
 *               (   
 *               ( norm1(A),         NORM = '1', 'O' or 'o'   
 *               (   
 *               ( normI(A),         NORM = 'I' or 'i'   
 *               (   
 *               ( normF(A),         NORM = 'F', 'f', 'E' or 'e'   
 *
 *   where  norm1  denotes the  one norm of a matrix (maximum column sum), 
 *   normI  denotes the  infinity norm  of a matrix  (maximum row sum) and 
 *   normF  denotes the  Frobenius norm of a matrix (square root of sum of 
 *   squares).  Note that  max(abs(A(i,j)))  is not a  matrix norm.   
 *
 *   Arguments   
 *   =========   
 *
 *   NORM    (input) CHARACTER*1   
 *           Specifies the value to be returned in ZLANGE as described above.   
 *   A       (input) SuperMatrix*
 *           The M by N sparse matrix A. 
 *
 *  =====================================================================
 * </pre>
 */

double zlangs(char *norm, SuperMatrix *A)
{
    
    /* Local variables */
    NCformat *Astore;
    doublecomplex   *Aval;
    int      i, j, irow;
    double   value, sum;
    double   *rwork;

    Astore = A->Store;
    Aval   = Astore->nzval;
    
    if ( SUPERLU_MIN(A->nrow, A->ncol) == 0) {
	value = 0.;
	
    } else if (lsame_(norm, "M")) {
	/* Find max(abs(A(i,j))). */
	value = 0.;
	for (j = 0; j < A->ncol; ++j)
	    for (i = Astore->colptr[j]; i < Astore->colptr[j+1]; i++)
		value = SUPERLU_MAX( value, z_abs( &Aval[i]) );
	
    } else if (lsame_(norm, "O") || *(unsigned char *)norm == '1') {
	/* Find norm1(A). */
	value = 0.;
	for (j = 0; j < A->ncol; ++j) {
	    sum = 0.;
	    for (i = Astore->colptr[j]; i < Astore->colptr[j+1]; i++) 
		sum += z_abs( &Aval[i] );
	    value = SUPERLU_MAX(value,sum);
	}
	
    } else if (lsame_(norm, "I")) {
	/* Find normI(A). */
	if ( !(rwork = (double *) SUPERLU_MALLOC(A->nrow * sizeof(double))) )
	    ABORT("SUPERLU_MALLOC fails for rwork.");
	for (i = 0; i < A->nrow; ++i) rwork[i] = 0.;
	for (j = 0; j < A->ncol; ++j)
	    for (i = Astore->colptr[j]; i < Astore->colptr[j+1]; i++) {
		irow = Astore->rowind[i];
		rwork[irow] += z_abs( &Aval[i] );
	    }
	value = 0.;
	for (i = 0; i < A->nrow; ++i)
	    value = SUPERLU_MAX(value, rwork[i]);
	
	SUPERLU_FREE (rwork);
	
    } else if (lsame_(norm, "F") || lsame_(norm, "E")) {
	/* Find normF(A). */
	ABORT("Not implemented.");
    } else
	ABORT("Illegal norm specified.");

    return (value);

} /* zlangs */

