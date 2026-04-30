import pandas as pd
import numpy as np
import json
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Load data
df = pd.read_csv('data/social_ecommerce_data.csv')

# Create age groups
df['age_group'] = pd.cut(df['age'], bins=[0, 25, 35, 45, 100], labels=['18-25', '26-35', '36-45', '46+'])

# Create spending levels
df['spend_level'] = pd.qcut(df['total_spend'], q=3, labels=['low', 'mid', 'high'], duplicates='drop')

# Aggregate by user
user_data = df.groupby('user_id').agg({
    'total_spend': 'first',
    'purchase_freq': 'first',
    'fans_num': 'first',
    'follow_num': 'first',
    'age': 'first',
    'age_group': 'first',
    'gender': 'first',
    'label': 'mean',
    'spend_level': 'first',
    'pv_count': 'mean'
}).reset_index()

user_data['social_activity'] = user_data['fans_num'] + user_data['follow_num']

# Create social activity levels
user_data['social_level'] = pd.qcut(user_data['social_activity'], q=3, labels=['low', 'mid', 'high'], duplicates='drop')

# Generate results
results = {
    'overview': {},
    'age_groups': {},
    'behavior_insights': {},
    'categories': {},
    'user_levels': sorted(df['user_level'].unique().tolist())
}

# Calculate overview (all data aggregated)
total_users = len(user_data)
gender_dist = user_data['gender'].value_counts().to_dict()

results['overview'] = {
    'total_users': int(total_users),
    'total_spend': float(user_data['total_spend'].sum()),
    'avg_spend': float(user_data['total_spend'].mean()),
    'avg_purchase_freq': float(user_data['purchase_freq'].mean()),
    'avg_social_activity': float(user_data['social_activity'].mean()),
    'purchase_rate': float(user_data['label'].mean()),
    'avg_pv': float(user_data['pv_count'].mean()),
    'gender_distribution': {
        'male': int(gender_dist.get(0, 0)),
        'female': int(gender_dist.get(1, 0)),
        'male_ratio': float(gender_dist.get(0, 0) / total_users) if total_users > 0 else 0,
        'female_ratio': float(gender_dist.get(1, 0) / total_users) if total_users > 0 else 0
    },
    'spend_distribution': [],
    'social_scatter': [],
    'top_categories': {}
}

# Spend distribution for overview
bins = [0] + list(range(501, 10001, 500)) + list(range(10001, 50001, 5000)) + [np.inf]
spend_bins = pd.cut(user_data['total_spend'], bins=bins, right=False)
spend_counts = spend_bins.value_counts().sort_index()

for interval, interval_count in spend_counts.items():
    if interval.right == np.inf:
        range_label = '50000+'
    else:
        left = int(interval.left)
        right = int(interval.right) - 1
        range_label = f'{left}-{right}'

    # Get top 5 most common categories for this spend range
    mask = (user_data['total_spend'] >= interval.left) & (user_data['total_spend'] < interval.right)
    if interval.right == np.inf:
        mask = user_data['total_spend'] >= interval.left

    range_df = df[df['user_id'].isin(user_data[mask]['user_id'])]
    top5_categories = range_df['category'].value_counts().head(5)

    top5_list = []
    for category, cat_count in top5_categories.items():
        top5_list.append({
            'category': str(category),
            'count': int(cat_count)
        })

    results['overview']['spend_distribution'].append({
        'range': range_label,
        'count': int(interval_count),
        'top5_categories': top5_list
    })

# Top categories for overview
category_stats = df.groupby('category').agg({
    'label': 'mean',
    'total_spend': 'mean',
    'user_id': 'count'
}).rename(columns={'label': 'purchase_rate', 'total_spend': 'avg_spend', 'user_id': 'count'})

category_stats = category_stats.sort_values('purchase_rate', ascending=False)

for cat in category_stats.index:
    results['overview']['top_categories'][cat] = {
        'purchase_rate': float(category_stats.loc[cat, 'purchase_rate']),
        'avg_spend': float(category_stats.loc[cat, 'avg_spend']),
        'count': int(category_stats.loc[cat, 'count'])
    }

# Social scatter for overview (all records for complete overview)
for _, user in user_data.iterrows():
    results['overview']['social_scatter'].append({
        'social_activity': float(user['social_activity']),
        'total_spend': float(user['total_spend']),
        'fans_num': int(user['fans_num']),
        'follow_num': int(user['follow_num'])
    })

