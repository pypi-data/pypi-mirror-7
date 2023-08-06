#ifndef HAVE_XOR_TABLE_HPP
#define HAVE_XOR_TABLE_HPP

#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <vector>
#include <array>
#include <memory>
#include <limits>
#include <climits>

#include "xor_table_ret.hpp"

#define MZ_MULTIPLIER 2
#define MZ_LENGTH 2
#define MZ_SIZE UCHAR_MAX*MZ_MULTIPLIER
#define PE_MULTIPLIER 4
#define PE_LENGTH 4
#define PE_SIZE UCHAR_MAX*PE_MULTIPLIER
#define PE_OFFSET 0x3C
#define INDEX_TO_KEY(IDX,KY) do { if (IDX % 2) { KY = IDX - 1 / MZ_MULTIPLIER; } else { KY = IDX / MZ_MULTIPLIER; }	} while(0)
#define KEY_TO_INDEX(K4, I4) do { I4 = static_cast< uint32_t >(K4) * PE_MULTIPLIER;} while(0)

class xor_table_t
{
	private:
		std::size_t						m_span;
		std::array< uint8_t, MZ_SIZE >	m_mzv;
		std::array< uint8_t, PE_SIZE >	m_pev;
		uint8_t*						m_vec;
		std::size_t						m_siz;

	protected:
		void init_tables(void);
		bool find_pe(std::size_t kidx, std::size_t off);
		uint32_t get_peoff(std::size_t, uint8_t);
		bool findAtOffset(xor_table_ret_t& out, std::size_t offset = 0);

	public:
		xor_table_t(std::size_t max_peoff = 512);
		xor_table_t(const std::vector< uint8_t >& v, std::size_t max_peoff = 512);
		~xor_table_t(void);
		void set_file(const std::vector< uint8_t >&);
		bool find_first(xor_table_ret_t&);
		bool find_all(xor_table_retvec_t&);
};

#endif
