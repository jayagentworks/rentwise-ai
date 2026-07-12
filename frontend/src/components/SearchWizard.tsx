import { useState } from 'react';
import { ArrowRight, BriefcaseBusiness, CircleAlert, House, SlidersHorizontal } from 'lucide-react';
import type { Preferences } from '../types';

const districts = ['浦东新区', '静安区', '徐汇区', '杨浦区', '闵行区', '宝山区'];
const soft = ['近地铁', '采光好', '安静', '商业便利', '适合家庭', '性价比'];

export function SearchWizard({ onSubmit, loading, lang }: {
  onSubmit: (value: Preferences) => void;
  loading: boolean;
  lang: 'zh' | 'en';
}) {
  const [step, setStep] = useState(0);
  const [form, setForm] = useState<Preferences>({
    city: '上海', districts: [], monthly_rent_max: 6000, monthly_total_max: 6800,
    bedrooms_min: 1, area_min: 30, rental_type: 'entire', move_in_date: '2026-08-01',
    lease_months: 12, accepts_agent_fee: false, needs_elevator: true, allows_pets: false,
    commute_mode: 'transit',
    destinations: [{ label: '我的公司', address: '上海市浦东新区陆家嘴', weight: 1, max_minutes: 45 }],
    soft_preferences: ['近地铁', '采光好'],
  });
  const patch = (value: Partial<Preferences>) => setForm({ ...form, ...value });
  const cn = lang === 'zh';
  const titles = cn
    ? ['先画出你的租房边界', '把每天的路算进去', '告诉我们什么叫“住得好”']
    : ['Set your rental boundaries', 'Count every commute', 'Define what feels like home'];
  const missingNumber = [form.monthly_rent_max, form.monthly_total_max, form.bedrooms_min, form.area_min].some(Number.isNaN);

  const numericValue = (value: number) => Number.isNaN(value) ? '' : value;
  const numericChange = (value: string) => value === '' ? Number.NaN : Number(value);

  return <section className="wizard" aria-labelledby="wizard-title">
    <div className="step-rail">
      {titles.map((title, index) => <button key={title} onClick={() => setStep(index)} className={index === step ? 'active' : ''}>
        <span>0{index + 1}</span>{title}
      </button>)}
    </div>
    <div className="form-panel">
      <div className="eyebrow">
        {step === 0 ? <House /> : step === 1 ? <BriefcaseBusiness /> : <SlidersHorizontal />}
        {cn ? '需求向导' : 'Rental brief'}
      </div>
      <h1 id="wizard-title">{titles[step]}</h1>

      {step === 0 && <div className="field-grid">
        <label>{cn ? '目标城市' : 'City'}<input value={form.city} onChange={e => patch({ city: e.target.value })} /></label>
        <label>{cn ? '入住日期' : 'Move-in'}<input type="date" value={form.move_in_date} onChange={e => patch({ move_in_date: e.target.value })} /></label>
        <label>{cn ? '挂牌租金上限' : 'Listed rent cap'}<div className="money"><span>¥</span><input type="number" min="1000" required value={numericValue(form.monthly_rent_max)} onChange={e => patch({ monthly_rent_max: numericChange(e.target.value) })} /></div></label>
        <label>
          <span className="label-with-help">
            {cn ? '月均综合居住成本上限' : 'All-in monthly housing cap'}
            <span className="cost-help">
              <button type="button" aria-label={cn ? '查看综合居住成本计算方式' : 'Explain all-in monthly cost'} aria-describedby="cost-help-content"><CircleAlert /></button>
              <span className="cost-tooltip" role="tooltip" id="cost-help-content">
                {cn ? '月租 + 服务费 + 物业费 + 预估水电燃气 + 一次性中介费按租期月数摊销' : 'Rent + service fee + property fee + estimated utilities + agent fee amortized over the lease.'}
              </span>
            </span>
          </span>
          <div className="money"><span>¥</span><input type="number" min="1000" required value={numericValue(form.monthly_total_max)} onChange={e => patch({ monthly_total_max: numericChange(e.target.value) })} /></div>
        </label>
        <label>{cn ? '最少卧室' : 'Bedrooms'}<input type="number" min="1" required value={numericValue(form.bedrooms_min)} onChange={e => patch({ bedrooms_min: numericChange(e.target.value) })} /></label>
        <label>{cn ? '最小面积 m²' : 'Min area m²'}<input type="number" min="5" required value={numericValue(form.area_min)} onChange={e => patch({ area_min: numericChange(e.target.value) })} /></label>
        <fieldset className="wide"><legend>{cn ? '目标区域（可多选）' : 'Districts'}</legend><div className="chips">
          {districts.map(district => <button type="button" key={district} className={form.districts.includes(district) ? 'selected' : ''} onClick={() => patch({ districts: form.districts.includes(district) ? form.districts.filter(item => item !== district) : [...form.districts, district] })}>{district}</button>)}
        </div></fieldset>
      </div>}

      {step === 1 && <div className="field-grid">
        <label className="wide">{cn ? '通勤目的地' : 'Destination'}<input value={form.destinations[0].address} onChange={e => patch({ destinations: [{ ...form.destinations[0], address: e.target.value }] })} /></label>
        <label>{cn ? '单程上限（分钟）' : 'Max minutes'}<input type="number" value={form.destinations[0].max_minutes} onChange={e => patch({ destinations: [{ ...form.destinations[0], max_minutes: Number(e.target.value) }] })} /></label>
        <label>{cn ? '交通方式' : 'Mode'}<select value={form.commute_mode} onChange={e => patch({ commute_mode: e.target.value as Preferences['commute_mode'] })}><option value="transit">{cn ? '公共交通' : 'Transit'}</option><option value="driving">{cn ? '驾车' : 'Driving'}</option><option value="bicycling">{cn ? '骑行' : 'Cycling'}</option></select></label>
        <div className="route-preview wide"><div className="route-dot start" /><div className="route-line" /><div className="route-dot end" /><p>{cn ? '系统将比较每套房到多个家庭目的地的加权通勤；当前首版先填写一个地点，结果页可继续追加。' : 'We compare weighted commutes across household destinations. Start with one; add more after search.'}</p></div>
      </div>}

      {step === 2 && <div>
        <div className="chips preference">{soft.map(item => <button type="button" key={item} className={form.soft_preferences.includes(item) ? 'selected' : ''} onClick={() => patch({ soft_preferences: form.soft_preferences.includes(item) ? form.soft_preferences.filter(value => value !== item) : [...form.soft_preferences, item] })}>{item}</button>)}</div>
        <div className="toggles">
          <label><input type="checkbox" checked={form.needs_elevator} onChange={e => patch({ needs_elevator: e.target.checked })} />{cn ? '必须有电梯' : 'Elevator required'}</label>
          <label><input type="checkbox" checked={form.allows_pets} onChange={e => patch({ allows_pets: e.target.checked })} />{cn ? '需要允许养宠' : 'Pets required'}</label>
          <label><input type="checkbox" checked={form.accepts_agent_fee} onChange={e => patch({ accepts_agent_fee: e.target.checked })} />{cn ? '接受一次性中介费' : 'Accept agent fee'}</label>
        </div>
      </div>}

      <div className="form-actions">
        {step > 0 && <button className="secondary" onClick={() => setStep(step - 1)}>{cn ? '上一步' : 'Back'}</button>}
        <button className="primary" disabled={loading || missingNumber} onClick={() => step < 2 ? setStep(step + 1) : onSubmit(form)}>
          {loading ? (cn ? '正在分析…' : 'Analysing…') : step < 2 ? (cn ? '继续' : 'Continue') : (cn ? '生成租房方案' : 'Build my shortlist')} <ArrowRight />
        </button>
      </div>
    </div>
  </section>;
}
