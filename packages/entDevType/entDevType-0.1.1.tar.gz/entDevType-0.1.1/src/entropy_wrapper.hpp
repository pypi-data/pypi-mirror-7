#ifndef HAVE_ENTROPY_WRAPPER_HPP
#define HAVE_ENTROPY_WRAPPER_HPP

#include <cstdint>
#include <vector>

#include <boost/python.hpp>

#include "entropy_retval.hpp"
#include "entropy_chunk.hpp"
#include "entropy.hpp"

class entropy_wrapper_t {
	private:
		chunk_vec_t				m_cvec;
		entropy_retvec_t 		m_retvec;
		entropy_retval_t 		m_whole;
		bool					m_wholeDone;
		entropy_t				m_entdev;
		std::vector< uint8_t >	m_data;
		std::vector< dist_t >	m_dist;

	protected:
	public:
		entropy_wrapper_t(std::size_t bs = 8192);
		entropy_wrapper_t(const std::vector< uint8_t >&, std::size_t bs = 8192, bool whole = false);

		~entropy_wrapper_t(void);

		void reset(void);

		void setDataOverload(const std::vector< uint8_t >&);
		void setData(const std::vector< uint8_t >&, std::size_t bs = 8192, bool whole = false);

		std::size_t getCount(void);
		std::size_t getMaxIndex(void);

		void calculate(void);
		void calculate(std::size_t);
		void calculate(std::size_t, std::size_t);

		entropy_retval_t getChunkScore(std::size_t);
		entropy_retval_t getWholeFileScore(void);
		entropy_retvec_t getAllChunkScores(void);

		entropy_retval_t getDeviation(std::size_t, std::size_t);
		entropy_retvec_t getAllDeviations(std::size_t);
		entropy_retval_t getWholeDeviation(std::size_t);
		
		void calculateDistribution(std::size_t, std::size_t);
		dist_vec_t getDistribution(void) { return m_dist; }
};

#endif
