#include <boost/python.hpp>

#include "entropy.hpp"
#include "entropy_retval.hpp"
#include "vector_wrapper.hpp"
#include "entropy_wrapper.hpp"
#include "xor_table_wrapper.hpp"
#include "xor_table_ret.hpp"
//#include "key_size_recover.hpp"

BOOST_PYTHON_MODULE(entDevType)
{
	using namespace boost::python;
	void (entropy_wrapper_t::*calc0)(void)				= &entropy_wrapper_t::calculate;
	void (entropy_wrapper_t::*calc1)(std::size_t)			= &entropy_wrapper_t::calculate;
	void (entropy_wrapper_t::*calc2)(std::size_t, std::size_t)	= &entropy_wrapper_t::calculate;

	to_python_converter< std::vector< entropy_retval_t >, vector_to_list < entropy_retval_t > >();
	vector_from_list< entropy_retval_t >();

	to_python_converter< std::vector< xor_table_ret_t >, vector_to_list< xor_table_ret_t > >();
	vector_from_list< xor_table_ret_t >();

	to_python_converter< std::vector< uint8_t >, vector_to_string< uint8_t > >();
	vector_from_string< uint8_t >();

	to_python_converter< std::vector< dist_t >, vector_to_list< dist_t > >();
	vector_from_list< dist_t >();

	class_< entropy_retval_t >("entDevReturnType", init< optional< long double, long double, long double, long double > >())
		.def_readonly("ChiSquareValue", &entropy_retval_t::chisquare)
		.def_readonly("chi_square_value", &entropy_retval_t::chisquare)
		.add_property("ChiSquare", &entropy_retval_t::getChiSquare, &entropy_retval_t::setChiSquare)
		.add_property("chi_square", &entropy_retval_t::getChiSquare, &entropy_retval_t::setChiSquare)

		.def_readonly("ShannonValue", &entropy_retval_t::shannon)
		.def_readonly("shannon_value", &entropy_retval_t::shannon)
		.add_property("Shannon", &entropy_retval_t::getShannon, &entropy_retval_t::setShannon)
		.add_property("shannon", &entropy_retval_t::getShannon, &entropy_retval_t::setShannon)

		.def_readonly("EstimateValue", &entropy_retval_t::estimate)
		.def_readonly("estimate_value", &entropy_retval_t::estimate)
		.add_property("Estimate", &entropy_retval_t::getEstimate, &entropy_retval_t::setEstimate)
		.add_property("estimate", &entropy_retval_t::getEstimate, &entropy_retval_t::setEstimate)

		.def_readonly("ErrorValue", &entropy_retval_t::error)
		.def_readonly("error_value", &entropy_retval_t::error)
		.add_property("Error", &entropy_retval_t::getError, &entropy_retval_t::setError)
		.add_property("error", &entropy_retval_t::getError, &entropy_retval_t::setError)
	;

	class_< entropy_wrapper_t >("entDevType", init< optional< std::size_t > >())
		.def(init< const std::vector< uint8_t >&, optional< std::size_t, bool > >())
		.def("setData", &entropy_wrapper_t::setData)
		.def("setData", &entropy_wrapper_t::setDataOverload)
		.def("calculate", calc0)
		.def("calculate", calc1)
		.def("calculate", calc2)
		.def("calculateDistribution", &entropy_wrapper_t::calculateDistribution)
		.def("count", &entropy_wrapper_t::getCount)
		.def("maxIndex", &entropy_wrapper_t::getMaxIndex)
		.def("getDeviation", &entropy_wrapper_t::getDeviation)
		.def("getAllDeviations", &entropy_wrapper_t::getAllDeviations)
		.def("getWholeFileDeviation", &entropy_wrapper_t::getWholeDeviation)
		.def("getScore", &entropy_wrapper_t::getChunkScore)
		.def("getWholeScore", &entropy_wrapper_t::getWholeFileScore)
		.def("getAllScores", &entropy_wrapper_t::getAllChunkScores)
		.def("reset", &entropy_wrapper_t::reset)
		.def("getDistribution", &entropy_wrapper_t::getDistribution)
	;

	class_< dist_t >("distributionType")
		.def(init< uint8_t, std::size_t >())
		.add_property("Value", &dist_t::getValue, &dist_t::setValue)
		.add_property("value", &dist_t::getValue, &dist_t::setValue)
		.add_property("count", &dist_t::getCount, &dist_t::setCount)
		.add_property("Count", &dist_t::getCount, &dist_t::setCount)
	;

	class_< xor_table_ret_t >("xorTableReturnType")
		.add_property("offset", &xor_table_ret_t::getOffset, &xor_table_ret_t::setOffset)
		.add_property("Offset", &xor_table_ret_t::getOffset, &xor_table_ret_t::setOffset)
		.add_property("key", &xor_table_ret_t::getKey, &xor_table_ret_t::setKey)
		.add_property("Key", &xor_table_ret_t::getKey, &xor_table_ret_t::setKey)
	;

	class_< xor_table_wrapper_t >("xorTableType", init< optional< std::size_t > >())
		.def(init< const std::vector< uint8_t >&, optional< std::size_t > >())
		.def("setData", &xor_table_wrapper_t::setData)
		.def("findFirst", &xor_table_wrapper_t::find_first)
		.def("findAll", &xor_table_wrapper_t::find_all)
	;	

	/*class_< key_size_recover_t >("keySizeRecoverType", init< optional< std::size_t > > ())
		.def("recover", &key_size_recover_t::recover)
		.add_property("block_size", &key_size_recover_t::getBlockSize, &key_size_recover_t::setBlockSize)
		.add_property("blockSize", &key_size_recover_t::getBlockSize, &key_size_recover_t::setBlockSize)
	;*/
}

