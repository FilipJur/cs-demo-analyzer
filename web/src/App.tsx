import { useCallback, useMemo, useRef, useState, type ReactNode } from 'react';
import { client, isAbortError, toApiError, type ApiError } from './api/client';
import type { DemoDetail, JobRecord } from './api/types';
import { DemosPanel } from './components/DemosPanel';
import { HealthBar } from './components/HealthBar';
import { ImportPanel } from './components/ImportPanel';
import { JobsPanel } from './components/JobsPanel';
import { ReplayPanel } from './components/ReplayPanel';
import { RootsPanel } from './components/RootsPanel';
import { SourcesPanel } from './components/SourcesPanel';
import { SubjectPanel } from './components/SubjectPanel';
import { usePolled } from './lib/usePolling';

export function App(): ReactNode {
  const health = usePolled((signal) => client.health(signal), 10000);
  const roots = usePolled((signal) => client.roots(signal), 15000);
  const sources = usePolled((signal) => client.sources(signal), 8000);
  const jobs = usePolled((signal) => client.jobs(signal), 3000);
  const demos = usePolled((signal) => client.demos({ limit: 200 }, signal), 5000);
  const [selectedDemoId, setSelectedDemoId] = useState<string | null>(null);
  const [subjectSteamId, setSubjectSteamId] = useState<string | null>(null);
  const [detail, setDetail] = useState<DemoDetail | null>(null);
  const [detailError, setDetailError] = useState<ApiError | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const detailRequest = useRef<AbortController | null>(null);

  const refreshLibrary = useCallback(() => {
    roots.refresh();
    sources.refresh();
    jobs.refresh();
    demos.refresh();
    health.refresh();
  }, [demos, health, jobs, roots, sources]);

  const selectDemo = useCallback((demoId: string) => {
    detailRequest.current?.abort();
    const controller = new AbortController();
    detailRequest.current = controller;
    setSelectedDemoId(demoId);
    setDetail(null);
    setDetailError(null);
    setDetailLoading(true);
    void (async () => {
      try {
        const value = await client.demoDetail(demoId, controller.signal);
        if (controller.signal.aborted) return;
        setDetail(value);
      } catch (exc) {
        if (!isAbortError(exc) && !controller.signal.aborted) setDetailError(toApiError(exc));
      } finally {
        if (!controller.signal.aborted) setDetailLoading(false);
      }
    })();
  }, []);

  const latestJobByDemo = useMemo(() => {
    const map = new Map<string, JobRecord>();
    for (const job of jobs.data ?? []) {
      const current = map.get(job.demo_id);
      if (current === undefined || job.updated_at > current.updated_at) map.set(job.demo_id, job);
    }
    return map;
  }, [jobs.data]);

  const activeJobs = (jobs.data ?? []).filter((job) => job.state === 'queued' || job.state === 'running').length;

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-title">
          <h1>CS2 Demo Analyzer</h1>
          <p className="hint">
            Local library and generation-pinned replay proof. Every request goes to this machine's <span className="mono">/api/v1</span>; the browser never parses
            demos and never requests a whole match.
          </p>
        </div>
        <HealthBar health={health.data} error={health.error} updatedAt={health.updatedAt} />
      </header>

      <main className="layout">
        <div className="column">
          <SubjectPanel subjectSteamId={subjectSteamId} onSubjectChanged={(config) => setSubjectSteamId(config.steam_id)} />
          <RootsPanel roots={roots.data} error={roots.error} onChanged={refreshLibrary} />
          <ImportPanel onChanged={refreshLibrary} />
          <SourcesPanel sources={sources.data} error={sources.error} />
          <JobsPanel jobs={jobs.data} error={jobs.error} onSelectDemo={selectDemo} />
        </div>
        <div className="column">
          <DemosPanel
            demos={demos.data}
            error={demos.error}
            latestJobByDemo={latestJobByDemo}
            selectedDemoId={selectedDemoId}
            onSelect={selectDemo}
            onChanged={refreshLibrary}
          />
          <ReplayPanel demoId={selectedDemoId} detail={detail} detailError={detailError} detailLoading={detailLoading} subjectSteamId={subjectSteamId} />
        </div>
      </main>

      <footer className="app-footer small">
        <span>{activeJobs > 0 ? `${activeJobs} active extraction job${activeJobs === 1 ? '' : 's'}` : 'No active extraction jobs'}</span>
        <span>Writes require an allowed local origin; cross-site mutation attempts are rejected by the API.</span>
      </footer>
    </div>
  );
}
