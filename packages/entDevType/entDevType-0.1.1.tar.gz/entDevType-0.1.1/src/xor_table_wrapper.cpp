#include "xor_table_wrapper.hpp"

xor_table_wrapper_t::xor_table_wrapper_t(std::size_t max_peoff) : m_xor(max_peoff)
{
	return;
}

xor_table_wrapper_t::xor_table_wrapper_t(const std::vector< uint8_t >& v, std::size_t max_peoff) : m_xor(v,max_peoff)
{
	return;
}

xor_table_wrapper_t::~xor_table_wrapper_t(void)
{
	return;
}

void 
xor_table_wrapper_t::setData(const std::vector< uint8_t >& v)
{
	m_xor.set_file(v);
	return;
}

xor_table_ret_t 
xor_table_wrapper_t::find_first(void)
{
	xor_table_ret_t r;

	if (false == m_xor.find_first(r)) {
		PyErr_SetString(PyExc_UserWarning, "No PE file was found");
		boost::python::throw_error_already_set();
		return xor_table_ret_t();
	}

	return r;
}

xor_table_retvec_t 
xor_table_wrapper_t::find_all(void)
{
	xor_table_retvec_t r;

	if (false == m_xor.find_all(r)) {
		PyErr_SetString(PyExc_UserWarning, "No PE file was found");
		boost::python::throw_error_already_set();
		return xor_table_retvec_t();
	}

	return r;
}

