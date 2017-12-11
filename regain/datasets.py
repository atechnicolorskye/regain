"""Dataset generation module."""
import numpy as np
import sys
import scipy.sparse as ss
import math

from sklearn.datasets import make_sparse_spd_matrix

from regain.plot import plot_graph_with_latent_variables


def normalize_matrix(x):
    """Normalize a matrix so to have 1 on the diagonal, in-place."""
    d = np.diag(x).reshape(1, x.shape[0])
    d = 1. / np.sqrt(d)
    x *= d
    x *= d.T


def is_pos_def(x, tol=1e-15):
    """Check if x is positive definite."""
    eigs = np.linalg.eigvalsh(x)
    eigs[np.abs(eigs) < tol] = 0
    return np.all(eigs > 0)


def is_pos_semidef(x, tol=1e-15):
    """Check if x is positive semi-definite."""
    eigs = np.linalg.eigvalsh(x)
    eigs[np.abs(eigs) < tol] = 0
    return np.all(eigs >= 0)

def generate_dataset_L1L2(n_dim_obs=10, n_dim_lat=2, T=10, degree=2, proportional=False, epsilon=1e-3):

    K_HO = np.zeros((n_dim_lat, n_dim_obs))
    for i in range(n_dim_lat):
        percentage = int(n_dim_obs * 0.8)
        indices = np.random.randint(0, high=n_dim_obs, size=percentage)
        K_HO[i, indices] = np.random.rand(percentage) * 0.12
    L = K_HO.T.dot(K_HO)
    assert(is_pos_semidef(L))
    assert np.linalg.matrix_rank(L) == n_dim_lat

    theta = np.eye(n_dim_obs)
    for i in range(n_dim_obs):
        l = list(set(np.arange(0, n_dim_obs)) -
                set().union(list(np.nonzero(theta[i,:])[0]),
                            list(np.where(np.count_nonzero(theta, axis=1)>=3)[0])))
        if len(l)==0: continue
        indices = np.random.choice(l, degree-(np.count_nonzero(theta[i,:])-1))
        theta[i, indices] = theta[indices, i] = .5 / degree
    assert(is_pos_def(theta))
    theta_observed = theta - L
    assert(is_pos_def(theta_observed))

    thetas = [theta]
    thetas_obs = [theta_observed]
    ells = [L]
    K_HOs = [K_HO]

    for i in range(1,T):
        if proportional:
            no = int(math.ceil(n_dim_obs/20))
        else:
            no=1

        rows = np.zeros(no)
        cols = np.zeros(no)
        while (np.any(rows==cols)):
            rows = np.random.randint(0, n_dim_obs, no)
            cols = np.random.randint(0, n_dim_obs, no)
        theta = thetas[-1].copy()
        for r, c in zip(rows, cols):
            theta[r,c] = 0.12 if theta[r,c] == 0 else 0;
            theta[c,r] = theta[r,c]
       # print(theta)
        assert(is_pos_def(theta))

        K_HO = K_HOs[-1].copy()
        addition = np.random.rand(*K_HO.shape)
        addition *= (epsilon / np.linalg.norm(addition))
        K_HO += addition
        K_HO = K_HO / np.sum(K_HO, axis=1)[:, None]
        K_HO *=0.12
        K_HO[np.abs(K_HO)<epsilon/(theta.shape[0])] = 0
        K_HOs.append(K_HO)
        L = K_HO.T.dot(K_HO)
        assert np.linalg.matrix_rank(L) == n_dim_lat
        assert(is_pos_semidef(L))
        assert(is_pos_def(theta - L))
        L = K_HO.T.dot(K_HO)
        assert np.linalg.matrix_rank(L) == n_dim_lat
        assert(is_pos_semidef(L))
        assert(is_pos_def(theta - L))

        thetas.append(theta)
        thetas_obs.append(theta - L)
        ells.append(L)
        K_HOs.append(K_HO)

    return thetas, thetas_obs, ells

