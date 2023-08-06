#ifndef HAVE_DIST_HPP
#define HAVE_DIST_HPP

#include <cstdint>

struct dist_t {
	uint8_t		value;
	std::size_t 	count;

	dist_t(void) : value(0), count(0) { return; }
	dist_t(uint8_t v, std::size_t c) : value(v), count(c) { return; }
	~dist_t(void) { return; }
	uint8_t getValue(void) { return value; }
	void setValue(uint8_t v) { value = v; return; }
	std::size_t getCount(void) { return count; }
	void setCount(std::size_t c) { count = c; return; }
};

#endif
