import os
import time

from skopt import gp_minimize
from skopt.plots import plot_convergence, plot_evaluations, plot_objective
from skopt.benchmarks import branin, hart6
from skopt.acquisition import gaussian_ei
import numpy as np

from trades.automatic import historical_calculations
from trades.manual import stock_calculations

np.random.seed(237)
import datetime
import matplotlib.pyplot as plt
from trades.automatic.historical_calculations import get_roi
import pandas as pd
from functools import partial
import cProfile
import pstats

def f(x, noise_level=0.1):
    return np.sin(5 * x[0]) * (1 - np.tanh(x[0] ** 2))\
           + np.random.randn() * noise_level


def test_optimize():
    noise_level = 0.1
    plt.rcParams["figure.figsize"] = (8, 14)

    x = np.linspace(-2, 2, 400).reshape(-1, 1)
    fx = np.array([f(x_i, noise_level=0.0) for x_i in x])

    res = gp_minimize(f,  # the function to minimize
                      [(-2.0, 2.0)],  # the bounds on each dimension of x
                      acq_func="EI",  # the acquisition function
                      n_calls=15,  # the number of evaluations of f
                      n_random_starts=5,  # the number of random initialization points
                      noise=0.1 ** 2,  # the noise level (optional)
                      random_state=1234)  # the random seed
    x_gp = res.space.transform(x.tolist())

    for n_iter in range(5):
        gp = res.models[n_iter]
        curr_x_iters = res.x_iters[:5 + n_iter]
        curr_func_vals = res.func_vals[:5 + n_iter]

        # Plot true function.
        plt.subplot(5, 2, 2 * n_iter + 1)
        plt.plot(x, fx, "r--", label="True (unknown)")
        plt.fill(np.concatenate([x, x[::-1]]),
                 np.concatenate([fx - 1.9600 * noise_level,
                                 fx[::-1] + 1.9600 * noise_level]),
                 alpha=.2, fc="r", ec="None")

        # Plot GP(x) + contours
        y_pred, sigma = gp.predict(x_gp, return_std=True)
        plt.plot(x, y_pred, "g--", label=r"$\mu_{GP}(x)$")
        plt.fill(np.concatenate([x, x[::-1]]),
                 np.concatenate([y_pred - 1.9600 * sigma,
                                 (y_pred + 1.9600 * sigma)[::-1]]),
                 alpha=.2, fc="g", ec="None")

        # Plot sampled points
        plt.plot(curr_x_iters, curr_func_vals,
                 "r.", markersize=8, label="Observations")

        # Adjust plot layout
        plt.grid()

        if n_iter == 0:
            plt.legend(loc="best", prop={'size': 6}, numpoints=1)

        if n_iter != 4:
            plt.tick_params(axis='x', which='both', bottom='off',
                            top='off', labelbottom='off')

        # Plot EI(x)
        plt.subplot(5, 2, 2 * n_iter + 2)
        acq = gaussian_ei(x_gp, gp, y_opt=np.min(curr_func_vals))
        plt.plot(x, acq, "b", label="EI(x)")
        plt.fill_between(x.ravel(), -2.0, acq.ravel(), alpha=0.3, color='blue')

        next_x = res.x_iters[5 + n_iter]
        next_acq = gaussian_ei(res.space.transform([next_x]), gp,
                               y_opt=np.min(curr_func_vals))
        plt.plot(next_x, next_acq, "bo", markersize=6, label="Next query point")

        # Adjust plot layout
        plt.ylim(0, 0.1)
        plt.grid()

        if n_iter == 0:
            plt.legend(loc="best", prop={'size': 6}, numpoints=1)

        if n_iter != 4:
            plt.tick_params(axis='x', which='both', bottom='off',
                            top='off', labelbottom='off')

    plt.savefig("test.png")


def test_optimize_6d():
    x = np.linspace(-2, 2, 400).reshape(-1, 1)
    fx = np.array([f(x_i, noise_level=0.0) for x_i in x])
    bounds = [(0., 1.)] * 6
    res = gp_minimize(hart6,  # the function to minimize
                      bounds,  # the bounds on each dimension of x
                      acq_func="EI",  # the acquisition function
                      n_calls=100,  # the number of evaluations of f
                      n_random_starts=10,  # the number of random initialization points
                      random_state=1234)  # the random seed

    # fig = plot_evaluations(res, bins=20)
    fig = plot_objective(res, n_samples=50)
    plt.savefig("test.png")