# Analyze by age group
for age_group in ['18-25', '26-35', '36-45', '46+']:
    group_data = user_data[user_data['age_group'] == age_group]
    group_df = df[df['age_group'] == age_group]

    # Gender distribution
    gender_dist = group_data['gender'].value_counts().to_dict()
    total_users = len(group_data)

    results['age_groups'][age_group] = {
        'user_count': int(total_users),
        'avg_spend': float(group_data['total_spend'].mean()),
        'avg_purchase_freq': float(group_data['purchase_freq'].mean()),
        'avg_social_activity': float(group_data['social_activity'].mean()),
        'purchase_rate': float(group_data['label'].mean()),
        'avg_pv': float(group_data['pv_count'].mean()),
        'gender_distribution': {
            'male': int(gender_dist.get(0, 0)),
            'female': int(gender_dist.get(1, 0)),
            'male_ratio': float(gender_dist.get(0, 0) / total_users) if total_users > 0 else 0,
            'female_ratio': float(gender_dist.get(1, 0) / total_users) if total_users > 0 else 0
        },
        'spend_distribution': [],
        'social_scatter': [],
        'top_categories': {}
    }

    # Spend distribution by custom intervals (0-500, 501-1000, ..., 50000+)
    bins = [0] + list(range(501, 10001, 500)) + list(range(10001, 50001, 5000)) + [np.inf]
    spend_bins = pd.cut(group_data['total_spend'], bins=bins, right=False)
    spend_counts = spend_bins.value_counts().sort_index()

    for interval, interval_count in spend_counts.items():
        if interval.right == np.inf:
            range_label = '50000+'
        else:
            left = int(interval.left)
            right = int(interval.right) - 1
            range_label = f'{left}-{right}'

        # Get top 5 most common categories for this spend range
        mask = (group_data['total_spend'] >= interval.left) & (group_data['total_spend'] < interval.right)
        if interval.right == np.inf:
            mask = group_data['total_spend'] >= interval.left

        range_df = group_df[group_df['user_id'].isin(group_data[mask]['user_id'])]
        top5_categories = range_df['category'].value_counts().head(5)

        top5_list = []
        for category, cat_count in top5_categories.items():
            top5_list.append({
                'category': str(category),
                'count': int(cat_count)
            })

        results['age_groups'][age_group]['spend_distribution'].append({
            'range': range_label,
            'count': int(interval_count),
            'top5_categories': top5_list
        })

    # All categories for this age group
    category_stats = group_df.groupby('category').agg({
        'label': 'mean',
        'total_spend': 'mean',
        'user_id': 'count'
    }).rename(columns={'label': 'purchase_rate', 'total_spend': 'avg_spend', 'user_id': 'count'})

    category_stats = category_stats.sort_values('purchase_rate', ascending=False)

    for cat in category_stats.index:
        results['age_groups'][age_group]['top_categories'][cat] = {
            'purchase_rate': float(category_stats.loc[cat, 'purchase_rate']),
            'avg_spend': float(category_stats.loc[cat, 'avg_spend']),
            'count': int(category_stats.loc[cat, 'count'])
        }

    # Social activity vs spend scatter data
    for _, user in group_data.iterrows():
        results['age_groups'][age_group]['social_scatter'].append({
            'social_activity': float(user['social_activity']),
            'total_spend': float(user['total_spend']),
            'fans_num': int(user['fans_num']),
            'follow_num': int(user['follow_num'])
        })

# Behavior insights aggregation
df['has_like'] = (df['like_num'] > 0).astype(int)
df['has_comment'] = (df['comment_num'] > 0).astype(int)
df['has_share'] = (df['share_num'] > 0).astype(int)

def compute_social_purchase(subset):
    result = []
    for col, label in [('has_like', '点赞'), ('has_comment', '评论'), ('has_share', '分享')]:
        for flag, group_label in [(1, '有互动'), (0, '无互动')]:
            group = subset[subset[col] == flag]
            result.append({
                'interaction': label,
                'group': group_label,
                'purchase_rate': float(group['label'].mean()) if len(group) > 0 else 0.0,
                'count': int(len(group))
            })
    return result

def compute_funnel(subset):
    n = len(subset)
    has_social = (
        (subset['like_num'] > 0) |
        (subset['comment_num'] > 0) |
        (subset['share_num'] > 0)
    )
    return [
        {'step': '浏览', 'count': int(n)},
        {'step': '社交互动', 'count': int(has_social.sum())},
        {'step': '加购物车', 'count': int(subset['add2cart'].sum())},
        {'step': '领券', 'count': int(subset['coupon_received'].sum())},
        {'step': '用券', 'count': int(subset['coupon_used'].sum())},
        {'step': '购买', 'count': int(subset['label'].sum())},
    ]

def compute_sankey(subset):
    node_names = [
        '点赞·有', '点赞·无',
        '评论·有', '评论·无',
        '分享·有', '分享·无',
        '购买', '未购买'
    ]
    nodes = [{'name': n} for n in node_names]
    links = []

    node_idx = 0
    for col in ['has_like', 'has_comment', 'has_share']:
        for flag in [1, 0]:
            group = subset[subset[col] == flag]
            purchased = int((group['label'] == 1).sum())
            not_purchased = int((group['label'] == 0).sum())
            if purchased > 0:
                links.append({'source': node_idx, 'target': 6, 'value': purchased})
            if not_purchased > 0:
                links.append({'source': node_idx, 'target': 7, 'value': not_purchased})
            node_idx += 1

    return {'nodes': nodes, 'links': links}

# Create segments
segments = {'all': df}

# Age group segments
for age in ['18-25', '26-35', '36-45', '46+']:
    segments[f'age_{age}'] = df[df['age_group'] == age]

# Gender segments
for gender, lbl in [(0, 'male'), (1, 'female')]:
    segments[f'gender_{lbl}'] = df[df['gender'] == gender]

# User level segments
for level in range(1, 11):
    segments[f'level_{level}'] = df[df['user_level'] == level]

# Compute behavior insights for each segment
for seg_name, seg_data in segments.items():
    if len(seg_data) > 0:
        results['behavior_insights'][seg_name] = {
            'social_purchase': compute_social_purchase(seg_data),
            'funnel': compute_funnel(seg_data),
            'sankey': compute_sankey(seg_data)
        }

# Save to JSON
with open('analysis_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("Results saved to analysis_results.json")
print("\nAge group analysis:")
for age_group, data in results['age_groups'].items():
    print(f"\n{age_group}:")
    print(f"  Users: {data['user_count']}")
    print(f"  Avg spend: {data['avg_spend']:.2f}")
    print(f"  Avg frequency: {data['avg_purchase_freq']:.2f}")
    print(f"  Gender: M {data['gender_distribution']['male_ratio']:.1%} / F {data['gender_distribution']['female_ratio']:.1%}")
    print(f"  Top category: {list(data['top_categories'].keys())[0] if data['top_categories'] else 'N/A'}")
