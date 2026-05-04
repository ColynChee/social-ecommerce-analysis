import pandas as pd
import numpy as np
import json

# =========================
# 1. Load data
# =========================
df = pd.read_csv('data/social_ecommerce_data.csv')

# =========================
# 2. Basic feature engineering
# =========================
df['age_group'] = pd.cut(
    df['age'],
    bins=[0, 25, 35, 45, 100],
    labels=['18-25', '26-35', '36-45', '46+']
)

df['spend_level'] = pd.qcut(
    df['total_spend'],
    q=3,
    labels=['low', 'mid', 'high'],
    duplicates='drop'
)

# Boolean behavior fields
df['has_like'] = (df['like_num'] > 0).astype(int)
df['has_comment'] = (df['comment_num'] > 0).astype(int)
df['has_share'] = (df['share_num'] > 0).astype(int)
df['has_collect'] = (df['collect_num'] > 0).astype(int)
df['has_social'] = (
    (df['like_num'] > 0) |
    (df['comment_num'] > 0) |
    (df['share_num'] > 0)
).astype(int)
df['has_cart'] = (df['add2cart'] > 0).astype(int)
df['has_coupon_received'] = (df['coupon_received'] > 0).astype(int)
df['has_coupon_used'] = (df['coupon_used'] > 0).astype(int)
df['has_purchase'] = (df['label'] == 1).astype(int)

# Avoid invalid values
df['safe_pv_count'] = df['pv_count'].replace(0, np.nan)
df['calc_interaction_rate'] = (
    (df['like_num'] + df['comment_num'] + df['share_num']) / df['safe_pv_count']
).replace([np.inf, -np.inf], np.nan).fillna(0)

# If original interaction_rate exists, keep it. Otherwise use calculated one.
if 'interaction_rate' not in df.columns:
    df['interaction_rate'] = df['calc_interaction_rate']

# =========================
# 3. Aggregate by user
# =========================
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

user_data['social_level'] = pd.qcut(
    user_data['social_activity'],
    q=3,
    labels=['low', 'mid', 'high'],
    duplicates='drop'
)

# =========================
# 4. Helper functions
# =========================
def safe_float(value, default=0.0):
    if pd.isna(value):
        return default
    return float(value)


def safe_int(value, default=0):
    if pd.isna(value):
        return default
    return int(value)


def make_spend_distribution(source_user_data, source_df):
    """消费金额分布，用于 overview 和 age_groups。"""
    distribution = []

    bins = [0] + list(range(501, 10001, 500)) + list(range(10001, 50001, 5000)) + [np.inf]
    spend_bins = pd.cut(source_user_data['total_spend'], bins=bins, right=False)
    spend_counts = spend_bins.value_counts().sort_index()

    for interval, interval_count in spend_counts.items():
        if interval.right == np.inf:
            range_label = '50000+'
            mask = source_user_data['total_spend'] >= interval.left
        else:
            left = int(interval.left)
            right = int(interval.right) - 1
            range_label = f'{left}-{right}'
            mask = (
                (source_user_data['total_spend'] >= interval.left) &
                (source_user_data['total_spend'] < interval.right)
            )

        range_df = source_df[source_df['user_id'].isin(source_user_data[mask]['user_id'])]
        top5_categories = range_df['category'].value_counts().head(5)

        top5_list = []
        for category, cat_count in top5_categories.items():
            top5_list.append({
                'category': str(category),
                'count': int(cat_count)
            })

        distribution.append({
            'range': range_label,
            'count': int(interval_count),
            'top5_categories': top5_list
        })

    return distribution


def make_top_categories(source_df):
    """按品类统计购买率、平均消费和样本量。"""
    result = {}

    if len(source_df) == 0:
        return result

    category_stats = source_df.groupby('category').agg({
        'label': 'mean',
        'total_spend': 'mean',
        'user_id': 'count'
    }).rename(columns={
        'label': 'purchase_rate',
        'total_spend': 'avg_spend',
        'user_id': 'count'
    })

    category_stats = category_stats.sort_values('purchase_rate', ascending=False)

    for cat in category_stats.index:
        result[str(cat)] = {
            'purchase_rate': safe_float(category_stats.loc[cat, 'purchase_rate']),
            'avg_spend': safe_float(category_stats.loc[cat, 'avg_spend']),
            'count': safe_int(category_stats.loc[cat, 'count'])
        }

    return result