def create_optimize_function(rules_list, buy_threshold, sell_threshold, ticker, base_time, now_time):
    def optimize_weights(weight_list):
        for i, weight in enumerate(weight_list):
            rules_list[i]["Percentage"] = weight

        values_df = get_roi(ticker, base_time, now_time, rules_list, buy_threshold, sell_threshold)
        roi = -1 * values_df['strategic_values'][-1] / values_df['strategic_values'][0]
        return roi

    return optimize_weights


def create_yearly_solutions():
    rules_list = [
        {'Larger: When?': -10, 'Larger: What?': 'Close', 'Smaller: When?': 0, 'Smaller: What?': 'Close',
         'Percentage': 1.0, "Weight": -2.0},
        {'Larger: When?': 0, 'Larger: What?': 'Close', 'Smaller: When?': -1, 'Smaller: What?': 'Close',
         'Percentage': 1.0, "Weight": -1.0},
        {'Larger: When?': 0, 'Larger: What?': 'Close', 'Smaller: When?': -3, 'Smaller: What?': 'Close',
         'Percentage': 1.0, "Weight": -1.0},
        {'Larger: When?': 0, 'Larger: What?': 'Close', 'Smaller: When?': -5, 'Smaller: What?': 'Close',
         'Percentage': 1.0, "Weight": -1.0},
    ]

    buy_threshold = -2.5
    sell_threshold = -2.5
    ticker = 'SPY'
    now_time = datetime.datetime.now() - datetime.timedelta(days=365)
    base_time = now_time - datetime.timedelta(days=365 * 10)

    results_list = []
    first_year = 2000
    for i in range(20):
        year = first_year+i
        base_time = datetime.datetime.strptime(f'{year}-01-01', '%Y-%m-%d')
        now_time = base_time+datetime.timedelta(days=365)
        optimize_weights_function = create_optimize_function(rules_list, buy_threshold, sell_threshold, ticker, base_time, now_time)
        yearly_results = optimize_roi(optimize_weights_function, base_time)
        results_list.append(yearly_results)

    data_dir = r'./assets/opt/'
    file = os.path.join(data_dir, ticker+".csv")
    results_df = pd.DataFrame.from_records(results_list)
    results_df.to_csv(file)


def optimize_roi(optimize_weights_function, base_time):
    tic = time.time()
    bounds = [(0., 10.), (0., 10), (0., 10), (0., 10.)]
    res = gp_minimize(optimize_weights_function,  # the function to minimize
                      bounds,  # the bounds on each dimension of x
                      acq_func="EI",  # the acquisition function
                      n_calls=50,  # the number of evaluations of f
                      n_random_starts=15,  # the number of random initialization points
                      random_state=1234)  # the random seed

    # fig = plot_evaluations(res, bins=20)
    print(res.x)
    print(res.fun)
    plot_objective(res, n_samples=50)
    plt.savefig("test_objective.png")
    plot_evaluations(res)
    plt.savefig("test_evaluations.png")
    toc=time.time()
    print(f"Optimize Time: {toc-tic}")
    results_dict = {'res_x': res.x, 'res_fun': res.fun, 'base_time': base_time}
    return results_dict


def test_data_speed():
    now_time = datetime.datetime.now()
    base_time = now_time-datetime.timedelta(days=100)
    tic = time.time()
    df1 = historical_calculations.get_data(["SPY"], base_time, now_time)
    print(df1.head())
    toc = time.time()
    print(f"With existing data: {toc-tic}")

    tic=time.time()
    df2 = stock_calculations.get_yahoo_stock_data(["SPY"], base_time, now_time)
    print(df2.head())
    toc = time.time()
    print(f"With downloaded data: {toc-tic}")


if __name__ == "__main__":
    # test_data_speed()
    # TODO:  Save optimum solution for each year for each stock.
    # optimize_roi()
    create_yearly_solutions()
    # timing_function()
    # test_optimize()
    # test_optimize_6D()
