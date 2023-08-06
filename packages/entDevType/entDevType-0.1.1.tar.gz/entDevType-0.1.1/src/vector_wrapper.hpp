#ifndef HAVE_VECTOR_WRAPPER_HPP
#define HAVE_VECTOR_WRAPPER_HPP

#include <vector>
#include <algorithm>
#include <cstdint>

#include <boost/python.hpp>

/* 
	XXX:
		The documentation for writing converters is horribly horrible. This code probably has bugs. 
		
		Specifically while I ensure that the reference counters are incremented on the PyObject's
		I'm not 100% that they are properly decremented, although I believe that will occur
		when the handles go out of scope.
		
		I also should double check the placement new's.

		All in all, the code works for me, but hasn't been extensively tested and I'd advise you
		to look deeply into the implementation below and cross-reference boost::python before you
		use the code in production or similar.
		
		YMMV / You have been warned.

		-jf / 03-Aug-2014
*/

template< typename T >
struct vector_to_string {
	static PyObject*
	convert(const std::vector< T >& v)
	{
		return boost::python::incref(boost::python::str(reinterpret_cast< const char* >(v.data()), v.size()).ptr());	
	}
};

template< typename T >
struct vector_from_string {
	vector_from_string(void) 
	{
		boost::python::converter::registry::push_back(	&vector_from_string::convertible, 
														&vector_from_string::construct,
														boost::python::type_id< std::vector< T > >()
		);

		return;
	}

	static void*
	convertible(PyObject* obj)
	{
		if (nullptr == obj || ! PyString_Check(obj))
			return nullptr;

		return obj;
	}

	static void
	construct(PyObject* obj, boost::python::converter::rvalue_from_python_stage1_data* data)
	{
		boost::python::handle<> handle(boost::python::borrowed(obj));
		const char* 			value 	= PyString_AsString(obj);
		ssize_t 				le 		= PyString_Size(obj);	

		if (nullptr == value || nullptr == data) {
			PyErr_SetString(PyExc_ValueError, "An error occurred while converting a Python object to a C++ object.");
			boost::python::throw_error_already_set();
			return;
		}

		void* storage = ((boost::python::converter::rvalue_from_python_storage< std::vector< T > >*)data)->storage.bytes;
        std::vector< T >& v = *(new (storage) std::vector< T >());

        v.resize(le);

		for(int i = 0;i!=le;++i)
			v[i] = value[i];

        data->convertible = storage;
		return;
	}
};

template< typename T >
struct vector_to_list {

	static PyObject* 
	convert(std::vector< T > const& v)
	{
		boost::python::list l;
		typename std::vector< T >::const_iterator p;

		for(p = v.begin(); p != v.end(); p++)
			l.append(boost::python::object(*p));
		
		return boost::python::incref(l.ptr());
	}
};
 
template< typename T >
struct vector_from_list {

	vector_from_list(void)
	{
		boost::python::converter::registry::push_back(	&vector_from_list< T >::convertible, 
														&vector_from_list< T >::construct, 
														boost::python::type_id<std::vector< T > >()
		);

	}


	static void* 
	convertible(PyObject* obj)
	{

		if (! PyList_Check(obj))
			return nullptr;

		return obj;
	}
 
	static void 
	construct(PyObject* obj, boost::python::converter::rvalue_from_python_stage1_data* data)
	{
		boost::python::list l(boost::python::handle< >(boost::python::borrowed(obj)));
		void* 				storage(nullptr); 
		int					le(len(l));

		if (nullptr == data) {
			PyErr_SetString(PyExc_ValueError, "An error occurred while converting a Python object to a C++ object.");
			boost::python::throw_error_already_set();
			return;
		}

		storage = ((boost::python::converter::rvalue_from_python_storage<std::vector<T> >*)data)->storage.bytes;
 
		std::vector<T>& v = *(new (storage) std::vector<T>());
 
		v.resize(le);
      
		for(int i = 0;i!=le;++i)
			v[i] = boost::python::extract<T>(l[i]);

		data->convertible = storage;
		return;
	}
};
 
#endif
