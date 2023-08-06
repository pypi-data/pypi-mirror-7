#ifndef HAVE_XOR_TABLE_WRAPPER_HPP
#define HAVE_XOR_TABLE_WRAPPER_HPP

#include <cstdint>
#include <vector>
#include <boost/python.hpp>
#include "xor_table.hpp"
#include "xor_table_ret.hpp"

class xor_table_wrapper_t {
	private:
		xor_table_t	m_xor;

	protected:
	public:
		xor_table_wrapper_t(std::size_t max_peoff = 512);
		xor_table_wrapper_t(const std::vector< uint8_t >&, std::size_t max_peoff = 512);
		~xor_table_wrapper_t(void);

		void setData(const std::vector< uint8_t >&);
		xor_table_ret_t find_first(void);
		xor_table_retvec_t find_all(void);
};

#endif

