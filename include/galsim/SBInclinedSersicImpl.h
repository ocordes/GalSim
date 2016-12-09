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

#ifndef GalSim_SBInclinedSersicImpl_H
#define GalSim_SBInclinedSersicImpl_H

#include "SBProfileImpl.h"
#include "SBInclinedSersic.h"
#include "SBSersicImpl.h"
#include "LRUCache.h"
#include "OneDimensionalDeviate.h"
#include "Table.h"

namespace galsim {

    class SBInclinedSersic::SBInclinedSersicImpl : public SBProfileImpl
    {
    public:
        SBInclinedSersicImpl(double n, Angle inclination, double size, double height,
                RadiusType rType, double flux,
                double trunc, bool flux_untruncated, const GSParamsPtr& gsparams);

        ~SBInclinedSersicImpl() {}

        double xValue(const Position<double>& p) const;
        std::complex<double> kValue(const Position<double>& k) const;

        double maxK() const;
        double stepK() const;

        void getXRange(double& xmin, double& xmax, std::vector<double>& splits) const
        {
            splits.push_back(0.);
            if (!_truncated) { xmin = -integ::MOCK_INF; xmax = integ::MOCK_INF; }
            else { xmin = -_trunc; xmax = _trunc; }
        }

        void getYRange(double& ymin, double& ymax, std::vector<double>& splits) const
        {
            splits.push_back(0.);
            if (!_truncated or _inclination.sin() != 0.) { ymin = -integ::MOCK_INF; ymax = integ::MOCK_INF; }
            else { ymin = -_trunc; ymax = _trunc; }
        }

        void getYRangeX(double x, double& ymin, double& ymax, std::vector<double>& splits) const
        {
            if (!_truncated or _inclination.sin() != 0.) { ymin = -integ::MOCK_INF; ymax = integ::MOCK_INF; }
            else if (std::abs(x) >= _trunc) { ymin = 0; ymax = 0; }
            else { ymax = sqrt(_trunc_sq - x*x);  ymin = -ymax; }

            if (std::abs(x/_re) < 1.e-2) splits.push_back(0.);
        }

        bool isAxisymmetric() const { return false; }
        bool hasHardEdges() const { return _truncated; }
        bool isAnalyticX() const { return false; } // not yet implemented, would require lookup table
        bool isAnalyticK() const { return true; }  // 1d lookup table

        Position<double> centroid() const
        { return Position<double>(0., 0.); }

        /// @brief Returns the true flux (may be different from the specified flux)
        double getFlux() const { return _flux; }
        double maxSB() const;

        /// @brief Sersic photon shooting done by rescaling photons from appropriate `SersicInfo`
        boost::shared_ptr<PhotonArray> shoot(int N, UniformDeviate ud) const;

        /// @brief Returns the Sersic index n
        double getN() const { return _n; }
        /// @brief Returns the inclination angle
        Angle getInclination() const { return _inclination; }
        /// @brief Returns the true half-light radius (may be different from the specified value)
        double getHalfLightRadius() const { return _re; }
        /// @brief Returns the scale radius
        double getScaleRadius() const { return _r0; }
        /// @brief Returns the scale height
        double getScaleHeight() const { return _h0; }
        /// @brief Returns the truncation radius
        double getTrunc() const { return _trunc; }

        // Overrides for better efficiency
        void fillKImage(ImageView<std::complex<double> > im,
                        double kx0, double dkx, int izero,
                        double ky0, double dky, int jzero) const;
        void fillKImage(ImageView<std::complex<double> > im,
                        double kx0, double dkx, double dkxy,
                        double ky0, double dky, double dkyx) const;

        std::string serialize() const;

    private:
        double _n;       ///< Sersic index.
        Angle _inclination; ///< Inclination angle
        double _flux;    ///< Actual flux (may differ from that specified at the constructor).
        double _r0;      ///< Scale radius specified at the constructor.
        double _re;      ///< Half-light radius specified at the constructor.
        double _h0;          ///< Scale height specified at the constructor.
        double _trunc;   ///< The truncation radius (if any)
        bool _truncated; ///< True if this Sersic profile is truncated.

        double _xnorm;     ///< Normalization of xValue relative to what SersicInfo returns.
        double _shootnorm; ///< Normalization for photon shooting.

        double _inv_r0;
        double _inv_exp_re;
        double _half_pi_h_sini_over_r;
        double _cosi;
        double _r0_sq;
        double _inv_r0_sq;
        double _trunc_sq;

        // Some derived values calculated in the constructor:
        double _ksq_max;   ///< If ksq < _kq_min, then use faster taylor approximation for kvalue
        double _ksq_min;   ///< If ksq > _kq_max, then use kvalue = 0
        double _maxk;    ///< Value of k beyond which aliasing can be neglected.
        double _stepk;   ///< Sampling in k space necessary to avoid folding.

        boost::shared_ptr<SersicInfo> _info; ///< Points to info structure for this n,trunc

        // Copy constructor and op= are undefined.
        SBInclinedSersicImpl(const SBInclinedSersicImpl& rhs);
        void operator=(const SBInclinedSersicImpl& rhs);

        // Helper function to get k values
        double kValueHelper(double kx, double ky) const;

        // Helper functor to solve for the proper _maxk
        class SBInclinedSersicKValueFunctor
        {
            public:
                SBInclinedSersicKValueFunctor(const SBInclinedSersic::SBInclinedSersicImpl * p_owner,
            double target_k_value);
            double operator() (double k) const;
            private:
            const SBInclinedSersic::SBInclinedSersicImpl * _p_owner;
            double _target_k_value;
        };

        friend class SBInclinedSersicKValueFunctor;

        static LRUCache<boost::tuple< double, double, GSParamsPtr >, SersicInfo> cache;

    };
}

#endif
