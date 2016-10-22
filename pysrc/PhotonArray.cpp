/* -*- c++ -*-
 * Copyright (c) 2012-2016 by the GalSim developers team on GitHub
 * https://github.com/GalSim-developers
 *
 * This file is part of GalSim: The modular galaxy image simulation toolkit.
 * https://github.com/GalSim-developers/GalSim
 *
 * GalSim is free software: redistribution and use in source and binary forms,
 * with or without modification, are permitted provided that the following
 * conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this
 *    list of conditions, and the disclaimer given in the accompanying LICENSE
 *    file.
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions, and the disclaimer given in the documentation
 *    and/or other materials provided with the distribution.
 */

#include "galsim/IgnoreWarnings.h"

#define BOOST_NO_CXX11_SMART_PTR
#include <boost/python.hpp> // header that includes Python.h always needs to come first
#include <boost/python/stl_iterator.hpp>

#include "PhotonArray.h"
#include "NumpyHelper.h"

namespace bp = boost::python;

namespace galsim {
namespace {

    struct PyPhotonArray {

        template <typename U, typename W>
        static void wrapTemplates(W & wrapper) {
            wrapper
                .def("addTo",
                     (double (PhotonArray::*)(ImageView<U>) const)&PhotonArray::addTo,
                     (bp::arg("image")),
                     "Add flux of photons to an image by binning into pixels.")
                ;
        }

        static void wrap()
        {
            bp::class_<PhotonArray> pyPhotonArray("PhotonArray", bp::no_init);
            pyPhotonArray
                .def(bp::init<int>(bp::args("N")))
                .def("size", &PhotonArray::size,
                     "Return the number of photons")
                .def("reserve", &PhotonArray::reserve, (bp::arg("N")),
                     "Reserve space for N photons")
                .def("setPhoton", &PhotonArray::setPhoton,
                     (bp::arg("i"), bp::arg("x"), bp::arg("y"), bp::arg("flux")),
                     "Set x,y,flux for photon number i")
                .def("getX", &PhotonArray::getX, (bp::arg("i")),
                     "Get x for photon number i")
                .def("getY", &PhotonArray::getY, (bp::arg("i")),
                     "Get y for photon number i")
                .def("getFlux", &PhotonArray::getFlux, (bp::arg("i")),
                     "Get flux for photon number i")
                .def("getTotalFlux", &PhotonArray::getTotalFlux,
                     "Return the total flux of all photons")
                .def("setTotalFlux", &PhotonArray::setTotalFlux, (bp::arg("flux")),
                     "Set the total flux to a new value")
                .def("scaleFlux", &PhotonArray::scaleFlux, (bp::arg("scale")),
                     "Scale the total flux by a given factor")
                .def("append", &PhotonArray::append, (bp::arg("rhs")),
                     "Append the contents of another PhotonArray to this one.")
                .enable_pickling()
                ;
            bp::register_ptr_to_python< boost::shared_ptr<PhotonArray> >();
            wrapTemplates<double>(pyPhotonArray);
            wrapTemplates<float>(pyPhotonArray);
        }

    }; // struct PyPhotonArray

} // anonymous

void pyExportPhotonArray()
{
    PyPhotonArray::wrap();
}

} // namespace galsim