def make_social_scatter(source_user_data):
    """社交活跃度与消费金额散点数据。"""
    scatter = []

    for _, user in source_user_data.iterrows():
        scatter.append({
            'social_activity': safe_float(user['social_activity']),
            'total_spend': safe_float(user['total_spend']),
            'fans_num': safe_int(user['fans_num']),
            'follow_num': safe_int(user['follow_num'])
        })

    return scatter


def compute_social_purchase(subset):
    """原有：有无点赞/评论/分享与购买率。"""
    result = []

    for col, label in [('has_like', '点赞'), ('has_comment', '评论'), ('has_share', '分享')]:
        for flag, group_label in [(1, '有互动'), (0, '无互动')]:
            group = subset[subset[col] == flag]
            result.append({
                'interaction': label,
                'group': group_label,
                'purchase_rate': safe_float(group['label'].mean()) if len(group) > 0 else 0.0,
                'count': int(len(group))
            })

    return result


def compute_funnel(subset):
    """原有漏斗：浏览、社交互动、加购物车、领券、用券、购买。"""
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
    """原有桑基图：点赞/评论/分享有无 -> 购买/未购买。"""
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


# =========================
# 5. New: social interaction analysis
# =========================
def build_fixed_group_analysis(subset, metric_col, group_col_name, bins, labels):
    """
    对点赞、评论、分享等计数字段分组，计算每组购买率、加购率、用券率等。
    """
    temp = subset.copy()

    temp[group_col_name] = pd.cut(
        temp[metric_col],
        bins=bins,
        labels=labels,
        include_lowest=True,
        right=True
    )

    grouped = temp.groupby(group_col_name, observed=False).agg(
        count=('user_id', 'count'),
        avg_metric=(metric_col, 'mean'),
        avg_like_num=('like_num', 'mean'),
        avg_comment_num=('comment_num', 'mean'),
        avg_share_num=('share_num', 'mean'),
        avg_collect_num=('collect_num', 'mean'),
        avg_pv_count=('pv_count', 'mean'),
        cart_rate=('has_cart', 'mean'),
        coupon_received_rate=('has_coupon_received', 'mean'),
        coupon_used_rate=('has_coupon_used', 'mean'),
        purchase_rate=('label', 'mean'),
        avg_purchase_intent=('purchase_intent', 'mean'),
        avg_interaction_rate=('interaction_rate', 'mean')
    ).reset_index()

    result = []
    for _, row in grouped.iterrows():
        result.append({
            'group': str(row[group_col_name]),
            'count': safe_int(row['count']),
            'avg_metric': safe_float(row['avg_metric']),
            'avg_like_num': safe_float(row['avg_like_num']),
            'avg_comment_num': safe_float(row['avg_comment_num']),
            'avg_share_num': safe_float(row['avg_share_num']),
            'avg_collect_num': safe_float(row['avg_collect_num']),
            'avg_pv_count': safe_float(row['avg_pv_count']),
            'cart_rate': safe_float(row['cart_rate']),
            'coupon_received_rate': safe_float(row['coupon_received_rate']),
            'coupon_used_rate': safe_float(row['coupon_used_rate']),
            'purchase_rate': safe_float(row['purchase_rate']),
            'avg_purchase_intent': safe_float(row['avg_purchase_intent']),
            'avg_interaction_rate': safe_float(row['avg_interaction_rate'])
        })

    return result


