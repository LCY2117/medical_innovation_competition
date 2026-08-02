/** DemoConsole：演示控制台（重置 / 初始化 / 触发SOS / 模拟体征 / 导出证据）。 */
import { useState } from "react";
import {
  demoInit,
  demoReset,
  demoTrigger,
  downloadEvidenceZip,
  downloadJson,
  getEvidence,
  postHealthReading,
} from "../../lib/api";
import { useStore } from "../../lib/store";
import { STATUS_LABELS } from "./meta";

function errMsg(e: unknown): string {
  return e instanceof Error ? e.message : String(e);
}

export default function DemoConsole() {
  const [busy, setBusy] = useState<string>("");
  const [result, setResult] = useState<string>("");

  const run = async (key: string, fn: () => Promise<void>) => {
    setBusy(key);
    setResult("");
    try {
      await fn();
    } catch (e) {
      setResult(`失败：${errMsg(e)}`);
    } finally {
      setBusy("");
    }
  };

  const doReset = () =>
    run("reset", async () => {
      await demoReset();
      useStore.getState().detachEvent();
      setResult("演示数据已重置 · 系统等待新事件");
    });

  const doInit = () =>
    run("init", async () => {
      await demoInit();
      setResult("种子数据已确保（幂等）");
    });

  const doTrigger = () =>
    run("trigger", async () => {
      const ev = await demoTrigger();
      await useStore.getState().attachEvent(ev.id);
      setResult(
        `事件 #${ev.id} 已触发并分派 · ${STATUS_LABELS[ev.status] ?? ev.status}`,
      );
    });

  const doVitals = () =>
    run("vitals", async () => {
      const eventId = useStore.getState().currentEventId;
      if (!eventId) {
        setResult("暂无进行中事件，无法模拟体征");
        return;
      }
      const hr = 76 + Math.floor(Math.random() * 30);
      const spo2 = 93 + Math.floor(Math.random() * 5);
      const stress = Math.floor(Math.random() * 40 + 30);
      await postHealthReading(eventId, {
        reading_type: "heart_rate",
        value: hr,
        unit: "bpm",
        source: "PRIME",
      });
      await postHealthReading(eventId, {
        reading_type: "spo2",
        value: spo2,
        unit: "%",
        source: "PRIME",
      });
      await postHealthReading(eventId, {
        reading_type: "stress",
        value: stress,
        unit: "",
        source: "SYSTEM",
      });
      setResult(`模拟体征：HR ${hr} bpm · SpO2 ${spo2}% · 压力 ${stress}`);
    });

  const doJson = () =>
    run("json", async () => {
      const eventId = useStore.getState().currentEventId;
      if (!eventId) {
        setResult("暂无进行中事件，无法导出");
        return;
      }
      const bundle = await getEvidence(eventId);
      downloadJson(`event-${eventId}-evidence.json`, bundle);
      setResult(`证据 JSON 已导出（event-${eventId}）`);
    });

  const doZip = () =>
    run("zip", async () => {
      const eventId = useStore.getState().currentEventId;
      if (!eventId) {
        setResult("暂无进行中事件，无法导出");
        return;
      }
      await downloadEvidenceZip(eventId);
      setResult(`证据 ZIP 已导出（event-${eventId}）`);
    });

  return (
    <section className="panel demo-console">
      <div className="panel-title">
        <span className="t">演示控制台 DEMO</span>
      </div>
      <div className="demo-btns">
        <button className="demo-btn danger" disabled={!!busy} onClick={() => void doReset()}>
          {busy === "reset" ? "重置中…" : "重置"}
        </button>
        <button className="demo-btn" disabled={!!busy} onClick={() => void doInit()}>
          {busy === "init" ? "初始化中…" : "初始化"}
        </button>
        <button className="demo-btn amber" disabled={!!busy} onClick={() => void doTrigger()}>
          {busy === "trigger" ? "触发中…" : "触发SOS"}
        </button>
        <button className="demo-btn" disabled={!!busy} onClick={() => void doVitals()}>
          {busy === "vitals" ? "采集中…" : "模拟体征"}
        </button>
        <button className="demo-btn" disabled={!!busy} onClick={() => void doJson()}>
          {busy === "json" ? "导出中…" : "导出JSON"}
        </button>
        <button className="demo-btn" disabled={!!busy} onClick={() => void doZip()}>
          {busy === "zip" ? "导出中…" : "导出ZIP"}
        </button>
      </div>
      <div className="demo-result">{result}</div>
    </section>
  );
}
