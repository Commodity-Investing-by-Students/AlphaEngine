from AlphaPackage.Logic.algoManager import Strategy
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn import tree

from subprocess import call
from sklearn.metrics import classification_report


class ClassifierStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self)
        self.has_initialized = False
        self.train_size = 0.75
        self.min_steps = 300

    def label_data(self):
        pass
    def assign_features(self):
        for ticker in self.asset_dictionary.keys():
            # put features in here
            '''
            feature area
            '''

            self.asset_dictionary[ticker].bars = self.asset_dictionary[ticker].bars.fillna(method="ffill")


    def prepare_data(self,features,target):
        self.model_data = {}
        for ticker in self.asset_dictionary.keys():

            self.target = target
            self.features = [feature_name for feature_name in list(self.asset_dictionary[ticker].bars.columns) if feature_name not in ['Open', 'High', 'Low', 'Close', 'Volume']]

            # defin
            current_dataset = self.asset_dictionary[ticker].bars
            X = current_dataset[self.features]
            y = current_dataset[self.target]


            # split the data into training and testing
            split = int(len(current_dataset) * self.train_size)
            X_train, X_test = X[:split], X[split:]
            y_train, y_test = y[:split], y[split:]
            self.model_data[ticker] = {'X_train':X_train,'X_test':X_test,'Y_train':y_train,'Y_test':y_test}

    # this method trains the random forest classifiers for each asset in the asset universe
    def train_model(self,ticker=None,random_state=5):
        if ticker is None:
            self.RFmodels = {}
            for ticker in self.asset_dictionary.keys():
                model = RandomForestClassifier(random_state=random_state)
                self.RFmodels[ticker] = model.fit(self.model_data[ticker]['X_train'],self.model_data['Y_train'])
        elif ticker in self.asset_dictionary.keys():
            model = RandomForestClassifier(random_state=random_state)
            self.RFmodels[ticker] = model.fit(self.model_data[ticker]['X_train'], self.model_data['Y_train'])



    # this method evaluates the random forest classifiers for each asset in the asset universe or a single asset
    def evaluate_model(self,ticker=None):
        if ticker is None:
            for ticker in self.asset_dictionary.keys():
                X_test, y_test = self.model_data[ticker]['X_test'],self.model_data[ticker]['Y_test']
                model = self.RFmodels[ticker]
                model_accuracy = accuracy_score(y_test, model.predict(X_test), normalize=True)
                if self.verbose:
                    print('Correct Prediction (%): ',model_accuracy * 100.0)
                else: pass
        elif ticker in self.asset_dictionary.keys():
            X_test, y_test = self.model_data[ticker]['X_test'], self.model_data[ticker]['Y_test']
            model = self.RFmodels[ticker]
            model_accuracy = accuracy_score(y_test, model.predict(X_test), normalize=True)
            if self.verbose:
                print('Correct Prediction (%): ', model_accuracy * 100.0)
            else:
                pass
        else:
            pass

    def run_model(self):
        for ticker in self.asset_dictionary.keys():
            model = self.RFmodels[ticker]
            X = self.asset_dictionary[ticker].bars[self.features]
            self.asset_dictionary[ticker].bars['prediction'] = model.predict(X)
            current_data = self.asset_dictionary[ticker].bars
            strategy_suggestion = 0
            current_price = self.asset_dictionary[ticker].bars.Close.iloc[-1].values[0]
            if current_data['prediction'].iloc[-1].values[0] == -1 :
                strategy_suggestion = -1
            elif current_data['prediction'].iloc[-1].values[0] == 0 :
                strategy_suggestion =  0
            elif current_data['prediction'].iloc[-1].values[0] == 1 :
                strategy_suggestion = 1
            else:
                pass


            #self.create_order(ticker=ticker,quantity=order_size,price=current_price)

    def process_1(self):
        pass
    def process_2(self):
        pass
