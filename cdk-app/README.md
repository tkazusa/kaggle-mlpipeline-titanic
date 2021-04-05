# 本ハンズオンのリソースを AWS CDK を使ってプロビジョニングする

### Requirements

- Python>=3.8.5
- npm>=6.14
- aws-cdk>=1.96.0

### CloudFormation スタックの作成方法

```
$ pip install -r requirements.txt
$ cdk synth
$ cdk deploy 
```

### スタックの削除方法

```
$ cdk destroy
```