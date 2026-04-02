import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)
  const [clientId, setClientID] = useState('')
  const [prUrl,setPrUrl] = useState('')


  useEffect(()=>{
    const clientId = crypto.randomUUID()
    setClientID(clientId)

    window.addEventListener('resize', ()=>{
      if(window.outerWidth < 600){
        setMediumDevice(true)
      }else{
        setMediumDevice(false)
      }
    })

    if(window.outerWidth < 600){
      setMediumDevice(true)
    }else{
      setMediumDevice(false)
    }
  })
  return (
    <div>
      <h1>AI Code Reviwer</h1>
      <input onChange={(e) => setPrUrl(e.target.value)}/>
      <div>
        <button>Review</button>
        <button>Clear</button>
      </div>

      <h2>Findings</h2>
      <textarea value={''}/>
      
    </div>
  )
}

export default App
