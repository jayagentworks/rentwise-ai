import { ArrowLeft, FileSearch, Scale, Upload } from 'lucide-react';

export type ContractReport = { filename: string; overall_risk: string; llm_enhanced: boolean; ocr_used: boolean; extraction_warnings: string[]; findings: { rule_id: string; risk_level: string; clause_excerpt: string; explanation: string; suggestion: string; sources: { title: string; provision: string; url: string }[] }[]; disclaimer: string };
export type ContractReviewItem = { id: string; filename: string; report: ContractReport; created_at: string };

export function ContractReview({ lang, report, history, loading, error, onBack, onReview, onSelectHistory }: { lang: 'zh' | 'en'; report: ContractReport | null; history: ContractReviewItem[]; loading: boolean; error: string; onBack: () => void; onReview: (files: File[]) => void; onSelectHistory: (report: ContractReport) => void }) {
  const cn = lang === 'zh';
  return <main className="contract-review">
    <button className="secondary library-back" onClick={onBack}><ArrowLeft/>{cn ? '返回规划' : 'Back to planner'}</button>
    <div className="eyebrow"><Scale/>{cn ? '租赁合同核验 Skill' : 'Rental contract review skill'}</div>
    <h1>{cn ? '拍下每一页，也能核验合同' : 'Photograph every page. Review the contract.'}</h1>
    <p className="contract-intro">{cn ? '支持合同照片、文本 PDF、扫描 PDF、TXT 和 Markdown。扫描 PDF 会自动逐页 OCR，原图和正文不会保存。' : 'Supports photos, text or scanned PDFs, TXT and Markdown. Scanned PDFs are OCRed page by page; originals and text are not stored.'}</p>
    <label className="contract-upload"><Upload/><span>{loading ? (cn ? '正在识别并核验…' : 'Reading and reviewing…') : (cn ? '选择合同照片或文件（可多选）' : 'Choose contract photos or files')}</span><input type="file" multiple accept=".jpg,.jpeg,.png,.webp,.pdf,.txt,.md" disabled={loading} onChange={event => { const files = Array.from(event.target.files || []); if (files.length) onReview(files); }}/></label>
    {error && <p className="contract-error">{error}</p>}
    {history.length > 0 && <section className="contract-history"><h2>{cn ? '核验历史' : 'Review history'}</h2><div>{history.map(item => <button type="button" key={item.id} onClick={() => onSelectHistory(item.report)}><span>{item.filename}</span><time>{new Date(item.created_at).toLocaleString(cn ? 'zh-CN' : 'en-US')}</time><b>{item.report.overall_risk}</b></button>)}</div></section>}
    {report && <section className="contract-report">
      {report.extraction_warnings.map(warning => <p className="contract-warning" key={warning}>{warning}</p>)}
      <div className="contract-overall"><FileSearch/><span>{cn ? '总体结果' : 'Overall result'}</span><strong>{report.overall_risk}</strong>{report.ocr_used && <em>{cn ? '照片/扫描件 OCR' : 'Image/scanned OCR'}</em>}{report.llm_enhanced && <em>{cn ? 'AI 证据解释' : 'AI evidence explanation'}</em>}</div>
      {report.findings.length ? <div className="finding-list">{report.findings.map((finding, index) => <article key={`${finding.rule_id}-${index}`}><span className="risk-level">{finding.risk_level}</span><h2>{finding.clause_excerpt}</h2><p>{finding.explanation}</p><div className="finding-suggestion"><b>{cn ? '建议' : 'Suggestion'}</b>{finding.suggestion}</div><ul>{finding.sources.map(source => <li key={`${finding.rule_id}-${source.url}`}><a href={source.url} target="_blank" rel="noreferrer">{source.title} · {source.provision}</a></li>)}</ul></article>)}</div> : <p>{cn ? '未触发当前预设规则，但仍建议人工核对合同及附件。' : 'No configured rule was triggered; manual review is still recommended.'}</p>}
      <p className="legal-disclaimer">{report.disclaimer}</p>
    </section>}
  </main>;
}
