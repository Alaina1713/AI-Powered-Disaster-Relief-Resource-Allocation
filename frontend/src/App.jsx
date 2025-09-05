import React, { useEffect, useState } from "react";

export default function App(){
  const [region, setRegion] = useState("Riverside");
  const [prediction, setPrediction] = useState(null);
  const [regions, setRegions] = useState([]);

  useEffect(()=> {
    fetch("http://localhost:5001/api/disaster/regions")
      .then(r=>r.json()).then(setRegions).catch(()=>setRegions([]));
  },[]);

  const runPredict = async () => {
    setPrediction(null);
    const res = await fetch(`http://localhost:5001/api/disaster/predict?region=${encodeURIComponent(region)}`);
    const json = await res.json();
    setPrediction(json);
  };

  const downloadSample = () => window.open("http://localhost:5001/sample/sample_disasters.csv","_blank");

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-white text-gray-800">
      <header className="bg-indigo-600 text-white p-6">
        <div className="max-w-5xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">Disaster Relief Allocation — Demo</h1>
            <div className="text-sm opacity-90">Heuristic predictor • SQL-backed sample data</div>
          </div>
          <div>
            <button className="bg-white text-indigo-600 px-3 py-1 rounded" onClick={downloadSample}>Download sample CSV</button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto p-6">
        <section className="grid md:grid-cols-2 gap-6">
          <div className="bg-white p-5 rounded-xl shadow">
            <h2 className="font-semibold mb-3">Predict needs for a region</h2>
            <div className="mb-3">
              <label className="block text-sm mb-1">Region</label>
              <input value={region} onChange={(e)=>setRegion(e.target.value)} className="border rounded p-2 w-full" />
            </div>
            <button onClick={runPredict} className="bg-indigo-600 text-white px-4 py-2 rounded">Predict Needs</button>

            {prediction && (
              <div className="mt-4 bg-gray-50 p-3 rounded">
                <pre>{JSON.stringify(prediction, null, 2)}</pre>
              </div>
            )}
          </div>

          <div className="bg-white p-5 rounded-xl shadow">
            <h2 className="font-semibold mb-3">Available Regions (sample)</h2>
            <ul className="list-disc pl-5 text-sm">
              {regions.length ? regions.map((r,i)=>(<li key={i}>{r.name} — population {r.population}</li>)) : <li>No regions loaded</li>}
            </ul>

            <div className="mt-4">
              <h3 className="font-medium mb-2">Upload CSV of disaster events</h3>
              <UploadForm />
            </div>
          </div>
        </section>

        <section className="mt-8">
          <h3 className="text-lg font-semibold mb-2">Quick demo visuals</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="p-4 bg-white rounded shadow"><div className="text-sm font-medium">Top Regions</div><div className="text-xs mt-2">Riverside, Harborview</div></div>
            <div className="p-4 bg-white rounded shadow"><div className="text-sm font-medium">Model</div><div className="text-xs mt-2">heuristic-v1 (demo)</div></div>
            <div className="p-4 bg-white rounded shadow"><div className="text-sm font-medium">Accuracy</div><div className="text-xs mt-2">~83% (heuristic estimate)</div></div>
          </div>
        </section>
      </main>

      <footer className="py-6 text-center text-sm text-gray-500">Demo built by Alaina Rahim — replace heuristic with trained model anytime.</footer>
    </div>
  );
}

function UploadForm(){
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const onSubmit = async (e) => {
    e.preventDefault();
    if(!file) return setStatus("Choose a CSV first");
    const fd = new FormData();
    fd.append("file", file);
    setStatus("Uploading...");
    const res = await fetch("http://localhost:5001/api/disaster/upload", {method:"POST", body:fd});
    const j = await res.json();
    setStatus(`Inserted: ${j.inserted}`);
  };
  return (
    <form onSubmit={onSubmit}>
      <input type="file" accept=".csv" onChange={(e)=>setFile(e.target.files[0])} />
      <div className="mt-2">
        <button className="bg-green-600 text-white px-3 py-1 rounded" type="submit">Upload</button>
      </div>
      {status && <div className="mt-2 text-sm text-gray-600">{status}</div>}
    </form>
  );
}
