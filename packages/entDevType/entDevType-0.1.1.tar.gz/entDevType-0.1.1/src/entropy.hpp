#ifndef HAVE_ENTROPY_HPP
#define HAVE_ENTROPY_HPP

#define _USE_MATH_DEFINES
#include <cstdint>
#include <stdexcept>
#include <vector>
#include <array>
#include <memory>
#include <random>
#include <math.h>
#include <string.h>

#include "entropy_retval.hpp"
#include "entropy_chunk.hpp"
#include "dist.hpp"

typedef std::vector< chunk_t > chunk_vec_t;
typedef std::vector< entropy_retval_t > entropy_retvec_t;
typedef std::vector< dist_t > dist_vec_t;

#define IDEAL_SIZE 256

class entropy_t
{
	private:
		std::size_t								m_bsize;
	
		std::array< std::size_t, IDEAL_SIZE >	m_dist;
		long double								m_freedom;
		long double								m_ideal;
		long double								m_csquare;
		long double								m_shannon;
		std::size_t								m_count;

		std::size_t								m_inside;
		std::size_t								m_outside;
		long double								m_estimate;
		long double								m_error;

	protected:
		inline long double getEstimate(void);
		inline long double getError(long double);

	public:
		entropy_t(std::size_t bs = 8192);
		entropy_t(const std::vector< uint8_t >&, std::size_t bs = 8192);
		~entropy_t(void);

		chunk_vec_t slice(const std::vector< uint8_t >&, std::size_t = 0);
		void update(const std::vector< uint8_t >&);
		void update(const std::vector< uint8_t >&, std::size_t);
		void update(const chunk_t&);
		void update(const uint8_t*, std::size_t);
		void reset(void);
		void calculateValues(void);
		entropy_retval_t getValues(bool calculate = true);
		entropy_retval_t getBlockDeviation(entropy_retval_t& v1, entropy_retval_t& v2);
		entropy_retvec_t getBlockDeviationFromAllBlocks(const entropy_retvec_t&, std::size_t);
		dist_vec_t getDistribution(void);
};

#endif

