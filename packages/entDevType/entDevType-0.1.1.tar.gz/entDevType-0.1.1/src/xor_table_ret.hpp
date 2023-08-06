#ifndef HAVE_XOR_TABLE_RET_HPP
#define HAVE_XOR_TABLE_RET_HPP

#include <cstdint>
#include <vector>

struct xor_table_ret_t {
	std::size_t     offset;
	std::uint16_t   key;

	xor_table_ret_t(void) : offset(0), key(0) { return; }
	~xor_table_ret_t(void) { return; }

	std::size_t getOffset(void) { return offset; }
	void setOffset(std::size_t o) { offset = o; return; }

	std::uint16_t getKey(void) { return key; }
	void setKey(std::uint16_t k) { key = k; return; }
};

typedef std::vector< xor_table_ret_t > xor_table_retvec_t;

#endif
