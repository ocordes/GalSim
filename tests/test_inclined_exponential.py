# Copyright (c) 2012-2016 by the GalSim developers team on GitHub
# https://github.com/GalSim-developers
#
# This file is part of GalSim: The modular galaxy image simulation toolkit.
# https://github.com/GalSim-developers/GalSim
#
# GalSim is free software: redistribution and use in source and binary forms,
# with or without modification, are permitted provided that the following
# conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions, and the disclaimer given in the accompanying LICENSE
#    file.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions, and the disclaimer given in the documentation
#    and/or other materials provided with the distribution.
#

"""This file contains tests for the InclinedExponential class. Since the InclinedSersic
   class is a generalization of this, we test it here as well in the case where we expect
   it to behave the same.
"""

from __future__ import print_function
import numpy as np
import os
import sys
from copy import deepcopy

from galsim_test_helpers import *

try:
    import galsim
except ImportError:
    path, filename = os.path.split(__file__)
    sys.path.append(os.path.abspath(os.path.join(path, "..")))
    import galsim
    
save_profiles = True

# set up any necessary info for tests
# Note that changes here should match changes to test image files
image_dir = './inclined_exponential_images'

# Values here are strings, so the filenames will be sure to work (without truncating zeros)
fluxes = ("1.0", "10.0", "0.1", "1.0", "1.0", "1.0")
image_inc_angles = ("0.0", "1.3", "0.2", "0.01", "0.1", "0.78")
image_scale_radii = ("3.0", "3.0", "3.0", "3.0", "2.0", "2.0")
image_scale_heights = ("0.3", "0.5", "0.5", "0.5", "1.0", "0.5")
image_pos_angles = ("0.0", "0.0", "0.0", "0.0", "-0.2", "-0.2")
image_nx = 64
image_ny = 64

def get_prof(mode, *args, **kwargs):
    """Function to get either InclinedExponential or InclinedSersic (with n=1, trunc=0)
       depending on mode
    """
    if mode=="InclinedSersic":
        new_kwargs = deepcopy(kwargs)
        if len(args)>0:
            new_kwargs["inclination"] = args[0]
        if len(args)>1:
            new_kwargs["scale_radius"] = args[1]
        if len(args)>2:
            new_kwargs["scale_height"] = args[2]
            
        if not "trunc" in new_kwargs:
            new_kwargs["trunc"] = 0.
        if not "n" in new_kwargs:
            new_kwargs["n"] = 1.
            
        prof = galsim.InclinedSersic(**new_kwargs)
    else:
        new_kwargs = deepcopy(kwargs)
        if "trunc" in new_kwargs:
            del new_kwargs["trunc"]
        if "n" in new_kwargs:
            del new_kwargs["n"]
        prof = galsim.InclinedExponential(*args,**new_kwargs)
        
    return prof

