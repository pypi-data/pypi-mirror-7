from mahotas.edge import sobel
from nose.tools import raises
import numpy as np

def test_sobel_shape():
    A = np.arange(100*100)
    A = (A % 15)
    A = A.reshape((100,100))
    assert sobel(A).shape == A.shape
    assert sobel(A, just_filter=True).shape == A.shape

def test_sobel_zeros():
    A = np.zeros((15,100))
    assert sobel(A).shape == A.shape
    assert sobel(A).sum() == 0

def test_sobel():
    I = np.array([
            [0,0,0,0,0,0],
            [0,0,0,1,0,0],
            [0,0,0,1,0,0],
            [0,0,0,1,0,0],
            [0,0,0,1,0,0],
            [0,0,0,0,0,0]])
    E = sobel(I)
    r,c = I.shape
    for y,x in zip(*np.where(E)):
        N = [I[y,x]]
        if y > 0: N.append(I[y-1,x])
        if x > 0: N.append(I[y,x-1])
        if y < (r-1): N.append(I[y+1,x])
        if x < (c-1): N.append(I[y,x+1])
        assert len(set(N)) > 1

def test_zero_images():
    assert np.isnan(sobel(np.zeros((16,16)))).sum() == 0
    assert sobel(np.zeros((16,16)), just_filter=True).sum() == 0

def test_find_edge():
    import mahotas as mh
    f = np.zeros((32,48))
    f[:,16:] = 255
    f = mh.gaussian_filter(f,4)
    fs = sobel(f)
    assert np.all(fs[:,15] > 0)

@raises(ValueError)
def test_3d_error():
    import mahotas as mh
    f = np.zeros((32,16,3))
    sobel(f)
