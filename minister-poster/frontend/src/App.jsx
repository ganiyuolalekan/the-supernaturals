import { useState } from 'react'
import Landing from './screens/Landing'
import Upload  from './screens/Upload'
import Result  from './screens/Result'

export default function App() {
  const [screen, setScreen] = useState('landing')
  const [result, setResult] = useState(null)

  return (
    <div className="min-h-dvh bg-cosmic-950 bg-stars">
      {screen === 'landing' && (
        <Landing onStart={() => setScreen('upload')} />
      )}
      {screen === 'upload' && (
        <Upload
          onResult={(data) => { setResult(data); setScreen('result') }}
          onBack={() => setScreen('landing')}
        />
      )}
      {screen === 'result' && result && (
        <Result
          data={result}
          onReset={() => { setResult(null); setScreen('landing') }}
        />
      )}
    </div>
  )
}
