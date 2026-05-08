<template>
  <div class="doc-overlay" @click="$emit('close')">
    <div class="doc-modal" @click.stop>
      <div class="doc-header">
        <h2>项目说明文档</h2>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>

      <div class="doc-content">
        <section>
          <h3>1. 项目主题</h3>
          <p>
            本项目主题为“社交电商用户行为分析”。项目基于 100,000 条社交电商用户行为数据，
            围绕用户从浏览、社交互动、加购物车、领券、用券到最终购买的行为过程展开分析。
          </p>
          <p>
            本项目的核心目标不是进行购买预测，而是通过交互式可视化帮助理解社交电商平台中用户行为如何逐步转化为购买行为。
          </p>
        </section>

        <section>
          <h3>2. 分析问题</h3>
          <ul>
            <li>
              不同用户群体的行为有什么差异？年龄、性别、用户等级不同，用户在浏览、消费、购买频率和购买率上是否存在差异？
            </li>
            <li>
              不同商品内容会引发怎样的用户行为？商品类目、价格区间和折扣区间不同，用户的浏览量、加购率和购买率是否存在差异？
            </li>
            <li>
              社交互动行为和购买行为之间有什么关系？点赞、评论、分享等“种草行为”是否真的能促进购买？
            </li>
            <li>
              用户从浏览到购买的典型行为路径是什么？哪些路径更容易转化，哪些阶段更容易流失？
            </li>
          </ul>
        </section>

        <section>
          <h3>3. 数据来源</h3>
          <p>
            本项目使用的数据集来自阿里云天池平台的社交电商用户行为数据集。
            数据集包含约 100,000 条社交电商用户行为记录，涵盖用户特征、商品内容特征、社交互动特征、
            行为序列特征以及是否购买标签。
          </p>
          <p>
            数据字段包括年龄、性别、用户等级、购买频率、消费金额、商品价格、折扣率、商品类目、
            点赞数、评论数、分享数、收藏数、加购物车、领券、用券、浏览次数、互动率、购买意向和最终购买标签等。
          </p>
          <p>
            数据来源链接：
            <a href="https://tianchi.aliyun.com/dataset/215680" target="_blank" rel="noopener noreferrer">
              https://tianchi.aliyun.com/dataset/215680
            </a>
          </p>
        </section>

        <section>
          <h3>4. 可视化设计思路</h3>
          <p>
            本项目按照“用户是谁 → 看什么商品 → 产生什么互动 → 是否加购/用券 → 是否购买”的逻辑组织页面结构。
            系统主要分为数据总览、年龄分群、商品内容分析和行为洞察几个部分。
          </p>
          <p>
            数据总览用于帮助用户理解整体数据结构，年龄分群用于比较不同用户群体的行为差异，
            商品内容分析用于观察价格、折扣和类目如何影响浏览、加购和购买，
            行为洞察模块则重点分析社交互动行为与购买行为之间的关系，并通过用户行为路径展示购买转化过程。
          </p>
        </section>

        <section>
          <h3>5. 可视化编码与交互设计</h3>

          <h4>5.1 数据总览</h4>
          <ul>
            <li>消费金额分布使用柱状图展示不同消费区间的用户数量。</li>
            <li>性别分布使用饼图展示男女用户比例。</li>
            <li>社交散点图使用横轴表示社交活跃度，纵轴表示消费金额，用于观察社交活跃用户是否具有更高消费水平。</li>
            <li>商品类别词云用于展示购买频率较高的商品类别。</li>
          </ul>

          <h4>5.2 年龄分群</h4>
          <p>
            年龄分群部分将用户划分为 18-25、26-35、36-45、46+ 四个年龄段，
            分别展示不同年龄段用户的消费能力、购买频率、性别比例和商品偏好。
            用户可以点击不同年龄段按钮查看对应群体的行为特征。
          </p>

          <h4>5.3 商品内容分析</h4>
          <ul>
            <li>
              价格 × 折扣转化热力图用于展示不同价格区间和折扣区间组合下的购买转化率。
            </li>
            <li>
              类目行为对比分组柱状图用于比较不同商品类目在浏览量、加购率和购买率上的差异。
            </li>
            <li>
              价格敏感度曲线用于展示价格提升对购买转化率的影响。
            </li>
            <li>
              商品内容模块支持按年龄段、性别和用户等级进行筛选，帮助比较不同用户群体面对商品内容时的行为差异。
            </li>
            <li>
              用户可以点击热力图中的色块，查看该价格和折扣组合下的类目行为详情；再次点击可取消选中。
            </li>
            <li>
              商品内容模块支持图表放大查看，便于观察热力图、类目对比图和价格敏感度曲线的细节。
            </li>
          </ul>

          <h4>5.4 行为洞察</h4>
          <ul>
            <li>社交购买桑基图用于展示点赞、评论、分享等社交互动行为与购买结果之间的流向关系。</li>
            <li>行为漏斗图用于展示用户从浏览、社交互动、加购物车、领券、用券到购买的阶段性转化。</li>
            <li>社交互动与购买关系分析用于比较不同互动水平下的购买率，并通过相关性矩阵观察多个行为变量之间的关系。</li>
            <li>用户行为路径分析将浏览、社交互动、加购物车、领券、用券和购买串联起来，展示用户从兴趣产生到最终购买的路径。</li>
          </ul>
        </section>

        <section>
          <h3>6. 设计决策依据</h3>
          <p>
            本项目没有将所有字段平均展示，而是围绕“用户行为如何转化为购买”这一核心问题进行筛选和组织。
            最终选择用户群体、商品内容、社交互动和行为路径作为主要分析维度。
          </p>
          <ul>
            <li>柱状图适合展示消费金额分布、购买率分组对比等分类统计数据。</li>
            <li>饼图适合展示性别比例，帮助理解用户构成。</li>
            <li>散点图适合观察社交活跃度与消费金额之间的关系。</li>
            <li>价格 × 折扣热力图适合展示两个商品内容变量组合下的购买转化差异，帮助识别更容易促进购买的价格和折扣区间。</li>
            <li>分组柱状图适合比较不同商品类目的浏览量、加购率和购买率差异。</li>
            <li>面积曲线适合展示价格变化与购买转化率之间的连续趋势。</li>
            <li>漏斗图适合展示用户行为阶段的转化过程。</li>
            <li>桑基图和路径流向图适合展示用户在不同行为阶段之间的流动。</li>
            <li>相关性矩阵适合展示多个行为变量之间的相关关系。</li>
          </ul>
        </section>

        <section>
          <h3>7. 考虑过的替代方案</h3>
          <p>
            在设计过程中，我们曾考虑使用多个独立柱状图分别展示点赞数、评论数、分享数与购买率的关系。
            但这种方式会使页面较为分散，也不利于用户比较不同互动指标之间的差异。因此，最终采用下拉菜单切换指标的方式，
            在同一图表区域中展示不同互动指标下的购买率变化。
          </p>
          <p>
            在商品内容分析中，我们曾考虑只按商品类目展示购买率排行榜，但这种方式难以体现价格和折扣的组合影响。
            因此，最终使用价格 × 折扣热力图展示两个变量组合下的购买转化率，并通过点击热力图色块联动类目行为对比图。
          </p>
          <p>
            我们也曾考虑只使用简单漏斗图展示浏览到购买的过程。但漏斗图只能显示每个阶段的总体人数，
            难以展示用户在不同路径上的流动情况。因此，我们增加了行为路径流向图和路径排行榜，
            用来展示用户的典型路径和流失环节。
          </p>
          <p>
            此外，我们没有将所有字段全部可视化，而是围绕用户行为转化过程选择关键字段，以避免页面信息过载。
          </p>
        </section>

        <section>
          <h3>8. 主要发现</h3>
          <ul>
            <li>
              不同年龄段用户在消费水平、购买频率和商品偏好上存在差异，说明用户群体特征会影响平台运营策略。
            </li>
            <li>
              商品内容分析显示，价格与折扣组合会影响购买转化率，不同商品类目在浏览量、加购率和购买率上存在差异。
            </li>
            <li>
              点赞、评论、分享之间相关性较强，说明社交互动行为往往会同时出现。
            </li>
            <li>
              点赞、评论、分享与最终购买之间的直接相关性相对较弱，说明社交互动更多代表用户兴趣，并不一定直接带来购买。
            </li>
            <li>
              加购物车、用券和购买意向与购买行为的关系更明显，说明这些行为比点赞、评论、分享更接近真实购买决策。
            </li>
            <li>
              行为路径分析显示，部分用户停留在社交互动阶段，没有继续加购或购买；而经过加购物车、领券、用券等阶段的用户更可能完成购买。
            </li>
            <li>
              用户购买行为不是单一步骤完成的，而是经历浏览、互动、加购、用券和购买等多个阶段。
            </li>
          </ul>
        </section>

        <section>
          <h3>9. 外部资源引用</h3>
          <ul>
            <li>
              数据来源：阿里云天池社交电商用户行为数据集。
              <a href="https://tianchi.aliyun.com/dataset/215680" target="_blank" rel="noopener noreferrer">
                https://tianchi.aliyun.com/dataset/215680
              </a>
            </li>
            <li>前端框架：Vue 3。</li>
            <li>可视化实现：D3.js、SVG、HTML/CSS。</li>
            <li>构建工具：Vite。</li>
            <li>项目部署：GitHub Pages。</li>
          </ul>
        </section>

        <section>
          <h3>10. 小组分工</h3>
          <ul>
            <li>
              徐詠荃：负责项目基础框架、数据总览、年龄分群和用户基础画像分析，包括消费金额分布、性别分布、社交散点图、商品类别词云、基础行为漏斗等模块。
            </li>
            <li>
              陈炳申：负责商品内容与用户行为分析模块，主要实现价格 × 折扣转化热力图、类目行为对比分组柱状图、价格敏感度曲线和商品分析筛选面板。
              该模块支持按年龄段、性别和用户等级筛选数据，并支持点击热力图色块联动查看对应价格和折扣组合下的类目行为差异。
            </li>
            <li>
              吴伟彰：负责社交互动与行为路径分析，主要实现社交互动分组购买率、互动行为相关性矩阵、用户行为路径流向图和路径排行榜，
              重点分析点赞、评论、分享等互动行为与购买转化之间的关系。
            </li>
          </ul>
        </section>

        <section>
          <h3>11. 开发流程与反思</h3>
          <p>
            本项目开发流程主要包括数据理解与字段确认、数据清洗与聚合、可视化组件开发、页面整合、交互调试和部署测试等阶段。
            项目总开发时间约为 30-40 工时。
          </p>
          <p>
            其中，数据处理和图表调试耗时最多。主要原因是原始数据字段较多，需要先确定哪些字段能够支持分析问题；
            同时，不同图表需要不同的数据结构，例如价格 × 折扣热力图需要聚合价格区间和折扣区间，
            行为路径图则需要将浏览、互动、加购、领券、用券和购买重新组织成节点与路径数据。
          </p>
          <p>
            在开发过程中，我们发现交互式可视化项目不能只追求图表数量，更重要的是围绕一个清晰的问题组织分析逻辑。
            因此，最终项目聚焦于“用户如何从浏览和社交互动走向购买”这一主线，通过用户画像、商品内容、社交互动和行为路径逐步展开分析。
          </p>
        </section>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProjectDocumentation',
  props: {
    isDark: {
      type: Boolean,
      default: true
    }
  },
  emits: ['close']
}
</script>

