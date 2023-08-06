#ifndef HAVE_ENTROPY_CHUNK_WRAPPER_HPP
#define HAVE_ENTROPY_CHUNK_WRAPPER_HPP

#include <cstdint>
#include <vector>
#include <memory>

typedef std::shared_ptr< uint8_t > byte_buf_t;

struct chunk_t {
	byte_buf_t  buf;
	std::size_t len;

	chunk_t(void) : buf(nullptr), len(0) { return; }

	chunk_t(const std::vector< uint8_t >& v) : buf(new uint8_t[v.size()]), len(v.size())
	{
		::memcpy(buf.get(), v.data(), len);
		return;
	}

	~chunk_t(void)
	{
		len = 0;
		buf = nullptr;

		return;
	}
};


#endif
