#include "entropy_wrapper.hpp"

entropy_wrapper_t::entropy_wrapper_t(std::size_t bs) : m_wholeDone(false), m_entdev(bs)
{
	return;
}

entropy_wrapper_t::entropy_wrapper_t(const std::vector< uint8_t >& v, std::size_t bs, bool whole) : m_wholeDone(false), 
																									m_entdev(bs), 
																									m_data(v)
{
	m_cvec = m_entdev.slice(v, bs);

	if (true == whole) {
		m_entdev.reset();
		m_entdev.update(v.data(), v.size());
		m_whole = m_entdev.getValues();
		m_entdev.reset();
		m_wholeDone = true;
	}

	return;
}

entropy_wrapper_t::~entropy_wrapper_t(void)
{
	m_cvec.clear();
	m_retvec.clear();

	return;
}

void
entropy_wrapper_t::reset(void)
{
	m_entdev.reset();
	return;
}

void
entropy_wrapper_t::setDataOverload(const std::vector< uint8_t >& v)
{
	setData(v);
}

void
entropy_wrapper_t::setData(const std::vector< uint8_t >& v, std::size_t bs, bool whole) 
{
	m_data = v;

	m_cvec.clear();
	m_cvec = m_entdev.slice(v, bs);

	if (true == whole) {
		m_entdev.reset();
		m_entdev.update(v.data(), v.size());
		m_whole = m_entdev.getValues();
		m_entdev.reset();
		m_wholeDone = true;	
	} 
		

	return;
}

std::size_t
entropy_wrapper_t::getCount(void)
{
	return m_cvec.size();
}

std::size_t
entropy_wrapper_t::getMaxIndex(void)
{
	if (! getCount())
		return 0;

	return m_cvec.size()-1;
}

void
entropy_wrapper_t::calculate(void)
{
	calculate(0, m_cvec.size());
	return;
}

void
entropy_wrapper_t::calculate(std::size_t ce)
{
	if (ce >= m_cvec.size()) {
		PyErr_SetString(PyExc_ValueError, "The index specified is invalid");
		boost::python::throw_error_already_set();
		return;
	}

	calculate(0, ce);
	return;
}		

void
entropy_wrapper_t::calculateDistribution(std::size_t cs, std::size_t ce)
{
    if (cs > ce) {
        PyErr_SetString(PyExc_ValueError, "The start index is greater than the end index and thus invalid");
        boost::python::throw_error_already_set();
        return;
    }

    if (cs >= m_cvec.size() || ce > m_cvec.size()) {
        PyErr_SetString(PyExc_ValueError, "One or more of the indicies specified is invalid");
        boost::python::throw_error_already_set();
        return;
    }

    m_entdev.reset();
    m_dist.clear();

    for (auto idx = cs; idx < ce; idx++) {
        chunk_t& cvec = m_cvec.at(idx);
        m_entdev.update(cvec);
        //m_retvec.push_back(m_entdev.getValues());
        //m_entdev.reset();
        //m_dist = m_entdev.getDistribution();
    }

	m_dist = m_entdev.getDistribution();
	m_entdev.reset();

    return;
}

void
entropy_wrapper_t::calculate(std::size_t cs, std::size_t ce)
{
	if (cs > ce) {
		PyErr_SetString(PyExc_ValueError, "The start index is greater than the end index and thus invalid");
		boost::python::throw_error_already_set();
		return;			
	}

	if (cs >= m_cvec.size() || ce > m_cvec.size()) {
		PyErr_SetString(PyExc_ValueError, "One or more of the indicies specified is invalid");
		boost::python::throw_error_already_set();
		return;
	}

	m_entdev.reset();

	for (auto idx = cs; idx < ce; idx++) {
		chunk_t& cvec = m_cvec.at(idx);
		m_entdev.update(cvec);
		m_retvec.push_back(m_entdev.getValues());
		m_entdev.reset();
	}

	return;
}

entropy_retval_t
entropy_wrapper_t::getChunkScore(std::size_t v1)
{
	if (v1 >= m_retvec.size()) {
		PyErr_SetString(PyExc_ValueError, "The index specified is invalid");
		boost::python::throw_error_already_set();
		return entropy_retval_t();
	}

	return m_retvec.at(v1);
}

entropy_retval_t
entropy_wrapper_t::getWholeFileScore(void)
{
	if (false == m_wholeDone) {
        m_entdev.reset();
        m_entdev.update(m_data.data(), m_data.size());
        m_whole = m_entdev.getValues();
        m_entdev.reset();
        m_wholeDone = true;
	}

	return m_whole;
}

entropy_retvec_t
entropy_wrapper_t::getAllChunkScores(void)
{
	return m_retvec;
}

entropy_retval_t
entropy_wrapper_t::getDeviation(std::size_t v1, std::size_t v2)
{
	if (v1 >= m_retvec.size() || v2 >= m_retvec.size()) {
		PyErr_SetString(PyExc_ValueError, "One or more of the indicies specified is invalid");
		boost::python::throw_error_already_set();
		return entropy_retval_t();
	}
	
	return m_entdev.getBlockDeviation(m_retvec.at(v1), m_retvec.at(v2));
}


entropy_retvec_t
entropy_wrapper_t::getAllDeviations(std::size_t v1)
{
	if (v1 >= m_retvec.size()) {
		PyErr_SetString(PyExc_ValueError, "The index specified is invalid");
		boost::python::throw_error_already_set();
		return entropy_retvec_t();
	}

	return m_entdev.getBlockDeviationFromAllBlocks(m_retvec, v1);
}

entropy_retval_t
entropy_wrapper_t::getWholeDeviation(std::size_t v1)
{
	if (v1 >= m_retvec.size()) {
		PyErr_SetString(PyExc_ValueError, "The index specified is invalid");
		boost::python::throw_error_already_set();
		return entropy_retval_t();
	}

	if (false == m_wholeDone) {
        m_entdev.reset();
        m_entdev.update(m_data.data(), m_data.size());
        m_whole = m_entdev.getValues();
        m_entdev.reset();
        m_wholeDone = true;	
	}

	return m_entdev.getBlockDeviation(m_whole, m_retvec.at(v1));
}

