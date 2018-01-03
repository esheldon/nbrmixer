from __future__ import print_function
import numpy
import esutil as eu
import fitsio

def add_true_shear(data, run, index):
    """
    get the matched catalog and add the shear
    """
    import nbrsim
    matched_file = nbrsim.files.get_sxcat_match_file(run, index)

    matched_data = fitsio.read(matched_file)

    assert numpy.all(data['number'] == matched_data['number'])

    add_dt=[
        ('sxflags','i4'),
        ('shear_true','f8',2),
        ('shear_index','i2'),
    ]
    newdata = eu.numpy_util.add_fields(data, add_dt)

    newdata['sxflags']     = matched_data['flags']
    newdata['shear_index'] = matched_data['shear_index']
    newdata['shear_true']  = matched_data['shear_true']

    return newdata


def match_truth(data, run, index, radius=8):
    """
    get the sextractor catalog, which should align with this one.

    match x,y to the truth catalog

    copy in shear and shear_index
    """
    import nbrsim

    sx_file = nbrsim.files.get_sxcat_file(run, index)
    truth_file = nbrsim.files.get_truth_file(run, index)

    print("matching")
    print("    reading:",sx_file)
    sx    = fitsio.read(sx_file, ext=2, lower=True)
    print("    reading:",truth_file)
    truth = fitsio.read(truth_file)

    if not numpy.all(sx['number']==data['number']):
        print("ERROR: not all numbers match")
        return None, None
    #assert numpy.all(sx['number']==data['number'])

    allow=1
    msx, mtruth = close_match(
        sx['xwin_image']-1,
        sx['ywin_image']-1,
        truth['x'],
        truth['y'],
        radius,
        allow,
    )

    nmatch=msx.size
    ntot=sx.size
    frac=float(nmatch)/ntot
    print("        matched %d/%d %.2f" % (nmatch, ntot, frac))

    add_dt=[
        ('sxflags','i4'),
        ('shear_true','f8',2),
        ('shear_index','i2'),
    ]
    newdata = eu.numpy_util.add_fields(data, add_dt)
    newdata['shear_index'] = -9999

    newdata['sxflags'] = sx['flags']

    if nmatch > 0:
        newdata['shear_true'][msx,0] = truth['shear1'][mtruth]
        newdata['shear_true'][msx,1] = truth['shear2'][mtruth]
        newdata['shear_index'][msx] = truth['shear_index'][mtruth]

    return newdata, nmatch

def close_match(t1,s1,t2,s2,ep,allow,verbose=False):
    """
    Find the nearest neighbors between two arrays of x/y

    parameters
    ----------
    ra1,dec1: scalar or array
         coordinates of a set of points.  Must be same length.
    ra2,dec2: scalar or array
         coordinates of a second set of points.  Must be same length.
    ep: scalar
         maximum match distance between pairs (pixels)
    allow: scalar
         maximum number of matches in second array to each element in first array.
    verbose: boolean
         make loud

    Original by Dave Johnston, University of Michigan, 1997
         
    Translated from IDL by Eli Rykoff, SLAC

    modified slightly by erin sheldon
    """
    t1=numpy.atleast_1d(t1)
    s1=numpy.atleast_1d(s1)
    t2=numpy.atleast_1d(t2)
    s2=numpy.atleast_1d(s2)

    n1=t1.size
    n2=t2.size

    matcharr=numpy.zeros([n1,allow],dtype='i8')
    matcharr.fill(-1)
    ind=numpy.arange(n2,dtype='i8')
    sor=t2.argsort()
    t2s=t2[sor]
    s2s=s2[sor]
    ind=ind[sor]
    runi=0
    endt=t2s[n2-1]

 
    for i in range(n1):
        t=t1[i]
        tm=t-ep
        tp=t+ep
        in1=_binary_search(t2s,tm)  # I can improve this?
        
        if in1 == -1:
            if (tm < endt) : in1=0
        if in1 != -1:
            in1=in1+1
            in2=in1-1
            jj=in2+1
            while (jj < n2):
                if (t2s[in2+1] < tp):
                    in2+=1
                    jj+=1
                else :
                    jj=n2
            if (n2 == 1) :
                in2=0  # hmmm

            if (in1 <= in2):
                if (n2 != 1) :
                    check = s2s[in1:in2+1]
                    tcheck = t2s[in1:in2+1]
                else :
                    check = s2s[0]
                    tcheck=t2s[0]
                s=s1[i]
                t=t1[i]
                offby=abs(check-s)
                toffby=abs(tcheck-t)
                good=numpy.where(numpy.logical_and(offby < ep,toffby < ep))[0]+in1
                ngood=good.size
                if (ngood != 0) :
                    if (ngood > allow) :
                        offby=offby[good-in1]
                        toffby=toffby[good-in1]
                        dist=numpy.sqrt(offby**2+toffby**2)
                        good=good[dist.argsort()]
                        ngood=allow
                    good=good[0:ngood]
                    matcharr[i,0:ngood]=good
                    runi=runi+ngood
        

    if verbose:
        print("total put in bytarr:",runi)

    #matches=numpy.where(matcharr != -1)[0]
    matches=numpy.where(matcharr != -1)
    #if (matches.size == 0):
    if (matches[0].size == 0):
        if verbose:
            print("no matches found")
        m1=numpy.array([])
        m2=numpy.array([])
        return m1,m2

    m1 = matches[0] % n1
    m2 = matcharr[matches]
    m2 = ind[m2].flatten()

    if verbose:
        print(m1.size,' matches')

    return m1,m2



def _binary_search(arr,x,edgedefault=False,round=False):
    n=arr.size
    if (x < arr[0]) or (x > arr[n-1]):
        if (edgedefault):
            if (x < arr[0]): index = 0
            elif (x > arr[n-1]): index = n-1
        else: index = -1
        return index

    down=-1
    up=n
    while (up-down) > 1:
        mid=down+(up-down)/2
        if x >= arr[mid]:
            down=mid
        else:
            up=mid

    index=down

    if (round) and (index != n-1):
        if (abs(x-arr[index]) >= abs(x-arr[index+1])): index=index+1

    return index