def build_quantile_group_analysis(subset, metric_col, group_col_name, label_prefix='Q'):
    """
    对 interaction_rate / purchase_intent 这类连续变量按分位数分组。
    """
    temp = subset.copy()

    if len(temp) == 0:
        return []

    # qcut 在重复值很多时可能无法切成 4 组，所以先尝试 qcut，失败则退化为 cut
    try:
        temp[group_col_name] = pd.qcut(temp[metric_col], q=4, duplicates='drop')
    except ValueError:
        temp[group_col_name] = pd.cut(temp[metric_col], bins=4, duplicates='drop')

    grouped = temp.groupby(group_col_name, observed=False).agg(
        count=('user_id', 'count'),
        avg_metric=(metric_col, 'mean'),
        avg_like_num=('like_num', 'mean'),
        avg_comment_num=('comment_num', 'mean'),
        avg_share_num=('share_num', 'mean'),
        avg_collect_num=('collect_num', 'mean'),
        avg_pv_count=('pv_count', 'mean'),
        cart_rate=('has_cart', 'mean'),
        coupon_received_rate=('has_coupon_received', 'mean'),
        coupon_used_rate=('has_coupon_used', 'mean'),
        purchase_rate=('label', 'mean'),
        avg_purchase_intent=('purchase_intent', 'mean'),
        avg_interaction_rate=('interaction_rate', 'mean')
    ).reset_index()

    result = []
    for i, row in grouped.iterrows():
        result.append({
            'group': f'{label_prefix}{i + 1}: {str(row[group_col_name])}',
            'count': safe_int(row['count']),
            'avg_metric': safe_float(row['avg_metric']),
            'avg_like_num': safe_float(row['avg_like_num']),
            'avg_comment_num': safe_float(row['avg_comment_num']),
            'avg_share_num': safe_float(row['avg_share_num']),
            'avg_collect_num': safe_float(row['avg_collect_num']),
            'avg_pv_count': safe_float(row['avg_pv_count']),
            'cart_rate': safe_float(row['cart_rate']),
            'coupon_received_rate': safe_float(row['coupon_received_rate']),
            'coupon_used_rate': safe_float(row['coupon_used_rate']),
            'purchase_rate': safe_float(row['purchase_rate']),
            'avg_purchase_intent': safe_float(row['avg_purchase_intent']),
            'avg_interaction_rate': safe_float(row['avg_interaction_rate'])
        })

    return result


def build_correlation_matrix(subset):
    """
    相关性矩阵：用于分析浏览、点赞、评论、分享、收藏、加购、用券、购买之间关系。
    输出格式：
    {
      "columns": [字段名...],
      "items": [字段名...],
      "matrix": [[相关系数...], ...]
    }
    这样前端 SocialInteractionAnalysis.vue 可以直接渲染热力图。
    """
    corr_cols = [
        'pv_count',
        'like_num',
        'comment_num',
        'share_num',
        'collect_num',
        'add2cart',
        'coupon_used',
        'interaction_rate',
        'purchase_intent',
        'label'
    ]

    available_cols = [col for col in corr_cols if col in subset.columns]

    if len(subset) == 0 or len(available_cols) == 0:
        return {
            'columns': available_cols,
            'items': available_cols,
            'matrix': []
        }

    corr_matrix = subset[available_cols].corr().fillna(0).round(3)

    return {
        'columns': [str(col) for col in available_cols],
        'items': [str(row) for row in available_cols],
        'matrix': [
            [
                safe_float(corr_matrix.loc[row, col])
                for col in available_cols
            ]
            for row in available_cols
        ]
    }


def compute_interaction_analysis(subset):
    """
    新增：社交互动与购买关系分析。
    用于回答：点赞、评论、分享这些“种草行为”是否真的会带来购买？
    """
    return {
        'like_groups': build_fixed_group_analysis(
            subset,
            metric_col='like_num',
            group_col_name='like_group',
            bins=[-1, 0, 5, 20, np.inf],
            labels=['0', '1-5', '6-20', '20+']
        ),
        'comment_groups': build_fixed_group_analysis(
            subset,
            metric_col='comment_num',
            group_col_name='comment_group',
            bins=[-1, 0, 2, 10, np.inf],
            labels=['0', '1-2', '3-10', '10+']
        ),
        'share_groups': build_fixed_group_analysis(
            subset,
            metric_col='share_num',
            group_col_name='share_group',
            bins=[-1, 0, 2, 10, np.inf],
            labels=['0', '1-2', '3-10', '10+']
        ),
        'interaction_rate_groups': build_quantile_group_analysis(
            subset,
            metric_col='interaction_rate',
            group_col_name='interaction_rate_group',
            label_prefix='互动率'
        ),
        'purchase_intent_groups': build_quantile_group_analysis(
            subset,
            metric_col='purchase_intent',
            group_col_name='purchase_intent_group',
            label_prefix='购买意向'
        ),
        'correlation_matrix': build_correlation_matrix(subset)
    }


