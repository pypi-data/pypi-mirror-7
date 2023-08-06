#include "xor_table.hpp"


xor_table_t::xor_table_t(std::size_t max_peoff) : m_span(max_peoff), m_vec(nullptr), m_siz(0)
{

	if (SIZE_MAX <= m_span)
		throw std::runtime_error("xor_table_t::xor_table_t(): Invalid PE magic span specified");

	init_tables();

	return;
}

xor_table_t::xor_table_t(const std::vector< uint8_t >& v, std::size_t max_peoff) : m_span(max_peoff), m_vec(nullptr), m_siz(0)
{

	if (SIZE_MAX <= m_span)
		throw std::runtime_error("xor_table_t::xor_table_t(): Invalid PE magic span specified");

	init_tables();
	set_file(v);

	return;
}

xor_table_t::~xor_table_t(void)
{
	if (nullptr != m_vec) {
		delete[] m_vec;
		m_vec = nullptr;
	}

	return;
}

void 
xor_table_t::init_tables(void)
{

	for (auto key = 0, idx = 0; idx < MZ_SIZE; idx += MZ_LENGTH, key++) {
		m_mzv[idx + 0] = ('M'^key);
		m_mzv[idx + 1] = ('Z'^key);
	}

	for (auto key = 0, idx = 0; idx < PE_SIZE; idx += PE_LENGTH, key++) {
		m_pev[idx + 0] = ('P'^key);
		m_pev[idx + 1] = ('E'^key);
		m_pev[idx + 2] = ('\0'^key);
		m_pev[idx + 3] = ('\0'^key);
	}

	return;
}

void
xor_table_t::set_file(const std::vector< uint8_t >& v)
{
	if (nullptr != m_vec) {
		delete[] m_vec;
		m_vec = nullptr;
	}

	m_siz = v.size();

	m_vec = new uint8_t[m_siz];

	::memcpy(m_vec, v.data(), m_siz);
	return;
}

bool
xor_table_t::find_pe(std::size_t kidx, std::size_t off)
{
	std::size_t max = off + m_span;
	
	if (off >= (SIZE_MAX - m_span) || max >= m_siz-PE_LENGTH || kidx > (PE_SIZE - PE_LENGTH))
		return false;

	for (std::size_t idx = off; idx < max; idx++) {
		if (! ::memcmp(m_vec+idx, &m_pev[kidx], PE_LENGTH))
			return true;
	}

	return false;
}

uint32_t
xor_table_t::get_peoff(std::size_t off, uint8_t key)
{
	return static_cast< uint32_t >((
		((m_vec[off + PE_OFFSET + 3] ^ key) << 24) |
		((m_vec[off + PE_OFFSET + 2] ^ key) << 16) |
		((m_vec[off + PE_OFFSET + 1] ^ key) << 8) |
		( m_vec[off + PE_OFFSET + 0] ^ key)
		));
}

bool
xor_table_t::find_first(xor_table_ret_t& out)
{
	out.key		= 0;
	out.offset	= 0;

	if (nullptr == m_vec || 0 == m_siz)
		return false;

	return findAtOffset(out, 0);
}

bool 
xor_table_t::findAtOffset(xor_table_ret_t& out, std::size_t offset)
{
	uint32_t			peoff = 0;
	uint32_t			kidx = 0;
	uint8_t				key = 0;

	if (offset >= m_siz)
		return false;

	for (auto idx = offset; idx < m_siz-PE_LENGTH; idx++) {
		for (auto mzidx = 0; mzidx < MZ_SIZE; mzidx += MZ_LENGTH) {
			if (idx + MZ_LENGTH >= m_siz || mzidx + 1 >= MZ_SIZE)
				break;

			if (!::memcmp(m_vec+idx, &m_mzv[mzidx], MZ_LENGTH)) {
				INDEX_TO_KEY(mzidx, key);
				KEY_TO_INDEX(key, kidx);


				if (true == find_pe(kidx, idx)) {
					if ((idx + PE_OFFSET + PE_SIZE) >= m_siz)
						continue;

					peoff = get_peoff(idx, key);

					if (peoff+idx >= m_siz)
						continue;

					if (!::memcmp(m_vec+idx+peoff, &m_pev[kidx], PE_LENGTH)) {
						out.key		= static_cast<uint16_t>(key);
						out.offset	= idx;
						return true;
					}
				}
				continue;
			}
		}
	}
	
	return false;
}

bool 
xor_table_t::find_all(xor_table_retvec_t& out)
{
	xor_table_ret_t ret;
	std::size_t	off = 0;

	if (nullptr == m_vec || 0 == m_siz)
		return false;

	while (1) {
		if (true == findAtOffset(ret, off)) {
			out.push_back(ret);
			off = ret.offset + MZ_LENGTH;
		} else
			break;
	}

	if (out.size())
		return true;

	return false;
}