@timer
def test_regression():
    """Test that the inclined exponential profile matches the results from Lance Miller's code.
       Reference images are provided in the ./inclined_exponential_images directory, as well as
       the code ('hankelcode.c') used to generate them."""
       
    for mode in ("InclinedExponential","InclinedSersic"):
    
        for inc_angle, scale_radius, scale_height, pos_angle in zip(image_inc_angles,
                                                                    image_scale_radii,
                                                                    image_scale_heights,
                                                                    image_pos_angles):
    
            image_filename = "galaxy_"+inc_angle+"_"+scale_radius+"_"+scale_height+"_"+pos_angle+".fits"
            print("Comparing "+mode+" against "+image_filename+"...")
            
            image = galsim.fits.read(image_filename, image_dir)
    
            # Get float values for the details
            inc_angle=float(inc_angle)
            scale_radius=float(scale_radius)
            scale_height=float(scale_height)
            pos_angle=float(pos_angle)
    
            # Now make a test image
            test_profile = get_prof(mode, inc_angle*galsim.radians, scale_radius,
                                    scale_height)
            check_basic(test_profile, mode)
    
            # Rotate it by the position angle
            test_profile = test_profile.rotate(pos_angle*galsim.radians)
            
            # Draw it onto an image
            test_image = galsim.Image(image_nx,image_ny,scale=1.0)
            test_profile.drawImage(test_image,offset=(0.5,0.5)) # Offset to match Lance's
            
            # Save if desired
            if save_profiles:
                test_image_filename = image_filename.replace(".fits","_"+mode+".fits")
                test_image.write(test_image_filename, image_dir, clobber=True)
    
            # Compare to the example - Due to the different fourier transforms used, some offset is
            # expected, so we just compare in the core to two decimal places
    
            image_core = image.array[image_ny//2-2:image_ny//2+3, image_nx//2-2:image_nx//2+3]
            test_image_core = test_image.array[image_ny//2-2:image_ny//2+3, image_nx//2-2:image_nx//2+3]
    
            ratio_core = image_core / test_image_core
    
            np.testing.assert_array_almost_equal(
                    ratio_core, np.mean(ratio_core)*np.ones_like(ratio_core),
                    decimal = 2,
                    err_msg = "Error in comparison of "+mode+" profile to "+image_filename,
                    verbose=True)

@timer
def test_exponential():
    """ Test that InclinedExponential looks identical to an exponential when inclination is zero.
    """

    scale_radius = 3.0
    
    # Prepare the exponential profile's image
    exp_profile = galsim.Exponential(scale_radius=scale_radius)
    exp_image = galsim.Image(image_nx, image_ny, scale=1.0)
    exp_profile.drawImage(exp_image)
       
    mode = "InclinedExponential"

    inc_profile = get_prof(mode,0*galsim.radians, scale_radius=scale_radius,
                                                 scale_height=scale_radius/10.)

    inc_image = galsim.Image(image_nx, image_ny, scale=1.0)

    inc_profile.drawImage(inc_image)

    # Check that they're the same
    np.testing.assert_array_almost_equal(inc_image.array, exp_image.array, decimal=4)

    # The face-on version should get the maxSB value exactly right.
    np.testing.assert_array_almost_equal(inc_profile.maxSB(), exp_profile.maxSB())

    check_basic(inc_profile, "Face-on "+ mode)

@timer
def test_sersic():
    """ Test that InclinedSersic looks identical to a Sersic when inclination is zero. 
    """
    
    ns = (1.1, 1.1, 2.5, 2.5)
    truncs = (0, 13.5, 0, 18.0)
    scale_radius = 1.0
    
    for n, trunc in zip(ns,truncs):
    
        # Prepare the sersic profile's image
        sersic_profile = galsim.Sersic(n=n, scale_radius=scale_radius, trunc=trunc)
        sersic_image = galsim.Image(image_nx, image_ny, scale=1.0)
        sersic_profile.drawImage(sersic_image)
        
        mode = "InclinedSersic"
    
        inc_profile = get_prof(mode,n=n,trunc=trunc, inclination=0*galsim.radians, scale_radius=scale_radius,
                               scale_height=scale_radius/10.)
    
        inc_image = galsim.Image(image_nx, image_ny, scale=1.0)
    
        inc_profile.drawImage(inc_image)
        
        if save_profiles:
            sersic_image.write("test_sersic.fits", image_dir, clobber=True)
            inc_image.write("test_inclined_sersic.fits", image_dir, clobber=True)
    
        # Check that they're the same. Note that since the inclined Sersic profile isn't
        # Real-space analytic and has hard edges in the truncated case,
        # we have to be a bit lax on rtol and atol
        if trunc != 0:
            rtol = 5e-3
            atol = 5e-5
        else:
            rtol = 1e-3
            atol = 1e-5
            
        d_array = atol + rtol*np.abs(sersic_image.array)
        badness_array = np.abs(inc_image.array-sersic_image.array)/d_array
            
        np.testing.assert_allclose(inc_image.array, sersic_image.array, rtol=rtol, atol=atol)
    
        # The face-on version should get the maxSB value exactly right.
        np.testing.assert_almost_equal(inc_profile.maxSB(), sersic_profile.maxSB())
    
        check_basic(inc_profile, "Face-on "+ mode)

@timer
def test_edge_on():
    """ Test that an edge-on profile looks similar to an almost-edge-on profile, and doesn't crash.
    """

    scale_radius = 3.0

    inclinations = (np.arccos(0.01),2*np.pi-np.arccos(0.01),np.pi/2.)
    
    for mode in ("InclinedExponential","InclinedSersic"):

        images = []
    
        for inclination in inclinations:
            # Set up the profile
            prof = get_prof(mode,inclination*galsim.radians, scale_radius=scale_radius,
                            scale_h_over_r=0.1)
    
            check_basic(prof, "Edge-on "+mode)
    
            # Draw an image of it
            image = galsim.Image(image_nx,image_ny,scale=1.0)
            prof.drawImage(image)
    
            # Add it to the list of images
            images.append(image.array)
    
        # Check they're all almost the same
        np.testing.assert_array_almost_equal(images[1], images[0], decimal=2)
        np.testing.assert_array_almost_equal(images[1], images[2], decimal=2)
    
        # Also the edge-on version should get the maxSB value exactly right = exp.maxSB * r/h.
        exp = galsim.Exponential(scale_radius=scale_radius)
        np.testing.assert_array_almost_equal(prof.maxSB(), exp.maxSB() / 0.1)
        prof.drawImage(image, method='sb', use_true_center=False)
        print('max pixel: ',image.array.max(),' cf.',prof.maxSB())
        np.testing.assert_allclose(image.array.max(), prof.maxSB(), rtol=0.01)


@timer
def test_sanity():
    """ Performs various sanity checks on a set of InclinedExponential and InclinedSersic profiles. """
    
    for mode in ("InclinedExponential","InclinedSersic"):

        print('flux, inc_angle, scale_radius, scale_height, pos_angle')
        for flux, inc_angle, scale_radius, scale_height, pos_angle in zip(fluxes,
                                                                          image_inc_angles,
                                                                          image_scale_radii,
                                                                          image_scale_heights,
                                                                          image_pos_angles):
    
            # Get float values for the details
            flux = float(flux)
            inc_angle=float(inc_angle)
            scale_radius=float(scale_radius)
            scale_height=float(scale_height)
            pos_angle=float(pos_angle)
            print(flux, inc_angle, scale_radius, scale_height, pos_angle)
    
            # Now make a test image
            test_profile = get_prof(mode,inc_angle*galsim.radians, scale_radius,
                                    scale_height, flux=flux)
    
            check_basic(test_profile, mode)
    
            # Check that h/r is properly given by the method and property for it
            np.testing.assert_almost_equal(test_profile.scale_height/test_profile.scale_radius,
                                           test_profile.scale_h_over_r)
            np.testing.assert_almost_equal(test_profile.getScaleHeight()/test_profile.getScaleRadius(),
                                           test_profile.getScaleHOverR())
    
            # Rotate it by the position angle
            test_profile = test_profile.rotate(pos_angle*galsim.radians)
    
            # Check that the k value for (0,0) is the flux
            np.testing.assert_almost_equal(test_profile.kValue(kx=0.,ky=0.),flux)
    
            # Check that the drawn flux for a large image is indeed the flux
            test_image = galsim.Image(5*image_nx,5*image_ny,scale=1.0)
            test_profile.drawImage(test_image)
            test_flux = test_image.array.sum()
            np.testing.assert_almost_equal(test_flux,flux,decimal=3)
    
            # Check that the centroid is (0,0)
            centroid = test_profile.centroid()
            np.testing.assert_equal(centroid.x, 0.)
            np.testing.assert_equal(centroid.y, 0.)
    
            # Check maxSB
            # We don't do a great job at estimating this, but it should be in the right ball park,
            # and typically too large.
            test_profile.drawImage(test_image, method='sb', use_true_center=False)
            print('max pixel: ',test_image.array.max(),' cf.',test_profile.maxSB())
            np.testing.assert_allclose(test_image.array.max(), test_profile.maxSB(), rtol=0.3)
            np.testing.assert_array_less(test_image.array.max(), test_profile.maxSB())


@timer
def test_k_limits():
    """ Check that the maxk and stepk give reasonable results for a few different profiles. """
    
    for mode in ("InclinedExponential","InclinedSersic"):

        for inc_angle, scale_radius, scale_height in zip(image_inc_angles,image_scale_radii,
                                                         image_scale_heights):
            # Get float values for the details
            inc_angle=float(inc_angle)
            scale_radius=float(scale_radius)
            scale_height=float(scale_height)
    
            gsparams = galsim.GSParams()
    
            # Now make a test image
            test_profile = get_prof(mode,inc_angle*galsim.radians, scale_radius,
                                    scale_height)
    
            # Check that the k value at maxK() is below maxk_threshold in both the x and y dimensions
            kx = test_profile.maxK()
            ky = test_profile.maxK()
    
            kx_value=test_profile.kValue(kx=kx,ky=0.)
            np.testing.assert_(np.abs(kx_value)<gsparams.maxk_threshold,
                               msg="kx_value is not below maxk_threshold: " + str(kx_value) + " >= "
                                + str(gsparams.maxk_threshold))
    
            ky_value=test_profile.kValue(kx=0.,ky=ky)
            np.testing.assert_(np.abs(ky_value)<gsparams.maxk_threshold,
                               msg="ky_value is not below maxk_threshold: " + str(ky_value) + " >= "
                                + str(gsparams.maxk_threshold))
    
            # Check that less than folding_threshold fraction of light falls outside r = pi/stepK()
            rmax = np.pi/test_profile.stepK()
    
            test_image = galsim.Image(int(10*rmax),int(10*rmax),scale=1.0)
            test_profile.drawImage(test_image)
    
            image_center = test_image.center()
    
            # Get an array of indices within the limits
            image_shape = np.shape(test_image.array)
            x, y = np.indices(image_shape, dtype=float)
    
            x -= image_center.x
            y -= image_center.y
    
            r = np.sqrt(np.square(x)+np.square(y))
    
            good = r<rmax
    
            # Get flux within the limits
            contained_flux = np.ravel(test_image.array)[np.ravel(good)].sum()
    
            # Check that we're not missing too much flux
            total_flux = 1.
            np.testing.assert_((total_flux-contained_flux)/(total_flux)<gsparams.folding_threshold,
                               msg="Too much flux lost due to folding.\nFolding threshold = " +
                               str(gsparams.folding_threshold) + "\nTotal flux = " +
                               str(total_flux) + "\nContained flux = " + str(contained_flux) +
                               "\nLost = " + str((total_flux-contained_flux)/(total_flux)))

@timer
def test_eq_ne():
    """ Check that equality/inequality works as expected."""
    gsp = galsim.GSParams(folding_threshold=1.1e-3)
    
    for mode in ("InclinedExponential","InclinedSersic"):

        # First test that some different initializations that should be equivalent:
        same_gals = [get_prof(mode,0.1*galsim.radians, 3.0),
                get_prof(mode,0.1*galsim.radians, 3.0, 0.3),  # default h/r = 0.1
                get_prof(mode,0.1*galsim.radians, 3.0, scale_height=0.3),
                get_prof(mode,0.1*galsim.radians, 3.0, scale_h_over_r=0.1),
                get_prof(mode,0.1*galsim.radians, 3.0, flux=1.0),  # default flux=1
                get_prof(mode,-0.1*galsim.radians, 3.0),  # negative i is equivalent
                get_prof(mode,(np.pi--0.1)*galsim.radians, 3.0),  # also pi-theta
                get_prof(mode,18./np.pi*galsim.degrees, 3.0),
                get_prof(mode,inclination=0.1*galsim.radians, scale_radius=3.0,
                                           scale_height=0.3, flux=1.0),
                get_prof(mode,flux=1.0, scale_radius=3.0,
                                           scale_height=0.3, inclination=0.1*galsim.radians)]
    
        for gal in same_gals[1:]:
            print(gal)
            gsobject_compare(gal, same_gals[0])
    
        diff_gals = [get_prof(mode,0.1*galsim.radians, 3.0, 0.3),
                get_prof(mode,0.1*galsim.degrees, 3.0, 0.3),
                get_prof(mode,0.1*galsim.degrees, 3.0, scale_h_over_r=0.2),
                get_prof(mode,0.1*galsim.radians, 3.0, 3.0),
                get_prof(mode,0.2*galsim.radians, 3.0, 0.3),
                get_prof(mode,0.1*galsim.radians, 3.1, 0.3),
                get_prof(mode,0.1*galsim.radians, 3.1),
                get_prof(mode,0.1*galsim.radians, 3.0, 0.3, flux=0.5),
                get_prof(mode,0.1*galsim.radians, 3.0, 0.3, gsparams=gsp)]
        all_obj_diff(diff_gals)

@timer
def test_pickle():
    """ Check that we can pickle it. """
    
    for mode in ("InclinedExponential","InclinedSersic"):

        prof = get_prof(mode,trunc=4.5,inclination=0.1*galsim.radians, scale_radius=3.0,
                                         scale_height=0.3)
        do_pickle(prof)
        do_pickle(prof.SBProfile)
        do_pickle(get_prof(mode,trunc=4.5,inclination=0.1*galsim.radians, scale_radius=3.0))
        do_pickle(get_prof(mode,trunc=4.5,inclination=0.1*galsim.radians, scale_radius=3.0,
                                             scale_h_over_r=0.2))
        do_pickle(get_prof(mode,trunc=4.5,inclination=0.1*galsim.radians, scale_radius=3.0,
                                             scale_height=0.3, flux=10.0))
        do_pickle(get_prof(mode,trunc=4.5,inclination=0.1*galsim.radians, scale_radius=3.0,
                                             scale_height=0.3,
                                             gsparams=galsim.GSParams(folding_threshold=1.1e-3)))
        do_pickle(get_prof(mode,trunc=4.5,inclination=0.1*galsim.radians, scale_radius=3.0,
                                             scale_height=0.3, flux=10.0,
                                             gsparams=galsim.GSParams(folding_threshold=1.1e-3)))

if __name__ == "__main__":
    test_sanity()
    test_k_limits()
    test_eq_ne()
    test_pickle()
    test_exponential()
    test_sersic()
    test_edge_on()
    test_regression()
