import math, os, re, time, random
from datetime import datetime, timedelta, date
import numpy as np
import pandas as pd

from sklearn.decomposition import PCA
import statsmodels.api as sm
from statsmodels import regression
from sklearn import linear_model
from sklearn.preprocessing import scale

import numpy as np, pandas as pd, math

date_necessity = '2018-06'


## 去重并得到相应数据的组合
## input: path
## output: (feature_file, object_file)
def get_files(path='./gupiao/'):
    ## get paths
    def feature_file(number):
        return path + 'features/' + number + '_20060101-20180725.csv'

    ## get paths
    def object_file(number):
        return path + 'objects/' + number + '_20060101-20180823.csv'

    ## test if last date is valid
    def lastdate_is_valid(x):
        pd_test1 = pd.read_csv(feature_file(x))
        return ('tradeDate' in pd_test1.columns) \
               and (len(pd_test1) > 1)
               # and (date_necessity in str(pd_test1.tradeDate.iloc[-1])) \


    feature_numbers = {x.split('_')[0] for x in os.listdir(path + 'features')}

    object_numbers = {x.split('_')[0] for x in os.listdir(path + 'objects')}

    file_numbers = feature_numbers.intersection(object_numbers)
    file_names = [(feature_file(x), object_file(x)) for x in file_numbers if lastdate_is_valid(x) == True]

    print(len(file_names))
    return file_names


## input: (feature_file, object_file)
## output: pd.Dataframe
def get_data(file_pair):
    (feature_file, object_file) = file_pair

    feature = pd.read_csv(feature_file)

    #### CURRENTLY USING ALL FEATURES
    #     pca_factors = ['LCAP','LFLO','EquityFixedAssetRatio','DAVOL20','Volatility','DAREC','ROA','OperatingRevenueGrowRate']
    pca_factors = ['LCAP', 'LFLO', 'PE', 'PB', 'PCF', 'PS', 'ROE', 'ROA', 'EPS', 'NetProfitRatio', 'GrossIncomeRatio',
                   'OperatingRevenueGrowRate', 'OperatingProfitGrowRate', 'OperCashGrowRate', 'DebtsAssetRatio',
                   'FixAssetRatio', 'CurrentRatio', 'QuickRatio', 'KDJ_K', 'BIAS20', 'BIAS60', 'PSY', 'VOL20', 'VOL60',
                   'Volatility', 'AR', 'BR', 'REC', 'DAREC']
    #### CURRENTLY USING ALL FEATURES

    pca_factors = list(set(list(feature.columns)).intersection(pca_factors))
    feature = feature.get(['tradeDate'] + pca_factors)

    feature['month'] = feature['tradeDate'].apply(
        lambda x: datetime.strftime(datetime.strptime(x, "%Y-%m-%d"), "%Y-%m"))

    #### VERY IMPORTANT
    #     feature = feature.fillna(feature.mean())
    feature.iloc[-5:] = feature.iloc[-5:].fillna(method='pad')
    feature.dropna(axis=1)
    feature.reset_index(drop=1)
    #### VERY IMPORTANT

    Object = pd.read_csv(object_file)
    Object = Object.get(['tradeDate', 'dailyReturnReinv'])
    Object['month'] = Object['tradeDate'].apply(lambda x: datetime.strftime(datetime.strptime(x, "%Y-%m-%d"), "%Y-%m"))

    new_feature = pd.DataFrame(columns=['month'] + pca_factors)
    for (i, (month, dat)) in enumerate(feature.groupby('month')):
        new_feature.loc[i, ['month']] = month
        new_feature.loc[i, pca_factors] = dat[pca_factors].apply(np.mean)

    new_Object = pd.DataFrame(columns=['month', 'dailyReturnReinv'])
    for (i, (month, dat)) in enumerate(Object.groupby('month')):
        new_Object.loc[i, ['month']] = month
        new_Object.loc[i, ['dailyReturnReinv']] = dat[['dailyReturnReinv']].apply(np.mean)

    new_data = pd.merge(new_feature, new_Object, how='left', on=['month'])
    new_data.sort_values(by="month", ascending=True, inplace=True)

    new_data.iloc[-5:] = new_data.iloc[-5:].fillna(method='pad')
    new_data.dropna(inplace=True)
    new_data.reset_index(drop=True, inplace=True)
    new_data.loc[new_data.shape[0] - 1, new_data.columns[-1]] = math.nan

    print(new_data)
    if date_necessity not in new_data.month.iloc[-1]:
        raise ValueError('No data of current month {}'.format(date_necessity))

    return new_data


## input: pd.Dataframe
## output: pd.Dataframe (with principle components)
def get_pca_data(data, describe_ratio=0.99):
    df = data[data.columns[1:-1]]
    df = df.values
    ## normalize principle components
    #     df = normalize(df, norm='l2', axis=1, copy=True, return_norm=False)
    df = scale(df)
    pca = PCA(copy=True, n_components=describe_ratio, svd_solver='full')

    pca.fit_transform(df)
    low_d = pca.transform(df)

    #     low_d = normalize(low_d, norm='l2', axis=1, copy=True, return_norm=False)
    low_d = scale(low_d)

    pr = pd.DataFrame(low_d, dtype='float64')
    pr.columns = ['pr_{}'.format(i) for i in range(len(pr.columns))]
    ## get data with only principle components
    data = pd.concat([data[data.columns[0]], pr, data[data.columns[-1]]], axis=1)

    return data


## input: pd.Dataframe (with last row unpredicted)
## output: prediction of last row
def get_regression_model(data):
    data, sample = data.iloc[:-1, ], data.iloc[-1,]
    data = data.values[:, 1:]

    sample[0] = 1.0;
    sample = sample[:-1]
    sample = np.array(sample, dtype='float64')
    X, Y = data[:, :-1], data[:, -1]
    X, Y = np.array(X, dtype='float64', copy=True), np.array(Y, dtype='float64')
    X = sm.add_constant(X)
    model = sm.OLS(Y, X)
    results = model.fit()
    print(results.summary())

    return results.predict(sample)[0]


if __name__ == '__main__':

    selection = {}
    for file_name in get_files():
        try:
            data = get_data(file_name)
            print(data)
            pca_data = get_pca_data(data)

            date = pca_data.iloc[-1, 0]
            dateyear = str(date).split('-')[0]
            datemonth = str(date).split('-')[1]
            score = get_regression_model(pca_data)
            name = file_name[0].split('/')[-1].split('_')[0]

            selection[name] = score
        #             print (name, score)
        except Exception as err:
            pass

    sorted_selection = sorted(selection.items(), key=lambda x: x[1], reverse=True)
    output_df = pd.DataFrame({'id': [str(x[0]) for x in sorted_selection], \
                              'profit': [float(x[1]) for x in sorted_selection]})

    output_df.to_csv("gupiao_profit.csv", index=False, sep=',')