def generate_dataset_L1(n_dim_obs=10, n_dim_lat=2, T=10, degree=2, proportional=False):

    K_HO = np.zeros((n_dim_lat, n_dim_obs))
    for i in range(n_dim_lat):
        percentage = int(n_dim_obs * 0.8)
        indices = np.random.randint(0, high=n_dim_obs, size=percentage)
        K_HO[i, indices] = np.random.rand(percentage) * 0.12
    L = K_HO.T.dot(K_HO)
    assert(is_pos_semidef(L))
    assert np.linalg.matrix_rank(L) == n_dim_lat

    theta = np.eye(n_dim_obs)
    for i in range(n_dim_obs):
        l = list(set(np.arange(0, n_dim_obs)) -
                set().union(list(np.nonzero(theta[i,:])[0]),
                            list(np.where(np.count_nonzero(theta, axis=1)>=3)[0])))
        if len(l)==0: continue
        indices = np.random.choice(l, degree-(np.count_nonzero(theta[i,:])-1))
        theta[i, indices] = theta[indices, i] = .5 / degree
    assert(is_pos_def(theta))
    theta_observed = theta - L
    assert(is_pos_def(theta_observed))

    thetas = [theta]
    thetas_obs = [theta_observed]
    ells = [L]
    K_HOs = [K_HO]

    for i in range(1,T):
        if proportional:
            no = int(math.ceil(n_dim_obs/20))
        else:
            no=1

        rows = np.zeros(no)
        cols = np.zeros(no)
        while (np.any(rows==cols)):
            rows = np.random.randint(0, n_dim_obs, no)
            cols = np.random.randint(0, n_dim_obs, no)
        theta = thetas[-1].copy()
        for r, c in zip(rows, cols):
            theta[r,c] = 0.12 if theta[r,c] == 0 else 0;
            theta[c,r] = theta[r,c]
       # print(theta)
        assert(is_pos_def(theta))

        K_HO = K_HOs[-1].copy()
        c = np.random.randint(0, n_dim_obs, 1)
        r = np.random.randint(0, n_dim_lat, 1)
        K_HO[r,c] = 0.12 if K_HO[r,c] == 0 else 0;
        #K_HO[c,r] = K_HO[r,c]

        L = K_HO.T.dot(K_HO)
        assert np.linalg.matrix_rank(L) == n_dim_lat
        assert(is_pos_semidef(L))
        assert(is_pos_def(theta - L))

        thetas.append(theta)
        thetas_obs.append(theta - L)
        ells.append(L)
        K_HOs.append(K_HO)

    return thetas, thetas_obs, ells


def generate_dataset_with_evolving_L(n_dim_obs=10, n_dim_lat=2, epsilon=1e-3,
                                     T=10, degree=2):

    K_HO = np.zeros((n_dim_lat, n_dim_obs))
    for i in range(n_dim_lat):
        percentage = int(n_dim_obs * 0.8)
        indices = np.random.randint(0, high=n_dim_obs, size=percentage)
        K_HO[i, indices] = np.random.rand(percentage) * 0.12
    L = K_HO.T.dot(K_HO)
    assert(is_pos_semidef(L))
    assert np.linalg.matrix_rank(L) == n_dim_lat

    theta = np.eye(n_dim_obs)
    for i in range(n_dim_obs):
        l = list(set(np.arange(0, n_dim_obs)) -
                set().union(list(np.nonzero(theta[i,:])[0]),
                            list(np.where(np.count_nonzero(theta, axis=1)>=3)[0])))
        if len(l)==0: continue
        indices = np.random.choice(l, degree-(np.count_nonzero(theta[i,:])-1))
        theta[i, indices] = theta[indices, i] = .5 / degree
    assert(is_pos_def(theta))
    theta_observed = theta - L
    assert(is_pos_def(theta_observed))

    thetas = [theta]
    thetas_obs = [theta_observed]
    ells = [L]
    K_HOs = [K_HO]

    for i in range(1,T):
        addition = np.zeros(thetas[-1].shape)

        for i in range(theta.shape[0]):
            addition[i, np.random.randint(0, theta.shape[0], size=degree)] = np.random.randn(degree)
        addition[np.triu_indices(theta.shape[0])[::-1]] = addition[np.triu_indices(theta.shape[0])]
        addition *= (epsilon/np.linalg.norm(addition))
        np.fill_diagonal(addition, 0)
        addition *= epsilon / np.linalg.norm(addition)
        theta = thetas[-1] + addition
        theta[np.abs(theta)<2*epsilon/(theta.shape[0])] = 0
        for j in range(n_dim_obs):
            indices = list(np.where(theta[j,:]!=0)[0])
            indices.remove(j)
            if(len(indices)>degree):
                choice = np.random.choice(indices, len(indices)-degree)
                theta[j,choice] = 0
                theta[choice,j] = 0
        # plot_graph_with_latent_variables(theta, 0, theta.shape[0], "Theta" + str(i))
        assert(is_pos_def(theta))

        K_HO = K_HOs[-1].copy()
        addition = np.random.rand(*K_HO.shape)
        addition *= (epsilon / np.linalg.norm(addition))
        K_HO += addition
        K_HO = K_HO / np.sum(K_HO, axis=1)[:, None]
        K_HO *=0.12
        K_HO[np.abs(K_HO)<epsilon/(theta.shape[0])] = 0
        K_HOs.append(K_HO)
        L = K_HO.T.dot(K_HO)
        assert np.linalg.matrix_rank(L) == n_dim_lat
        assert(is_pos_semidef(L))
        assert(is_pos_def(theta - L))
        thetas.append(theta)
        thetas_obs.append(theta - L)
        ells.append(L)
        K_HOs.append(K_HO)

    return thetas, thetas_obs, ells