# =========================
# 6. New: behavior path analysis
# =========================
def make_behavior_path(row):
    """
    生成单条记录的行为路径。
    """
    path = ['浏览']

    if row['has_social'] == 1:
        path.append('社交互动')
    else:
        path.append('无社交互动')

    if row['has_cart'] == 1:
        path.append('加购物车')
    else:
        path.append('未加购')

    if row['has_coupon_received'] == 1:
        path.append('领券')

    if row['has_coupon_used'] == 1:
        path.append('用券')

    if row['has_purchase'] == 1:
        path.append('购买')
    else:
        path.append('未购买')

    return ' → '.join(path)


def compute_behavior_path_analysis(subset):
    """
    新增：浏览 → 社交互动 → 加购物车 → 领券/用券 → 购买 的路径分析。
    用于回答：用户从浏览到购买的典型行为路径是什么？
    """
    temp = subset.copy()

    if len(temp) == 0:
        return {
            'funnel': [],
            'sankey_links': [],
            'sankey': {'nodes': [], 'links': []},
            'path_ranking': []
        }

    # Funnel
    funnel = [
        {'stage': '浏览', 'value': int(len(temp))},
        {'stage': '社交互动', 'value': int(temp['has_social'].sum())},
        {'stage': '加购物车', 'value': int(temp['has_cart'].sum())},
        {'stage': '领券', 'value': int(temp['has_coupon_received'].sum())},
        {'stage': '用券', 'value': int(temp['has_coupon_used'].sum())},
        {'stage': '购买', 'value': int(temp['has_purchase'].sum())}
    ]

    # Sankey links with source/target text
    sankey_links = [
        {
            'source': '浏览',
            'target': '社交互动',
            'value': int(((temp['has_social'] == 1)).sum())
        },
        {
            'source': '浏览',
            'target': '无社交互动',
            'value': int(((temp['has_social'] == 0)).sum())
        },
        {
            'source': '社交互动',
            'target': '加购物车',
            'value': int(((temp['has_social'] == 1) & (temp['has_cart'] == 1)).sum())
        },
        {
            'source': '社交互动',
            'target': '未加购',
            'value': int(((temp['has_social'] == 1) & (temp['has_cart'] == 0)).sum())
        },
        {
            'source': '无社交互动',
            'target': '加购物车',
            'value': int(((temp['has_social'] == 0) & (temp['has_cart'] == 1)).sum())
        },
        {
            'source': '无社交互动',
            'target': '未加购',
            'value': int(((temp['has_social'] == 0) & (temp['has_cart'] == 0)).sum())
        },
        {
            'source': '加购物车',
            'target': '领券',
            'value': int(((temp['has_cart'] == 1) & (temp['has_coupon_received'] == 1)).sum())
        },
        {
            'source': '加购物车',
            'target': '未领券',
            'value': int(((temp['has_cart'] == 1) & (temp['has_coupon_received'] == 0)).sum())
        },
        {
            'source': '领券',
            'target': '用券',
            'value': int(((temp['has_coupon_received'] == 1) & (temp['has_coupon_used'] == 1)).sum())
        },
        {
            'source': '领券',
            'target': '未用券',
            'value': int(((temp['has_coupon_received'] == 1) & (temp['has_coupon_used'] == 0)).sum())
        },
        {
            'source': '用券',
            'target': '购买',
            'value': int(((temp['has_coupon_used'] == 1) & (temp['has_purchase'] == 1)).sum())
        },
        {
            'source': '用券',
            'target': '未购买',
            'value': int(((temp['has_coupon_used'] == 1) & (temp['has_purchase'] == 0)).sum())
        },
        {
            'source': '未用券',
            'target': '购买',
            'value': int(((temp['has_coupon_received'] == 1) & (temp['has_coupon_used'] == 0) & (temp['has_purchase'] == 1)).sum())
        },
        {
            'source': '未用券',
            'target': '未购买',
            'value': int(((temp['has_coupon_received'] == 1) & (temp['has_coupon_used'] == 0) & (temp['has_purchase'] == 0)).sum())
        },
        {
            'source': '未领券',
            'target': '购买',
            'value': int(((temp['has_cart'] == 1) & (temp['has_coupon_received'] == 0) & (temp['has_purchase'] == 1)).sum())
        },
        {
            'source': '未领券',
            'target': '未购买',
            'value': int(((temp['has_cart'] == 1) & (temp['has_coupon_received'] == 0) & (temp['has_purchase'] == 0)).sum())
        },
        {
            'source': '未加购',
            'target': '购买',
            'value': int(((temp['has_cart'] == 0) & (temp['has_purchase'] == 1)).sum())
        },
        {
            'source': '未加购',
            'target': '未购买',
            'value': int(((temp['has_cart'] == 0) & (temp['has_purchase'] == 0)).sum())
        }
    ]

    sankey_links = [link for link in sankey_links if link['value'] > 0]

    # Also provide ECharts-style sankey object with node names
    node_names = sorted(list(set(
        [link['source'] for link in sankey_links] +
        [link['target'] for link in sankey_links]
    )))
    sankey = {
        'nodes': [{'name': name} for name in node_names],
        'links': sankey_links
    }

    # Path ranking
    temp['behavior_path'] = temp.apply(make_behavior_path, axis=1)

    path_stats = temp.groupby('behavior_path').agg(
        count=('user_id', 'count'),
        purchase_rate=('label', 'mean'),
        avg_spend=('total_spend', 'mean'),
        avg_pv_count=('pv_count', 'mean'),
        avg_interaction_rate=('interaction_rate', 'mean'),
        cart_rate=('has_cart', 'mean'),
        coupon_used_rate=('has_coupon_used', 'mean')
    ).reset_index()

    path_stats = path_stats.sort_values(['count', 'purchase_rate'], ascending=[False, False])

    path_ranking = []
    for _, row in path_stats.iterrows():
        path_ranking.append({
            'path': str(row['behavior_path']),
            'count': safe_int(row['count']),
            'purchase_rate': safe_float(row['purchase_rate']),
            'avg_spend': safe_float(row['avg_spend']),
            'avg_pv_count': safe_float(row['avg_pv_count']),
            'avg_interaction_rate': safe_float(row['avg_interaction_rate']),
            'cart_rate': safe_float(row['cart_rate']),
            'coupon_used_rate': safe_float(row['coupon_used_rate'])
        })

    return {
        'funnel': funnel,
        'sankey_links': sankey_links,
        'sankey': sankey,
        'path_ranking': path_ranking
    }


