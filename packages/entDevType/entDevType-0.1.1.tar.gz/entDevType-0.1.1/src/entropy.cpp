#include "entropy.hpp"

entropy_t::entropy_t(std::size_t bs) : m_bsize(bs)
{
	reset();
	return;
}

entropy_t::entropy_t(const std::vector< uint8_t >& v, std::size_t bs) : m_bsize(bs)
{
	reset();
	update(v, bs);
	return;
}

entropy_t::~entropy_t(void)
{
	return;
}

void
entropy_t::reset(void)
{
	m_ideal		= IDEAL_SIZE;
	m_freedom	= m_ideal - 1;
	m_csquare	= 0.0;
	m_shannon	= 0.0;
	m_count		= 0;
	m_inside	= 0;
	m_outside	= 0;

	for (std::size_t idx = 0; idx < IDEAL_SIZE; idx++)
		m_dist[idx] = 0;

	return;
}

chunk_vec_t
entropy_t::slice(const std::vector< uint8_t >& v, std::size_t bs)
{
	chunk_vec_t			retval;
	std::size_t			csize  = (0 == bs ? m_bsize : bs);
	std::size_t			remain = v.size() % csize;
	std::size_t			offset = 0;
	chunk_t				cdes;
	byte_buf_t			rbuf(new uint8_t[remain]);

	for (offset = 0; offset < v.size() - remain; offset += csize) {
		byte_buf_t tmp(new uint8_t[m_bsize]);

		::memcpy(tmp.get(), v.data() + offset, csize);

		cdes.buf = tmp;
		cdes.len = csize;
		retval.push_back(cdes);
		tmp = nullptr;
	}

	if (0 != remain) {
		cdes.buf = rbuf;
		cdes.len = remain;
		::memcpy(rbuf.get(), v.data() + offset, remain);
		retval.push_back(cdes);
		rbuf = nullptr;
	}

	return retval;
}

void
entropy_t::update(const chunk_t& chunk)
{
	update(chunk.buf.get(), chunk.len);
	return;
}

void
entropy_t::update(const std::vector< uint8_t >& v, std::size_t bs)
{
	chunk_vec_t cv(slice(v, bs));

	for (auto& cvs : cv)
		update(cvs);

	return;
}

void
entropy_t::update(const std::vector< uint8_t >& v)
{
	update(v.data(), v.size());
	return;
}

void
entropy_t::update(const uint8_t* ptr, std::size_t len)
{
	std::size_t c			= 0;
	long double x			= 0.0;
	long double y			= 0.0;
	long double z			= 0.0;

	if (nullptr == ptr || 0 == len)
		throw std::runtime_error("entropy_t::update(): Error invalid parameter (nullptr or 0 length buffer) encountered");

	m_count += len;

	for (std::size_t idx = 0; idx < len; idx++) {
		m_dist.at(ptr[idx])++;


		if (7 == c) {
			x = static_cast<long double>(static_cast<uint32_t>((ptr[idx - 7] << 24 | ptr[idx - 6] << 16 | ptr[idx - 5] << 8 | ptr[idx - 4]))) / UINT32_MAX;
			y = static_cast<long double>(static_cast<uint32_t>((ptr[idx - 3] << 24 | ptr[idx - 2] << 16 | ptr[idx - 1] << 8 | ptr[idx]))) / UINT32_MAX;
			z = x*x + y*y;

			if (1.0 >= z)
				m_inside++;

			m_outside++;
			c = 0;
		} else
			c++;
	}

}

inline long double
entropy_t::getError(long double v2)
{
	static const long double v1 = M_PI;

	return (long double)(std::fabs(v1 - v2) / ((v1 + v2) / 2)) * 100.0;
}

inline long double
entropy_t::getEstimate(void)
{
	return (long double)m_inside / m_outside * 4;
}

void
entropy_t::calculateValues(void)
{
	long double px			= 0.0;
	long double expected	= m_count / m_ideal;

	m_csquare = 0.0;
	m_shannon = 0.0;
	m_estimate = (long double)m_inside / m_outside * 4; //getEstimate();
	m_error = (long double)std::fabs(1.0 - (M_PI / m_estimate)) * 100.0; // getError(m_estimate);

	for (auto idx = 0; idx < IDEAL_SIZE; idx++) {
		if (expected)
			m_csquare += std::pow(m_dist.at(idx) - expected, 2) / expected;

		px = (long double)m_dist.at(idx) / m_count;

		if (0 < px)
			m_shannon += -px * std::log2(px);
	}

	return;
}

entropy_retval_t
entropy_t::getValues(bool calculate)
{
	entropy_retval_t ret = { 0.0, 0.0, 0.0, 0.0 };

	if (true == calculate)
		calculateValues();

	ret.chisquare = m_csquare;
	ret.shannon = m_shannon;
	ret.estimate = m_estimate;
	ret.error = m_error;

	return ret;
}

entropy_retval_t
entropy_t::getBlockDeviation(entropy_retval_t& v1, entropy_retval_t& v2)
{
	entropy_retval_t ret;

	ret.chisquare	= (long double)(std::fabs(v1.chisquare - v2.chisquare) / ((v1.chisquare + v2.chisquare) / 2)) * 100.0;
	ret.error		= (long double)(std::fabs(v1.error - v2.error) / ((v1.error + v2.error) / 2)) * 100.0;
	ret.estimate	= (long double)(std::fabs(v1.estimate - v2.estimate) / ((v1.estimate + v2.estimate) / 2)) * 100.0;
	ret.shannon		= (long double)(std::fabs(v1.shannon - v2.shannon) / ((v1.shannon + v2.shannon) / 2)) * 100.0;

	return ret;
}

entropy_retvec_t
entropy_t::getBlockDeviationFromAllBlocks(const entropy_retvec_t& blocks, std::size_t bnum)
{
	std::vector< entropy_retval_t > ret;
	entropy_retval_t				v1, v2;

	if (bnum >= blocks.size())
		throw std::runtime_error("entropy_t::getBlockDeviation(): Invalid block number specified");

	v2 = blocks.at(bnum);

	for (std::size_t idx = 0; idx < blocks.size(); idx++) {
		if (idx == bnum)
			continue;

		v1 = blocks.at(idx);
		ret.push_back(getBlockDeviation(v1, v2));
	}

	return ret;
}

dist_vec_t 
entropy_t::getDistribution(void)
{
	dist_vec_t v;

	v.resize(IDEAL_SIZE);

	for (auto idx = 0; idx < IDEAL_SIZE; idx++) {
		v.at(idx).value = idx;
		v.at(idx).count = m_dist.at(idx);
	}

	return v;
}