def generate_dataset_with_fixed_L(
        n_dim_obs=10, n_dim_lat=2, epsilon=1e-3, T=10, degree=2):
    """Generate precisions with a fixed L matrix."""
    K_HO = np.zeros((n_dim_lat, n_dim_obs))
    for i in range(n_dim_lat):
        percentage = int(n_dim_obs * 0.8)
        indices = np.random.randint(0, high=n_dim_obs, size=percentage)
        K_HO[i, indices] = np.random.rand(percentage)
    L = K_HO.T.dot(K_HO)
    L *= (0.12/np.sqrt(n_dim_obs))/np.max(L)
    assert(is_pos_semidef(L))
    assert np.linalg.matrix_rank(L) == n_dim_lat

    theta = np.eye(n_dim_obs)
    for i in range(n_dim_obs):
        l = list(set(np.arange(0, n_dim_obs)) -
                set().union(list(np.nonzero(theta[i,:])[0]),
                            list(np.where(np.count_nonzero(theta, axis=1)>=3)[0])))
        if len(l) == 0:
            continue
        indices = np.random.choice(l, degree-(np.count_nonzero(theta[i,:])-1))
        theta[i, indices] = theta[indices, i] = .5 / degree
    assert(is_pos_def(theta))
    theta_observed = theta - L
    assert(is_pos_def(theta_observed))

    thetas = [theta]
    thetas_obs = [theta_observed]

    for i in range(1, T):
        addition = np.zeros(thetas[-1].shape)
        for i in range(n_dim_obs):
            addition[i, np.random.randint(0, n_dim_obs, size=degree)] = np.random.randn(degree)
        addition[np.triu_indices(n_dim_obs)[::-1]] = addition[np.triu_indices(n_dim_obs)]
        addition *= (epsilon/np.linalg.norm(addition))
        np.fill_diagonal(addition, 0)
        theta = thetas[-1] + addition
        theta[np.abs(theta)<2*epsilon/(theta.shape[0])] = 0
        for j in range(n_dim_obs):
            indices = list(np.where(theta[j,:]!=0)[0])
            indices.remove(j)
            if(len(indices)>degree):
                choice = np.random.choice(indices, len(indices)-degree)
                theta[j,choice] = 0
                theta[choice,j] = 0

        #plot_graph_with_latent_variables(theta, 0, theta.shape[0], "Theta"+str(i))
        assert(is_pos_def(theta))
        assert(is_pos_def(theta - L))
        thetas.append(theta)
        thetas_obs.append(theta - L)

    return thetas, thetas_obs, L