# =========================
# 7. Product behavior analysis
#    This can support teammate B if needed.
# =========================
def compute_product_behavior_analysis(subset):
    """
    商品内容与用户行为分析。
    可以给 B 同学使用：价格、折扣、类目对浏览、互动、加购、用券、购买的影响。
    """
    temp = subset.copy()

    if len(temp) == 0:
        return {
            'category_behavior': [],
            'price_groups': [],
            'discount_groups': [],
            'price_discount_heatmap': []
        }

    # Price groups
    price_bins = [0, 50, 100, 200, 500, np.inf]
    price_labels = ['0-50', '50-100', '100-200', '200-500', '500+']
    temp['price_group'] = pd.cut(
        temp['price'],
        bins=price_bins,
        labels=price_labels,
        include_lowest=True,
        right=True
    )

    # Discount rate groups
    # discount_rate 通常可能是 0-1；这里按照比例分组。
    discount_bins = [-0.001, 0.2, 0.5, 0.8, 1.0, np.inf]
    discount_labels = ['0-20%', '20%-50%', '50%-80%', '80%-100%', '100%+']
    temp['discount_group'] = pd.cut(
        temp['discount_rate'],
        bins=discount_bins,
        labels=discount_labels,
        include_lowest=True,
        right=True
    )

    def grouped_behavior(group_col):
        grouped = temp.groupby(group_col, observed=False).agg(
            count=('user_id', 'count'),
            avg_price=('price', 'mean'),
            avg_discount_rate=('discount_rate', 'mean'),
            avg_pv_count=('pv_count', 'mean'),
            avg_like_num=('like_num', 'mean'),
            avg_comment_num=('comment_num', 'mean'),
            avg_share_num=('share_num', 'mean'),
            avg_interaction_rate=('interaction_rate', 'mean'),
            cart_rate=('has_cart', 'mean'),
            coupon_received_rate=('has_coupon_received', 'mean'),
            coupon_used_rate=('has_coupon_used', 'mean'),
            purchase_rate=('label', 'mean'),
            avg_purchase_intent=('purchase_intent', 'mean')
        ).reset_index()

        result = []
        for _, row in grouped.iterrows():
            result.append({
                'group': str(row[group_col]),
                'count': safe_int(row['count']),
                'avg_price': safe_float(row['avg_price']),
                'avg_discount_rate': safe_float(row['avg_discount_rate']),
                'avg_pv_count': safe_float(row['avg_pv_count']),
                'avg_like_num': safe_float(row['avg_like_num']),
                'avg_comment_num': safe_float(row['avg_comment_num']),
                'avg_share_num': safe_float(row['avg_share_num']),
                'avg_interaction_rate': safe_float(row['avg_interaction_rate']),
                'cart_rate': safe_float(row['cart_rate']),
                'coupon_received_rate': safe_float(row['coupon_received_rate']),
                'coupon_used_rate': safe_float(row['coupon_used_rate']),
                'purchase_rate': safe_float(row['purchase_rate']),
                'avg_purchase_intent': safe_float(row['avg_purchase_intent'])
            })

        return result

    # Category behavior
    category_grouped = temp.groupby('category').agg(
        count=('user_id', 'count'),
        avg_price=('price', 'mean'),
        avg_discount_rate=('discount_rate', 'mean'),
        avg_pv_count=('pv_count', 'mean'),
        avg_like_num=('like_num', 'mean'),
        avg_comment_num=('comment_num', 'mean'),
        avg_share_num=('share_num', 'mean'),
        avg_interaction_rate=('interaction_rate', 'mean'),
        cart_rate=('has_cart', 'mean'),
        coupon_received_rate=('has_coupon_received', 'mean'),
        coupon_used_rate=('has_coupon_used', 'mean'),
        purchase_rate=('label', 'mean'),
        avg_purchase_intent=('purchase_intent', 'mean')
    ).reset_index()

    category_grouped = category_grouped.sort_values('purchase_rate', ascending=False)

    category_behavior = []
    for _, row in category_grouped.iterrows():
        category_behavior.append({
            'category': str(row['category']),
            'count': safe_int(row['count']),
            'avg_price': safe_float(row['avg_price']),
            'avg_discount_rate': safe_float(row['avg_discount_rate']),
            'avg_pv_count': safe_float(row['avg_pv_count']),
            'avg_like_num': safe_float(row['avg_like_num']),
            'avg_comment_num': safe_float(row['avg_comment_num']),
            'avg_share_num': safe_float(row['avg_share_num']),
            'avg_interaction_rate': safe_float(row['avg_interaction_rate']),
            'cart_rate': safe_float(row['cart_rate']),
            'coupon_received_rate': safe_float(row['coupon_received_rate']),
            'coupon_used_rate': safe_float(row['coupon_used_rate']),
            'purchase_rate': safe_float(row['purchase_rate']),
            'avg_purchase_intent': safe_float(row['avg_purchase_intent'])
        })

    # Price x discount heatmap
    heatmap_grouped = temp.groupby(['price_group', 'discount_group'], observed=False).agg(
        count=('user_id', 'count'),
        purchase_rate=('label', 'mean'),
        cart_rate=('has_cart', 'mean'),
        avg_interaction_rate=('interaction_rate', 'mean'),
        avg_purchase_intent=('purchase_intent', 'mean')
    ).reset_index()

    heatmap = []
    for _, row in heatmap_grouped.iterrows():
        heatmap.append({
            'price_group': str(row['price_group']),
            'discount_group': str(row['discount_group']),
            'count': safe_int(row['count']),
            'purchase_rate': safe_float(row['purchase_rate']),
            'cart_rate': safe_float(row['cart_rate']),
            'avg_interaction_rate': safe_float(row['avg_interaction_rate']),
            'avg_purchase_intent': safe_float(row['avg_purchase_intent'])
        })

    return {
        'category_behavior': category_behavior,
        'price_groups': grouped_behavior('price_group'),
        'discount_groups': grouped_behavior('discount_group'),
        'price_discount_heatmap': heatmap
    }


