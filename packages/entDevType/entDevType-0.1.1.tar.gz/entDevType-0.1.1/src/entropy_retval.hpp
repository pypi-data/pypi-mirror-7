#ifndef HAVE_ENTROPY_RETVAL_WRAPPER_HPP
#define HAVE_ENTROPY_RETVAL_WRAPPER_HPP

struct entropy_retval_t {
	long double chisquare;
	long double shannon;
	long double estimate;
	long double error;

	entropy_retval_t(long double c = 0.0, long double s = 0.0, long double es = 0.0, long double er = 0.0) 
	{
		chisquare 	= c;
		shannon		= s;
		estimate	= es;
		error 		= er;
		return;
	}

	~entropy_retval_t(void) { return; }

	void setChiSquare(long double c) { chisquare = c; return; }
	long double getChiSquare(void) { return chisquare; }
	void setShannon(long double s) { shannon = s; return; }
	long double getShannon(void) { return shannon; }
	void setEstimate(long double e) { estimate = e; return; }
	long double getEstimate(void) { return estimate; }
	void setError(long double e) { error = e; return; }
	long double getError(void) { return error; }
  
};

#endif
