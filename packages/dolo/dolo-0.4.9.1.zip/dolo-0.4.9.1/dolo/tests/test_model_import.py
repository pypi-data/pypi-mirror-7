import unittest
import numpy


from dolo import yaml_import

def test_model_evaluation(compiler='numpy', data_layout='columns'):

    #model = yaml_import('examples/models/rbc_fg.yaml', compiler=compiler, order=data_layout)
    model = yaml_import('examples/models/rbc_fg.yaml')

    s0 = model.calibration['states']
    x0 = model.calibration['controls']
    p = model.calibration['parameters']

    assert(s0.ndim == 1)
    assert(x0.ndim == 1)
    assert(p.ndim == 1)

    N = 10
    f = model.functions['arbitrage']

    if data_layout == 'rows':
        ss = numpy.ascontiguousarray( numpy.tile(s0, (N,1)).T )
        xx = numpy.ascontiguousarray( numpy.tile(x0, (N,1)).T )
    else:
        ss = ( numpy.tile(s0, (N,1)) )
        xx = ( numpy.tile(x0, (N,1)) )

    vec_res = f(ss,xx,ss,xx,p)


    res = f(s0, x0, s0, x0, p)

    assert(res.ndim==1)

    d = 0
    for i in range(N):
        if data_layout == 'columns':
            d += abs(vec_res[i,:] - res).max()
        else:
            d += abs(vec_res[:,i] - res).max()
    assert(d == 0)


class TestModelImport(unittest.TestCase):

    def test_standard_import_rows(self):

        test_model_evaluation(data_layout='rows')

    def test_import_numexpr_rows(self):

        test_model_evaluation(compiler='numexpr', data_layout='rows')

    def test_standard_import_columns(self):

        test_model_evaluation(data_layout='columns')

    def test_import_numexpr_columns(self):

        test_model_evaluation(compiler='numexpr', data_layout='columns')

if __name__ == '__main__':
    unittest.main()