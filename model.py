def autoClusterer(main_df_path, x_df_path, do_pca=True):

    import os
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import DBSCAN, KMeans
    from sklearn.metrics import silhouette_score
    from sklearn.decomposition import PCA
    from sklearn.ensemble import IsolationForest


    df = pd.read_csv(main_df_path)


    X = pd.read_csv(x_df_path)


    if do_pca:
        if len(X.columns) > 2:
            pca = PCA(n_components=2)

            X = pca.fit_transform(X)


    scaler = StandardScaler()


    X = scaler.fit_transform(X)


    isoforest = IsolationForest(contamination=0.1, random_state=42, n_jobs=-1)

    outliers = isoforest.fit_predict(X)

    plt.scatter(X[:,0], X[:,1], c=outliers)
    

    def delete_where_minus1(data, mask, axis=0):
        mask = np.asarray(mask)
        

        if data.shape[axis] != mask.shape[0]:
            raise ValueError("طول mask با طول داده در محور انتخابی برابر نیست")
        

        keep = mask != -1
        

        if axis == 0:
            return data[keep]
        elif axis == 1:
            return data[:, keep]
        elif axis == 2:
            return data[:, :, keep]
        else:

            slicer = [slice(None)] * data.ndim
            slicer[axis] = keep
            return data[tuple(slicer)]



    X = delete_where_minus1(X, outliers)
    df = delete_where_minus1(df, outliers)


    scores = {}

    for k in range(2, 21):
        model = KMeans(init="k-means++", random_state=42, n_clusters=k)

        model.fit(X)

        if -1 in list(set(model.labels_)):
            if len(list(set(model.labels_))) >= 3:
                scores[k] = silhouette_score(X, model.labels_)
        else:
            if len(list(set(model.labels_))) >= 2:
                scores[k] = silhouette_score(X, model.labels_)

    score = 2
    for i in scores.keys():
        if scores[i] == max(scores.values()):
            best_k = i
        score += 1



    scores = {}
    for eps in range(1, 21):
        model = DBSCAN(eps=eps/10, n_jobs=-1)

        model.fit(X)

        
        if -1 in list(set(model.labels_)):
            if len(list(set(model.labels_))) >= 3:
                scores[eps/10] = silhouette_score(X, model.labels_)
        else:
            if len(list(set(model.labels_))) >= 2:
                scores[eps/10] = silhouette_score(X, model.labels_)


    score = 0.1
    for i in scores.keys():
        if scores[i] == max(scores.values()):
            best_eps = i
        score += 1



    model2 = DBSCAN(eps=best_eps, n_jobs=-1)
    model2.fit(X)


    model_scores = {}


    model1 = KMeans(init="k-means++", random_state=42, n_clusters=best_k)
    model2 = DBSCAN(eps=best_eps, n_jobs=-1)

    model1.fit(X)
    model2.fit(X)

    model_scores[model1.__class__] = silhouette_score(X, model1.labels_)
    model_scores[model2.__class__] = silhouette_score(X, model2.labels_)




    for i in model_scores.keys():
        if model_scores[i] == max(model_scores.values()):
            model_type = i



    if str(model_type) == "sklearn.cluster._kmeans.KMeans":
        model = KMeans(init="k-means++", random_state=42, n_clusters=best_k)
        model.fit(X)
        model_score = silhouette_score(X, model1.labels_)
        model_labels = model.labels_

    else:
        model = DBSCAN(eps=best_eps, n_jobs=-1)
        model.fit(X)
        model_score = silhouette_score(X, model1.labels_)
        model_labels = model.labels_




    def split_clusters(df, labels, as_dict=True):

        if len(labels) != len(df):
            raise ValueError("طول labels با تعداد سطرهای df برابر نیست!")


        df_labeled = df.copy()
        df_labeled["cluster"] = labels


        clusters = {
            cid: part.drop(columns="cluster").reset_index(drop=True)
            for cid, part in df_labeled.groupby("cluster")
        }

        return clusters if as_dict else list(clusters.values())


    clusters = split_clusters(df, model_labels)


    try:
        os.listdir("results/dfs")
        for i in os.listdir("results/dfs"):
            os.remove(f"results/dfs/{i}")
    except Exception as e:
        os.makedirs("results/dfs")
        for i in os.listdir("results/dfs"):
            os.remove(f"results/dfs/{i}")

    try:
        os.listdir("results/images")
        for i in os.listdir("results/images"):
            os.remove(f"results/images/{i}")
    except Exception as e:
        os.makedirs("results/images")
        for i in os.listdir("results/images"):
            os.remove(f"results/images/{i}")

    if do_pca or len(pd.DataFrame(X).columns) == 2:
        plt.figure(figsize=(12,8))
        plt.scatter(pd.DataFrame(scaler.inverse_transform(X)).iloc[:, 0], pd.DataFrame(scaler.inverse_transform(X)).iloc[:, 1], c=model_labels)
        plt.savefig("results/images/plot.jpg")

    for n,i in enumerate(clusters.values()):
        i.to_csv(f"results/dfs/df_{n}.csv")


    return model_score