import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 加载数据
df = pd.read_csv('data/social_ecommerce_data.csv')
print(f"数据形状: {df.shape}")
print(f"列数: {len(df.columns)}")
print(f"\n缺失值: {df.isnull().sum().sum()}")

# ===== 1. 用户分群分析 =====
print("\n" + "="*50)
print("1. 用户分群分析")
print("="*50)

# 按用户聚合数据
user_data = df.groupby('user_id').agg({
    'total_spend': 'first',
    'purchase_freq': 'first',
    'fans_num': 'first',
    'follow_num': 'first',
    'age': 'first',
    'gender': 'first',
    'user_level': 'first',
    'register_days': 'first',
    'label': 'mean'
}).reset_index()

# 计算社交活跃度
user_data['social_activity'] = user_data['fans_num'] + user_data['follow_num']

print(f"\n用户总数: {len(user_data)}")
print(f"\n用户指标统计:")
print(user_data[['total_spend', 'purchase_freq', 'social_activity']].describe())

# 聚类
clustering_features = ['total_spend', 'purchase_freq', 'social_activity']
X = user_data[clustering_features].copy()
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
user_data['cluster'] = kmeans.fit_predict(X_scaled)

# 分析各聚类特征
print("\n各用户群体特征:")
print("-" * 80)
for cluster_id in range(4):
    cluster_users = user_data[user_data['cluster'] == cluster_id]
    print(f"\n群体 {cluster_id} (用户数: {len(cluster_users)})")
    print(f"  平均消费: ¥{cluster_users['total_spend'].mean():.2f}")
    print(f"  平均购买频率: {cluster_users['purchase_freq'].mean():.2f}次")
    print(f"  平均社交活跃度: {cluster_users['social_activity'].mean():.2f}")
    print(f"  平均年龄: {cluster_users['age'].mean():.1f}岁")
    print(f"  购买率: {cluster_users['label'].mean():.2%}")

# ===== 2. 商品内容特征分析 =====
print("\n" + "="*50)
print("2. 商品内容特征分析")
print("="*50)

# 视频影响
print("\n有视频 vs 无视频:")
print("-" * 80)
video_analysis = df.groupby('has_video').agg({
    'like_num': 'mean',
    'comment_num': 'mean',
    'share_num': 'mean',
    'label': 'mean',
    'interaction_rate': 'mean'
}).round(2)
print(video_analysis)

# 图片数量影响
print("\n图片数量与互动:")
print("-" * 80)
df['img_group'] = pd.cut(df['img_count'], bins=[0, 2, 4, 6, 10], labels=['1-2张', '3-4张', '5-6张', '7+张'])
img_analysis = df.groupby('img_group').agg({
    'like_num': 'mean',
    'interaction_rate': 'mean',
    'label': 'mean'
}).round(2)
print(img_analysis)

# 标题情感与互动
print("\n标题情感分数与互动:")
print("-" * 80)
df['emo_group'] = pd.cut(df['title_emo_score'], bins=[0, 0.4, 0.6, 0.8, 1.0],
                          labels=['低情感', '中低情感', '中高情感', '高情感'])
emo_analysis = df.groupby('emo_group').agg({
    'like_num': 'mean',
    'interaction_rate': 'mean',
    'label': 'mean'
}).round(2)
print(emo_analysis)

# 折扣率影响
print("\n折扣率与购买:")
print("-" * 80)
df['discount_group'] = pd.cut(df['discount_rate'], bins=[0, 0.1, 0.2, 0.3, 0.5],
                               labels=['无折扣', '10%以下', '10-20%', '20%以上'])
discount_analysis = df.groupby('discount_group').agg({
    'label': 'mean',
    'interaction_rate': 'mean'
}).round(2)
print(discount_analysis)

# ===== 3. 类目分析 =====
print("\n" + "="*50)
print("3. 商品类目分析")
print("="*50)

print("\n各类目表现:")
print("-" * 80)
category_analysis = df.groupby('category').agg({
    'label': ['mean', 'count'],
    'like_num': 'mean',
    'interaction_rate': 'mean',
    'total_spend': 'mean'
}).round(2)
print(category_analysis)

# ===== 4. 关键洞见 =====
print("\n" + "="*50)
print("4. 关键洞见")
print("="*50)

# 高价值用户特征
high_value = user_data[user_data['total_spend'] > user_data['total_spend'].quantile(0.75)]
low_value = user_data[user_data['total_spend'] < user_data['total_spend'].quantile(0.25)]

print(f"\n高价值用户 vs 低价值用户:")
print(f"  高价值用户平均社交活跃度: {high_value['social_activity'].mean():.2f}")
print(f"  低价值用户平均社交活跃度: {low_value['social_activity'].mean():.2f}")
print(f"  高价值用户购买率: {high_value['label'].mean():.2%}")
print(f"  低价值用户购买率: {low_value['label'].mean():.2%}")

# 内容特征对购买的影响
print(f"\n内容特征对购买的影响:")
print(f"  有视频商品购买率: {df[df['has_video']==1]['label'].mean():.2%}")
print(f"  无视频商品购买率: {df[df['has_video']==0]['label'].mean():.2%}")

high_emo = df[df['title_emo_score'] > 0.7]
low_emo = df[df['title_emo_score'] < 0.4]
print(f"  高情感标题购买率: {high_emo['label'].mean():.2%}")
print(f"  低情感标题购买率: {low_emo['label'].mean():.2%}")

print("\n分析完成！")
