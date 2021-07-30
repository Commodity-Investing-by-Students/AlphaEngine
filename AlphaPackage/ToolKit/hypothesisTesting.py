from scipy.stats import ttest_ind

def compare(array_1,array_2,alpha,verbose=False):
    t_statistic, pvalue = ttest_ind(array_1,array_2)
    if verbose:
        print('t-statistic: %.3f p-value: %.3f' % (t_statistic,pvalue))
        print('Null hypothesis: The two series cannot be distinguished from one another (Fail to reject H_0)')
        print('Alternative hypothesis: The two series cannot be distinguished from one another')

    if pvalue > alpha:
        if verbose:
            print('Fail to reject H_0')
        else: pass
        reject = False
    else:

        print('reject H_0')
        reject = True

    return reject