<style scoped>
.doc-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.72);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
}

.doc-modal {
  width: min(980px, 96vw);
  max-height: 88vh;
  overflow-y: auto;
  background: var(--bg-card);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  box-shadow: 0 0 30px var(--shadow-glow);
}

.doc-header {
  position: sticky;
  top: 0;
  z-index: 2;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  padding: 20px 28px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.doc-header h2 {
  margin: 0;
  color: var(--text-accent);
}

.close-btn {
  background: var(--bg-btn);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  font-size: 24px;
  width: 42px;
  height: 42px;
  cursor: pointer;
}

.close-btn:hover {
  border-color: var(--border-hover);
  box-shadow: 0 0 12px var(--shadow-glow);
}

.doc-content {
  padding: 28px;
  line-height: 1.8;
}

.doc-content section {
  margin-bottom: 26px;
}

.doc-content h3 {
  color: var(--text-accent);
  margin-top: 8px;
  margin-bottom: 10px;
  font-size: 21px;
}

.doc-content h4 {
  margin: 16px 0 8px;
  color: var(--text-primary);
  font-size: 17px;
}

.doc-content p {
  margin: 8px 0;
}

.doc-content ul {
  padding-left: 24px;
  margin: 8px 0;
}

.doc-content li {
  margin: 6px 0;
}

.doc-content a {
  color: var(--text-accent);
  word-break: break-all;
}

@media (max-width: 760px) {
  .doc-overlay {
    padding: 12px;
  }

  .doc-modal {
    max-height: 92vh;
  }

  .doc-header {
    padding: 16px 18px;
  }

  .doc-content {
    padding: 20px;
  }
}
</style>