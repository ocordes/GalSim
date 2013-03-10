// -*- c++ -*-
/*
 * Copyright 2012, 2013 The GalSim developers:
 * https://github.com/GalSim-developers
 *
 * This file is part of GalSim: The modular galaxy image simulation toolkit.
 *
 * GalSim is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * GalSim is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with GalSim.  If not, see <http://www.gnu.org/licenses/>
 */

#ifndef SBCONVOLVE_IMPL_H
#define SBCONVOLVE_IMPL_H

#include "SBProfileImpl.h"
#include "SBConvolve.h"

namespace galsim {

    class SBConvolve::SBConvolveImpl: public SBProfileImpl
    {
    public:

        SBConvolveImpl(const std::list<SBProfile>& slist, bool real_space,
                       boost::shared_ptr<GSParams> gsparams);
        ~SBConvolveImpl() {}

        void add(const SBProfile& rhs); 

        // Do the real-space convolution to calculate this.
        double xValue(const Position<double>& p) const;

        std::complex<double> kValue(const Position<double>& k) const;

        bool isAxisymmetric() const { return _isStillAxisymmetric; }
        bool hasHardEdges() const { return false; }
        bool isAnalyticX() const { return _real_space; }
        bool isAnalyticK() const { return !_real_space; }    // convolvees must all meet this
        double maxK() const { return _minMaxK; }
        double stepK() const { return _netStepK; }

        void getXRange(double& xmin, double& xmax, std::vector<double>& splits) const 
        { 
            // Getting the splits correct would require a bit of work.
            // So if we ever do real-space convolutions where one of the elements 
            // is (or includes) another convolution, we might want to rework this a 
            // bit.  But I don't think this is really every going to be used, so
            // I didn't try to get that right.  (Note: ignoring the splits won't be
            // wrong -- just not optimal.)
            std::vector<double> splits0;
            ConstIter pptr = _plist.begin();
            pptr->getXRange(xmin,xmax,splits0);
            for (++pptr; pptr!=_plist.end(); ++pptr) {
                double xmin_1, xmax_1;
                pptr->getXRange(xmin_1,xmax_1,splits0);
                xmin += xmin_1;
                xmax += xmax_1;
            }
        }

        void getYRange(double& ymin, double& ymax, std::vector<double>& splits) const 
        {
            std::vector<double> splits0;
            ConstIter pptr = _plist.begin();
            pptr->getYRange(ymin,ymax,splits0);
            for (++pptr; pptr!=_plist.end(); ++pptr) {
                double ymin_1, ymax_1;
                pptr->getYRange(ymin_1,ymax_1,splits0);
                ymin += ymin_1;
                ymax += ymax_1;
            }
        }

        void getYRangeX(double x, double& ymin, double& ymax, std::vector<double>& splits) const 
        {
            std::vector<double> splits0;
            ConstIter pptr = _plist.begin();
            pptr->getYRangeX(x,ymin,ymax,splits0);
            for (++pptr; pptr!=_plist.end(); ++pptr) {
                double ymin_1, ymax_1;
                pptr->getYRangeX(x,ymin_1,ymax_1,splits0);
                ymin += ymin_1;
                ymax += ymax_1;
            }
        }

        Position<double> centroid() const 
        { return Position<double>(_x0, _y0); }

        double getFlux() const { return _fluxProduct; }

        double getPositiveFlux() const;
        double getNegativeFlux() const;
        /**
         * @brief Shoot photons through this SBConvolve.
         *
         * SBConvolve will add the displacements of photons generated by each convolved component.
         * Their fluxes are multiplied (modulo factor of N).
         * @param[in] N Total number of photons to produce.
         * @param[in] ud UniformDeviate that will be used to draw photons from distribution.
         * @returns PhotonArray containing all the photons' info.
         */
        boost::shared_ptr<PhotonArray> shoot(int N, UniformDeviate ud) const;

        void fillKGrid(KTable& kt) const;

    private:
        typedef std::list<SBProfile>::iterator Iter;
        typedef std::list<SBProfile>::const_iterator ConstIter;

        std::list<SBProfile> _plist; ///< list of profiles to convolve
        double _x0; ///< Centroid position in x.
        double _y0; ///< Centroid position in y.
        bool _isStillAxisymmetric; ///< Is output SBProfile shape still circular?
        double _minMaxK; ///< Minimum maxK() of the convolved SBProfiles.
        double _netStepK; ///< Minimum stepK() of the convolved SBProfiles.
        double _sumMinX; ///< sum of minX() of the convolved SBProfiles.
        double _sumMaxX; ///< sum of maxX() of the convolved SBProfiles.
        double _sumMinY; ///< sum of minY() of the convolved SBProfiles.
        double _sumMaxY; ///< sum of maxY() of the convolved SBProfiles.
        double _fluxProduct; ///< Flux of the product.
        bool _real_space; ///< Whether to do convolution as an integral in real space.

        void initialize();

        // Copy constructor and op= are undefined.
        SBConvolveImpl(const SBConvolveImpl& rhs);
        void operator=(const SBConvolveImpl& rhs);
    };
}

#endif // SBCONVOLVE_IMPL_H