# =========================
# 8. Generate results
# =========================
results = {
    'overview': {},
    'age_groups': {},
    'behavior_insights': {},
    'categories': {},
    'user_levels': sorted([int(x) for x in df['user_level'].dropna().unique().tolist()]),
    # New global-level analysis
    'interaction_analysis': {},
    'behavior_path_analysis': {},
    'product_behavior_analysis': {}
}

# =========================
# 9. Overview
# =========================
total_users = len(user_data)
gender_dist = user_data['gender'].value_counts().to_dict()

results['overview'] = {
    'total_users': int(total_users),
    'total_spend': safe_float(user_data['total_spend'].sum()),
    'avg_spend': safe_float(user_data['total_spend'].mean()),
    'avg_purchase_freq': safe_float(user_data['purchase_freq'].mean()),
    'avg_social_activity': safe_float(user_data['social_activity'].mean()),
    'purchase_rate': safe_float(user_data['label'].mean()),
    'avg_pv': safe_float(user_data['pv_count'].mean()),
    'gender_distribution': {
        'male': int(gender_dist.get(0, 0)),
        'female': int(gender_dist.get(1, 0)),
        'male_ratio': safe_float(gender_dist.get(0, 0) / total_users) if total_users > 0 else 0,
        'female_ratio': safe_float(gender_dist.get(1, 0) / total_users) if total_users > 0 else 0
    },
    'spend_distribution': make_spend_distribution(user_data, df),
    'social_scatter': make_social_scatter(user_data),
    'top_categories': make_top_categories(df)
}

