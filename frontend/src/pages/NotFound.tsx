import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 text-center text-white">
      <h1 className="text-6xl font-bold">404</h1>
      <p className="mt-4 text-xl text-slate-300">
        This TalentIQ page does not exist.
      </p>
      <Link
        to="/"
        className="mt-8 rounded-lg bg-cyan-400 px-5 py-3 font-semibold text-slate-950"
      >
        Return Home
      </Link>
    </div>
  );
}
