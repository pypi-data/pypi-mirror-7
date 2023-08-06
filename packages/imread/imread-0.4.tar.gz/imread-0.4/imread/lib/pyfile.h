// Copyright 2014 Luis Pedro Coelho <luis@luispedro.org>
// License: MIT (see COPYING.MIT file)
#ifndef LPC_PYFILE_H_INCLUDE_GUARD_TUE_JAN_14_18_22_59_CET_2014
#define LPC_PYFILE_H_INCLUDE_GUARD_TUE_JAN_14_18_22_59_CET_2014

#include <Python.h>
#include "base.h"

class pyfile_input : public byte_source {
    public:
        pyfile_input(PyObject* file_like)
            :file_like_(file_like)
            {
                Py_INCREF(file_like_);
            }
        ~pyfile_input() {
                Py_DECREF(file_like_);
        }
        virtual size_t read(byte* buffer, size_t n) {

            return ::read(fd_, buffer, n);
        }
    private:
        PyObject* file_like_;
};

#endif // LPC_PYFILE_H_INCLUDE_GUARD_TUE_JAN_14_18_22_59_CET_2014
