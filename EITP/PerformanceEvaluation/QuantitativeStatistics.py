import numpy as np
import pandas as pd
from mosek.fusion import *

class PerformanceMetrics:

    def __init__(self, portfolio=np.ones(100)*5, indexOoS=np.ones(100)*5, enhancedIndexOoS=np.ones(100)*5):

        # Set value arrays
        self.portfolio = portfolio.flatten();
        self.index = indexOoS.flatten();
        self.enhancedIndex = enhancedIndexOoS.flatten();

        # Compute returns to compare
        self.returnEnhancedIndex = np.array([(self.enhancedIndex[i+1]/self.enhancedIndex[i]-1) for i in range(len(self.enhancedIndex)-1)]);
        self.returnIndex = np.array([(self.index[i+1]/self.index[i]-1) for i in range(len(self.index)-1)]);
        self.returnsPortfolio = np.array([(self.portfolio[i+1]/self.portfolio[i]-1) for i in range(len(self.portfolio)-1)]);

    def setData(self, portfolio=np.ones(100)*5, index=np.ones(100)*5, enhancedIndex=np.ones(100)*5):

        # Set value arrays
        self.portfolio = portfolio.flatten();
        self.index = index.flatten();
        self.enhancedIndex = enhancedIndex.flatten();

        # Compute returns to compare
        self.returnEnhancedIndex = np.array([(self.enhancedIndex[i+1]/self.enhancedIndex[i]-1) for i in range(len(self.enhancedIndex)-1)]);
        self.returnIndex = np.array([(self.index[i+1]/self.index[i]-1) for i in range(len(self.index)-1)]);
        self.returnsPortfolio = np.array([(self.portfolio[i+1]/self.portfolio[i]-1) for i in range(len(self.portfolio)-1)]);

    # METRICS
    def DownsideSemiStandardDeviation(self, returns, target):
        return np.sqrt(np.mean(np.square(np.minimum(returns - target, 0))));

    def UpsideSemiStandardDeviation(self, returns, target):
        return np.sqrt(np.mean(np.square(np.maximum(returns - target, 0))));

    def AverageExcessReturn(self, returns, target):
        return np.mean(returns - target);

    def SortinoIndex(self, returns, target):
        if self.DownsideSemiStandardDeviation(returns, target) == 0:
            return 0;
        else:
            return self.AverageExcessReturn(returns, target)/self.DownsideSemiStandardDeviation(returns, target);

    def BeatBenchmarkRatio(self, returns, target):
        return np.mean(returns > target);

    def BeatBenchmarkExcess(self, returns, target):
        L = returns[returns > target]
        if len(L) != 0:
            return np.mean(L);
        else:
            return 0;

    def BeatBenchmarkShortfall(self, returns, target):
        L = returns[returns <= target]
        if len(L) != 0:
            return np.mean(L);
        else:
            return 0;

    def BeatBenchmarkRewardRiskRatio(self, returns, target):
        if self.UpsideSemiStandardDeviation(returns, target) == 0:
            return 0;
        else:
            return self.BeatBenchmarkExcess(returns, target)/self.UpsideSemiStandardDeviation(returns, target);

    def BeatBenchmarkShortfallRewardRiskRatio(self, returns, target):
        if self.DownsideSemiStandardDeviation(returns, target) == 0:
            return 0;
        else:
            return self.BeatBenchmarkShortfall(returns, target)/self.DownsideSemiStandardDeviation(returns, target);

    def MarketBeta(self, returnsPortfolio, returnsBenchmark):
        return np.cov(returnsPortfolio,returnsBenchmark, ddof=1)[1,0]/(np.var(returnsBenchmark, ddof=1));

    def TotalReturn(self, portfolio):
        return (portfolio[-1] - 100);

    def TotalExcessReturn(self, portfolio, benchmark):
        return (portfolio[-1] - benchmark[-1]);

    def RMSE(self, returns, target):
        return np.sqrt(np.mean(np.square(returns - target)));

    def MAD(self, returns, target):
        return np.mean(np.abs(returns - target));

    def VaR(self, returns, target, beta=0.05):
        return np.percentile(returns-target, (1-beta)*100);

    def CVaR(self, returns, target, beta=0.05):
        e = returns-target
        return -np.mean(e[e <= self.VaR(returns, target, beta=beta)]);

    def VaRAbs(self, returns, target, beta=0.05):
        return np.percentile(-np.abs(returns-target), (1-beta)*100);

    def CVaRAbs(self, returns, target, beta=0.05):
        e = -np.abs(returns-target)
        return -np.mean(e[e <= self.VaRAbs(returns, target, beta=beta)]);

    def AverageReturn(self, returns):
        return np.mean(returns)*100;

    def ExcessReturnAverage(self, returns, target):
        rAvg = self.AverageReturn(returns);
        rIAvg = self.AverageReturn(target);
        return rAvg - rIAvg;

    def Percentile(self, returns, target, pth=10):
        return np.percentile(returns-target, pth);

    # Printing the table of metrics
    def getMetrics(self, objective=None, rho=0.6, beta=0.80, printResult=False):

        result = dict();

        # Compute the metrics for all the returns defined in the constructor (21 in total)
        result['Objective'] = objective;
        result['DownsideSemiStandardDeviation'] = self.DownsideSemiStandardDeviation(self.returnsPortfolio, self.returnEnhancedIndex);
        result['RMSE'] = self.RMSE(self.returnsPortfolio, self.returnEnhancedIndex)
        result['MAD'] = self.MAD(self.returnsPortfolio, self.returnEnhancedIndex)
        result['VaR-{}'.format(beta)] = self.VaR(self.returnsPortfolio, self.returnEnhancedIndex, beta=beta)
        result['CVaR-{}'.format(beta)] = self.CVaR(self.returnsPortfolio, self.returnEnhancedIndex, beta=beta)
        result['AverageExcessReturn'] = self.AverageExcessReturn(self.returnsPortfolio, self.returnEnhancedIndex);
        result['ExcessReturn'] = self.TotalExcessReturn(self.portfolio, self.enhancedIndex);
        result['SortinoIndex'] = self.SortinoIndex(self.returnsPortfolio, self.returnEnhancedIndex);
        result['BeatBenchmarkRatio'] = self.BeatBenchmarkRatio(self.returnsPortfolio, self.returnEnhancedIndex);
        result['BeatBenchmarkExcess'] = self.BeatBenchmarkExcess(self.returnsPortfolio, self.returnEnhancedIndex);
        result['BeatBenchmarkShortfall'] = self.BeatBenchmarkShortfall(self.returnsPortfolio, self.returnEnhancedIndex);
        result['BeatBenchmarkRewardRiskRatio'] = self.BeatBenchmarkRewardRiskRatio(self.returnsPortfolio, self.returnEnhancedIndex);
        #result['BeatBenchmarkShortfallRewardRiskRatio'] = self.BeatBenchmarkShortfallRewardRiskRatio(self.returnsPortfolio, self.returnEnhancedIndex);
        result['CVaRAbs-{}'.format(beta)] = self.CVaRAbs(self.returnsPortfolio, self.returnEnhancedIndex, beta=beta);
        result['MarketBeta'] = self.MarketBeta(self.returnsPortfolio, self.returnIndex);
        result['TotalReturn'] = self.TotalReturn(self.portfolio);
        result['AverageReturn'] = self.AverageReturn(self.returnsPortfolio);
        result['P5'] = self.Percentile(self.returnsPortfolio, self.returnEnhancedIndex, pth=5);
        result['P10'] = self.Percentile(self.returnsPortfolio, self.returnEnhancedIndex, pth=10);
        result['P90'] = self.Percentile(self.returnsPortfolio, self.returnEnhancedIndex, pth=90);
        result['P95'] = self.Percentile(self.returnsPortfolio, self.returnEnhancedIndex, pth=90);

        # Make a nice latex table that can be saved to a file
        if printResult:
            print(pd.DataFrame(result).to_latex(float_format="%.4f"));

        # Return the results
        return result;


