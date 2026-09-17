import { ArrowRight, BriefcaseBusiness, BrainCircuit, Users } from "lucide-react";
import "../index.css";

function App() {
  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6 lg:px-8">
        <div className="flex items-center gap-2">
          <div className="rounded-xl bg-cyan-400 p-2 text-slate-950">
            <BrainCircuit size={24} />
          </div>
          <span className="text-xl font-bold tracking-tight">TalentIQ</span>
        </div>

        <div className="hidden items-center gap-8 text-sm text-slate-300 md:flex">
          <a href="#features" className="transition hover:text-cyan-300">
            Features
          </a>
          <a href="#how-it-works" className="transition hover:text-cyan-300">
            How It Works
          </a>
          <a href="#about" className="transition hover:text-cyan-300">
            About
          </a>
        </div>

        <button className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium transition hover:border-cyan-400 hover:text-cyan-300">
          Sign In
        </button>
      </nav>

      <section className="mx-auto grid max-w-7xl items-center gap-16 px-6 pb-24 pt-16 lg:grid-cols-2 lg:px-8 lg:pt-24">
        <div>
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-cyan-400/30 bg-cyan-400/10 px-4 py-2 text-sm text-cyan-300">
            <BrainCircuit size={16} />
            AI-Powered Career Intelligence
          </div>

          <h1 className="max-w-3xl text-5xl font-bold leading-tight tracking-tight sm:text-6xl">
            Make smarter career and hiring decisions.
          </h1>

          <p className="mt-6 max-w-xl text-lg leading-8 text-slate-300">
            TalentIQ connects candidates and recruiters with intelligent,
            explainable insights for better career opportunities and more
            informed hiring workflows.
          </p>

          <div className="mt-8 flex flex-col gap-4 sm:flex-row">
            <button className="inline-flex items-center justify-center gap-2 rounded-lg bg-cyan-400 px-5 py-3 font-semibold text-slate-950 transition hover:bg-cyan-300">
              Explore as a Candidate
              <ArrowRight size={18} />
            </button>

            <button className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-700 px-5 py-3 font-semibold text-white transition hover:border-cyan-400 hover:text-cyan-300">
              For Recruiters
              <BriefcaseBusiness size={18} />
            </button>
          </div>
        </div>

        <div className="relative">
          <div className="absolute -inset-6 rounded-3xl bg-cyan-400/10 blur-3xl" />
          <div className="relative rounded-3xl border border-slate-800 bg-slate-900 p-8 shadow-2xl">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Candidate Match Preview</p>
                <h2 className="mt-2 text-2xl font-bold">Backend Developer</h2>
              </div>
              <Users className="text-cyan-300" size={32} />
            </div>

            <div className="mt-8 rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-5">
              <p className="text-sm text-cyan-300">Suitability Assessment</p>
              <p className="mt-2 text-4xl font-bold">Potential Fit</p>
              <p className="mt-2 text-sm text-slate-300">
                Explore the skills and experience behind this assessment.
              </p>
            </div>

            <div className="mt-6 space-y-4">
              <div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-300">Technical Skills</span>
                  <span className="text-cyan-300">Strong</span>
                </div>
                <div className="mt-2 h-2 rounded-full bg-slate-800">
                  <div className="h-2 w-4/5 rounded-full bg-cyan-400" />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-300">Role Alignment</span>
                  <span className="text-cyan-300">Promising</span>
                </div>
                <div className="mt-2 h-2 rounded-full bg-slate-800">
                  <div className="h-2 w-3/5 rounded-full bg-cyan-400" />
                </div>
              </div>
            </div>

            <p className="mt-6 text-xs leading-5 text-slate-500">
              Demonstration interface only. Suitability assessments support
              human judgment and do not make hiring decisions.
            </p>
          </div>
        </div>
      </section>

      <section id="features" className="border-t border-slate-800 bg-slate-900/50 px-6 py-20">
        <div className="mx-auto max-w-7xl">
          <div className="max-w-2xl">
            <p className="text-sm font-semibold uppercase tracking-widest text-cyan-300">
              Built for both sides
            </p>
            <h2 className="mt-3 text-3xl font-bold sm:text-4xl">
              Intelligence for every career journey.
            </h2>
          </div>

          <div className="mt-12 grid gap-6 md:grid-cols-2">
            <article className="rounded-2xl border border-slate-800 bg-slate-950 p-8">
              <Users className="text-cyan-300" size={32} />
              <h3 className="mt-5 text-xl font-semibold">For Candidates</h3>
              <p className="mt-3 leading-7 text-slate-300">
                Understand your strengths, discover skill gaps, and explore
                opportunities aligned with your profile.
              </p>
            </article>

            <article className="rounded-2xl border border-slate-800 bg-slate-950 p-8">
              <BriefcaseBusiness className="text-cyan-300" size={32} />
              <h3 className="mt-5 text-xl font-semibold">For Recruiters</h3>
              <p className="mt-3 leading-7 text-slate-300">
                Analyze candidate profiles, compare job alignment, and support
                more structured recruitment workflows.
              </p>
            </article>
          </div>
        </div>
      </section>

      <footer id="about" className="border-t border-slate-800 px-6 py-8 text-center text-sm text-slate-500">
        © 2026 TalentIQ. AI-assisted insights for better career decisions.
      </footer>
    </main>
  );
}

export default App;
