pyautoweka
==========

Description
-----------

pyautoweka is a python wrapper for [Auto-WEKA](http://www.cs.ubc.ca/labs/beta/Projects/autoweka/), a Java application for algorithm selection and hyperparameter optimizations, that is build on [WEKA](http://www.cs.waikato.ac.nz/ml/weka/). 


Installation
------------

Download, go to the project sources and install:
```
git clone git@github.com:tdomhan/pyautoweka.git
cd pyautoweka
python setup.py install
```

Running a classification experiment
-----------------------------------

AutoWeka for python.

```python
import pyautoweka

#Create an experiment
experiment = pyautoweka.ClassificationExperiment(tuner_timeout=360)
```
`tuner_timeout` is the time the optimization will run in seconds. So e.g. 360 seconds = 6 minutes. The longer you run the optimization, the better of course. (Note that the `experiment` object has an interface similar to sklearn classifiers.) 

First we need to load some data. Let's for example the famous [Iris dataset](http://archive.ics.uci.edu/ml/datasets/Iris). Download it using [this link](http://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data).

Let's load it into python:

```python
#load the data:
import numpy as np
import random

X = np.loadtxt("iris.data", delimiter=",", usecols=range(4))
y = np.loadtxt("iris.data", delimiter=",", usecols=[4], dtype="object")

#shuffle the data:
indices = range(len(X))
random.shuffle(indices)
X = X[indices]
y = y[indices]

#split into train and test set:
X_train = X[0:100]
y_train = y[0:100]

X_test = X[100:]
y_test = y[100:]

#now we can fit a model:
experiment.fit(X_train, y_train)

#and predict the labels of the held out data:
y_predict = experiment.predict(X_test)

#Let's check what accuracy we get:
num_correct = sum([1 for predicted, correct in zip(y_predict, y_test) if predicted == correct])
print "Accuracy: %f" % (float(num_correct) / len(y_test))
```

This should give you an accuracy in the high 90%s.

Running a regression experiment
-----------------------------------

```python
import pyautoweka

#Create an experiment
experiment = pyautoweka.RegressionExperiment(tuner_timeout=360)
```

First we need to load some data. Let's for example the [Boston housing dataset](https://archive.ics.uci.edu/ml/datasets/Housing). Download it using [this link](https://archive.ics.uci.edu/ml/machine-learning-databases/housing/housing.data).

```python
#load the data:
import numpy as np
import random

X = np.loadtxt("housing.data.txt", usecols=range(13))
y = np.loadtxt("housing.data.txt", usecols=[13])

#shuffle the data:
indices = range(len(X))
random.shuffle(indices)
X = X[indices]
y = y[indices]

#split into train and test set:
X_train = X[0:100]
y_train = y[0:100]

X_test = X[100:]
y_test = y[100:]

#now we can fit a model:
experiment.fit(X_train, y_train)

#and regress on held out test data:
y_predict = experiment.predict(X_test)

#RMSE of the prediction:
rmse = np.sqrt(((y_predict-y_test)**2).mean())
```


Advanced: Selecting specific classifiers
----------------------------------------

When you don't set a specific classifier all available classifiers will be tried. You have the option to limit the search to certain classifiers as follows:

First of all let's see what classifiers are available:

```python
import pyautoweka
print pyautoweka.AVAILABLE_CLASSIFIERS
```

Now let's say we want to just use the Simple Logistic classifier:
```python
experiment.add_classfier("weka.classifiers.functions.SimpleLogistic")
```


Advanced: files created
-----------------------

When you create a new experiment theres a bunch of files that will be generated before and during the run of AutoWeka. For each experiment there will be a new folder within in the `experiments` folder. The folder will have the name of the experiment, if it was specified in the constructor. Each time you fit data a tempraroy arff file will be created that holds all the data in it. This file will be delete after the `fit` call.

