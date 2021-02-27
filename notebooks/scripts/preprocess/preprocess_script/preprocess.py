import re
import joblib
import os
import argparse

import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn import preprocessing


def deriveTitles(name: str) -> str:
    """ name に含まれるタイトルをそれぞれのカテゴリに変換
    Args:
        name (str): 登場者の名前
    Returns:
        名前から抽出されたタイトルに従って変換されたカテゴリ (int)
    """
    title = re.search('(?:\S )(?P<title>\w*)', name).group('title')
    
    if title == "Mr":             return "adult"
    elif title == "Don":          return "gentry"
    elif title == "Dona":         return "gentry"
    elif title == "Miss":         return "miss"
    elif title == "Col":          return "military"
    elif title == "Rev":          return "other"
    elif title == "Lady":         return "gentry"
    elif title == "Master":       return "child"
    elif title == "Mme":          return "adult"
    elif title == "Captain":      return "military"
    elif title == "Dr":           return "other"
    elif title == "Mrs":          return "adult"
    elif title == "Sir":          return "gentry"
    elif title == "Jonkheer":     return "gentry"
    elif title == "Mlle":         return "miss"
    elif title == "Major":        return "military"
    elif title == "Ms":           return "miss"
    elif title == "the Countess": return "gentry"
    else:                         return "other"
    

def deriveChildren(age: int, parch: int) -> int:
    """ 連れている両親の数だけを抽出。18歳以上は両親がいないと仮定。
    Args:
        age (int): 搭乗者の年齢
        parch (int): 両親、子供の数
    Returns:
        両親の数 (int)
    """
    if(age < 18):
        return parch
    else:
        return 0
    
def deriveParents(age: int, parch: int) -> int:
    """ 連れている子供の数だけを抽出。18歳未満は子供がいないと仮定。
    Args:
        age (int): 搭乗者の年齢
        parch (int): 両親、子供の数
    Returns:
        子供の数 (int)
    """
    if(age > 17):
        return parch
    else:
        return 0 

def deriveResponsibleFor(children: int, SibSp: int) -> float:
    """ 自分を含めた同行者における18歳以上のの大人と責任を持つべき子供の割合を算出。
    Args:
        children (int): 子供の数
        SibSp (int): 兄弟、配偶者の数
    Returns:
        責任 (XXX)
    """
    if(children > 0):
        return children / (SibSp + 1)  # float何にする?
    else:
        return 0
    

def deriveResponsibleFor(children: int, SibSp: int) -> float:
    """ 自分を含めた同行者における18歳以上のの大人と責任を持つべき子供の割合を算出。
    Args:
        children (int): 子供の数
        SibSp (int): 兄弟、配偶者の数
    Returns:
        責任 (XXX)
    """
    if(children > 0):
        return children / (SibSp + 1)  # float何にする?
    else:
        return 0
    
def deriveAccompaniedBy(parents, SibSp):
    """ 親が1以上いる場合に、自分を含めた同行者における、両親の割合を算出。
    Args:
        parents (int): 親の数
        SibSp (int): 兄弟、配偶者の数
    Returns:
        親に対する子供の割合 (XXX)
    """
    if(parents > 0): return parents / (SibSp + 1)
    else: return 0
    
    
def deriveAccompaniedBy(parents, SibSp):
    """ 親が1以上いる場合に、自分を含めた同行者における、両親の割合を算出。
    Args:
        parents (int): 親の数
        SibSp (int): 兄弟、配偶者の数
    Returns:
        親に対する子供の割合 (XXX)
    """
    if(parents > 0): return parents / (SibSp + 1)

    
def unaccompaniedChild(age: int, parch: int) -> bool:
    """ 同行者がいない16歳以下の搭乗者かどうかを判定。
    Args:
        age (int): 搭乗者の年齢
        parch (int): 同行者の数
    Returns:
        同行者がいない場合 True, いる場合 False (bool)
    """
    if((age < 16) & (parch == 0)):
        return True
    else:
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_type', type=str)
    parser.add_argument('--input_dir', type=str, default=None)
    parser.add_argument('--output_dir', type=str, default=None)

    args, _ = parser.parse_known_args()
    
    data_type = args.data_type
    input_data_path = os.path.join(args.input_dir, data_type+'.csv')
    output_data_path = os.path.join(args.output_dir, data_type+'.csv')
    
    data = pd.read_csv(input_data_path)
    
    data = data.drop(['Cabin'], axis=1)
    data = data.dropna(how="any")
    
    data["title"] = data.Name.apply(deriveTitles)
    le = preprocessing.LabelEncoder()
    titles = ['adult', 'gentry', 'miss', 'military', 'other', 'child']
    le.fit(titles)
    data['encodedTitle'] = le.transform(data['title']).astype('int')
    
    data = data.assign(SibSpGroup1=data['SibSp'] < 2)
    data = data.assign(SibSpGroup2=data['SibSp'].between(2, 3, inclusive=True))
    data = data.assign(SibSpGroup3=data['SibSp'] > 2)

    data = data.assign(ParChGT2=data['Parch'] > 2)
    data = data.assign(familySize=data['Parch'] + data['SibSp'])

    data = data.assign(children=data.apply(lambda row: deriveChildren(row['Age'], row['Parch']), axis = 1))

    data['parents'] = data.apply(lambda row: deriveParents(row['Age'], row['Parch']), axis = 1)
    data['responsibleFor'] = data.apply(lambda row: deriveResponsibleFor(row['children'], row['SibSp']), axis = 1)
    data['accompaniedBy'] = data.apply(lambda row: deriveAccompaniedBy(row['parents'], row['SibSp']), axis = 1)
    data['unaccompaniedChild'] = data.apply(lambda row: unaccompaniedChild(row['Age'], row['Parch']), axis = 1)

    data = data.astype({"Pclass": int, "Age": int, "SibSp": int, "Parch": int})

    categorical_names = {}
    categorical_features = ['Embarked', 'Sex']
    for feature in categorical_features:
        le = preprocessing.LabelEncoder()
        le.fit(data[feature])
        data[feature] = le.transform(data[feature])
        categorical_names[feature] = le.classes_


    data['class'] = data['Pclass'].astype(int, copy=False)
    data = data.drop(['Pclass'], axis=1)
    data = data.drop(['Name', 'Parch', 'SibSp', 'title', 'Ticket', 'PassengerId'], axis=1)
    
    data.to_csv(output_data_path, header=True, index=False)