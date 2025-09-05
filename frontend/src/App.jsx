import React, {useEffect, useState} from 'react'

export default function App(){
  const [emails, setEmails] = useState([])
  const [selected, setSelected] = useState(null)
  const [draft, setDraft] = useState('')

  useEffect(()=>{ fetchEmails() },[])
  async function fetchEmails(){
    const r = await fetch('http://localhost:8000/emails')
    const d = await r.json()
    setEmails(d)
  }
  async function viewEmail(id){
    const r = await fetch(`http://localhost:8000/emails/${id}`)
    const d = await r.json()
    setSelected(d)
    setDraft(d.draft || '')
  }
  async function genDraft(id){
    await fetch(`http://localhost:8000/generate-draft/${id}`, {method: 'POST'})
    await viewEmail(id)
  }
  async function sendEmail(id){
    await fetch(`http://localhost:8000/send/${id}`, {method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({override_body: draft})})
    alert('Sent (simulated)')
    fetchEmails()
  }

  return (
    <div style={{display:'flex',gap:20,padding:20,fontFamily:'sans-serif'}}>
      <div style={{width:420}}>
        <h2>Inbox</h2>
        <div>
          {emails.map(e=> (
            <div key={e.id} onClick={()=>viewEmail(e.id)} style={{padding:8,border:'1px solid #ddd',marginBottom:8,cursor:'pointer'}}>
              <strong>{e.subject}</strong>
              <div style={{fontSize:12}}>{e.sender} • {e.priority} • {e.sentiment}</div>
            </div>
          ))}
        </div>
      </div>
      <div style={{flex:1}}>
        {selected ? (
          <div>
            <h3>{selected.subject}</h3>
            <div><em>From: {selected.sender}</em></div>
            <div style={{whiteSpace:'pre-wrap',marginTop:12,background:'#fafafa',padding:12}}>{selected.body}</div>
            <div style={{marginTop:12}}>
              <button onClick={()=>genDraft(selected.id)}>Generate Draft</button>
            </div>
            <div style={{marginTop:12}}>
              <h4>Draft</h4>
              <textarea value={draft} onChange={e=>setDraft(e.target.value)} style={{width:'100%',height:220}} />
              <div style={{marginTop:8}}>
                <button onClick={()=>sendEmail(selected.id)}>Send (simulate)</button>
              </div>
            </div>
          </div>
        ) : (
          <div>Select an email to view</div>
        )}
      </div>
    </div>
  )
}
