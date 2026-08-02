import React, { useState } from 'react';
import { HeartPulse, LogIn, UserPlus } from 'lucide-react';
import { demoPersonaInfo } from '../lib/rescue';

interface AuthPanelProps {
  onLogin: (phone: string, password: string) => Promise<void>;
  onRegister: (form: {
    displayName: string;
    phone: string;
    password: string;
    organization: string;
    healthCondition: string;
    professionIdentity: string;
    profileBio: string;
  }) => Promise<void>;
  onEnterdemo: (persona: 'patient' | 'prime' | 'runner' | 'guide') => Promise<void>;
}

type AuthMode = 'login' | 'register';

const personaPresets = [
  { key: 'patient', label: '患者端', healthCondition: '存在心脏骤停风险', professionIdentity: '患者侧', org: '社区 / 家庭场景', bio: '多年冠心病病史，有一定心脏骤停风险，需要重点监测。' },
  { key: 'prime', label: '急救医生', healthCondition: '身体状态一般', professionIdentity: '急救科医生', org: '市医院急救科', bio: '市医院急救科医生，可执行高质量 CPR 与现场判断。' },
  { key: 'runner', label: 'AED 保障', healthCondition: '身体素质良好', professionIdentity: '有一定急救常识', org: '大学校园', bio: '跑动能力强，熟悉路线，可快速取送 AED。' },
  { key: 'guide', label: '清障接驳', healthCondition: '身体状态一般', professionIdentity: '安保 / 场地协调', org: '校园安保', bio: '熟悉楼栋与出入口，能协调人员流线、电梯和救护车接驳。' },
];

export function AuthPanel({ onLogin, onRegister, onEnterdemo }: AuthPanelProps) {
  const [mode, setMode] = useState<AuthMode>('login');
  const [busy, setBusy] = useState<string | null>(null);
  const [notice, setNotice] = useState<{ kind: 'ok' | 'error'; text: string } | null>(null);
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [form, setForm] = useState({
    displayName: '',
    phone: '',
    password: '',
    organization: '',
    healthCondition: '身体状态一般',
    professionIdentity: '有一定急救常识',
    profileBio: '',
  });

  const handleDemo = async (persona: 'patient' | 'prime' | 'runner' | 'guide') => {
    setBusy(persona);
    setNotice(null);
    try {
      await onEnterdemo(persona);
    } catch (error) {
      setNotice({ kind: 'error', text: error instanceof Error ? error.message : '进入演示模式失败' });
    } finally {
      setBusy(null);
    }
  };

  const handleSubmit = async () => {
    setBusy('submit');
    setNotice(null);
    try {
      if (mode === 'login') {
        if (!phone || !password) throw new Error('请输入手机号和密码');
        await onLogin(phone, password);
      } else {
        if (!form.phone || !form.password || !form.displayName) throw new Error('请填写昵称、手机号和密码');
        await onRegister(form);
      }
    } catch (error) {
      setNotice({ kind: 'error', text: error instanceof Error ? error.message : '操作失败' });
    } finally {
      setBusy(null);
    }
  };

  const applyPreset = (preset: (typeof personaPresets)[number]) => {
    setForm((current) => ({
      ...current,
      displayName: current.displayName || preset.label,
      healthCondition: preset.healthCondition,
      professionIdentity: preset.professionIdentity,
      organization: preset.org,
      profileBio: preset.bio,
    }));
  };

  return (
    <main className="mobile-shell mobile-auth-shell">
      <section className="mobile-hero">
        <div className="mobile-app-mark">
          <HeartPulse size={28} />
        </div>
        <p className="mobile-kicker">生命反射弧</p>
        <h1>移动应急端</h1>
        <p>无需安装应用，手机浏览器即可登录、接入事件、触发 SOS、执行急救任务。</p>
        <p className="mobile-safety-copy">仅用于协同训练、训练复盘与研究验证，不替代 120、AED 语音提示、专业医护判断或真实医疗诊断。</p>
      </section>

      <section className="mobile-panel" id="top">
        <div className="mobile-section-head">
          <div>
            <p className="mobile-kicker">演示模式</p>
            <h2>一键进入</h2>
          </div>
        </div>
        <div className="mobile-demo-grid">
          {demoPersonaInfo().map((persona) => (
            <button key={persona.key} type="button" onClick={() => handleDemo(persona.key)} disabled={Boolean(busy)}>
              <strong>{busy === persona.key ? '进入中...' : persona.label}</strong>
              <span>{persona.description}</span>
            </button>
          ))}
        </div>
      </section>

      <section className="mobile-panel">
        <div className="mobile-segment">
          <button className={mode === 'login' ? 'active' : ''} onClick={() => setMode('login')}>登录</button>
          <button className={mode === 'register' ? 'active' : ''} onClick={() => setMode('register')}>注册</button>
        </div>

        {mode === 'register' && (
          <div className="mobile-presets">
            {personaPresets.map((preset) => (
              <button key={preset.key} type="button" onClick={() => applyPreset(preset)}>
                {preset.label}
              </button>
            ))}
          </div>
        )}

        <label>手机号</label>
        <input
          value={mode === 'login' ? phone : form.phone}
          onChange={(e) => mode === 'login' ? setPhone(e.target.value) : setForm((f) => ({ ...f, phone: e.target.value }))}
          placeholder="手机号"
          inputMode="tel"
        />

        <label>密码</label>
        <input
          value={mode === 'login' ? password : form.password}
          onChange={(e) => mode === 'login' ? setPassword(e.target.value) : setForm((f) => ({ ...f, password: e.target.value }))}
          placeholder="至少 6 位"
          type="password"
        />

        {mode === 'register' && (
          <>
            <label>昵称</label>
            <input
              value={form.displayName}
              onChange={(e) => setForm((f) => ({ ...f, displayName: e.target.value }))}
              placeholder="昵称"
            />
            <label>组织</label>
            <input
              value={form.organization}
              onChange={(e) => setForm((f) => ({ ...f, organization: e.target.value }))}
              placeholder="组织 / 场景"
            />
            <label>身体状况</label>
            <select value={form.healthCondition} onChange={(e) => setForm((f) => ({ ...f, healthCondition: e.target.value }))}>
              <option>身体状态一般</option>
              <option>身体素质良好</option>
              <option>存在心脏骤停风险</option>
              <option>体能受限</option>
            </select>
            <label>职业身份</label>
            <select value={form.professionIdentity} onChange={(e) => setForm((f) => ({ ...f, professionIdentity: e.target.value }))}>
              <option>有一定急救常识</option>
              <option>急救科医生</option>
              <option>专业急救人员</option>
              <option>安保 / 场地协调</option>
              <option>患者侧</option>
            </select>
            <label>个人介绍</label>
            <textarea value={form.profileBio} onChange={(e) => setForm((f) => ({ ...f, profileBio: e.target.value }))} placeholder="简要介绍" rows={3} />
          </>
        )}

        {notice && <div className={`mobile-notice ${notice.kind}`}>{notice.text}</div>}

        <button className="mobile-primary-button" onClick={handleSubmit} disabled={Boolean(busy)}>
          {busy === 'submit' ? '提交中...' : mode === 'login' ? <><LogIn size={18} /> 登录</> : <><UserPlus size={18} /> 注册</>}
        </button>
      </section>
    </main>
  );
}