# Keep a categories alias if any old component uses it
results['categories'] = results['overview']['top_categories']

# =========================
# 10. Age groups
# =========================
for age_group in ['18-25', '26-35', '36-45', '46+']:
    group_data = user_data[user_data['age_group'] == age_group]
    group_df = df[df['age_group'] == age_group]

    gender_dist = group_data['gender'].value_counts().to_dict()
    total_group_users = len(group_data)

    results['age_groups'][age_group] = {
        'user_count': int(total_group_users),
        'avg_spend': safe_float(group_data['total_spend'].mean()),
        'avg_purchase_freq': safe_float(group_data['purchase_freq'].mean()),
        'avg_social_activity': safe_float(group_data['social_activity'].mean()),
        'purchase_rate': safe_float(group_data['label'].mean()),
        'avg_pv': safe_float(group_data['pv_count'].mean()),
        'gender_distribution': {
            'male': int(gender_dist.get(0, 0)),
            'female': int(gender_dist.get(1, 0)),
            'male_ratio': safe_float(gender_dist.get(0, 0) / total_group_users) if total_group_users > 0 else 0,
            'female_ratio': safe_float(gender_dist.get(1, 0) / total_group_users) if total_group_users > 0 else 0
        },
        'spend_distribution': make_spend_distribution(group_data, group_df),
        'social_scatter': make_social_scatter(group_data),
        'top_categories': make_top_categories(group_df)
    }

# =========================
# 11. Behavior insights by segments
# =========================
segments = {'all': df}

for age in ['18-25', '26-35', '36-45', '46+']:
    segments[f'age_{age}'] = df[df['age_group'] == age]

for gender, lbl in [(0, 'male'), (1, 'female')]:
    segments[f'gender_{lbl}'] = df[df['gender'] == gender]

for level in sorted(df['user_level'].dropna().unique().tolist()):
    segments[f'level_{int(level)}'] = df[df['user_level'] == level]

for seg_name, seg_data in segments.items():
    if len(seg_data) > 0:
        results['behavior_insights'][seg_name] = {
            # Original components
            'social_purchase': compute_social_purchase(seg_data),
            'funnel': compute_funnel(seg_data),
            'sankey': compute_sankey(seg_data),

            # New components for your part
            'interaction_analysis': compute_interaction_analysis(seg_data),
            'behavior_path_analysis': compute_behavior_path_analysis(seg_data),

            # Optional support for teammate B
            'product_behavior_analysis': compute_product_behavior_analysis(seg_data)
        }

# Global-level convenience keys
results['interaction_analysis'] = compute_interaction_analysis(df)
results['behavior_path_analysis'] = compute_behavior_path_analysis(df)
results['product_behavior_analysis'] = compute_product_behavior_analysis(df)

# =========================
# 12. Save to JSON
# =========================
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

print("\nNew analysis added:")
print("  - interaction_analysis")
print("  - behavior_path_analysis")
print("  - product_behavior_analysis")
print("\nGlobal behavior path top 5:")
for item in results['behavior_path_analysis']['path_ranking'][:5]:
    print(f"  {item['path']} | count={item['count']} | purchase_rate={item['purchase_rate']:.2%}")
