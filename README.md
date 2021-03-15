# Kaggle の Titanic データセットを使った機械学習パイプラインの構築
Kaggle の Titanic データセットを活用して、機械学習におけるデータの前処理、学習、推論を自動化するパイプラインを AWS 上に構築します。

## 実行環境の構築
サンプルノートブックは Amazon SageMaker の Jupyter 環境であるノートブックインスタンス上で実行することを想定しています。また、Amazon SageMaker ノートブックインスタンス インスタンスと AWS StepFunctions にそれぞれ IAM ロールのやポリシーの準備が必要になります。詳細は[コチラ](https://github.com/aws-samples/amazon-sagemaker-examples-jp/blob/legacy/step-functions-data-science-sdk/machine_learning_workflow_abalone.ipynb)をご参考に下さい。

## サンプルの構成

### データの準備

[0_preparation.ipynb](https://github.com/tkazusa/kaggle-mlpipeline-titanic/blob/main/notebooks/0_preparation.ipynb) では Kaggle API を活用してデータのダウンロードを行います。

### Jyupyter ノートブック上での前処理、学習、推論

[1_train_inference_notebook.ipynb](https://github.com/tkazusa/kaggle-mlpipeline-titanic/blob/main/notebooks/1_train_inference_notebook.ipynb) ではデータの前処理、学習、推論を Jupyter ノートブック上で行います。 モデルは [`scikit-learn` ](https://scikit-learn.org/) のランダムフォレストを活用します。特徴量作成やアルゴリズムの選択、ハイパーパラメータの探索など、精度向上の余地などはありますが、まずはパイプラインのベースとします。 Code にあった [Titanic: random forest using sklearn and pandas](https://www.kaggle.com/edeastwood/titanic-random-forest-using-sklearn-and-pandas) を参考にさせて頂きました。

### AWS のサービスを使ったサーバレスな前処理、学習、推論

[2_train_inference_SageMakerJobs.ipynb](https://github.com/tkazusa/kaggle-mlpipeline-titanic/blob/main/notebooks/2_train_inference_SageMakerJobs.ipynb) では、AWS のマネージドな機械学習基盤サービスである、Amazon SageMaker を活用して、前処理や学習、推論を行います。データサイズが大きい、学習に時間がかかる、など Jupyter 環境では処理がしにくいような計算をそれぞれのジョブとしてサーバレスに実行するすることができます。


### 機械学習パイプラインを構築した前処理、学習、推論の自動化

[3_ml_pipeline_StepFunctions.ipynb](https://github.com/tkazusa/kaggle-mlpipeline-titanic/blob/main/notebooks/3_ml_pipeline_StepFunctions.ipynb) では、AWS StepFunctions を活用し、2 で活用したジョブを一つのパイプラインにまとめます。その際、エラーハンドリングを行う機構も構築します。構築したパイプラインはそのまま AWS 上に構築することができ、CloudFormation のテンプレートとしてもエクスポートできます。


## 参考資料
- [Titanic: random forest using sklearn and pandas](https://www.kaggle.com/edeastwood/titanic-random-forest-using-sklearn-and-pandas)
