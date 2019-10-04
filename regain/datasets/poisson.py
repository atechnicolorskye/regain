import warnings
import numpy as np
import networkx as nx


def update_l1(G, how_many, n_dim_obs):
    G = G.copy()
    rows = np.zeros(how_many)
    cols = np.zeros(how_many)
    while (np.any(rows == cols)):
        rows = np.random.randint(0, n_dim_obs, how_many)
        cols = np.random.randint(0, n_dim_obs, how_many)
        for r, c in zip(rows, cols):
            G[r, c] = np.random.choice([0, G[r, c]]) \
                      if G[r, c] != 0 \
                      else np.random.choice([0, np.random.normal(0.1, 0.01)])
            G[c, r] = G[r, c]
    assert (np.all(G == G.T))
    return G


def poisson_theta_generator(n_dim_obs=10, T=1, mode='l1',
                            random_graph='erdos-renyi', probability=0.2,
                            degree=3, n_to_change=3, **kwargs):
    if random_graph.lower() == 'erdos-renyi':
        graph = nx.random_graphs.fast_gnp_random_graph(n=n_dim_obs,
                                                      p=probability)
    elif random_graph.lower() == 'scale-free':
        graph = nx.random_graphs.barabasi_albert_graph(n=n_dim_obs, m=degree)
    elif random_graph.lower() == 'small-world':
        graph = nx.random_graphs.watts_strogatz_graph(n=n_dim_obs, k=degree,
                                                     p=probability)
    else:
        graph = nx.random_graphs.gnm_random_graph(n=n_dim_obs, m=degree)
    graph = nx.adjacency_matrix(graph).todense()
    print(graph)
    weights = np.ones((n_dim_obs, n_dim_obs))#np.random.normal(0.1, 0.01, size=(n_dim_obs, n_dim_obs))
    print(graph.shape)
    print(weights.shape)
    graphs = [np.multiply(graph, weights)]
    print(graphs[-1])
    for t in range(1, T):
        if mode == 'l2':
            raise ValueError("Still not implemented")
        elif mode == 'reshuffle':
            raise ValueError("Still not implemented")
        elif mode == 'l1':
            graph_t = update_l1(graphs[-1], n_to_change, graphs[0].shape[0])
        else:
            warnings.warn("Mode not implemented. Using l1.")
            graph_t = update_l1(graphs[-1], n_to_change, graphs[0].shape[0])
        graphs.append(graph_t)

    return graphs


def _adjacency_to_A(graph, typ='full'):
    A = np.eye(graph.shape[0])
    for i in range(graph.shape[0]-1):
        for j in range(i+1, graph.shape[0]):
            if typ == "full" or graph[i, j] != 0:
                tmp = np.zeros((graph.shape[0], 1))
                tmp[np.array([i, j]), 0] = 1
                A = np.hstack((A, tmp))
    return A


def poisson_sampler(theta, variances=None, n_samples=100, _type='LPGM',
                    _lambda=1, _lambda_noise=0.5, max_iter=200):
    n_dim_obs = theta.shape[0]
    if _type == 'LPGM':
        A = _adjacency_to_A(theta, typ='full')
        sigma = _lambda * theta
        ltri_sigma = sigma[np.tril_indices(sigma.shape[0], -1)]
        aux = np.array([_lambda]*sigma.shape[0]).reshape(sigma.shape[0])
        print()
        print(aux.shape)
        Y_lambda = np.array(list(aux) + ltri_sigma.ravel().tolist()[0])
        print(Y_lambda.shape)

        Y = np.array([np.random.poisson(l, n_samples) for l in Y_lambda]).T
        print(Y.shape)
        X = Y.dot(A.T)

        # add noise
        X = X + np.random.poisson(_lambda_noise, size=(n_samples, n_dim_obs))

    else:  # Gibbs sampling
        if variances is None or variances.size != n_dim_obs:
            variances = np.zeros(n_dim_obs)
        variances.reshape(n_dim_obs, 1)

        X = np.random.poisson(1, size=(n_samples, n_dim_obs))

        for iter_ in range(max_iter):
            for i in range(n_dim_obs):
                selector = np.array([j for j in range(n_dim_obs) if j != i])
                par = np.exp(variances[i] +
                             X[:, selector].dot(theta[selector, j]))
                X[:, i] = np.array([np.random.poisson(p) for p in par])

    return X