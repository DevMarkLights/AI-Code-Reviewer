import { useState, useEffect } from 'react'
import './App.css'
import ReactMarkdown from 'react-markdown'

function App() {
  const [clientId, setClientID] = useState('')
  const [prUrl,setPrUrl] = useState('')
  const [findings, setFindings] = useState('review Url')
  const [loading,setLoading] = useState(false)
  const [mediumDevice, setMediumDevice] = useState(true)
  const [steps, setSteps] = useState([])

  useEffect(()=>{

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

    const clientId = crypto.randomUUID()
    setClientID(clientId)
    // var url = `ws://localhost:8085/ai-code-reviewer/ws?client_id=${clientId}`
    var url = `wws://marks-pi.com/ai-code-reviewer/ws?client_id=${clientId}`
    const ws = new WebSocket(url);

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.hasOwnProperty('ping') && data.ping) return;
        if (data.hasOwnProperty("message")) {
            setSteps(prev => [...prev, data.message]);
        }
        
    };

    ws.onerror = (error) => console.error(error);
    ws.onclose = (event) => {
      console.log('webSocket closed:',event.code,event.reason)
    }

    return () => ws.close(); 
  },[])

  async function review(){
    setLoading(true)
    // var url = "http://localhost:8085/ai-code-reviewer/getReview"
    var url = 'https://marks-pi.com/ai-code-reviewer/getReview'
    try{
      const response = await fetch(url, {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({"url":prUrl, "client_id": clientId}), 
      })

      var result = await response.json()
      setFindings(result['result'].replace(/\\n/g, '\n'))

      window.open(prUrl, '_blank')

    } catch(error){
      setLoading(false)
    }
    
    setLoading(false)
  }

  return (
    <div>
      {loading &&
        <div style={{position:'fixed', width:'100vw', height:'100vh', display:'flex', justifyContent:'center', alignItems:'center', backgroundColor:'rgba(0,0,0,0.6)'}}>
          <div className="loader"></div>
        </div>
      }
      <h1>AI Code Reviwer</h1>
      <input placeholder='Enter github url' value={prUrl} onChange={(e) => setPrUrl(e.target.value)}/>
      <div>
        <button disabled={loading} onClick={()=> review()}>Review</button>
        <button disabled={loading} onClick={() => {setSteps([]), setFindings('review Url'), setPrUrl('')}}>Clear</button>
      </div>
      <h2>Steps</h2>
      <textarea id='steps' readOnly value={steps.join('\n')}/>
      <h2>Findings</h2>
      <div id='findings'>
        <ReactMarkdown>{findings}</ReactMarkdown>
      </div>
    </div>
  )
}

export default App