def generate_dataset(n_dim_obs=3, n_dim_lat=2, eps=1e-3, T=10, degree=2,
                     n_samples=50, mode="evolving"):
    if mode == "evolving":
        func = generate_dataset_with_evolving_L
    elif mode == "fixed":
        func = generate_dataset_with_fixed_L
    elif mode == "l1":
        func = generate_dataset_L1
    elif mode == "l1l2":
        func = generate_dataset_L1L2
    else:
        return generate_dataset_fede(n_dim_obs, n_dim_lat, eps, T, n_samples)

    thetas, thetas_obs, ells = func(n_dim_obs, n_dim_lat, eps, T, degree)
    sigmas = np.array(map(np.linalg.inv, thetas_obs))
    map(normalize_matrix, sigmas)  # in place
    data_list = [np.random.multivariate_normal(
        np.zeros(n_dim_obs), sigma, size=n_samples) for sigma in sigmas]
    return data_list, thetas, thetas_obs, ells


def generate_dataset_fede(
        n_dim_obs=3, n_dim_lat=2, eps=1e-3, T=10, n_samples=50):
    """Generate dataset (new version)."""
    b = np.random.rand(1, n_dim_obs)
    es, Q = np.linalg.eigh(b.T.dot(b))  # Q random

    b = np.random.rand(1, n_dim_obs)
    es, R = np.linalg.eigh(b.T.dot(b))  # R random

    start_sigma = np.random.rand(n_dim_obs) + 1
    start_lamda = np.zeros(n_dim_obs)
    idx = np.random.randint(n_dim_obs, size=n_dim_lat)
    start_lamda[idx] = np.random.rand(2)

    Ks = []
    Ls = []
    Kobs = []

    for i in range(T):
        K = np.linalg.multi_dot((Q, np.diag(start_sigma), Q.T))
        L = np.linalg.multi_dot((R, np.diag(start_lamda), R.T))

        K[np.abs(K) < eps] = 0  # enforce sparsity on K

        assert is_pos_def(K - L)
        assert is_pos_semidef(L)

        start_sigma += 1 + np.random.rand(n_dim_obs)
        start_lamda[idx] += np.random.rand(n_dim_lat) * 2 - 1
        start_lamda = np.maximum(start_lamda, 0)

        Ks.append(K)
        Ls.append(L)
        Kobs.append(K - L)

    ll = map(np.linalg.inv, Kobs)
    map(normalize_matrix, ll)  # in place

    data_list = [np.random.multivariate_normal(
        np.zeros(n_dim_obs), l, size=n_samples) for l in ll]
    return data_list, Kobs, Ks, Ls


def generate_ma_xue_zou(n_dim_obs=12, epsilon=1e-3, sparsity = 0.1):
    """Generate the dataset as in Ma, Xue, Zou (2012)."""
    p = n_dim_obs + int(n_dim_obs+0.05)
    po = n_dim_obs
    ph = p - n_dim_obs
    W = np.zeros((p,p))
    picks = np.random.permutation(p*p)
    dim = int(p*p*sparsity)
    picks = picks[1:dim]
    W = W.ravel()
    W[picks] = np.random.randn(dim);
    W.reshape((p,p))

    C = W.T.dot(W)
    print(C)
    C[0:po,po:p] = C[0:po,po:p] + 0.5*np.random.randn((po,ph))
    C = (C+C.T)/2;

    d = diag(C)
    np.clip(C, -1, 1, out=C)
    eig, Q = np.linalg.eigh(C)
    K = C + max(-1.2 * np.min(eig), 0.001) * np.eye(p)
    KO = K[0:po,0:po]
    KOH = K[0:po,po:p]
    KHO = K[po:p,0:po]
    KH = K[po:p,po:p]
    assert(is_pos_semidef(KH))
    assert(np.linalg.matrix_rank( np.divide(KOH, KH.dot(KHO))) == ph)
    KOtilde = KO - np.divide(KOH, KH.dot(KHO))
    assert(is_pos_def(KOtilde))
    N = 5*po;

    EmpCov = np.linalg.inverse(KOtilde)
    EmpCov = (EmpCov + EmpCov.T)/2
    data = np.random.multivariate_normal(np.zeros(po), EmpCov, size=N)
    SigmaO = (1/N)*data.T.dot(data)
