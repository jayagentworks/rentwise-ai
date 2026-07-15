import { useState } from "react";
import {
  ExternalLink,
  Heart,
  MapPin,
  Sparkles,
  ThumbsDown,
  ThumbsUp,
  TrainFront,
  WalletCards,
} from "lucide-react";
import type { SearchResponse } from "../types";
export type ImageReport = { observations: { category: string; observation: string; confidence: string; needs_offline_check: boolean }[]; warnings: string[]; disclaimer: string };

export function Results({
  data,
  lang,
  onReset,
  favoriteIds,
  onToggleFavorite,
  onFeedback,
  imageReports,
  onAnalyzeImages,
}: {
  data: SearchResponse;
  lang: "zh" | "en";
  onReset: () => void;
  favoriteIds: Set<string>;
  onToggleFavorite: (
    recommendation: SearchResponse["recommendations"][number],
  ) => void;
  onFeedback: (listingId: string, feedbackType: "like" | "dislike") => void;
  imageReports: Record<string, ImageReport>;
  onAnalyzeImages: (listingId: string, files: File[]) => void;
}) {
  const cn = lang === "zh";
  const [activeImages, setActiveImages] = useState<Record<string, number>>({});
  return (
    <main className="results">
      <div className="results-head">
        <div>
          <p className="eyebrow">
            <Sparkles />
            {cn ? "Agent 决策结果" : "Agent decision"}
          </p>
          <h1>
            {cn ? "不是最便宜，而是最适合" : "Not the cheapest. The best fit."}
          </h1>
          <p>
            {cn
              ? `已分析 ${data.total_candidates} 套候选房源。结果同时考虑真实成本、硬性条件和通勤。`
              : `Analysed ${data.total_candidates} listings across true cost, constraints and commute.`}
          </p>
        </div>
        <button className="secondary" onClick={onReset}>
          {cn ? "调整需求" : "Edit brief"}
        </button>
      </div>
      <div className="assumption-rail">
        {data.assumptions.map((x) => (
          <span key={x}>{x}</span>
        ))}
      </div>
      <div className="listing-grid">
        {data.recommendations.map((r, i) => {
          const images = r.listing.image_urls?.length ? r.listing.image_urls : [r.listing.image_url];
          const activeImage = Math.min(activeImages[r.listing.id] || 0, images.length - 1);
          return (
          <article
            key={r.listing.id}
            className={`listing ${!r.hard_constraints_passed ? "dimmed" : ""}`}
          >
            <div className="image-wrap">
              <img src={images[activeImage]} loading="lazy" alt={cn ? `${r.listing.title}第 ${activeImage + 1} 张图片` : `${r.listing.title}, image ${activeImage + 1}`} />
              <span className="rank">#{i + 1}</span>
              {r.listing.tags.includes("illustrative-image") && (
                <span className="image-note">{cn ? "示意图" : "Illustration"}</span>
              )}
              <span className={r.hard_constraints_passed ? "pass" : "fail"}>
                {r.hard_constraints_passed
                  ? cn
                    ? "硬条件通过"
                    : "Constraints pass"
                  : cn
                    ? "存在冲突"
                    : "Has conflicts"}
              </span>
            </div>
            {images.length > 1 && (
              <div className="image-strip" aria-label={cn ? "房源图片" : "Listing images"}>
                {images.map((image, imageIndex) => (
                  <button type="button" key={image} className={imageIndex === activeImage ? "active" : ""} onClick={() => setActiveImages(current => ({ ...current, [r.listing.id]: imageIndex }))} aria-label={cn ? `查看第 ${imageIndex + 1} 张图片` : `View image ${imageIndex + 1}`} aria-pressed={imageIndex === activeImage}>
                    <img src={image} loading="lazy" alt="" />
                  </button>
                ))}
                <span>{activeImage + 1} / {images.length}</span>
              </div>
            )}
            <div className="listing-body">
              <div className="title-row">
                <div>
                  <p>
                    {r.listing.district} · {r.listing.neighborhood}
                  </p>
                  <h2>{r.listing.title}</h2>
                </div>
                <div
                  className="recommendation-score"
                  title={
                    cn
                      ? "内部综合排序分：结合成本、通勤、偏好和硬条件计算，不代表概率。"
                      : "Internal ranking score based on cost, commute, preferences and constraints; not a probability."
                  }
                >
                  <span>{cn ? "推荐分" : "Score"}</span>
                  <strong>{r.score}</strong>
                </div>
              </div>
              <div className="score-evidence">
                <p>{cn ? "评分组成" : "Score breakdown"}<span>{cn ? "确定性规则计算" : "Deterministic rules"}</span></p>
                <dl>
                  <div><dt>{cn ? "成本" : "Cost"}</dt><dd>{r.score_breakdown.cost} / 35</dd></div>
                  <div><dt>{cn ? "通勤" : "Commute"}</dt><dd>{r.score_breakdown.commute} / 35</dd></div>
                  <div><dt>{cn ? "硬条件" : "Constraints"}</dt><dd>{r.score_breakdown.constraints} / 20</dd></div>
                  <div><dt>{cn ? "偏好" : "Preferences"}</dt><dd>{r.score_breakdown.preferences} / 10</dd></div>
                  {r.score_breakdown.fairness_penalty > 0 && <div><dt>{cn ? "公平性扣分" : "Fairness penalty"}</dt><dd>-{r.score_breakdown.fairness_penalty}</dd></div>}
                  {r.score_breakdown.feedback !== 0 && <div><dt>{cn ? "历史反馈" : "Past feedback"}</dt><dd>{r.score_breakdown.feedback > 0 ? "+" : ""}{r.score_breakdown.feedback}</dd></div>}
                </dl>
              </div>
              <div className="metrics">
                <div>
                  <WalletCards />
                  <span>
                    {cn ? "真实月成本" : "True monthly"}
                    <b>¥{r.monthly_true_cost.toLocaleString()}</b>
                  </span>
                </div>
                <div>
                  <TrainFront />
                  <span>
                    {cn ? "加权 / 最差通勤" : "Weighted / worst"}
                    <b>
                      {r.weighted_commute_minutes} / {r.worst_commute_minutes}{" "}
                      min
                    </b>
                  </span>
                </div>
                <div>
                  <MapPin />
                  <span>
                    {cn ? "面积 / 户型" : "Area / rooms"}
                    <b>
                      {r.listing.area_sqm}m² · {r.listing.bedrooms}
                      {cn ? "室" : " bd"}
                    </b>
                  </span>
                </div>
              </div>
              <div className="attribute-evidence">
                <span>{cn ? "楼层" : "Floor"}<b>{r.listing.floor ?? (cn ? "待确认" : "Unknown")}</b></span>
                <span>{cn ? "电梯" : "Elevator"}<b>{r.listing.has_elevator == null ? (cn ? "待确认" : "Unknown") : r.listing.has_elevator ? (cn ? "有" : "Yes") : (cn ? "无" : "No")}</b></span>
                <span>{cn ? "养宠" : "Pets"}<b>{r.listing.allows_pets == null ? (cn ? "待确认" : "Unknown") : r.listing.allows_pets ? (cn ? "允许" : "Allowed") : (cn ? "不允许" : "Not allowed")}</b></span>
              </div>
              <div className="commute-breakdown">
                <div className="commute-summary">
                  <span>
                    {cn ? "家庭每周总通勤" : "Household weekly total"}
                    <b>
                      {Math.round(r.weekly_total_commute_minutes / 6) / 10}h
                    </b>
                  </span>
                  <span>
                    {cn ? "成员通勤差距" : "Fairness gap"}
                    <b>{r.commute_fairness_gap_minutes} min</b>
                  </span>
                </div>
                {r.commutes.map((commute) => (
                  <div className="commute-person" key={commute.destination}>
                    <span>{commute.destination}</span>
                    <b>
                      {commute.minutes} min · {commute.distance_km} km
                    </b>
                    <em className={commute.within_limit ? "within" : "over"}>
                      {commute.within_limit
                        ? cn
                          ? "满足上限"
                          : "Within limit"
                        : cn
                          ? "超过上限"
                          : "Over limit"}
                    </em>
                  </div>
                ))}
              </div>
              <label className="image-analysis-button">
                {cn ? "上传照片进行视觉核验" : "Upload photos for visual review"}
                <input type="file" multiple accept=".jpg,.jpeg,.png,.webp" onChange={(event) => { const files = Array.from(event.target.files || []); if (files.length) onAnalyzeImages(r.listing.id, files); }} />
              </label>
              {imageReports[r.listing.id] && <div className="image-analysis-report"><b>{cn ? "图片观察" : "Visual observations"}</b><ul>{imageReports[r.listing.id].observations.map((item, index) => <li key={`${item.category}-${index}`}>{item.category}：{item.observation}（{item.confidence}）</li>)}</ul><small>{imageReports[r.listing.id].disclaimer}</small></div>}
              <div className="why">
                <h3>{cn ? "为什么推荐" : "Why this one"}</h3>
                <ul>
                  {r.reasons.map((x) => (
                    <li key={x}>{x}</li>
                  ))}
                </ul>
              </div>
              <div className="tradeoff">
                <h3>{cn ? "你需要接受" : "Trade-offs"}</h3>
                <ul>
                  {r.tradeoffs.map((x) => (
                    <li key={x}>{x}</li>
                  ))}
                </ul>
              </div>
              <div className="tags">
                {r.listing.tags.map((x) => (
                  <span key={x}>{x}</span>
                ))}
              </div>
              <div className="listing-actions">
                <button
                  type="button"
                  className={favoriteIds.has(r.listing.id) ? "favorited" : ""}
                  onClick={() => onToggleFavorite(r)}
                >
                  <Heart />
                  {favoriteIds.has(r.listing.id)
                    ? cn
                      ? "已收藏"
                      : "Saved"
                    : cn
                      ? "收藏"
                      : "Save"}
                </button>
                <span>{cn ? "这个推荐有帮助吗？" : "Helpful?"}</span>
                <button
                  type="button"
                  aria-label={cn ? "有帮助" : "Helpful"}
                  onClick={() => onFeedback(r.listing.id, "like")}
                >
                  <ThumbsUp />
                </button>
                <button
                  type="button"
                  aria-label={cn ? "没帮助" : "Not helpful"}
                  onClick={() => onFeedback(r.listing.id, "dislike")}
                >
                  <ThumbsDown />
                </button>
              </div>
              <a
                className="contact"
                href={r.listing.source_url}
                target="_blank"
                rel="noreferrer"
              >
                {cn ? "一键联系原平台" : "Contact on source"} <ExternalLink />
              </a>
            </div>
          </article>
        )})}
      </div>
    </main>
  );
}
